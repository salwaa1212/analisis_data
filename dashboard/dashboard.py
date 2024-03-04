import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_yearly_orders(all_data):
    yearly_orders = all_data.resample(rule='Y', on='order_approved_at').agg({
        "order_id": "nunique"
    })
    yearly_orders.index = yearly_orders.index.strftime('%Y')
    yearly_orders = yearly_orders.reset_index()
    yearly_orders.rename(columns={
        "order_approved_at": "year",
        "order_id": "order_count"
    }, inplace=True)

    return yearly_orders

def creat_monthly_orders(all_data):
    monthly_orders = all_data.resample(rule='M', on='order_approved_at').agg({
        "order_id": "nunique"
    })
    monthly_orders = monthly_orders.reset_index()
    monthly_orders.rename(columns={
        "order_approved_at": "date",
        "order_id": "order_count"
    }, inplace=True)

    return monthly_orders

def create_sum_order_items(all_data):
    sum_order_items = all_data.groupby("product_category_name_english")["product_id"].count().reset_index().sort_values(
        by="product_id", ascending=False)
    sum_order_items = sum_order_items.rename(columns={
        "product_id": "count",
        "product_category_name_english": "product"})

    return sum_order_items

def create_sum_demografi_sellers(all_data):
    sum_demografi_sellers = all_data.groupby("seller_state")["seller_id"].count().reset_index().sort_values(
        by="seller_id", ascending=False)
    sum_demografi_sellers = sum_demografi_sellers.rename(columns={
        "seller_id": "count",
        "seller_state": "state"})

    return sum_demografi_sellers

def create_customer_reviews(all_data):
    customer_reviews = all_data.groupby("review_score")["order_id"].count().reset_index().sort_values(by="order_id",
                                                                                                      ascending=False)
    customer_reviews = customer_reviews.rename(columns={
        "order_id": "count",
        "review_score": "rate"})

    return customer_reviews

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["shipping_limit_date", "review_creation_date", "review_answer_timestamp", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
   all_df[column] = pd.to_datetime(all_df[column], format="%Y-%m-%d %H:%M:%S", errors='coerce')

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://img.freepik.com/premium-vector/online-shop-e-commerce-logo-design-vector_122317-6.jpg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & (all_df["order_approved_at"] <= str(end_date))]

yearly_orders = create_yearly_orders(main_df)
monthly_orders = creat_monthly_orders(main_df)
sum_order_item = create_sum_order_items(main_df)
sum_demografi_sellers = create_sum_demografi_sellers(main_df)
customer_reviews = create_customer_reviews(main_df)

st.header('E-Commerce Dataset Dashboard :sparkles:')

st.subheader('Yearly Orders')

col1 = st.columns(1)

# Menampilkan total pesanan di kolom pertama
total_orders = yearly_orders.order_count.sum()
st.metric("Total orders", value=total_orders)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    yearly_orders["year"],
    yearly_orders["order_count"],
    marker='o',
    linewidth=2,
    color="#990F02"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader('Monthly Orders')

col1, col2 = st.columns(2)

with col1:
    year = start_date.strftime("%Y")
    monthly_orders_2018_df = monthly_orders[monthly_orders['date'].astype(str).str.startswith(year)]
    total_orders = monthly_orders_2018_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    st.metric("Year", value=year)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders["date"],
    monthly_orders["order_count"],
    marker='o',
    linewidth=2,
    color="#990F02"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#990F02", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="count", y="product", hue="product", data=sum_order_item.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=40)
ax[0].tick_params(axis='x', labelsize=35)
ax[0].tick_params(axis='y', labelsize=35)

sns.barplot(x="count", y="product", hue="product", data=sum_order_item.sort_values(by="count", ascending=True).head(5),
            palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=40)
ax[1].tick_params(axis='x', labelsize=35)
ax[1].tick_params(axis='y', labelsize=35)

st.pyplot(fig)

st.subheader("Sellers Demographics")

fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(
    x="state",
    y="count",
    data=sum_demografi_sellers.sort_values(by="count", ascending=False),
    color="#990F02"
)
plt.title("Number of Sellers by State", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.subheader("Reviews Score")

fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(
    x="rate",
    y="count",
    color="#990F02",
    data=customer_reviews.sort_values(by="count", ascending=False)
    )
plt.title("Review Score by Customer", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.caption('Copyright (c) Salwa 2024')
