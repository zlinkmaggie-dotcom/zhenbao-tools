import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import io
from datetime import datetime

# 页面标题
st.set_page_config(page_title="外贸单证自动生成", page_icon="📄")
st.title("📄 震宝外贸单证自动生成系统")

# === 1. 左侧：填写客户信息 ===
with st.sidebar:
    st.header("📝 第一步：填写订单信息")
    # 如果你模板里是 {{ buyer_name }}，这里就对应 buyer_name
    buyer_name = st.text_input("买方名称 (Buyer)", "LLC OSIYO KOSMETIK")
    buyer_address = st.text_area("买方地址 (Address)")
    contract_no = st.text_input("合同号 (Contract No)", "ZB2025-001")
    date_input = st.date_input("日期 (Date)", datetime.today())
    payment_terms = st.selectbox("付款方式", ["100% T/T", "30% Deposit, 70% Balance"])
    
    st.info("👇 填完左边和中间，点这个按钮下载")
    # 这个按钮是最后一步
    generate_btn = st.button("🚀 生成合同 (.docx)", type="primary")

# === 2. 中间：填写产品 ===
st.header("📦 第二步：填写产品列表")

if 'df' not in st.session_state:
    # 默认显示一行示例数据
    data = {
        "Name (En)": ["Folding Machine"],
        "Name (Cn)": ["折叠机"],
        "Qty": [1],
        "Price (USD)": [34200.00],
        "Amount": [34200.00] # 这一列其实可以通过计算得出，为了简单先放着
    }
    st.session_state.df = pd.DataFrame(data)

# 让用户可以编辑表格
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# === 3. 生成逻辑 ===
if generate_btn:
    # 1. 整理数据
    items = []
    total_amount = 0
    
    for idx, row in edited_df.iterrows():
        qty = float(row['Qty'])
        price = float(row['Price (USD)'])
        total = qty * price
        
        items.append({
            'no': idx + 1,
            'desc_en': row['Name (En)'],
            'desc_cn': row['Name (Cn)'],
            'qty': qty,
            'price': f"{price:,.2f}",
            'total': f"{total:,.2f}"
        })
        total_amount += total

    # 2. 准备要填入 Word 的字典
    context = {
        'buyer_name': buyer_name,
        'buyer_address': buyer_address,
        'contract_no': contract_no,
        'date': date_input.strftime("%Y-%m-%d"),
        'payment_terms': payment_terms,
        'total_amount': f"{total_amount:,.2f}",
        'items': items # 这里对应 Word 表格里的循环
    }
    
    # 3. 读取并生成
    try:
        # 注意：这里的名字必须和你上传的 Word 文件名一模一样！
        doc = DocxTemplate("template_contract.docx") 
        doc.render(context)
        
        # 保存到内存准备下载
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.success(f"✅ 成功！总金额: ${total_amount:,.2f}")
        st.download_button(
            label="📥 点击下载最终合同",
            data=bio,
            file_name=f"Contract_{contract_no}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error(f"❌ 出错了！可能是没找到模板文件。\n错误信息: {e}")
        st.warning("请确保你上传到 GitHub 的 Word 文件名必须叫：template_contract.docx")