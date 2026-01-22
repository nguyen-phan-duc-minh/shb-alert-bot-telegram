# 🤖 SHB Alert Bot - Hướng dẫn Sử dụng

Bot cảnh báo giá cổ phiếu SHB qua Telegram với tính năng:
- ✅ Cảnh báo tự động khi giá thay đổi
- ✅ Gửi giá mỗi 5 phút
- ✅ Quản lý vị thế mua qua Telegram
- ✅ Chạy 24/7 trên Android (Termux) hoặc máy tính

## 📱 Chạy trên Android (Termux)

**Xem hướng dẫn chi tiết: [TERMUX.md](TERMUX.md)**

### Quick Start:
```bash
# 1. Cài Termux từ F-Droid
# 2. Setup môi trường
pkg update && pkg upgrade -y
pkg install python git -y

# 3. Clone và cài đặt
cd ~ && git clone <repo> shb-alert-bot
cd shb-alert-bot
python -m venv env
source env/bin/activate
pip install -r requirements.txt

# 4. Cấu hình .env (điền token và chat_id)
nano .env

# 5. Chạy background
./start.sh background
```

Bot sẽ chạy nền, bạn có thể đóng Termux!

## 💻 Chạy trên Máy tính (Mac/Linux)

### Cài đặt:
```bash
cd shb-alert-bot
./setup.sh
```

### Chạy bot:

**Background mode (không cần giữ terminal):**
```bash
./start.sh background
```

**Foreground mode (debug):**
```bash
./start.sh
```

## 🎮 Lệnh Telegram

Gửi các lệnh sau trong chat với bot:

### `/start`
Xem hướng dẫn sử dụng

### `/buy <giá> <số_lượng>`
Thêm vị thế mua mới

**Ví dụ:**
```
/buy 16500 1000
```
→ Mua 1000 CP @ 16,500 VND

### `/position`
Xem tất cả vị thế hiện tại
- Danh sách từng lớp mua
- Giá trung bình
- Tổng số lượng
- Tổng giá trị

## 📊 Tính năng tự động

### 1. Gửi giá mỗi 5 phút ⏰
Bot tự động gửi:
- Giá hiện tại
- Giá trung bình vị thế
- Lãi/lỗ (số tiền và %)

### 2. Cảnh báo giá
Bot tự động cảnh báo khi:
- Giá gần vùng mua
- Đạt mục tiêu chốt lời
- Giá vượt ngưỡng cắt lỗ

## 🛠️ Quản lý Bot

### Xem logs:
```bash
tail -f logs/bot.log
```

### Xem status:
```bash
./status.sh
```

### Dừng bot:
```bash
./stop.sh
```

### Khởi động lại:
```bash
./stop.sh && ./start.sh background
```

## 📁 Cấu trúc File

```
shb-alert-bot/
├── .env                 # Cấu hình (token, chat_id)
├── main.py              # Bot chính
├── requirements.txt     # Dependencies
├── start.sh             # Khởi động bot
├── stop.sh              # Dừng bot
├── status.sh            # Kiểm tra status
├── TERMUX.md            # Hướng dẫn Termux chi tiết
├── storage/
│   └── data.json        # Lưu vị thế
├── logs/
│   ├── bot.log          # Logs runtime
│   └── bot.pid          # Process ID
├── core/                # Logic bot
├── services/            # Price & Notification
└── utils/               # Utilities
```

## 🔐 Cấu hình (.env)

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Stock
STOCK_SYMBOL=SHB

# Market hours (Vietnam timezone)
MARKET_OPEN_HOUR=9
MARKET_OPEN_MINUTE=0
MARKET_CLOSE_HOUR=15
MARKET_CLOSE_MINUTE=0

# Polling intervals (seconds)
POLL_INTERVAL_OPEN=60      # Check every 60s during market hours
POLL_INTERVAL_CLOSED=300   # Check every 5 minutes when closed

# Health check
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_PORT=8080
```

## 💡 Tips

### Termux Android:
- Dùng điện thoại cũ làm server 24/7
- Cài Termux:Boot để auto-start khi reboot
- Tắt Battery Optimization cho Termux
- Dùng WiFi thay vì 4G (tiết kiệm data)

### Máy tính:
- Có thể dùng `screen` hoặc `tmux` để detach terminal
- Hoặc tạo systemd service (Linux) / launchd (Mac)

## 🔄 Backup & Restore

### Backup vị thế:
```bash
cp storage/data.json storage/data.json.backup
```

### Restore:
```bash
cp storage/data.json.backup storage/data.json
```

## 📝 Ví dụ Sử dụng

### Kịch bản 1: Thêm vị thế mới
```
Bạn: /buy 16400 500
Bot: ✅ Đã thêm vị thế mua:
     Giá: 16,400 VND
     SL: 500 CP

     💼 Tổng vị thế (2 lớp):
     Giá TB: 16,425 VND
     Tổng SL: 1,500 CP
```

### Kịch bản 2: Kiểm tra vị thế
```
Bạn: /position
Bot: 💼 Vị thế SHB (2 lớp):

     1. 1,000 CP @ 16,500 VND
        🕐 22/01 09:15

     2. 500 CP @ 16,400 VND
        🕐 22/01 10:30

     📈 Tổng kết:
     Giá TB: 16,425 VND
     Tổng SL: 1,500 CP
     Tổng giá trị: 24,637,500 VND
```

### Kịch bản 3: Cập nhật giá tự động (mỗi 5 phút)
```
Bot: 📊 Giá SHB: 16,450 VND
     🕐 11:32:06

     💼 Vị thế:
     Giá TB: 16,425 VND
     SL: 1,500 CP
     Lãi/Lỗ: +37,500 (+0.15%)
```

## ⚠️ Lưu ý

1. **Dữ liệu giá:** Bot dùng thư viện `vnstock` lấy từ nguồn HOSE/VCI
2. **Giờ giao dịch:** Mặc định 9:00-15:00 (có thể config trong .env)
3. **Vị thế:** Lưu local trong `storage/data.json` - nhớ backup!
4. **Internet:** Bot cần kết nối internet liên tục

## 🐛 Troubleshooting

### Bot không chạy
```bash
# Kiểm tra logs
cat logs/bot.log

# Thử chạy foreground để xem lỗi
./start.sh
```

### Không nhận thông báo
```bash
# Test Telegram connection
python -c "
from services.notify_service import Notifier
from core.config import Config
n = Notifier(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID)
n.send('Test message')
"
```

### Process bị kill
```bash
# Termux: Tắt Battery Optimization
# hoặc dùng termux-wake-lock
termux-wake-lock
```

## 📚 Tài liệu thêm

- [TERMUX.md](TERMUX.md) - Hướng dẫn chi tiết cho Android
- [README.md](README.md) - Tài liệu tổng quan
- vnstock docs: https://vnstocks.com

## 🤝 Hỗ trợ

Gặp vấn đề? Tạo Issue hoặc liên hệ qua Telegram!

---

**Chúc bạn trade thành công! 🚀📈**
