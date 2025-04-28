import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="川浩產品－成本計算工具", layout="centered")

# 密碼保護登入
PASSWORD = "gsc2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.image("https://raw.githubusercontent.com/hsieh0138/gsc-product-cost/main/logo.png", width=300)
    st.markdown("""
    <div style="text-align:center;">
        <h1>🏦 川浩產品－成本計算工具</h1>
        <h3 style="margin-top: 0.5em; color: #666;">密碼保護</h3>
    </div>
    """, unsafe_allow_html=True)
    pwd = st.text_input("🔐 請輸入存取密碼", type="password", placeholder="請輸入密碼...")

    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("密碼錯誤，請聯絡管理者")
        st.stop()
else:
    st.title("🏦 川浩產品－成本計算工具")

    st.markdown("""
    本工具支援多筆產品成本試算，可即時計算各產品之：
    
    - 原料成本
    - 直接人工（依據工時與時薪）
    - 製造間接費用
    - 包裝成本
    - 機台使用成本
    - 品管檢驗成本
    - 毛利率設定與建議售價
    
    支援多筆輸入與 Excel 匯出，適合對內核算與對外報價使用。
    """, unsafe_allow_html=True)

    # 預設表格
    default_data = pd.DataFrame({
        "產品名稱 Product": ["\u7522\u54c1A", "\u7522\u54c1B"],
        "原料成本 Material Cost": [80, 100],
        "製造時間 (\u5206) Work Time (min)": [30, 20],
        "包裝成本 Packaging Cost": [5, 6],
        "品管成本 QC Cost": [5, 3],
        "毛利率 Profit Margin(%)": [20, 25]
    })

    edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

    # 定義參數
    monthly_salary = 27470
    work_hours_per_month = 22 * 8
    labor_insurance_ratio = 0.13
    machine_cost_per_hour = 80
    overhead_per_hour = 50
    exchange_rate = st.number_input("\ud83d\udcb1 請輸入自定匯率（\u7f8e\u5143\uff09", value=32.0)

    # 成本計算
    results = []
    for _, row in edited_df.iterrows():
        if row["產品名稱 Product"]:
            time_hr = row["製造時間 (\u5206) Work Time (min)"] / 60
            hourly_wage = monthly_salary / work_hours_per_month
            real_hourly_cost = hourly_wage * (1 + labor_insurance_ratio)

            labor_cost = round(real_hourly_cost * time_hr, 2)
            overhead_cost = round(overhead_per_hour * time_hr, 2)
            machine_cost = round(machine_cost_per_hour * time_hr, 2)

            total_cost = round(
                row["原料成本 Material Cost"] + labor_cost + overhead_cost +
                row["包裝成本 Packaging Cost"] + machine_cost + row["品管成本 QC Cost"], 2)

            profit_margin = row["毛利率 Profit Margin(%)"] / 100
            suggested_price = round(total_cost * (1 + profit_margin), 2)
            usd_price = round(suggested_price / exchange_rate, 2)
            profit_amount = round(suggested_price - total_cost, 2)

            results.append({
                "產品名稱 Product": row["產品名稱 Product"],
                "原料成本 Material": row["原料成本 Material Cost"],
                "人工成本 Labor": labor_cost,
                "間接費用 Overhead": overhead_cost,
                "包裝成本 Packaging": row["包裝成本 Packaging Cost"],
                "機台成本 Machine": machine_cost,
                "品管成本 QC": row["品管成本 QC Cost"],
                "總成本 Total Cost": total_cost,
                "建議售價 NT$": suggested_price,
                "售價美元 US$": usd_price,
                "利潤額 Profit": profit_amount
            })

    if results:
        st.markdown("---")
        st.subheader("📊 成本分析結果 Cost Breakdown")
        df_result = pd.DataFrame(results)
        st.dataframe(df_result, use_container_width=True)

        # 下載 CSV
        csv = df_result.to_csv(index=False).encode("utf-8-sig")
        today = datetime.today().strftime("%Y-%m-%d")
        st.download_button(
            "📥 下載 CSV",
            csv,
            file_name=f"成本試算結果_{today}.csv",
            mime="text/csv"
        )

        # 生成 PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('ArialUnicode', '', fname_or_ttf='msjh.ttf', uni=True)
        pdf.set_font("ArialUnicode", size=12)

        pdf.cell(0, 10, txt=f"成本試算結果 ({today})", ln=True, align="C")
        pdf.ln(10)

        col_width = pdf.w / 10
        row_height = 8

        for col in df_result.columns:
            pdf.cell(col_width, row_height, col, border=1)
        pdf.ln(row_height)

        for _, row in df_result.iterrows():
            for item in row:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)

        summary = f"\n合計筆數: {len(df_result)}  平均成本: {df_result['總成本 Total Cost'].mean():.2f}  平均售價 NT$: {df_result['建議售價 NT$'].mean():.2f}"
        pdf.ln(10)
        pdf.multi_cell(0, 10, summary)

        pdf_output = BytesIO()
        pdf.output(pdf_output)

        st.download_button(
            "🔖 下載 PDF",
            pdf_output.getvalue(),
            file_name=f"成本試算結果_{today}.pdf",
            mime="application/pdf"
        )


