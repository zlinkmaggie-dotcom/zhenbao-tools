import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# === 1. 页面设置 ===
st.set_page_config(page_title="震宝单证系统", layout="wide")
st.title("📄 震宝外贸单证自动生成系统 (最终版)")

# === 2. 侧边栏：必须手动上传模板 ===
# 既然 GitHub 读取有问题，我们就强制要求在网页上传，这样绝对不会错
with st.sidebar:
    st.header("📂 第一步：上传模板")
    uploaded_template = st.file_uploader(
        "请把做好的 Word 模板拖到这里：", 
        type=['docx'],
        help="必须是包含 {{ }} 标签的 .docx 文件"
    )
    
    st.markdown("---")
    st.header("📝 第二步：填写订单信息")
    contract_no = st.text_input("合同号 (Contract No)", "ZB2025-001")
    date_input = st.date_input("签约日期 (Date)", datetime.today())
    buyer_name = st.text_input("买方名称 (Buyer)", "LLC OSIYO KOSMETIK")

# === 3. 主界面：填写详细条款 ===
st.header("1️⃣ 商业条款")
col1, col2 = st.columns(2)
with col1:
    buyer_address = st.text_area("买方地址", "Republic of Tajikistan, Dushanbe...")
    payment_terms = st.selectbox("付款方式", [
        "30% Deposit, 70% Balance before shipment", 
        "100% T/T in advance", 
        "L/C at sight"
    ])
with col2:
    lead_time = st.text_input("交货期", "20 Working Days after deposit")
    shipping_method = st.text_input("运输方式", "By Truck (Land Transportation)")

# === 4. 产品表格 ===
st.markdown("---")
st.header("2️⃣ 产品明细")
st.info("💡 请直接修改下方表格。注意：不要留空行！")

# 初始数据
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

edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# === 5. 生成按钮 ===
st.markdown("---")
if st.button("🚀 生成合同 (Generate)", type="primary"):
    
    # 检查有没有传模板
    if uploaded_template is None:
        st.error("❌ 请先在左侧侧边栏上传 Word 模板！")
        st.stop()

    # 准备数据
    items = []
    total_amount = 0
    
    # 安全处理表格数据（防止空格报错）
    safe_df = edited_df.fillna(0)
    
    for idx, row in safe_df.iterrows():
        try:
            qty = float(row.get('数量', 0))
            price = float(row.get('单价', 0))
            
            # 跳过数量为 0 的空行
            if qty == 0: continue
            
            total = qty * price
            
            items.append({
                'no': row['序号'],
                'desc_en': str(row['英文品名']),
                '
