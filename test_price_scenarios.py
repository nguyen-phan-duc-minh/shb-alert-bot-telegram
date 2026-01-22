#!/usr/bin/env python3
"""
Test chi tiết các trường hợp giá cổ phiếu SHB
"""
import sys
from core.position import Position
from core.strategy import Strategy
from core.calculator import unrealized_pnl, unrealized_pnl_pct

def test_scenario(name, position, current_price, strategy, config):
    """Test một scenario cụ thể"""
    print(f"\n{'='*70}")
    print(f"📊 {name}")
    print(f"{'='*70}")
    
    avg = position.average_price()
    qty = position.total_quantity()
    
    print(f"Vị thế hiện tại:")
    print(f"  - Số lượng: {qty:,} cổ phiếu")
    print(f"  - Giá TB: {avg:.2f} VND")
    if qty > 0:
        for i, layer in enumerate(position.layers, 1):
            print(f"  - Lớp {i}: {layer.quantity:,} cp @ {layer.price:.2f} VND")
    
    print(f"\nGiá hiện tại: {current_price:.2f} VND")
    
    if qty > 0:
        pnl = unrealized_pnl(current_price, avg, qty)
        pnl_pct = unrealized_pnl_pct(current_price, avg)
        
        status = "🟢 LỜI" if pnl > 0 else "🔴 LỖ" if pnl < 0 else "⚪ HÒA"
        print(f"\nP&L: {status}")
        print(f"  - Chênh lệch: {pnl:,.0f} VND")
        print(f"  - Tỷ lệ: {pnl_pct:+.2f}%")
    
    # Check strategy
    messages = strategy.check(current_price, position)
    
    if messages:
        print(f"\n🔔 CẢNH BÁO:")
        for msg in messages:
            print(f"\n{msg}")
    else:
        print(f"\n✅ Không có cảnh báo")
    
    return len(messages) > 0

