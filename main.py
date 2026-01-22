import time
import signal
import sys
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from core.config import Config
from core.market_time import is_market_open
from core.position import Position
from core.strategy import Strategy
from services.price_service import fetch_price, StockAPIError
from services.notify_service import Notifier
from utils.logger import get_logger
from utils.data_store import DataStore
from utils.health_check import HealthCheckServer

# Initialize logger
logger = get_logger('main')

# Global state for graceful shutdown
shutdown_requested = False

# Global instances for Telegram handlers
bot_position = None
bot_notifier = None
bot_data_store = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True

def send_price_update():
    """Send price update every 5 minutes"""
    global bot_notifier
    try:
        price = fetch_price(symbol=Config.STOCK_SYMBOL)
        current_time = datetime.now().strftime("%H:%M:%S")
        msg = f"📊 Giá {Config.STOCK_SYMBOL}: {price:,.0f} VND\n🕐 {current_time}"
        
        if bot_position and bot_position.layers:
            avg_price = bot_position.average_price()
            total_qty = bot_position.total_quantity()
            profit_loss = (price - avg_price) * total_qty
            profit_pct = ((price - avg_price) / avg_price) * 100
            
            msg += f"\n\n💼 Vị thế:\n"
            msg += f"   Giá TB: {avg_price:,.0f} VND\n"
            msg += f"   SL: {total_qty:,} CP\n"
            msg += f"   Lãi/Lỗ: {profit_loss:,.0f} ({profit_pct:+.2f}%)"
        
        if bot_notifier:
            bot_notifier.send(msg)
            logger.info(f"Sent 5-minute price update: {price}")
    except Exception as e:
        logger.error(f"Failed to send price update: {e}")

def telegram_buy_handler(update, context):
    """Handle /buy command: /buy <price> <quantity>"""
    global bot_position, bot_data_store
    try:
        if len(context.args) != 2:
            update.message.reply_text(
                "❌ Sử dụng: /buy <giá> <số_lượng>\n"
                "Ví dụ: /buy 16500 1000"
            )
            return
        
        price = float(context.args[0])
        quantity = int(context.args[1])
        
        bot_position.add_layer(price, quantity)
        
        # Save to storage
        data = {
            "layers": [
                {"price": l.price, "quantity": l.quantity, "time": l.time}
                for l in bot_position.layers
            ]
        }
        bot_data_store.save(data)
        
        avg_price = bot_position.average_price()
        total_qty = bot_position.total_quantity()
        
        msg = f"✅ Đã thêm vị thế mua:\n"
        msg += f"   Giá: {price:,.0f} VND\n"
        msg += f"   SL: {quantity:,} CP\n\n"
        msg += f"💼 Tổng vị thế ({len(bot_position.layers)} lớp):\n"
        msg += f"   Giá TB: {avg_price:,.0f} VND\n"
        msg += f"   Tổng SL: {total_qty:,} CP"
        
        update.message.reply_text(msg)
        logger.info(f"Added buy position: {quantity} @ {price}")
        
    except ValueError:
        update.message.reply_text("❌ Giá và số lượng phải là số")
    except Exception as e:
        update.message.reply_text(f"❌ Lỗi: {str(e)}")
        logger.error(f"Error in buy handler: {e}")

def telegram_position_handler(update, context):
    """Handle /position command to show current positions"""
    global bot_position
    try:
        if not bot_position or not bot_position.layers:
            update.message.reply_text("📭 Chưa có vị thế nào")
            return
        
        avg_price = bot_position.average_price()
        total_qty = bot_position.total_quantity()
        
        msg = f"💼 Vị thế {Config.STOCK_SYMBOL} ({len(bot_position.layers)} lớp):\n\n"
        
        for i, layer in enumerate(bot_position.layers, 1):
            timestamp = datetime.fromisoformat(layer.time).strftime("%d/%m %H:%M")
            msg += f"{i}. {layer.quantity:,} CP @ {layer.price:,.0f} VND\n"
            msg += f"   🕐 {timestamp}\n\n"
        
        msg += f"📈 Tổng kết:\n"
        msg += f"   Giá TB: {avg_price:,.0f} VND\n"
        msg += f"   Tổng SL: {total_qty:,} CP\n"
        msg += f"   Tổng giá trị: {avg_price * total_qty:,.0f} VND"
        
        update.message.reply_text(msg)
        
    except Exception as e:
        update.message.reply_text(f"❌ Lỗi: {str(e)}")
        logger.error(f"Error in position handler: {e}")

def telegram_start_handler(update, context):
    """Handle /start command"""
    msg = (
        f"🤖 SHB Alert Bot\n\n"
        f"Lệnh hỗ trợ:\n"
        f"/buy <giá> <SL> - Thêm vị thế mua\n"
        f"   Ví dụ: /buy 16500 1000\n\n"
        f"/position - Xem vị thế hiện tại\n\n"
        f"Bot tự động gửi giá mỗi 5 phút ⏰"
    )
    update.message.reply_text(msg)

