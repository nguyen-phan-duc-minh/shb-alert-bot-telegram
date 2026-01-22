def unrealized_pnl(current_price, avg_price, total_qty): # tinh loi nhuan chua thuc hien
    if total_qty == 0:
        return 0
    return (current_price - avg_price) * total_qty

def unrealized_pnl_pct(current_price, avg_price): # tinh ti le loi nhuan chua thuc hien
    if avg_price == 0:
        return 0
    return (current_price - avg_price) / avg_price * 100