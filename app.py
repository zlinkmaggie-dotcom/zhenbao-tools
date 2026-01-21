import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
import os
from datetime import datetime

# === 1. 页面基本设置 ===
st.set_page_config(page_title="震宝单证系统", layout="wide")
st.title("📄 震宝外贸单证自动生成系统")

# === 🔍 侦探模式：帮您看服务器上到底有啥 ===
# 这行字会显示在网页最上面，告诉我们文件在不在
current_files = os.listdir('.')
st.info(f"👀 服务器当前目录下的文件有：{current_files}")

# === 2. 侧边栏：模板与基础信息 ===
with st.sidebar:
    st.header("📂 模板设置 (必选)")
    
    # 🌟 双保险功能：如果GitHub文件读不到，您可以手动传！
    uploaded_template = st.file_uploader("如果不成功，请把Word模板拖到这里：", type=['docx'])
    
    st.markdown("---")
    st.header("📝 订单信息")
    buyer_name = st.text_input("买方名称 (Buyer)", "LLC OSIYO KOSMETIK")
    contract_no = st.text_input("合同号 (No.)", "ZB2025-001")
    date_input = st.date_input("日期 (Date)", datetime.today())

# === 3. 主界面：条款与产品 ===
st.header("1️⃣ 商业条款")
col1, col2 = st.columns(2)
with col1:
    payment_terms = st.selectbox("付款方式", ["30% Deposit, 70% Balance", "100% T/T", "L/C at sight"])
with col2:
    lead_time = st.text_input("交货期", "20 Working Days")
    shipping_method = st.text_input("运输方式", "By Truck")
    buyer_address = st.text_area("买方地址", "Republic of Tajikistan...")

st.markdown("---")
st.header("2️⃣ 产品列表")
# 初始化表格
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

# === 4. 生成按钮 ===
st.markdown("---")
if st.button("🚀 立即生成合同", type="primary"):
    
    # 🅰️ 确定用哪个模板
    tpl_object = None
    
    # 优先用您刚才拖进来的文件
    if uploaded_template is not None:
        tpl_object = DocxTemplate(uploaded_template)
    # 如果没拖，就去GitHub里找
    elif "template_contract.docx" in current_files:
        try:
            tpl_object = DocxTemplate("template_contract.docx")
        except Exception as e:
            st.error(f"GitHub里的模板文件损坏，请检查是否是直接改了后缀名？错误：{e}")
            st.stop()
    else:
        st.error("❌ 找不到模板！请在左侧侧边栏手动上传 template_contract.docx")
        st.stop()

    # 🅱️ 整理数据
    items = []
    total_amount = 0
    safe_df = edited_df.fillna(0) # 防止空格报错
    
    for idx, row in safe_df.iterrows():
        try:
            qty = float(row.get('数量', 0))
            price = float(row.get('单价', 0))
            if qty == 0: continue # 跳过空行
            
            total = qty * price
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
        except:
            continue

    context = {
        'buyer_name': buyer_name,
        'buyer_address': buyer_address,
        'contract_no': contract_no,
        'date': date_input.strftime("%Y-%m-%d"),
        'payment_terms': payment_terms,
        'lead_time': lead_time,
        'shipping_method': shipping_method,
        'total_amount': f"{total_amount:,.2f}",
        'items': items
    }

    # ©️ 渲染并下载
    try:
        tpl_object.render(context)
        bio = io.BytesIO()
        tpl_object.save(bio)
        bio.seek(0)
        
        st.success("✅ 生成成功！")
        st.download_button(
            label="📥 下载合同 (.docx)",
            data=bio,
            file_name=f"Contract_{contract_no}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"生成时出错：{e}")