def main():
    print("="*70)
    print("🧪 TEST CHI TIẾT CÁC TRƯỜNG HỢP GIÁ CỔ PHIẾU SHB")
    print("="*70)
    
    # Cấu hình chiến lược
    config = {
        'symbol': 'SHB',
        'strategy': {
            'pre_buy_range': 0.05,
            'pre_sell_range': 0.05,
            'down_threshold': 0.3,    # Giảm 0.3 VND
            'up_threshold': 0.5,       # Tăng 0.5 VND
        }
    }
    
    strategy = Strategy(config)
    results = []
    
    # ============================================
    # SCENARIO 1: Chưa có vị thế - Giá ổn định
    # ============================================
    position1 = Position('SHB')
    has_alert = test_scenario(
        "SCENARIO 1: Chưa có vị thế - Giá ổn định",
        position1, 16.0, strategy, config
    )
    results.append(("Scenario 1", has_alert))
    
    # ============================================
    # SCENARIO 2: Có 1 lớp - Giá tăng nhẹ
    # ============================================
    position2 = Position('SHB')
    position2.add_layer(15.5, 1000)
    has_alert = test_scenario(
        "SCENARIO 2: Có 1 lớp @ 15.5 - Giá tăng nhẹ lên 15.8",
        position2, 15.8, strategy, config
    )
    results.append(("Scenario 2", has_alert))
    
    # ============================================
    # SCENARIO 3: Có 1 lớp - Giá giảm mạnh (mua thêm)
    # ============================================
    position3 = Position('SHB')
    position3.add_layer(16.0, 1000)
    has_alert = test_scenario(
        "SCENARIO 3: Có 1 lớp @ 16.0 - Giá giảm xuống 15.6 (TRIGGER MUA THÊM)",
        position3, 15.6, strategy, config
    )
    results.append(("Scenario 3 - Buy signal", has_alert))
    
    # ============================================
    # SCENARIO 4: Có 1 lớp - Giá tăng mạnh (chốt lời)
    # ============================================
    position4 = Position('SHB')
    position4.add_layer(15.0, 1000)
    has_alert = test_scenario(
        "SCENARIO 4: Có 1 lớp @ 15.0 - Giá tăng lên 15.6 (TRIGGER CHỐT LỜI)",
        position4, 15.6, strategy, config
    )
    results.append(("Scenario 4 - Sell signal", has_alert))
    
    # ============================================
    # SCENARIO 5: DCA - Nhiều lớp - Giá giảm
    # ============================================
    position5 = Position('SHB')
    position5.add_layer(16.5, 500)
    position5.add_layer(16.0, 500)
    position5.add_layer(15.5, 500)
    has_alert = test_scenario(
        "SCENARIO 5: DCA 3 lớp (16.5, 16.0, 15.5) - Giá giảm xuống 15.5",
        position5, 15.5, strategy, config
    )
    results.append(("Scenario 5 - DCA down", has_alert))
    
    # ============================================
    # SCENARIO 6: DCA - Nhiều lớp - Giá tăng về TB
    # ============================================
    position6 = Position('SHB')
    position6.add_layer(16.5, 500)
    position6.add_layer(16.0, 500)
    position6.add_layer(15.5, 500)
    avg = position6.average_price()
    has_alert = test_scenario(
        f"SCENARIO 6: DCA 3 lớp - Giá tăng về giá TB ({avg:.2f})",
        position6, avg, strategy, config
    )
    results.append(("Scenario 6 - Break even", has_alert))
    
    # ============================================
    # SCENARIO 7: DCA - Giá tăng vượt ngưỡng
    # ============================================
    position7 = Position('SHB')
    position7.add_layer(15.0, 1000)
    position7.add_layer(14.8, 500)
    avg = position7.average_price()
    target_price = avg + 0.6  # Vượt ngưỡng 0.5
    has_alert = test_scenario(
        f"SCENARIO 7: DCA 2 lớp - Giá tăng vượt ngưỡng chốt lời ({target_price:.2f})",
        position7, target_price, strategy, config
    )
    results.append(("Scenario 7 - Profit target", has_alert))
    
    # ============================================
    # SCENARIO 8: Giá giảm sâu - Lỗ nặng
    # ============================================
    position8 = Position('SHB')
    position8.add_layer(17.0, 2000)
    has_alert = test_scenario(
        "SCENARIO 8: Mua @ 17.0 - Giá giảm sâu xuống 15.5 (LỖ NẶNG)",
        position8, 15.5, strategy, config
    )
    results.append(("Scenario 8 - Heavy loss", has_alert))
    
    # ============================================
    # SCENARIO 9: Giá tăng mạnh - Lời lớn
    # ============================================
    position9 = Position('SHB')
    position9.add_layer(14.0, 3000)
    has_alert = test_scenario(
        "SCENARIO 9: Mua @ 14.0 - Giá tăng mạnh lên 17.0 (LỜI LỚN)",
        position9, 17.0, strategy, config
    )
    results.append(("Scenario 9 - Big profit", has_alert))
    
    # ============================================
    # SCENARIO 10: Giá sát ngưỡng nhưng chưa kích hoạt
    # ============================================
    position10 = Position('SHB')
    position10.add_layer(16.0, 1000)
    has_alert = test_scenario(
        "SCENARIO 10: Mua @ 16.0 - Giá 15.75 (gần ngưỡng 15.7 nhưng chưa đủ)",
        position10, 15.75, strategy, config
    )
    results.append(("Scenario 10 - Near threshold", has_alert))
    
    # ============================================
    # SUMMARY
    # ============================================
    print(f"\n{'='*70}")
    print("📊 TỔNG KẾT KẾT QUẢ TEST")
    print(f"{'='*70}")
    
    alerts_triggered = sum(1 for _, has_alert in results if has_alert)
    
    print(f"\nTổng số scenarios: {len(results)}")
    print(f"Số scenarios có cảnh báo: {alerts_triggered}")
    print(f"Số scenarios không cảnh báo: {len(results) - alerts_triggered}")
    
    print(f"\nChi tiết:")
    for scenario, has_alert in results:
        status = "🔔 CÓ CẢNH BÁO" if has_alert else "✅ Không cảnh báo"
        print(f"  {scenario}: {status}")
    
    print(f"\n{'='*70}")
    print("✅ HOÀN THÀNH KIỂM TRA!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
