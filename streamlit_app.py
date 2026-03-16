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
# TAB 1: DASHBOARD (สรุปต้นทุนสะสมแบบที่ต้องการ)
# -----------------------
with tab1:
    st.header("📊 บทสรุปทางธุรกิจ")
    
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        # แปลงคอลัมน์ต้นทุนให้เป็นตัวเลขเพื่อคำนวณ
        df_hist["ต้นทุนรวม (บาท)"] = pd.to_numeric(df_hist["ต้นทุนรวม (บาท)"])
        
        # --- ส่วนที่ 1: ตารางสรุปต้นทุนสะสมแยกตามเมนู ---
        st.subheader("📝 สรุปยอดสะสมรายเมนู")
        # รวมกลุ่มตามชื่อเมนู และนับจำนวนครั้ง พร้อมรวมต้นทุน
        summary_df = df_hist.groupby("เมนู").agg({
            "เมนู": "count",
            "ต้นทุนรวม (บาท)": "sum"
        }).rename(columns={"เมนู": "จำนวนครั้งที่ผลิต", "ต้นทุนรวม (บาท)": "ต้นทุนสะสมรวม (บาท)"})
        
        st.table(summary_df)
        
        # --- ส่วนที่ 2: กราฟแท่งโชว์ต้นทุนสะสม ---
        st.bar_chart(summary_df["ต้นทุนสะสมรวม (บาท)"])

        st.divider()

        # --- ส่วนที่ 3: ประวัติการผลิตแบบละเอียด (Log) ---
        st.subheader("📜 ประวัติการบันทึกรายครั้ง")
        st.dataframe(df_hist.iloc[::-1], use_container_width=True) # แสดงตัวล่าสุดก่อน
        
    else:
        st.info("ยังไม่มีข้อมูลการผลิต โปรดไปที่หน้า 'ระบบผลิต' เพื่อเริ่มบันทึกข้อมูล")

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
            u = st.text_input("หน่วย (g/ml/pcs)")
            p = st.number_input("ราคาต่อหน่วย")
            if st.form_submit_button("เพิ่ม"):
                if n:
                    new_item = pd.DataFrame([{"name":n, "stock":s, "unit":u, "price":p}])
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                    st.rerun()

# -----------------------
# TAB 3: RECIPES (ส่วนผสมไม่จำกัด)
# -----------------------
with tab3:
    st.header("🍪 จัดการสูตรอาหาร")
    for r_name, r_ing in st.session_state.recipes.items():
        with st.expander(f"📖 สูตร: {r_name}"):
            for i, q in r_ing.items():
                st.write(f"- {i}: {q} g")
    
    st.subheader("➕ สร้างสูตรใหม่")
    new_menu_name = st.text_input("ชื่อเมนูใหม่")
    available_ing = st.session_state.inventory["name"].tolist()
    df_template = pd.DataFrame(columns=["วัตถุดิบ", "ปริมาณ (g)"])
    
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

    if st.button("💾 บันทึกสูตร"):
        if new_menu_name and not edited_recipe.empty:
            new_recipe_dict = {row["วัตถุดิบ"]: row["ปริมาณ (g)"] for _, row in edited_recipe.iterrows() if pd.notnull(row["วัตถุดิบ"])}
            st.session_state.recipes[new_menu_name] = new_recipe_dict
            st.success(f"บันทึกสูตร {new_menu_name} สำเร็จ")
            st.rerun()

# -----------------------
# TAB 4: PRODUCTION
# -----------------------
with tab4:
    st.header("🏭 ระบบผลิต")
    menu_sel = st.selectbox("เลือกเมนู", list(st.session_state.recipes.keys()))
    qty_sel = st.number_input("จำนวนที่ผลิต (สูตร)", min_value=1)
    
    if menu_sel:
        recipe = st.session_state.recipes[menu_sel]
        cost = 0.0
        can_make = True
        
        for ing, amt in recipe.items():
            need = amt * qty_sel
            stock_row = st.session_state.inventory[st.session_state.inventory["name"] == ing]
            if not stock_row.empty and stock_row.iloc[0]["stock"] >= need:
                cost += (need * stock_row.iloc[0]["price"])
            else:
                st.error(f"❌ {ing} ไม่พอ")
                can_make = False
                
        st.info(f"💰 ต้นทุนรอบนี้: {cost:.2f} บาท")
        
        if st.button("🚀 ยืนยันการผลิต"):
            if can_make:
                for ing, amt in recipe.items():
                    st.session_state.inventory.loc[st.session_state.inventory["name"] == ing, "stock"] -= (amt * qty_sel)
                
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M") 
                st.session_state.history.append({
                    "วันที่-เวลา": timestamp,
                    "เมนู": menu_sel, 
                    "จำนวน": qty_sel, 
                    "ต้นทุนรวม (บาท)": cost
                })
                st.success("ผลิตสำเร็จ!")
                st.balloons()
                st.rerun()
