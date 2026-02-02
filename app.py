import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("global_sales.csv")
    df.columns = df.columns.str.strip().str.lower()

    date_col = next(c for c in df.columns if "date" in c)
    qty_col = next(c for c in df.columns if "quant" in c)
    price_col = next(c for c in df.columns if "price" in c)
    country_col = next(c for c in df.columns if "country" in c)
    invoice_col = next(c for c in df.columns if "invoice" in c)
    customer_col = next(c for c in df.columns if "customer" in c)

    df[date_col] = pd.to_datetime(df[date_col])
    df["sales"] = df[qty_col] * df[price_col]
    df = df[df["sales"] > 0]

    return df, date_col, country_col, invoice_col, customer_col

df, date_col, country_col, invoice_col, customer_col = load_data()

st.title("Global Sales Analytics Dashboard")
st.markdown("Interactive dashboard exploring global sales performance, customer behavior, and country-level insights.")

st.sidebar.header("Dashboard Filters")

countries = st.sidebar.multiselect(
    "Select Countries",
    sorted(df[country_col].unique()),
    default=sorted(df[country_col].unique())[:5]
)

years = st.sidebar.slider(
    "Select Year Range",
    int(df[date_col].dt.year.min()),
    int(df[date_col].dt.year.max()),
    (int(df[date_col].dt.year.min()), int(df[date_col].dt.year.max()))
)

months = st.sidebar.multiselect(
    "Select Months",
    list(range(1, 13)),
    default=list(range(1, 13))
)

filtered_df = df[
    (df[country_col].isin(countries)) &
    (df[date_col].dt.year.between(years[0], years[1])) &
    (df[date_col].dt.month.isin(months))
]

total_sales = filtered_df["sales"].sum()
total_customers = filtered_df[customer_col].nunique()
total_orders = filtered_df[invoice_col].nunique()

order_level = (
    filtered_df
    .groupby(invoice_col, as_index=False)["sales"]
    .sum()
)

avg_order_value = order_level["sales"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Sales", f"${total_sales:,.0f}")
c2.metric("👥 Total Customers", f"{total_customers:,}")
c3.metric("🧾 Total Orders", f"{total_orders:,}")
c4.metric("📦 Avg Order Value", f"${avg_order_value:,.2f}")

sales_by_year = (
    filtered_df
    .groupby(filtered_df[date_col].dt.year)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig_trend = px.line(
    sales_by_year,
    x=date_col,
    y="total_sales",
    markers=True,
    title="Global Sales Trend Over Time"
)

st.plotly_chart(fig_trend, use_container_width=True)

country_sales = (
    filtered_df
    .groupby(country_col)["sales"]
    .sum()
    .reset_index()
    .sort_values("sales", ascending=False)
    .head(10)
)

fig_country_sales = px.bar(
    country_sales,
    x="sales",
    y=country_col,
    orientation="h",
    title="Top 10 Countries by Total Sales"
)

st.plotly_chart(fig_country_sales, use_container_width=True)

monthly_sales = (
    filtered_df
    .groupby(filtered_df[date_col].dt.month)["sales"]
    .sum()
    .reset_index(name="total_sales")
)

fig_monthly = px.area(
    monthly_sales,
    x=date_col,
    y="total_sales",
    title="Seasonal Sales Pattern"
)

st.plotly_chart(fig_monthly, use_container_width=True)

country_perf = (
    filtered_df
    .groupby(country_col)
    .agg(
        total_sales=("sales", "sum"),
        total_orders=(invoice_col, "nunique")
    )
    .reset_index()
    .sort_values("total_sales", ascending=False)
    .head(10)
)

fig_perf = px.bar(
    country_perf,
    x="total_sales",
    y=country_col,
    orientation="h",
    color="total_orders",
    title="Top Countries: Sales vs Orders"
)

st.plotly_chart(fig_perf, use_container_width=True)

aov_country = (
    filtered_df
    .groupby(country_col)
    .apply(lambda x: x.groupby(invoice_col)["sales"].sum().mean())
    .reset_index(name="avg_order_value")
    .sort_values("avg_order_value", ascending=False)
    .head(10)
)

fig_aov = px.bar(
    aov_country,
    x="avg_order_value",
    y=country_col,
    orientation="h",
    title="Top Countries by Average Order Value"
)

st.plotly_chart(fig_aov, use_container_width=True)

st.subheader("Filtered Dataset Preview")
st.dataframe(filtered_df.head(100))
