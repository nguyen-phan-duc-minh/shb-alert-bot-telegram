# 🤖 SHB Alert Bot

Bot Telegram theo dõi giá cổ phiếu SHB trên thị trường chứng khoán Việt Nam, tự động gửi cảnh báo khi có cơ hội mua/bán theo chiến lược được cấu hình.

## ✨ Tính năng

- 📊 **Theo dõi giá thời gian thực**: Lấy dữ liệu từ API VND Direct hoặc SSI
- 🔔 **Cảnh báo thông minh**: Thông báo khi giá đạt ngưỡng mua thêm hoặc chốt lời
- 📈 **Quản lý vị thế**: Hỗ trợ quản lý nhiều lớp mua vào (DCA)
- ⏰ **Theo giờ giao dịch**: Chỉ hoạt động trong giờ mở cửa thị trường
- 🔄 **Retry logic**: Tự động thử lại khi API lỗi
- 📝 **Logging đầy đủ**: Ghi log chi tiết với rotation
- 🏥 **Health check**: HTTP endpoint để monitor trạng thái bot
- 🐳 **Docker ready**: Dễ dàng deploy với Docker
- 💾 **Backup tự động**: Tự động backup dữ liệu vị thế

## 📋 Yêu cầu

- Python 3.12+
- Telegram Bot Token
- Telegram Chat ID

## 🚀 Cài đặt nhanh (5 phút)

### Bước 1: Setup tự động
```bash
chmod +x setup.sh
./setup.sh
```

### Bước 2: Lấy Telegram Bot Token
1. Chat với [@BotFather](https://t.me/BotFather) trên Telegram
2. Gửi `/newbot` và làm theo hướng dẫn
3. Copy token được cung cấp

### Bước 3: Lấy Chat ID
1. Chat với [@userinfobot](https://t.me/userinfobot)
2. Copy ID được trả về

### Bước 4: Cấu hình .env
```bash
nano .env  # hoặc code .env
```

Sửa 2 dòng bắt buộc:
```bash
TELEGRAM_BOT_TOKEN=paste_your_token_here
TELEGRAM_CHAT_ID=paste_your_chat_id_here
```

### Bước 5: Chạy bot
```bash
./start.sh
```

## ⚙️ Cấu hình chiến lược

Mở file `.env` và tùy chỉnh:

```bash
# Chiến lược giao dịch
STRATEGY_DOWN_THRESHOLD=0.3  # Giảm 0.3 VND → Thông báo mua thêm
STRATEGY_UP_THRESHOLD=0.5    # Tăng 0.5 VND → Thông báo chốt lời
STRATEGY_COOLDOWN_MINUTES=15 # Thời gian giữa các thông báo (phút)

# API Provider (vnd hoặc ssi)
STOCK_API_PROVIDER=vnd

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 📊 Quản lý vị thế

Thêm các lớp mua vào trong `storage/data.json`:

```json
{
  "layers": [
    {
      "price": 15.5,
      "quantity": 1000,
      "time": "2026-01-21T10:00:00"
    },
    {
      "price": 15.2,
      "quantity": 500,
      "time": "2026-01-21T14:15:00"
    }
  ]
}
```

Bot sẽ tự động:
- Tính giá trung bình
- Đề xuất mua thêm khi giá giảm dưới ngưỡng
- Đề xuất chốt lời khi giá tăng đạt mục tiêu

## 🎯 Sử dụng

### Scripts tiện ích

```bash
# Khởi động bot
./start.sh

# Kiểm tra trạng thái
./status.sh

# Dừng bot
./stop.sh
```

### Docker (tùy chọn)

```bash
# Build và chạy
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng
docker-compose down
```

## 🏥 Health Check & Monitoring

```bash
# Kiểm tra trạng thái bot
curl http://localhost:8080/health

# Xem metrics
curl http://localhost:8080/metrics
```

Response mẫu:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-21T10:30:00",
  "details": {
    "status": "running",
    "last_price": 16.2,
    "total_checks": 1234,
    "total_alerts": 45
  }
}
```

## 📝 Logs

```bash
# Xem logs realtime
tail -f logs/bot.log

# Xem logs lỗi
grep "ERROR" logs/bot.log
```

## 🔧 Troubleshooting

### Bot không khởi động
```bash
# Kiểm tra config
python -c "from core.config import Config; Config.validate()"

# Xem logs
tail -50 logs/bot.log
```

### Không nhận thông báo Telegram
```bash
# Test kết nối
python -c "from services.notify_service import Notifier; from core.config import Config; Notifier(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID).send('Test')"
```

### API lỗi liên tục
- Kiểm tra internet
- Thử đổi provider: `STOCK_API_PROVIDER=ssi` trong .env

## 📁 Cấu trúc dự án

```
shb-alert-bot/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env                    # Configuration
├── .env.example           # Template
├── .gitignore             # Git ignore
├── README.md              # Documentation
├── LICENSE                # MIT License
├── Dockerfile             # Docker image
├── docker-compose.yml     # Docker compose
├── setup.sh               # Auto setup
├── start.sh               # Start script
├── stop.sh                # Stop script
├── status.sh              # Status check
├── core/                  # Core logic
│   ├── config.py          # Config management
│   ├── position.py        # Position tracking
│   ├── strategy.py        # Trading strategy
│   ├── market_time.py     # Market hours
│   └── calculator.py      # P&L calc
├── services/              # External services
│   ├── price_service.py   # Stock API
│   └── notify_service.py  # Telegram
├── utils/                 # Utilities
│   ├── logger.py          # Logging
│   ├── data_store.py      # Data persistence
│   └── health_check.py    # Health check
├── storage/               # Data storage
│   ├── data.json          # Position data
│   └── backup/            # Backups
└── logs/                  # Log files
    └── bot.log
```

## 🔐 Bảo mật

- ✅ Không commit `.env` vào git
- ✅ Token từ environment variables
- ✅ Docker container chạy non-root user
- ✅ Logs không chứa thông tin nhạy cảm

## ⚠️ Disclaimer

Bot này chỉ mang tính chất hỗ trợ thông tin. Người dùng tự chịu trách nhiệm về quyết định đầu tư của mình.

## 📄 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.

---

**Happy Trading! 📈💰**

# shb-alert-bot-telegram
