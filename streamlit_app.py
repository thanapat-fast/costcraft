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
# TAB 1: DASHBOARD & HISTORY (เพิ่มระบบประวัติละเอียด)
# -----------------------
with tab1:
    st.header("📊 ภาพรวมและประวัติการผลิต")
    
    c1, c2 = st.columns(2)
    c1.metric("จำนวนวัตถุดิบ", len(st.session_state.inventory))
    c2.metric("จำนวนสูตรอาหาร", len(st.session_state.recipes))
    
    st.divider()
    
    st.subheader("📜 ประวัติการผลิต (Log)")
    if st.session_state.history:
        # แสดงตารางประวัติจากล่าสุดขึ้นก่อน
        df_hist = pd.DataFrame(st.session_state.history)
        st.table(df_hist.iloc[::-1]) 
        
        # กราฟต้นทุนรวมแยกตามเมนู
        st.subheader("📈 สรุปต้นทุนสะสม")
        df_chart = df_hist.copy()
        df_chart["ต้นทุนรวม (บาท)"] = df_chart["ต้นทุนรวม (บาท)"].astype(float)
        st.bar_chart(df_chart.groupby("เมนู")["ต้นทุนรวม (บาท)"].sum())
    else:
        st.info("ยังไม่มีข้อมูลการผลิตในระบบ")

# -----------------------
# TAB 2: INVENTORY
# -----------------------
with tab2:
    st.header("📦 คลังวัตถุดิบ")
    st.dataframe(st.session_state.inventory, use_container_width=True)
    
    with st.expander("➕ เพิ่มวัตถุดิบใหม่"):
        with st.form("add_inv_form"):
            n = st.text_input("ชื่อวัตถุดิบ")
            s = st.number_input("ปริมาณเริ่มต้น", min_value=0.0)
            u = st.text_input("หน่วย (เช่น g, ml, pcs)")
            p = st.number_input("ราคาต่อหน่วย")
            if st.form_submit_button("เพิ่มเข้าคลัง"):
                if n:
                    new_item = pd.DataFrame([{"name":n, "stock":s, "unit":u, "price":p}])
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                    st.success("เพิ่มสำเร็จ!")
                    st.rerun()

# -----------------------
# TAB 3: RECIPES (เพิ่มสูตรและส่วนผสมได้ไม่จำกัด)
# -----------------------
with tab3:
    st.header("🍪 การจัดการสูตรอาหาร")
    
    for r_name, r_ing in st.session_state.recipes.items():
        with st.expander(f"📖 สูตร: {r_name}"):
            for i, q in r_ing.items():
                st.write(f"- {i}: {q} g")
    
    st.divider()
    st.subheader("➕ สร้างสูตรใหม่ (เพิ่มส่วนผสมได้ไม่จำกัด)")
    new_menu_name = st.text_input("ชื่อเมนูใหม่")
    
    # ดึงชื่อวัตถุดิบจากคลังมาทำตัวเลือก
    available_ing = st.session_state.inventory["name"].tolist()
    df_template = pd.DataFrame(columns=["วัตถุดิบ", "ปริมาณ (g)"])
    
    # ตารางเพิ่มส่วนผสมแบบ Dynamic
    edited_recipe = st.data_editor(
        df_template,
        num_rows="dynamic",
        column_config={
            "วัตถุดิบ": st.column_config.SelectboxColumn("เลือกวัตถุดิบ", options=available_ing, required=True),
            "ปริมาณ (g)": st.column_config.NumberColumn("ปริมาณ", min_value=0.1, required=True)
        },
        use_container_width=True,
        key="recipe_editor"
    )

    if st.button("💾 บันทึกสูตรอาหาร"):
        if not new_menu_name:
            st.error("กรุณาระบุชื่อเมนู")
        elif edited_recipe.empty or edited_recipe["วัตถุดิบ"].isnull().all():
            st.error("กรุณาเพิ่มส่วนผสมอย่างน้อย 1 อย่าง")
        else:
            new_recipe_dict = {}
            for _, row in edited_recipe.iterrows():
                if pd.notnull(row["วัตถุดิบ"]):
                    new_recipe_dict[row["วัตถุดิบ"]] = row["ปริมาณ (g)"]
            
            st.session_state.recipes[new_menu_name] = new_recipe_dict
            st.success(f"บันทึกสูตร '{new_menu_name}' สำเร็จ!")
            st.rerun()

# -----------------------
# TAB 4: PRODUCTION (บันทึกประวัติละเอียด)
# -----------------------
with tab4:
    st.header("🏭 ระบบผลิตและตัดสต็อก")
    menu_sel = st.selectbox("เลือกเมนูที่จะผลิต", list(st.session_state.recipes.keys()))
    qty_sel = st.number_input("จำนวนที่ผลิต (สูตร/ชุด)", min_value=1)
    
    if menu_sel:
        recipe = st.session_state.recipes[menu_sel]
        cost = 0.0
        can_make = True
        
        for ing, amt in recipe.items():
            need = amt * qty_sel
            stock_row = st.session_state.inventory[st.session_state.inventory["name"] == ing]
            if not stock_row.empty:
                current_stock = stock_row.iloc[0]["stock"]
                price = stock_row.iloc[0]["price"]
                if current_stock < need:
                    st.error(f"❌ {ing} ไม่พอ (ต้องการ {need}, มีอยู่ {current_stock})")
                    can_make = False
                cost += (need * price)
            else:
                st.error(f"❌ ไม่พบ {ing} ในคลัง")
                can_make = False
                
        st.info(f"💰 ต้นทุนรวมรอบนี้: {cost:.2f} บาท")
        
        if st.button("🚀 ยืนยันการผลิต"):
            if can_make:
                for ing, amt in recipe.items():
                    st.session_state.inventory.loc[st.session_state.inventory["name"] == ing, "stock"] -= (amt * qty_sel)
                
                # บันทึกประวัติแบบละเอียด: วัน/เดือน/ปี เวลา เมนู จำนวน ต้นทุน
                now = datetime.now()
                timestamp = now.strftime("%d/%m/%Y %H:%M") 
                
                st.session_state.history.append({
                    "วันที่-เวลา": timestamp,
                    "เมนู": menu_sel, 
                    "จำนวน": f"{qty_sel} สูตร", 
                    "ต้นทุนรวม (บาท)": f"{cost:.2f}"
                })
                
                st.success("การผลิตสำเร็จ! ข้อมูลถูกบันทึกลงประวัติแล้ว")
                st.balloons()
                st.rerun()
