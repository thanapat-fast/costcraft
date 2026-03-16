# -----------------------
# TAB 3: RECIPES (ฉบับแก้ TypeError แน่นอน)
# -----------------------
with tab3:
    st.header("🍪 จัดการสูตรอาหาร")
    for r_name, r_ing in st.session_state.recipes.items():
        with st.expander(f"📖 สูตร: {r_name}"):
            for i, q in r_ing.items():
                st.write(f"- {i}: {q} g")
    
    st.divider()
    st.subheader("➕ สร้างสูตรใหม่")
    
    new_menu_name = st.text_input("ชื่อเมนูใหม่", key="menu_input_unique")
    available_ing = st.session_state.inventory["name"].tolist()
    
    # แก้จุดตาย: กำหนดให้ค่าเริ่มต้นในตารางเป็นข้อความ "0" เพื่อให้เข้ากับ TextColumn
    df_init = pd.DataFrame([{"วัตถุดิบ": None, "ปริมาณ (g)": "0"}])

    edited_recipe = st.data_editor(
        df_init,
        num_rows="dynamic",
        column_config={
            "วัตถุดิบ": st.column_config.SelectboxColumn(
                "เลือกวัตถุดิบ", 
                options=available_ing,
                width="large"
            ),
            "ปริมาณ (g)": st.column_config.TextColumn(
                "ปริมาณ (g)", 
                placeholder="พิมพ์เลขที่นี่ (เช่น 100)"
            )
        },
        use_container_width=True,
        key="recipe_editor_vFinal"
    )

    if st.button("💾 บันทึกสูตรอาหาร"):
        if not new_menu_name:
            st.error("กรุณาระบุชื่อเมนู")
        else:
            try:
                # กรองเอาเฉพาะแถวที่มีการเลือกวัตถุดิบ
                valid_rows = edited_recipe.dropna(subset=["วัตถุดิบ"])
                
                if not valid_rows.empty:
                    new_dict = {}
                    for _, row in valid_rows.iterrows():
                        # แปลงข้อความกลับเป็นตัวเลขตอนบันทึก
                        # ใช้ str() ครอบเพื่อให้แน่ใจว่าเป็นข้อความก่อนเปลี่ยนเป็น float
                        val_str = str(row["ปริมาณ (g)"]).strip()
                        val = float(val_str) if val_str else 0.0
                        new_dict[row["วัตถุดิบ"]] = val
                    
                    st.session_state.recipes[new_menu_name] = new_dict
                    st.success(f"บันทึกสูตร {new_menu_name} สำเร็จ!")
                    st.rerun()
                else:
                    st.error("กรุณาเพิ่มส่วนผสมอย่างน้อย 1 อย่าง")
            except ValueError:
                st.error("❌ ช่องปริมาณต้องพิมพ์เป็น 'ตัวเลข' เท่านั้นครับ")

