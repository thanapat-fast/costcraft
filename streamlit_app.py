import streamlit as st
import pandas as pd

st.set_page_config(page_title="CostCraft", layout="wide")

st.title("🍫 CostCraft")
st.subheader("Smart Kitchen Inventory & Cost System")

# -----------------------
# SESSION STATE
# -----------------------

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"name":"แป้งสาลี","stock":1000,"unit":"g","price":0.05},
        {"name":"น้ำตาล","stock":500,"unit":"g","price":0.03},
        {"name":"เนย","stock":200,"unit":"g","price":0.20}
    ])

if "recipes" not in st.session_state:
    st.session_state.recipes = {
        "บราวนี่":{
            "แป้งสาลี":100,
            "น้ำตาล":150,
            "เนย":50
        }
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
# DASHBOARD
# -----------------------

with tab1:

    st.header("ภาพรวมระบบ")

    total_items = len(st.session_state.inventory)

    low_stock = st.session_state.inventory[
        st.session_state.inventory["stock"] < 100
    ]

    col1,col2 = st.columns(2)

    col1.metric("จำนวนวัตถุดิบ", total_items)
    col2.metric("วัตถุดิบใกล้หมด", len(low_stock))

    st.divider()

    st.subheader("วัตถุดิบใกล้หมด")

    if len(low_stock) > 0:
        st.warning(low_stock)
    else:
        st.success("สต็อกปกติ")

    st.divider()

    st.subheader("ต้นทุนการผลิตที่ผ่านมา")

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.bar_chart(df["cost"])
    else:
        st.info("ยังไม่มีการผลิต")

# -----------------------
# INVENTORY
# -----------------------

with tab2:

    st.header("คลังวัตถุดิบ")

    st.dataframe(st.session_state.inventory)

    st.subheader("เพิ่มวัตถุดิบ")

    name = st.text_input("ชื่อวัตถุดิบ")
    stock = st.number_input("ปริมาณ",0)
    unit = st.text_input("หน่วย")
    price = st.number_input("ราคาต่อหน่วย")

    if st.button("เพิ่มวัตถุดิบ"):

        new = pd.DataFrame([{
            "name":name,
            "stock":stock,
            "unit":unit,
            "price":price
        }])

        st.session_state.inventory = pd.concat(
            [st.session_state.inventory,new],
            ignore_index=True
        )

        st.success("เพิ่มสำเร็จ")

# -----------------------
# RECIPES
# -----------------------

with tab3:

    st.header("สูตรอาหาร")

    for r in st.session_state.recipes:

        st.subheader(r)

        recipe = st.session_state.recipes[r]

        for ing in recipe:

            st.write(ing,"-",recipe[ing],"g")

# -----------------------
# PRODUCTION
# -----------------------

with tab4:

    st.header("ระบบผลิต")

    menu = st.selectbox(
        "เลือกเมนู",
        list(st.session_state.recipes.keys())
    )

    qty = st.number_input(
        "จำนวนที่ผลิต",
        min_value=1,
        value=1
    )

    recipe = st.session_state.recipes[menu]

    cost = 0
    can_make = True

    for ing in recipe:

        need = recipe[ing] * qty

        row = st.session_state.inventory[
            st.session_state.inventory["name"] == ing
        ]

        if not row.empty:

            stock = row.iloc[0]["stock"]
            price = row.iloc[0]["price"]

            if stock < need:
                st.error(f"{ing} ไม่พอ")
                can_make = False

            cost += need * price

    st.info(f"ต้นทุนรวม {cost:.2f} บาท")

    if st.button("ผลิต"):

        if can_make:

            for ing in recipe:

                need = recipe[ing] * qty

                st.session_state.inventory.loc[
                    st.session_state.inventory["name"] == ing,
                    "stock"
                ] -= need

            st.session_state.history.append({
                "menu":menu,
                "qty":qty,
                "cost":cost
            })

            st.success("ผลิตสำเร็จ")

        else:

            st.error("วัตถุดิบไม่พอ")
            
