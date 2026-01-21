import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# === 1. 页面基本设置 ===
st.set_page_config(page_title="震宝单证系统", layout="wide")
st.title("📄 震宝外贸单证自动生成系统")

# === 2. 侧边栏：上传模板 ===
with st.sidebar:
    st.header("📂 第一步：上传模板")
    uploaded_template = st.file_uploader(
        "请把 Word 模板拖到这里：", 
        type=['docx'],
        help="必须是包含 {{ }} 标签的 .docx 文件"
    )
    
    st.markdown("---")
    st.header("📝 第二步：填写订单信息")
    contract_no = st.text_input("合同号 (No.)", "ZB2025-001")
    date_input = st.date_input("日期 (Date)", datetime.today())
    buyer_name = st.text_input("买方 (Buyer)", "LLC OSIYO KOSMETIK")

# === 3. 主界面：商业条款 ===
st.header("1️⃣ 商业条款")
col1, col2 = st.columns(2)

with col1:
    buyer_address = st.text_area("买方地址", "Republic of Tajikistan...")
    payment_terms = st.selectbox("付款方式", [
        "30% Deposit, 70% Balance before shipment", 
        "100% T/T in advance", 
        "L/C at sight"
    ])

with col2:
    lead_time = st.text_input("交货期", "20 Working Days")
    shipping_method = st.text_input("运输方式", "By Truck")

# === 4. 产品表格 ===
st.markdown("---")
st.header("2️⃣ 产品明细")
st.info("💡 提示：请直接在表格中修改数据。确保“数量”和“单价”都是数字。")

# 初始化表格数据
if 'df' not in st.session_state:
    data = {
        "序号": [1, 2],
        "英文品名": ["Folding Machine", "Water Tank"],
        "中文品名": ["折叠机", "水箱"],
        "数量": [1, 1],
        "单位": ["Set", "Pcs"],
        "单价": [34200.00, 5000.00]
    }
    st.session_state.df = pd.DataFrame(data)

# 显示表格
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# === 5. 生成按钮逻辑 ===
st.markdown("---")
if st.button("🚀 生成合同", type="primary"):
    
    # 检查模板是否上传
    if uploaded_template is None:
        st.error("❌ 请先在左侧侧边栏上传 Word 模板！")
        st.stop()

    # 准备数据容器
    items = []
    total_amount = 0
    
    # === 关键修正：防止 NameError ===
    # 下面这行就是您刚才报错的地方，这次我把它写完整了
    safe_df = edited_df.fillna(0)
    
    # 遍历表格
    for idx, row in safe_df.iterrows():
        try:
            # 获取数据，如果是空的就当成 0
            qty = float(row.get('数量', 0))
            price = float(row.get('单价', 0))
            
            # 跳过空行
            if qty == 0: continue
            
            total = qty * price
            
            # 加入列表
            items.append({
                'no': row['序号'],
                'desc_en': str(row['英文品名']),
                'desc_cn': str(row['中文品名']),
                'qty': qty,
                'unit': str(row['单位']),
                'price': f"{price:,.2f}",
                'total': f"{total:,.2f}"
            })
            total_amount += total
        except Exception:
            continue # 如果这一行数据有问题，就跳过，不让程序崩掉

    if len(items) == 0:
        st.error("❌ 表格数据无效！请填写数量和单价。")
        st.stop()

    # 打包数据
    context = {
        'contract_no': contract_no,
        'date': date_input.strftime("%Y-%m-%d"),
        'buyer_name': buyer_name,
        'buyer_address': buyer_address,
        'payment_terms': payment_terms,
        'lead_time': lead_time,
        'shipping_method': shipping_method,
        'total_amount': f"{total_amount:,.2f}",
        'items': items
    }

    # 生成文件
    try:
        doc = DocxTemplate(uploaded_template)
        doc.render(context)
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.success(f"✅ 生成成功！总金额: ${total_amount:,.2f}")
        st.download_button(
            label="📥 下载合同文件",
            data=bio,
            file_name=f"Contract_{contract_no}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"❌ 生成失败！模板可能有问题。\n错误信息: {e}")
