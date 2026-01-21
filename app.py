import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime

# === 页面配置 ===
st.set_page_config(page_title="震宝单证系统", layout="centered")
st.title("📄 震宝外贸单证自动生成系统")
st.markdown("---")

# === 第一部分：买家与合同信息 ===
st.header("1️⃣ 基础信息 (Basic Info)")
col1, col2 = st.columns(2)

with col1:
    buyer_name = st.text_input("买方名称 (Buyer Name)", "LLC OSIYO KOSMETIK")
    contract_no = st.text_input("合同号 (Contract No)", "ZB2025-001")
    date_input = st.date_input("签约日期 (Date)", datetime.today())

with col2:
    buyer_address = st.text_area("买方地址 (Address)", height=100)
    # 这里是您要求的：运输方式
    shipping_method = st.text_input("运输方式 (Shipping)", "By Truck")

# === 第二部分：关键商业条款 (您要求的重点) ===
st.markdown("---")
st.header("2️⃣ 商业条款 (Terms)")

col3, col4 = st.columns(2)
with col3:
    # 这里是您要求的：付款方式
    payment_terms = st.selectbox(
        "付款方式 (Payment Terms)", 
        ["30% Deposit, 70% Balance before shipment", 
         "100% T/T in advance", 
         "L/C at sight"]
    )

with col4:
    # 这里是您要求的：交货日期
    lead_time = st.text_input("交货期 (Lead Time)", "20 Working Days after deposit")

# === 第三部分：产品明细 (您要求的产品、数量、价格) ===
st.markdown("---")
st.header("3️⃣ 产品明细 (Products)")
st.info("💡 提示：直接点击下方的表格，修改品名、数量和价格。")

# 初始化数据
if 'df' not in st.session_state:
    data = {
        "序号": [1, 2],
        "英文品名 (Desc En)": ["Folding Machine", "Water Tank"],
        "中文品名 (Desc Cn)": ["折叠机", "水箱"],
        "数量 (Qty)": [1, 1],
        "单位 (Unit)": ["Set", "Pcs"],
        "单价 (Price USD)": [34200.00, 5000.00]
    }
    st.session_state.df = pd.DataFrame(data)

# 显示可编辑表格 (关键：允许添加和删除行)
edited_df = st.data_editor(
    st.session_state.df, 
    num_rows="dynamic", # 允许用户自己加行
    use_container_width=True,
    column_config={
        "单价 (Price USD)": st.column_config.NumberColumn(format="$%.2f")
    }
)

# === 第四部分：生成按钮 ===
st.markdown("---")
if st.button("🚀 生成合同文件 (Generate Contract)", type="primary", use_container_width=True):
    
    # 1. 自动计算总价
    items = []
    total_amount = 0
    
    for idx, row in edited_df.iterrows():
        qty = float(row['数量 (Qty)'])
        price = float(row['单价 (Price USD)'])
        total = qty * price
        
        items.append({
            'no': row['序号'],
            'desc_
