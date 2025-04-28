import streamlit as st
import pandas as pd

# 頁面設定
st.set_page_config(page_title="川浩產品－成本計算工具", layout="centered")

# 密碼保護登入
PASSWORD = "gsc2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # 首頁 Logo
    st.image("https://raw.githubusercontent.com/hsieh0138/gsc-product-cost/main/logo.png", width=300)

    st.markdown(
        """
        <div style="text-align:center;">
            <h1>\ud83d\udce6 川浩產品－成本計算工具</h1>
            <h3 style="margin-top: 0.5em; color: #666;">密碼保護</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    pwd = st.text_input("\ud83d\udd12 請輸入存取密碼", type="password", placeholder="請輸入密碼...")

    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("密碼錯誤，請聯絡管理者")
        st.stop()

else:
    # 登入成功後主畫面
    st.image("https://raw.githubusercontent.com/hsieh0138/gsc-product-cost/main/logo.png", width=300)
    st.markdown(
        """
        <div style="text-align:center;">
            <h1>\ud83d\udce6 川浩產品－成本計算工具</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

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

    # 預設輸入資料
    default_data = pd.DataFrame({
        "產品名稱 Product": ["產品A", "產品B"],
        "原料成本 Material Cost": [80, 100],
        "製造時間 (分鐘) Work Time (min)": [30, 20],
        "包裝成本 Packaging Cost": [5, 6],
        "品管成本 QC Cost": [5, 3],
        "毛利率 Profit Margin (%)": [20, 25],
        "其他%1 Extra %1": ["", ""],
        "其他%2 Extra %2": ["", ""],
        "其他%3 Extra %3": ["", ""],
    })

    edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

    # 固定參數設定
    monthly_salary = 27470
    work_hours_per_month = 22 * 8
    labor_insurance_ratio = 0.13
    machine_cost_per_hour = 80
    overhead_per_hour = 50
    usd_exchange_rate = 32  # 美金匯率，暫定32

    # 成本計算
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

            profit_margin = row["毛利率 Profit Margin (%)"] / 100  # 將百分比轉成小數
            suggested_price = round(total_cost * (1 + profit_margin), 2)

            usd_price = round(suggested_price / usd_exchange_rate, 2)

            results.append({
                "產品名稱 Product": row["產品名稱 Product"],
                "原料成本 Material": row["原料成本 Material Cost"],
                "人工成本 Labor": labor_cost,
                "間接費用 Overhead": overhead_cost,
                "包裝成本 Packaging": row["包裝成本 Packaging Cost"],
                "機台成本 Machine": machine_cost,
                "品管成本 QC": row["品管成本 QC Cost"],
                "總成本 Total Cost": total_cost,
                "建議售價 Suggested Price (TWD)": suggested_price,
                "美金售價 Suggested Price (USD)": usd_price,
            })

    if results:
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align:center;">
                <h2>\ud83d\udcca 成本分析結果 Cost Breakdown</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        df_result = pd.DataFrame(results)
        st.dataframe(df_result, use_container_width=True)

        csv = df_result.to_csv(index=False).encode("utf-8-sig")
        st.download_button("\ud83d\udce5 下載結果 (CSV)", csv, file_name="product_cost_results.csv", mime="text/csv")
