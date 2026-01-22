# Hướng dẫn chạy Bot trên Termux Android

## 📱 Cài đặt Termux

1. **Tải Termux:**
   - Tải từ F-Droid: https://f-droid.org/packages/com.termux/
   - KHÔNG dùng Google Play (phiên bản cũ)

2. **Cập nhật packages:**
```bash
pkg update && pkg upgrade -y
```

## 🔧 Cài đặt môi trường

```bash
# Cài Python, Git và các tools cần thiết
pkg install python git nano openssh -y

# Cài pip packages
pip install --upgrade pip
```

## 📥 Clone và setup bot

```bash
# Clone repo (hoặc copy từ máy tính)
cd ~
git clone <your-repo-url> shb-alert-bot
# HOẶC dùng scp/rsync để copy từ máy tính

cd shb-alert-bot

# Tạo virtual environment
python -m venv env
source env/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

## ⚙️ Cấu hình

```bash
# Tạo file .env
nano .env
```

Paste nội dung (Ctrl+X để save):
```
TELEGRAM_BOT_TOKEN=8564763751:AAFt8SzV_hu7duVu6dCvVGjLQJphCd7wnWs
TELEGRAM_CHAT_ID=6134211810
STOCK_SYMBOL=SHB
HEALTH_CHECK_ENABLED=false
```

## 🚀 Chạy Bot

### Cách 1: Chạy background (không cần giữ terminal)
```bash
./start.sh background
```

Bot sẽ chạy nền, bạn có thể đóng Termux!

### Cách 2: Chạy foreground (debug)
```bash
./start.sh
```

## 📋 Các lệnh quản lý

```bash
# Xem logs
tail -f logs/bot.log

# Xem status
./status.sh

# Dừng bot
./stop.sh

# Khởi động lại
./stop.sh && ./start.sh background
```

## 📱 Sử dụng Bot qua Telegram

Gửi các lệnh sau trong chat với bot:

```
/start - Xem hướng dẫn
/buy 16500 1000 - Thêm vị thế mua 1000 CP @ 16,500 VND
/position - Xem tất cả vị thế hiện tại
```

Bot tự động gửi giá mỗi 5 phút! ⏰

## 🔄 Auto-start khi khởi động Android (Optional)

1. **Cài Termux:Boot:**
   - Tải từ F-Droid: https://f-droid.org/packages/com.termux.boot/

2. **Tạo script auto-start:**
```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-bot.sh
```

Nội dung:
```bash
#!/data/data/com.termux/files/usr/bin/bash
cd ~/shb-alert-bot
./start.sh background
```

```bash
chmod +x ~/.termux/boot/start-bot.sh
```

3. **Reboot Android** - Bot sẽ tự động chạy!

## 🛡️ Keep Termux alive

### Cách 1: Termux:Boot (recommended)
- Như hướng dẫn trên

### Cách 2: Acquire Wake Lock
```bash
termux-wake-lock
```

### Cách 3: Dùng Termux:Widget
- Tạo shortcut trên home screen để start/stop bot

## 📊 Kiểm tra Bot hoạt động

```bash
# Xem process
ps aux | grep python

# Xem logs realtime
tail -f logs/bot.log

# Test Telegram
# Gửi /position trong chat với bot
```

## ⚠️ Lưu ý quan trọng

1. **Termux cần quyền:**
   - Storage: `termux-setup-storage`
   - Battery optimization: Tắt "Battery optimization" cho Termux

2. **Mạng:**
   - Bot cần internet liên tục
   - Nên dùng WiFi thay vì 4G (tiết kiệm data)

3. **Giữ điện thoại:**
   - Cắm sạc khi chạy lâu
   - Hoặc dùng điện thoại cũ làm server

4. **Backup:**
```bash
# Backup vị thế
cp storage/data.json storage/data.json.backup
```

## 🔧 Troubleshooting

### Bot không chạy background
```bash
# Thử dùng screen
pkg install screen -y
screen -S bot
./start.sh
# Nhấn Ctrl+A rồi D để detach
```

### Bot bị kill
```bash
# Check log
cat logs/bot.log

# Khởi động lại
./start.sh background
```

### Không nhận được thông báo
```bash
# Test connection
python -c "from services.notify_service import Notifier; n = Notifier('TOKEN', 'CHAT_ID'); n.send('Test')"
```

## 🎯 Kết quả

✅ Bot chạy 24/7 trên Android
✅ Không cần máy tính
✅ Tự động gửi giá mỗi 5 phút
✅ Nhận lệnh mua qua Telegram
✅ Auto-start khi reboot

## 💡 Tips

- Dùng điện thoại Android cũ làm server
- Đặt điện thoại ở nơi thoáng mát
- Bật "Developer options" → "Stay awake when charging"
- Backup `.env` và `storage/data.json` thường xuyên
