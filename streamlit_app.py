import streamlit as st

# --- CostCraft: Core Logic Simulation ---

# 1. จำลองฐานข้อมูลวัตถุดิบ (Inventory)
inventory = {
    "แป้งสาลี": {"amount": 1000, "unit": "กรัม", "price_per_unit": 0.05},
    "น้ำตาล": {"amount": 500, "unit": "กรัม", "price_per_unit": 0.03},
    "เนย": {"amount": 200, "unit": "กรัม", "price_per_unit": 0.20}
}

# 2. สูตรอาหาร
recipes = {
    "บราวนี่": {
        "แป้งสาลี": 100,
        "น้ำตาล": 150,
        "เนย": 50
    }
}

# UI
st.title("🍫 CostCraft")
st.write("ระบบคำนวณต้นทุนและจัดการสต็อกวัตถุดิบสำหรับร้านอาหาร")

menu = st.selectbox("เลือกเมนู", list(recipes.keys()))
quantity = st.number_input("จำนวนที่ต้องการผลิต", min_value=1, value=1)

def calculate_and_deduct(menu_name, quantity):
    recipe = recipes[menu_name]
    total_cost = 0
    can_produce = True
    messages = []

    # ตรวจสอบสต็อก
    for ingredient, amount_needed in recipe.items():
        required = amount_needed * quantity
        current_stock = inventory[ingredient]["amount"]

        if current_stock < required:
            messages.append(
                f"❌ ของไม่พอ! {ingredient} ขาดอีก {required-current_stock} {inventory[ingredient]['unit']}"
            )
            can_produce = False

        total_cost += required * inventory[ingredient]["price_per_unit"]

    if can_produce:
        for ingredient, amount_needed in recipe.items():
            required = amount_needed * quantity
            inventory[ingredient]["amount"] -= required

        messages.append(f"✅ ผลิตสำเร็จ!")
        messages.append(f"💰 ต้นทุนรวม: {total_cost:.2f} บาท")
        messages.append("📦 สต็อกคงเหลือ:")

        for item, data in inventory.items():
            messages.append(f"- {item}: {data['amount']} {data['unit']}")
    else:
        messages.append("⚠️ การผลิตล้มเหลวเนื่องจากวัตถุดิบไม่พอ")

    return messages


if st.button("เริ่มผลิต"):
    results = calculate_and_deduct(menu, quantity)
    for line in results:
        st.write(line)
