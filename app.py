import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bakery Sales Analysis", layout="wide")

st.title("🥐 Bakery Sales Dashboard – La Petit Bakery")
st.write("Upload your Excel file (`.xlsx`) to begin analysis.")

# File Upload
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=3)
    df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col or col == 'daywk'])
    
    product_cols = ['Cakes', 'Pies', 'Cookies', 'Smoothies', 'Coffee']
    df['Date'] = pd.to_datetime(df['Date'])
    df['Total_Sales'] = df[product_cols].sum(axis=1)
    df['Day_of_Week'] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month_name()
    
    # Section 1: Overall Sales Summary
    st.subheader("1️⃣ Overall Sales Summary")
    st.dataframe(df['Total_Sales'].describe())

    # Section 2: Day of Week Impact
    st.subheader("2️⃣ Average Sales by Day of the Week")
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_sales = df.groupby('Day_of_Week')['Total_Sales'].mean().reindex(weekday_order)

    fig1, ax1 = plt.subplots()
    weekday_sales.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Average Daily Sales by Day of Week')
    ax1.set_ylabel('Sales')
    st.pyplot(fig1)

    # Section 3: Product Seasonality
    st.subheader("3️⃣ Product Seasonality (Monthly Trends)")
    months_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
    monthly_product_sales = df.groupby('Month')[product_cols].mean().reindex(months_order)

    fig2, ax2 = plt.subplots()
    for col in product_cols:
        ax2.plot(months_order, monthly_product_sales[col], label=col)
    ax2.set_title('Monthly Product Sales')
    ax2.set_ylabel('Sales')
    ax2.legend()
    st.pyplot(fig2)

    # Section 4: Trend Over Time
    st.subheader("4️⃣ Sales Trend Over Time")
    df.set_index('Date', inplace=True)
    fig3, ax3 = plt.subplots()
    df['Total_Sales'].plot(ax=ax3, label='Daily Sales')
    df['Total_Sales'].rolling(30).mean().plot(ax=ax3, label='30-Day Rolling Avg')
    ax3.set_title("Sales Trend with Rolling Mean")
    ax3.set_ylabel("Sales")
    ax3.legend()
    st.pyplot(fig3)
    df.reset_index(inplace=True)

    # Section 5: Promotion Impact
    st.subheader("5️⃣ Promotion vs Non-Promotion Sales")
    promo_sales = df.groupby('promotion')['Total_Sales'].mean()
    promo_sales.index = ['No Promotion' if x == 'none' else 'Promotion Applied' for x in promo_sales.index]

    fig4, ax4 = plt.subplots()
    promo_sales.plot(kind='bar', ax=ax4, color='lightgreen')
    ax4.set_title('Effect of Promotion on Sales')
    ax4.set_ylabel('Average Sales')
    st.pyplot(fig4)

    st.dataframe(promo_sales.reset_index().rename(columns={'index': 'Promotion Type', 'Total_Sales': 'Avg Daily Sales'}))
else:
    st.warning("👆 Please upload a valid `.xlsx` file to start.")
