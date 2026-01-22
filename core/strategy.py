from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

class Strategy:
    def __init__(self, config):
        self.config = config
        self.last_notify = {}

    def can_notify(self, key, cooldown_minutes=15): # kiem tra co the gui thong bao khong
        now = datetime.now()
        last = self.last_notify.get(key)

        if not last or now - last > timedelta(minutes=cooldown_minutes):
            self.last_notify[key] = now
            logger.debug(f"Notification allowed for key: {key}")
            return True
        
        remaining = cooldown_minutes - (now - last).seconds // 60
        logger.debug(f"Notification blocked for key: {key}, cooldown remaining: {remaining}m")
        return False

    def check(self, price, position):
        messages = []

        avg = position.average_price()
        qty = position.total_quantity()
        
        logger.debug(f"Strategy check - Price: {price}, Avg: {avg}, Qty: {qty}")

        if qty == 0:
            target = price
            if abs(price - target) <= self.config["strategy"]["pre_buy_range"]:
                if self.can_notify("pre_buy"):
                    msg = f"🔔 {self.config['symbol']} gần vùng mua\nGiá hiện tại: {price}"
                    messages.append(msg)
                    logger.info(f"Alert: Pre-buy zone - {msg}")
            return messages

        down = self.config["strategy"]["down_threshold"]
        up = self.config["strategy"]["up_threshold"]

        if price <= avg - down:
            if self.can_notify("buy_more"):
                pnl_pct = ((price - avg) / avg) * 100
                msg = (
                    f"📉 {self.config['symbol']} giảm đủ ngưỡng mua thêm\n"
                    f"Avg: {avg:.2f} | Giá hiện tại: {price}\n"
                    f"Lỗ: {pnl_pct:.2f}%"
                )
                messages.append(msg)
                logger.info(f"Alert: Buy more signal - {msg}")

        if price >= avg + up:
            if self.can_notify("sell"):
                pnl_pct = ((price - avg) / avg) * 100
                profit = (price - avg) * qty
                msg = (
                    f"📈 {self.config['symbol']} đạt ngưỡng chốt lời\n"
                    f"Avg: {avg:.2f} | Giá hiện tại: {price}\n"
                    f"Lời: {pnl_pct:.2f}% | +{profit:,.0f} VND"
                )
                messages.append(msg)
                logger.info(f"Alert: Sell signal - {msg}")

        return messages

