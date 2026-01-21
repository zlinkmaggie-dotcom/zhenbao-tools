import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime

# === 1. 页面基本设置 ===
st.set_page_config(page_title="震宝单证系统", layout="wide")
st.title("📄 震宝外贸单证自动生成系统")
st.markdown("---")

# === 2. 基础信息填写区 ===
st.header("1️⃣ 订单基础信息 (Basic Info)")

# 使用列布局，让界面更紧凑
col1, col2 = st.columns(2)

with col1:
    buyer_name = st.text_input("买方名称 (Buyer Name)", "LLC OSIYO KOSMETIK")
    contract_no = st.text_input("合同号 (Contract No)", "ZB2025-001")
    date_input = st.date_input("签约日期 (Date)", datetime.today())

with col2:
    buyer_address = st.text_area("买方地址 (Address)", height=100, help="填入客户的详细地址")
    shipping_method = st.text_input("运输方式 (Shipping)", "By Truck (Land Transportation)")

# === 3. 商业条款填写区 ===
st.markdown("---")
st.header("2️⃣ 商业条款 (Terms)")

col3, col4 = st.columns(2)
with col3:
    payment_terms = st.selectbox(
        "付款方式 (Payment Terms)", 
        [
            "30% Deposit, 70% Balance before shipment", 
            "100% T/T in advance", 
            "L/C at sight",
            "50% Deposit, 50% Balance against B/L copy"
        ]
    )

with col4:
    lead_time = st.text_input("交货期 (Lead Time)", "20 Working Days after deposit")

# === 4. 产品明细填写区 ===
st.markdown("---")
st.header("3️⃣ 产品明细 (Products)")
st.info("💡 操作提示：直接在表格里修改内容。点击表格下方的 '+' 号可以添加新产品。")

# 初始化表格数据
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

# 显示可编辑表格
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic", # 允许添加/删除行
    use_container_width=True,
    column_config={
        "单价 (Price USD)": st.column_config.NumberColumn(format="$%.2f", step=0.01),
        "数量 (Qty)": st.column_config.NumberColumn(step=1),
        "序号": st.column_config.NumberColumn(step=1)
    }
)

# === 5. 生成按钮与核心逻辑 ===
st.markdown("---")
if st.button("🚀 生成合同文件 (Generate Contract)", type="primary", use_container_width=True):
    
    # --- A. 整理数据 ---
    items = []
    total_amount = 0
    
    # 遍历表格每一行
    for idx, row in edited_df.iterrows():
        # 强制转换为数字，防止出错
        try:
            qty = float(row['数量 (Qty)'])
            price = float(row['单价 (Price USD)'])
        except ValueError:
            st.error(f"❌ 第 {idx+1} 行的数量或价格格式不对，请检查！")
            st.stop()
            
        total = qty * price
        
        # 将这一行的数据加入列表
        items.append({
            'no': row['序号'],
            'desc_en': row['英文品名 (Desc En)'],
            'desc_cn': row['中文品名 (Desc Cn)'],
            'qty': qty,
            'unit': row['单位 (Unit)'],
            'price': f"{price:,.2f}", # 格式化：34,200.00
            'total': f"{total:,.2f}"
        })
        total_amount += total

    # --- B. 准备填入 Word 的数据包 ---
    context = {
        'buyer_name': buyer_name,
        'buyer_address': buyer_address,
        'contract_no': contract_no,
        'date': date_input.strftime("%Y-%m-%d"),
        'shipping_method': shipping_method,
        'payment_terms': payment_terms,
        'lead_time': lead_time,
        'total_amount': f"{total_amount:,.2f}", # 总金额
        'items': items # 这里对应 Word 表格里的循环
    }
    
    # --- C. 读取模板并生成 ---
    try:
        # 加载模板 (注意文件名必须对！)
        doc = DocxTemplate("template_contract.docx")
        
        # 填入数据
        doc.render(context)
        
        # 保存到内存
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        # 成功提示
        st.success(f"✅ 生成成功！订单总金额: ${total_amount:,.2f}")
        st.balloons()
        
        # 提供下载按钮
        st.download_button(
            label="📥 点击下载合同 (.docx)",
            data=bio,
            file_name=f"Contract_{contract_no}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error("❌ 生成失败！")
        st.warning(f"请检查 GitHub 上是否上传了 'template_contract.docx' 文件。\n错误详情: {e}")
