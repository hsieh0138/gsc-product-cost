import streamlit as st
import pandas as pd

st.set_page_config(page_title="川浩產品-成本計算工具", layout="centered")

# 密碼保護
PASSWORD = "gsc2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("📦 川浩產品－成本計算工具") -   密碼保護")
    pwd = st.text_input("請輸入訪問密碼 (Enter Password)", type="password")
    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()

    elif pwd:
        st.error("密碼錯誤，請聯絡管理者 Password incorrect")
    st.stop()

st.title("📦 川浩產品成本計算公式")

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
""")

st.markdown("---")

# 輸入多筆產品資料
st.subheader("📋 輸入多筆產品資料 (Multiple Product Inputs)")
default_data = pd.DataFrame({
    "產品名稱 Product": ["產品A", "產品B"],
    "原料成本 Material Cost": [80, 100],
    "製造時間 (分鐘) Work Time (min)": [15, 20],
    "包裝成本 Packaging Cost": [5, 6],
    "品管成本 QC Cost": [3, 3],
    "毛利率 Profit Margin": [0.2, 0.25],
})

edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

# 固定參數（可自訂）
monthly_salary = 27470
work_hours_per_month = 22 * 8
labor_insurance_ratio = 0.13
machine_cost_per_hour = 80
overhead_per_hour = 50

# 成本計算公式
results = []
for _, row in edited_df.iterrows():
    if row["產品名稱 Product"]:
        time_hr = row["製造時間 (分鐘) Work Time (min)"] / 60
        hourly_wage = monthly_salary / work_hours_per_month
        real_hourly_cost = hourly_wage * (1 + labor_insurance_ratio)

        labor_cost = round(real_hourly_cost * time_hr, 2)
        overhead_cost = round(overhead_per_hour * time_hr, 2)
        machine_cost = round(machine_cost_per_hour * time_hr, 2)

        total_cost = round(
            row["原料成本 Material Cost"] + labor_cost + overhead_cost +
            row["包裝成本 Packaging Cost"] + machine_cost + row["品管成本 QC Cost"], 2)

        suggested_price = round(total_cost * (1 + row["毛利率 Profit Margin"]), 2)

        results.append({
            "產品名稱 Product": row["產品名稱 Product"],
            "原料成本 Material": row["原料成本 Material Cost"],
            "人工成本 Labor": labor_cost,
            "間接費用 Overhead": overhead_cost,
            "包裝成本 Packaging": row["包裝成本 Packaging Cost"],
            "機台成本 Machine": machine_cost,
            "品管成本 QC": row["品管成本 QC Cost"],
            "總成本 Total Cost": total_cost,
            "建議售價 Suggested Price": suggested_price,
        })

if results:
    st.markdown("---")
    st.subheader("📊 成本分析結果 Cost Breakdown")
    df_result = pd.DataFrame(results)
    st.dataframe(df_result, use_container_width=True)

    csv = df_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 下載結果 (CSV)", csv, file_name="product_cost_results.csv", mime="text/csv")
