import streamlit as st
import pandas as pd

st.set_page_config(page_title="\ud83d\udce6\u5ddd\u6d69\u7522\u54c1\uff5e\u6210\u672c\u8a08\u7b97\u5de5\u5177", layout="centered")

# \u5bc6\u78bc\u4fdd\u8b77\nPASSWORD = "gsc2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.image("https://raw.githubusercontent.com/hsieh0138/gsc-product-cost/main/logo.png", width=300)
    st.markdown("""
        <div style='text-align:center;'>
            <h1>\ud83d\udce6 \u5ddd\u6d69\u7522\u54c1\uff5e\u6210\u672c\u8a08\u7b97\u5de5\u5177</h1>
            <h3 style='margin-top:0.5em; color:#666;'>\u5bc6\u78bc\u4fdd\u8b77</h3>
        </div>
    """, unsafe_allow_html=True)
    pwd = st.text_input("\ud83d\udd12 \u8acb\u8f38\u5165\u5b58\u53d6\u5bc6\u78bc", type="password", placeholder="\u8acb\u8f38\u5165\u5bc6\u78bc...")
    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("\u5bc6\u78bc\u932f\u8aa4\uff0c\u8acb\u806f\u7d61\u7ba1\u7406\u8005")
        st.stop()
else:
    st.title("\ud83d\udce6 \u5ddd\u6d69\u7522\u54c1\uff5e\u6210\u672c\u8a08\u7b97\u5de5\u5177")

st.markdown("""
\u672c\u5de5\u5177\u652f\u63f4\u591a\u7b46\u7522\u54c1\u6210\u672c\u8a66\u7b97\uff0c\u53ef\u5373\u6642\u8a08\u7b97\u5404\u7522\u54c1\u4e4b：

- \u539f\u6599\u6210\u672c
- \u76f4\u63a5\u4eba\u5de5\uff08\u4f9d\u64da\u5de5\u6642\u8207\u6642\u85aa\uff09
- \u88fd\u9020\u9593\u63a5\u8cbb\u7528
- \u5305\u88dd\u6210\u672c
- \u6a5f\u53f0\u4f7f\u7528\u6210\u672c
- \u54c1\u7ba1\u6aa2\u9a57\u6210\u672c
- \u6bdb\u5229\u7387\u8a2d\u5b9a\u8207\u5efa\u8b70\u552e\u50f9

\u652f\u63f4\u591a\u7b46\u8f38\u5165\u8207 Excel \u532f\u51fa\uff0c\u9069\u5408\u5c0d\u5167\u6838\u7b97\u8207\u5c0d\u5916\u5831\u50f9\u4f7f\u7528\u3002
""", unsafe_allow_html=True)

st.markdown("---")

# \u9810\u8a2d\u8cc7\u6599
default_data = pd.DataFrame({
    "\u7522\u54c1\u540d\u7a31 Product": ["\u7522\u54c1A", "\u7522\u54c1B"],
    "\u539f\u6599\u6210\u672c Material Cost": [80, 100],
    "\u88fd\u9020\u6642\u9593 (\u5206\u9418) Work Time (min)": [30, 20],
    "\u5305\u88dd\u6210\u672c Packaging Cost": [5, 6],
    "\u54c1\u7ba1\u6210\u672c QC Cost": [5, 3],
    "\u6bdb\u5229\u7387 Profit Margin (%)": [20, 25],
})

edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

# \u5b9a\u5b9a\u53c3\u6578
monthly_salary = 27470
work_hours_per_month = 22 * 8
labor_insurance_ratio = 0.13
machine_cost_per_hour = 80
overhead_per_hour = 50
exchange_rate = st.number_input("\ud83c\udf0d \u8acb\u8f38\u5165\u7c73\u5143\u532f\u7387 (\u9ed8\u8a8d 32)", value=32)

# \u8a08\u7b97\u7d50\u679c
results = []
for _, row in edited_df.iterrows():
    if row["\u7522\u54c1\u540d\u7a31 Product"]:
        time_hr = row["\u88fd\u9020\u6642\u9593 (\u5206\u9418) Work Time (min)"] / 60
        hourly_wage = monthly_salary / work_hours_per_month
        real_hourly_cost = hourly_wage * (1 + labor_insurance_ratio)

        labor_cost = round(real_hourly_cost * time_hr, 2)
        overhead_cost = round(overhead_per_hour * time_hr, 2)
        machine_cost = round(machine_cost_per_hour * time_hr, 2)

        total_cost = round(
            row["\u539f\u6599\u6210\u672c Material Cost"] + labor_cost + overhead_cost +
            row["\u5305\u88dd\u6210\u672c Packaging Cost"] + machine_cost + row["\u54c1\u7ba1\u6210\u672c QC Cost"], 2)

        profit_margin = row["\u6bdb\u5229\u7387 Profit Margin (%)"] / 100
        suggested_price_ntd = round(total_cost / (1 - profit_margin), 2)
        suggested_price_usd = round(suggested_price_ntd / exchange_rate, 2)

        results.append({
            "\u7522\u54c1\u540d\u7a31 Product": row["\u7522\u54c1\u540d\u7a31 Product"],
            "\u539f\u6599\u6210\u672c Material": row["\u539f\u6599\u6210\u672c Material Cost"],
            "\u4eba\u5de5\u6210\u672c Labor": labor_cost,
            "\u9593\u63a5\u8cbb\u7528 Overhead": overhead_cost,
            "\u5305\u88dd\u6210\u672c Packaging": row["\u5305\u88dd\u6210\u672c Packaging Cost"],
            "\u6a5f\u53f0\u6210\u672c Machine": machine_cost,
            "\u54c1\u7ba1\u6210\u672c QC": row["\u54c1\u7ba1\u6210\u672c QC Cost"],
            "\u7e3d\u6210\u672c Total Cost": total_cost,
            "\u5efa\u8b70\u552e\u50f9\uff08\u53f0\u5e63\uff09Suggested Price (NTD)": suggested_price_ntd,
            "\u5efa\u8b70\u552e\u50f9\uff08\u7c73\u5143\uff09Suggested Price (USD)": suggested_price_usd,
        })

if results:
    st.markdown("---")
    st.subheader("\ud83d\udcca \u6210\u672c\u5206\u6790\u7d50\u679c Cost Breakdown")
    df_result = pd.DataFrame(results)
    st.dataframe(df_result, use_container_width=True)

    csv = df_result.to_csv(index=False).encode("utf-8-sig")
    st.download_button("\ud83d\udce5 \u4e0b\u8f09\u7d50\u679c (CSV)", csv, file_name="product_cost_results.csv", mime="text/csv")

