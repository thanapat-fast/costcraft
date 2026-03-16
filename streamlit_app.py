import streamlit as st
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CostCraft Pro", layout="wide")

st.title("🍫 CostCraft")
st.subheader("Smart Kitchen Inventory & Cost System")

# -----------------------
# SESSION STATE (ฐานข้อมูล)
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
    st.header("📊 บทสรุปการผลิต")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        df_hist["ต้นทุนรวม (บาท)"] = pd.to_numeric(df_hist["ต้นทุนรวม (บาท)"])
        
        st.subheader("📝 สรุปยอดสะสมรายเมนู")
        summary_df = df_hist.groupby("เมนู").agg({
            "เมนู": "count",
            "ต้นทุนรวม (บาท)": "sum"
        }).rename(columns={"เมนู": "จำนวนครั้งที่ผลิต", "ต้นทุนรวม (บาท)": "ต้นทุนสะสมรวม (บาท)"})
        st.table(summary_df)

        st.divider()
        st.subheader("📜 ประวัติการผลิตรายครั้ง")
        st.dataframe(df_hist.iloc[::-1], use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลการผลิตในระบบ")

# -----------------------
# TAB 2: INVENTORY (พิมพ์ตัวเลขเอง ไม่มีปุ่มบวกลบ)
# -----------------------
with tab2:
    st.header("📦 คลังวัตถุดิบ")
    st.dataframe(st.session_state.inventory, use_container_width=True)
    
    with st.expander("➕ เพิ่มวัตถุดิบใหม่"):
        with st.form("add_inv_form"):
            n = st.text_input("ชื่อวัตถุดิบ")
            # step=None ทำให้ไม่มีปุ่มลูกศรบวกลบ
            s = st.number_input("ปริมาณเริ่มต้น", min_value=0.0, step=None, value=100.0)
            u = st.text_input("หน่วย", value="g")
            p = st.number_input("ราคาต่อหน่วย", format="%.4f", step=None)
            
            if st.form_submit_button("บันทึก"):
                if n:
                    new_item = pd.DataFrame([{"name":n, "stock":s, "unit":u, "price":p}])
                    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
                    st.rerun()

# -----------------------
# TAB 3: RECIPES (พิมพ์ปริมาณได้แน่นอน 100%)
# -----------------------
with tab3:
    st.header("🍪 จัดการสูตรอาหาร")
    for r_name, r_ing in st.session_state.recipes.items():
        with st.expander(f"📖 สูตร: {r_name}"):
            for i, q in r_ing.items():
                st.write(f"- {i}: {q} g")
    
    st.divider()
    st.subheader("➕ สร้างสูตรใหม่")
    
    new_menu_name = st.text_input("ชื่อเมนูใหม่", key="new_menu_name")
    available_ing = st.session_state.inventory["name"].tolist()
    
    # ใช้ TextColumn เพื่อให้คลิกแล้วพิมพ์เลขได้ทันที (ไม่มีบั๊กเด้งกลับเป็น 0)
    df_init = pd.DataFrame([{"วัตถุดิบ": None, "ปริมาณ (g)": "0"}])

    edited_recipe = st.data_editor(
        df_init,
        num_rows="dynamic",
        column_config={
            "วัตถุดิบ": st.column_config.SelectboxColumn("เลือกวัตถุดิบ", options=available_ing, width="large"),
            "ปริมาณ (g)": st.column_config.TextColumn(
                "ปริมาณ (g)", 
                help="คลิกแล้วพิมพ์ตัวเลขได้เลย",
                placeholder="เช่น 150"
            )
        },
        use_container_width=True,
        key="recipe_editor_v6"
    )

    if st.button("💾 บันทึกสูตรอาหาร"):
        if not new_menu_name:
            st.error("กรุณาระบุชื่อเมนู")
        else:
            try:
                # กรองแถวที่เลือกวัตถุดิบไว้
                clean_df = edited_recipe.dropna(subset=["วัตถุดิบ"])
                if not clean_df.empty:
                    new_dict = {}
                    for _, row in clean_df.iterrows():
                        # แปลงข้อความเป็นตัวเลข
                        val = float(str(row["ปริมาณ (g)"]).replace(',', ''))
                        new_dict[row["วัตถุดิบ"]] = val
                    
                    st.session_state.recipes[new_menu_name] = new_dict
                    st.success(f"บันทึกสูตร {new_menu_name} สำเร็จ!")
                    st.rerun()
                else:
                    st.error("กรุณาเลือกส่วนผสมในตาราง")
            except ValueError:
                st.error("❌ กรุณากรอกเฉพาะ 'ตัวเลข' ในช่องปริมาณ (ห้ามใส่ตัวอักษร)")

# -----------------------
# TAB 4: PRODUCTION (มีปุ่มบวกลบเฉพาะที่นี่)
# -----------------------
with tab4:
    st.header("🏭 ระบบผลิต")
    menu_sel = st.selectbox("เลือกเมนู", list(st.session_state.recipes.keys()))
    
    # ส่วนเดียวที่ยอมให้มีปุ่มบวกลบ (step=1)
    qty_sel = st.number_input("จำนวนที่ผลิต (ชุด)", min_value=1, value=1, step=1)
    
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
                
        st.info(f"💰 ต้นทุนรวมรอบนี้: {cost:.2f} บาท")
        
        if st.button("🚀 ยืนยันการผลิต"):
            if can_make:
                for ing, amt in recipe.items():
                    st.session_state.inventory.loc[st.session_state.inventory["name"] == ing, "stock"] -= (amt * qty_sel)
                
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M") 
                st.session_state.history.append({
                    "วันที่-เวลา": timestamp,
                    "เมนู": menu_sel, 
                    "จำนวน": f"{qty_sel} สูตร", 
                    "ต้นทุนรวม (บาท)": cost
                })
                st.success("ผลิตสำเร็จ!")
                st.balloons()
                st.rerun()
