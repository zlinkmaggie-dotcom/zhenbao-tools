import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# === 1. 页面设置 ===
st.set_page_config(page_title="震宝单证系统", layout="wide")
st.title("📄 震宝外贸单证自动生成系统")

# === 2. 侧边栏：上传模板与基础信息 ===
with st.sidebar:
    st.header("📂 第一步：上传模板")
    # 强制要求手动上传，确保不会因为找不到文件报错
    uploaded_template = st.file_uploader(
        "请把 Word 模板拖到这里：", 
        type=['docx'],
        help="必须是包含 {{ }} 标签的 .docx 文件"
    )
    
    st.markdown("---")
    st.header("📝 第二步：填写订单信息")
    contract_no = st.text_input("合同号 (Contract No)", "ZB2025-001")
    date_input = st.date_input("签约日期 (Date)", datetime.today())
    buyer_name = st.text_input("买方名称 (Buyer)", "LLC OSIYO KOSMETIK")

# === 3. 主界面：商业条款 ===
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

# === 4. 产品明细表格 ===
st.markdown("---")
st.header("2️⃣ 产品明细")
st.info("💡 请直接修改下方表格。注意：不要留空行，确保数量和单价都有数字。")

# 初始化数据
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

# 显示可编辑表格
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# === 5. 生成按钮逻辑 ===
st.markdown("---")
if st.button("🚀 生成合同 (Generate)", type="primary"):
    
    # 1. 检查有没有上传模板
    if uploaded_template is None:
        st.error("❌ 请先在左侧侧边栏上传 Word 模板文件！")
        st.stop()

    # 2. 准备数据
    items = []
    total_amount = 0
    
    # 防止空格报错：先把所有空值填为 0
    safe
