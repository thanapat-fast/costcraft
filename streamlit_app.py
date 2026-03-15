# --- CostCraft: Core Logic Simulation ---

# 1. จำลองฐานข้อมูลวัตถุดิบ (Inventory)
# เก็บข้อมูล: ปริมาณที่มีอยู่ (Stock) และ ราคาต่อหน่วย (Price per gram)
inventory = {
    "แป้งสาลี": {"amount": 1000, "unit": "กรัม", "price_per_unit": 0.05},  # 50 บาท/กก.
    "น้ำตาล": {"amount": 500, "unit": "กรัม", "price_per_unit": 0.03},   # 30 บาท/กก.
    "เนย": {"amount": 200, "unit": "กรัม", "price_per_unit": 0.20}      # 200 บาท/กก.
}

# 2. จำลองฐานข้อมูลสูตรอาหาร (Recipe)
# 1 สูตรของ 'บราวนี่' ใช้ส่วนผสมดังนี้
recipes = {
    "บราวนี่": {
        "แป้งสาลี": 100,
        "น้ำตาล": 150,
        "เนย": 50
    }
}

def calculate_and_deduct(menu_name, quantity):
    print(f"\n--- กำลังประมวลผลการผลิต: {menu_name} จำนวน {quantity} ชุด ---")
    
    if menu_name not in recipes:
        print("ไม่พบข้อมูลสูตรอาหารนี้")
        return

    recipe = recipes[menu_name]
    total_cost = 0
    can_produce = True

    # ขั้นตอนที่ 1: ตรวจสอบว่าของในสต็อกพอไหม และคำนวณต้นทุน
    for ingredient, amount_needed in recipe.items():
        required = amount_needed * quantity
        current_stock = inventory[ingredient]["amount"]
        
        if current_stock < required:
            print(f"❌ ของไม่พอ! {ingredient} ขาดอีก {required - current_stock} {inventory[ingredient]['unit']}")
            can_produce = False
        
        # คำนวณต้นทุนรวม (ปริมาณที่ใช้ x ราคาต่อหน่วย)
        total_cost += required * inventory[ingredient]["price_per_unit"]

    # ขั้นตอนที่ 2: ถ้าของพอ ให้ดำเนินการตัดสต็อก (Deduct)
    if can_produce:
        for ingredient, amount_needed in recipe.items():
            required = amount_needed * quantity
            inventory[ingredient]["amount"] -= required
        
        print(f"✅ ผลิตสำเร็จ!")
        print(f"💰 ต้นทุนการผลิตรอบนี้: {total_cost:.2f} บาท")
        print("📦 สต็อกคงเหลือปัจจุบัน:")
        for item, data in inventory.items():
            print(f" - {item}: {data['amount']} {data['unit']}")
    else:
        print("⚠️ การผลิตล้มเหลวเนื่องจากวัตถุดิบไม่เพียงพอ")

# --- ทดลองรันระบบ ---
# ครั้งที่ 1: สั่งผลิตบราวนี่ 2 ชุด
calculate_and_deduct("บราวนี่", 2)

# ครั้งที่ 2: สั่งผลิตบราวนี่ 5 ชุด (ลองทดสอบกรณีของไม่พอ)
calculate_and_deduct("บราวนี่", 5)
