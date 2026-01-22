from datetime import datetime, time
import pytz # thu vien xu ly timezone

def is_market_open(config): # kiem tra thi truong co dang mo hay khong
    tz = pytz.timezone(config["market"]["timezone"]) # time zone cua thi truong
    now = datetime.now(tz) # lay thoi gian hien tai theo timezone

    if now.weekday() not in config["market"]["days"]: # kiem tra ngay hien tai co phai la ngay thi truong mo cua
        return False

    open_time = time.fromisoformat(config["market"]["open"]) # thoi gian thi truong mo cua
    close_time = time.fromisoformat(config["market"]["close"]) # thoi gian thi truong dong cua

    return open_time <= now.time() <= close_time # tra ve True neu thi truong dang mo cua, nguoc lai tra ve False
