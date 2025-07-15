import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bakery Sales Dashboard", layout="wide")
st.title("🥐 La Petit Bakery – Sales Analysis Dashboard")
st.write("Upload your Excel file (.xlsx) and specify the correct header row if needed.")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    st.info("👀 Previewing first 10 rows to help you choose the header row:")
    preview = pd.read_excel(uploaded_file, header=None).head(10)
    st.dataframe(preview)

    # Ask user to select header row
    header_row = st.number_input("🧾 Select the header row number (0-indexed)", min_value=0, max_value=20, value=3)

    try:
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.str.strip()
        st.success("✅ File processed successfully with header row: " + str(header_row))
        st.write("📋 **Detected Columns:**", list(df.columns))

        # Validate required column
        if 'Date' not in df.columns:
            st.error("❌ Column 'Date' not found. Please check your header row.")
        else:
            # Clean columns
            df = df.drop(columns=[col for col in df.columns if 'Unnamed' in str(col)], errors='ignore')

            # Define expected product columns
            product_cols = ['Cakes', 'Pies', 'Cookies', 'Smoothies', 'Coffee']
            missing_products = [col for col in product_cols if col not in df.columns]
            if missing_products:
                st.error(f"❌ Missing product columns: {missing_products}")
            else:
                df['Date'] = pd.to_datetime(df['Date'])
                df['Total_Sales'] = df[product_cols].sum(axis=1)
                df['Day_of_Week'] = df['Date'].dt.day_name()
                df['Month'] = df['Date'].dt.month_name()

                # 1️⃣ Summary
                st.subheader("1️⃣ Overall Sales Summary")
                st.dataframe(df['Total_Sales'].describe().to_frame("Value"))

                # 2️⃣ Day of Week
                st.subheader("2️⃣ Average Sales by Day of Week")
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_sales = df.groupby('Day_of_Week')['Total_Sales'].mean().reindex(weekday_order)
                fig1, ax1 = plt.subplots()
                weekday_sales.plot(kind="bar", ax=ax1, color="skyblue")
                ax1.set_ylabel("Sales")
                ax1.set_title("Sales by Day")
                st.pyplot(fig1)

                # 3️⃣ Product Seasonality
                st.subheader("3️⃣ Product Seasonality")
                months_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
                monthly_product_sales = df.groupby("Month")[product_cols].mean().reindex(months_order)
                fig2, ax2 = plt.subplots()
                for col in product_cols:
                    ax2.plot(months_order, monthly_product_sales[col], label=col, marker="o")
                ax2.set_ylabel("Sales")
                ax2.set_title("Monthly Product Sales")
                ax2.legend()
                st.pyplot(fig2)

                # 4️⃣ Trend
                st.subheader("4️⃣ Sales Trend")
                df_trend = df.set_index("Date")
                fig3, ax3 = plt.subplots()
                df_trend["Total_Sales"].plot(ax=ax3, label="Daily", linewidth=1)
                df_trend["Total_Sales"].rolling(30).mean().plot(ax=ax3, label="30-Day Avg", linewidth=2)
                ax3.set_title("Sales Trend")
                ax3.legend()
                st.pyplot(fig3)
                df.reset_index(drop=False, inplace=True)

                # 5️⃣ Promotion
                st.subheader("5️⃣ Promotion Effect")
                if 'promotion' in df.columns:
                    promo_sales = df.groupby('promotion')['Total_Sales'].mean()
                    promo_sales.index = ['Promotion Applied' if str(x).lower().startswith('promo') else 'No Promotion'
                                         for x in promo_sales.index]
                    fig4, ax4 = plt.subplots()
                    promo_sales.plot(kind="bar", ax=ax4, color="lightgreen")
                    ax4.set_title("Promo vs No Promo Sales")
                    st.pyplot(fig4)
                else:
                    st.info("⚠️ No 'promotion' column found.")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