def main():
    """Main bot loop"""
    global shutdown_requested, bot_position, bot_notifier, bot_data_store
    
    # Health check server
    health_server = None
    scheduler = None
    updater = None
    
    try:
        # Validate configuration
        logger.info("Starting SHB Alert Bot...")
        logger.info(f"Validating configuration...")
        Config.validate()
        logger.info(f"Configuration validated successfully")
        
        # Start health check server
        health_server = HealthCheckServer(
            port=Config.HEALTH_CHECK_PORT,
            enabled=Config.HEALTH_CHECK_ENABLED
        )
        health_server.start()
        HealthCheckServer.update_status('starting')
        
        # Initialize components
        logger.info(f"Initializing components for symbol: {Config.STOCK_SYMBOL}")
        
        data_store = DataStore()
        data = data_store.load()
        
        position = Position(Config.STOCK_SYMBOL)
        for layer in data.get("layers", []):
            position.add_layer(layer["price"], layer["quantity"])
        
        logger.info(f"Loaded {len(position.layers)} position layers")
        
        strategy = Strategy(Config.to_dict())
        notifier = Notifier(
            Config.TELEGRAM_BOT_TOKEN,
            Config.TELEGRAM_CHAT_ID
        )
        
        # Set global instances for Telegram handlers
        bot_position = position
        bot_notifier = notifier
        bot_data_store = data_store
        
        # Setup Telegram bot for commands
        updater = Updater(token=Config.TELEGRAM_BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', telegram_start_handler))
        dispatcher.add_handler(CommandHandler('buy', telegram_buy_handler))
        dispatcher.add_handler(CommandHandler('position', telegram_position_handler))
        updater.start_polling()
        logger.info("Telegram bot handlers registered")
        
        # Setup scheduler for 5-minute price updates
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        scheduler = BackgroundScheduler(timezone=tz)
        scheduler.add_job(
            send_price_update,
            'interval',
            minutes=5,
            id='price_update'
        )
        scheduler.start()
        logger.info("Scheduler started for 5-minute price updates")
        
        # Send first price update immediately
        send_price_update()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Send startup notification
        notifier.send(
            f"🚀 SHB Alert Bot started\n"
            f"Symbol: {Config.STOCK_SYMBOL}\n"
            f"API Provider: {Config.STOCK_API_PROVIDER}\n"
            f"Positions: {len(position.layers)} layers"
        )
        logger.info("Bot started successfully")
        HealthCheckServer.update_status('running')
        
        # Main loop
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while not shutdown_requested:
            try:
                if is_market_open(Config.to_dict()):
                    # Fetch price
                    price = fetch_price(symbol=Config.STOCK_SYMBOL)
                    logger.info(f"{Config.STOCK_SYMBOL} price: {price}")
                    
                    # Update health status
                    HealthCheckServer.update_status('running', last_price=price)
                    
                    # Check strategy
                    messages = strategy.check(price, position)
                    for msg in messages:
                        notifier.send(msg)
                        HealthCheckServer.increment_alerts()
                    
                    # Reset error counter on success
                    consecutive_errors = 0
                    
                    # Sleep during market hours
                    time.sleep(Config.POLL_INTERVAL_OPEN)
                else:
                    logger.debug("Market closed, sleeping...")
                    time.sleep(Config.POLL_INTERVAL_CLOSED)
                    
            except StockAPIError as e:
                consecutive_errors += 1
                logger.error(f"Stock API error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                HealthCheckServer.update_status('error', error=e)
                
                if consecutive_errors >= max_consecutive_errors:
                    error_msg = f"⚠️ Bot paused after {consecutive_errors} consecutive API errors. Please check API status."
                    logger.critical(error_msg)
                    notifier.send(error_msg)
                    
                    # Wait longer before retrying
                    time.sleep(300)  # 5 minutes
                    consecutive_errors = 0
                else:
                    time.sleep(60)  # Wait 1 minute before retry
                    
            except Exception as e:
                consecutive_errors += 1
                logger.exception(f"Unexpected error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                HealthCheckServer.update_status('error', error=e)
                
                try:
                    notifier.send(f"❌ Bot error: {str(e)[:200]}")
                except:
                    logger.error("Failed to send error notification")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical("Too many consecutive errors, shutting down")
                    break
                
                time.sleep(60)
        
        # Graceful shutdown
        logger.info("Shutting down gracefully...")
        HealthCheckServer.update_status('stopping')
        
        # Stop scheduler
        if scheduler:
            scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")
        
        # Stop Telegram bot
        if updater:
            updater.stop()
            logger.info("Telegram bot stopped")
        
        # Save data
        try:
            data_store.save({
                "layers": [
                    {"price": l.price, "quantity": l.quantity, "time": l.time}
                    for l in position.layers
                ]
            })
            logger.info("Data saved successfully")
        except Exception as e:
            logger.error(f"Error saving data on shutdown: {e}")
        
        # Send shutdown notification
        try:
            notifier.send("🛑 SHB Alert Bot stopped")
        except:
            logger.error("Failed to send shutdown notification")
        
        # Stop health check server
        if health_server:
            health_server.stop()
        
        logger.info("Bot stopped")
        
    except ValueError as e:
        logger.critical(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error:\n{e}\n")
        print("Please check your .env file and ensure all required variables are set correctly.")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Fatal error during startup: {e}", exc_info=True)
        print(f"\n❌ Fatal Error:\n{e}\n")
        sys.exit(1)
    
    finally:
        # Ensure health server is stopped
        if health_server:
            try:
                health_server.stop()
            except:
                pass

if __name__ == "__main__":
    main()

