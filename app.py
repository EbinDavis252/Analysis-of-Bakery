import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ───────────────────────────────────────────────
st.set_page_config(page_title="Bakery Sales Dashboard", layout="wide")
st.title("🥐 La Petit Bakery – Sales Analysis Dashboard")
st.write("Upload an Excel file (`.xlsx`) with your bakery data to explore insights.")

# ───────────────────────────────────────────────
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Try reading from row 4 (0-indexed header=3)
        df = pd.read_excel(uploaded_file, header=3)
        df.columns = df.columns.str.strip()  # remove extra spaces
        st.success("✅ File uploaded successfully.")
        st.write("📋 **Detected Columns:**", list(df.columns))  # DEBUG

        # Ensure required column exists
        if 'Date' not in df.columns:
            st.error("❌ Column 'Date' is missing. Please check the Excel structure.")
        else:
            # Drop unnamed columns safely
            df = df.drop(columns=[col for col in df.columns if 'Unnamed' in str(col)], errors='ignore')

            # Define product columns (check if all exist)
            product_cols = ['Cakes', 'Pies', 'Cookies', 'Smoothies', 'Coffee']
            missing_products = [col for col in product_cols if col not in df.columns]

            if missing_products:
                st.error(f"❌ Missing product columns: {missing_products}")
            else:
                # Preprocessing
                df['Date'] = pd.to_datetime(df['Date'])
                df['Total_Sales'] = df[product_cols].sum(axis=1)
                df['Day_of_Week'] = df['Date'].dt.day_name()
                df['Month'] = df['Date'].dt.month_name()

                # ───────────────────────────────────────────
                st.subheader("1️⃣ Overall Sales Summary")
                st.dataframe(df['Total_Sales'].describe().to_frame("Value"))

                # ───────────────────────────────────────────
                st.subheader("2️⃣ Average Sales by Day of Week")
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_sales = df.groupby('Day_of_Week')['Total_Sales'].mean().reindex(weekday_order)

                fig1, ax1 = plt.subplots()
                weekday_sales.plot(kind="bar", ax=ax1, color="skyblue", edgecolor="black")
                ax1.set_title("Average Sales per Weekday")
                ax1.set_ylabel("Sales")
                st.pyplot(fig1)

                # ───────────────────────────────────────────
                st.subheader("3️⃣ Product Seasonality by Month")
                months_order = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
                monthly_product_sales = df.groupby("Month")[product_cols].mean().reindex(months_order)

                fig2, ax2 = plt.subplots()
                for col in product_cols:
                    ax2.plot(months_order, monthly_product_sales[col], label=col, marker="o")
                ax2.set_ylabel("Average Daily Sales")
                ax2.set_title("Monthly Product Sales Pattern")
                ax2.legend()
                plt.xticks(rotation=45)
                st.pyplot(fig2)

                # ───────────────────────────────────────────
                st.subheader("4️⃣ Sales Trend Over Time")
                df_trend = df.set_index("Date")
                fig3, ax3 = plt.subplots()
                df_trend["Total_Sales"].plot(ax=ax3, label="Daily Sales", linewidth=1)
                df_trend["Total_Sales"].rolling(30).mean().plot(ax=ax3, label="30-Day Rolling Avg", linewidth=2)
                ax3.set_title("Sales Trend")
                ax3.set_ylabel("Sales")
                ax3.legend()
                st.pyplot(fig3)
                df.reset_index(drop=False, inplace=True)

                # ───────────────────────────────────────────
                st.subheader("5️⃣ Promotion vs No Promotion Impact")
                if 'promotion' in df.columns:
                    promo_sales = df.groupby('promotion')['Total_Sales'].mean()
                    promo_sales.index = ['Promotion Applied' if str(x).lower().startswith('promo') else 'No Promotion'
                                         for x in promo_sales.index]

                    fig4, ax4 = plt.subplots()
                    promo_sales.plot(kind='bar', ax=ax4, color='lightgreen', edgecolor="black")
                    ax4.set_title("Effect of Promotion on Sales")
                    ax4.set_ylabel("Average Sales")
                    st.pyplot(fig4)

                    st.dataframe(
                        promo_sales.reset_index().rename(columns={'index': 'Promotion Type', 'Total_Sales': 'Avg Sales'})
                    )
                else:
                    st.info("⚠️ No 'promotion' column found in the data. Skipping this section.")
    except Exception as e:
        st.error(f"❌ Error while processing file: `{e}`")

else:
    st.info("👆 Upload your `.xlsx` file to start analysis.")
