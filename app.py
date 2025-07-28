
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Monthly Sales Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
month = st.text_input("Enter Month (e.g. July)", "")
goal = st.number_input("Enter Sales Goal (£)", value=0)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.write("📄 **Detected Columns in CSV:**", df.columns.tolist())

    # Try to detect correct column names
    col_sales = next((c for c in df.columns if c.strip().lower() in ['sales', 'amount', 'revenue']), None)
    col_person = next((c for c in df.columns if 'person' in c.lower() or 'rep' in c.lower()), None)

    if not col_sales or not col_person:
        st.error("❌ Could not detect required columns ('Sales Amount' and 'Sales Person'). Please check your CSV headers.")
    else:
        df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)

        selected_rep = st.selectbox("Filter by Salesperson", options=["All"] + sorted(df[col_person].unique().tolist()))

        if selected_rep != "All":
            df = df[df[col_person] == selected_rep]

        total_sales = df[col_sales].sum()
        st.markdown(f"### 💰 Total Sales for {month or 'Selected Month'}: £{int(total_sales):,}")

        # Chart
        chart_data = df.groupby(col_person)[col_sales].sum().reset_index()
        chart_data['GOAL'] = goal

        chart = alt.Chart(chart_data).transform_fold(
            [col_sales, 'GOAL'],
            as_=['Metric', 'Value']
        ).mark_bar().encode(
            x=f'{col_person}:N',
            y='Value:Q',
            color='Metric:N',
            column='Metric:N'
        ).properties(width=150, height=400)

        st.altair_chart(chart, use_container_width=True)

        # Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered Data", data=csv, file_name="filtered_sales_report.csv", mime="text/csv")
else:
    st.info("Please upload a CSV file to get started.")
