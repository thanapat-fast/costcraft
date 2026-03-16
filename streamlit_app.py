import streamlit as st
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CostCraft Pro", layout="wide")

st.title("🍫 CostCraft")
st.subheader("Smart Kitchen Inventory & Cost System")

# -----------------------
# SESSION STATE (ฐานข้อมูลจำลอง)
# -----------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"name":"แป้งสาลี","stock":1000.0,"unit":"g","price":0.05},
        {"name":"น้ำตาล","stock":500.0,"unit":"g","price":0.03},
        {"name":"เนย","stock":200.0,"unit":"g","price":0.20}
    ])

if "recipes" not in st.session_state:
    st.session_state.recipes = {
        "บราวนี่": {"แป้งสาลี": 100.0, "น้ำตาล": 150.0, "เนย": 50.0}
    }

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------
# TABS
# -----------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard", 
    "📦 Inventory", 
    "🍪 Recipes", 
    "🏭 Production"
])

# -----------------------
# TAB 1: DASHBOARD
# -----------------------
with tab1:
    st.header("ภาพรวมระบบ")
    col1, col2 = st.columns(2)
    col1.metric("จำนวนวัตถุดิบ", len(st.session_state.inventory))
    col2.metric("จำนวนสูตรอาหาร", len(st.session_state.recipes))
    
    st.divider()
    st.subheader("ประวัติการผลิต")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.bar_chart(df_hist.set_index("menu")["cost"])
        st.table(df_hist)
    else:
        st.info("ยังไม่มีข้อมูลการผลิต")

# -----------------------
# TAB 2: INVENTORY (จัดการคลัง)
# -----------------------
with tab2:
    st.header("คลังวัตถุดิบ")
    st.table(st.session_state.inventory)
    
    with st.expander("➕ เพิ่มวัตถุดิบใหม่เข้าคลัง"):
        with st.form("add_inv"):
            n = st.text_input("ชื่อวัตถุดิบ")
            s = st.number_input("ปริมาณ", min_value=0.0)
            u = st.text_input("หน่วย (g/ml)")
            p = st.number_input("ราคาต่อหน่วย")
            if st.form_submit_button("เพิ่ม"):
                new_row = pd.DataFrame([{"name":n, "stock":s, "unit":u, "price":p}])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.rerun()

# -----------------------
# TAB 3: RECIPES (ฟีเจอร์เพิ่มสูตรอาหาร)
# -----------------------
with tab3:
    st.header("การจัดการสูตรอาหาร")
    
    # แสดงสูตรปัจจุบัน
    st.subheader("📖 สูตรอาหารที่มีอยู่")
    for name, ingredients in st.session_state.recipes.items():
        with st.expander(f"เมนู: {name}"):
            for ing, amt in ingredients.items():
                st.write(f"- {ing}: {amt} g")

    st.divider()
    
    # ฟอร์มเพิ่มสูตรใหม่
    st.subheader("➕ สร้างสูตรอาหารใหม่")
    with st.form("new_recipe_form"):
        new_menu_name = st.text_input("ชื่อเมนูใหม่")
        st.write("เลือกส่วนผสม (เลือกจากวัตถุดิบในคลัง)")
        
        # ดึงรายชื่อวัตถุดิบจากคลังมาทำ Dropdown
        ing_list = st.session_state.inventory["name"].tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            i1 = st.selectbox("ส่วนผสมที่ 1", ["-"] + ing_list)
            i2 = st.selectbox("ส่วนผสมที่ 2", ["-"] + ing_list)
            i3 = st.selectbox("ส่วนผสมที่ 3", ["-"] + ing_list)
        with col2:
            a1 = st.number_input("ปริมาณที่ใช้ (1)", min_value=0.0)
            a2 = st.number_input("ปริมาณที่ใช้ (2)", min_value=0.0)
            a3 = st.number_input("ปริมาณที่ใช้ (3)", min_value=0.0)
            
        if st.form_submit_button("บันทึกสูตร"):
            if new_menu_name:
                new_recipe = {}
                if i1 != "-" and a1 > 0: new_recipe[i1] = a1
                if i2 != "-" and a2 > 0: new_recipe[i2] = a2
                if i3 != "-" and a3 > 0: new_recipe[i3] = a3
                
                if new_recipe:
                    st.session_state.recipes[new_menu_name] = new_recipe
                    st.success(f"บันทึกสูตร '{new_menu_name}' สำเร็จ!")
                    st.rerun()
                else:
                    st.error("กรุณาใส่ส่วนผสมอย่างน้อย 1 อย่าง")
            else:
                st.error("กรุณาใส่ชื่อเมนู")

# -----------------------
# TAB 4: PRODUCTION (ระบบสั่งผลิตและตัดสต็อก)
# -----------------------
with tab4:
    st.header("ระบบสั่งผลิต")
    menu_sel = st.selectbox("เลือกเมนู", list(st.session_state.recipes.keys()))
    qty_sel = st.number_input("จำนวนที่ผลิต", min_value=1)
    
    if menu_sel:
        recipe = st.session_state.recipes[menu_sel]
        total_cost = 0
        can_make = True
        
        for ing, amt in recipe.items():
            need = amt * qty_sel
            # เช็คสต็อก
            stock_row = st.session_state.inventory[st.session_state.inventory["name"] == ing]
            if not stock_row.empty:
                current_stock = stock_row.iloc[0]["stock"]
                price = stock_row.iloc[0]["price"]
                if current_stock < need:
                    st.error(f"❌ {ing} ไม่พอ (มี {current_stock}, ต้องการ {need})")
                    can_make = False
                total_cost += need * price
            else:
                st.error(f"❌ ไม่พบ {ing} ในคลัง")
                can_make = False
        
        st.info(f"💰 ต้นทุนการผลิต: {total_cost:.2f} บาท")
        
        if st.button("🚀 ยืนยันการผลิต (ตัดสต็อก)"):
            if can_make:
                for ing, amt in recipe.items():
                    st.session_state.inventory.loc[st.session_state.inventory["name"] == ing, "stock"] -= (amt * qty_sel)
                
                st.session_state.history.append({
                    "menu": menu_sel, 
                    "qty": qty_sel, 
                    "cost": total_cost,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("ผลิตสำเร็จ! หักสต็อกเรียบร้อย")
                st.balloons()
                st.rerun()
