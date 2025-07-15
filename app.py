import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ───────────────────────────────────────────────
# Basic page setup
# ───────────────────────────────────────────────
st.set_page_config(page_title="Bakery Sales Dashboard", layout="wide")
st.title("🥐 La Petit Bakery – Sales Analysis Dashboard")
st.write("Upload an Excel file (`.xlsx`) with your bakery data to explore insights.")

# ───────────────────────────────────────────────
# File upload widget
# ───────────────────────────────────────────────
uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

# ───────────────────────────────────────────────
# When a file is provided, run all analyses
# ───────────────────────────────────────────────
if uploaded_file is not None:
    try:
        # 1️⃣ READ DATA  (header row 3 in the sample file)
        df = pd.read_excel(uploaded_file, header=3)

        # 2️⃣ CLEAN DATA
        df.columns = df.columns.str.strip()   # remove leading/trailing spaces
        df = df.drop(
            columns=[col for col in df.columns if "Unnamed" in str(col) or col == "daywk"],
            errors="ignore",
        )

        # Expected product columns (adjust if your file differs)
        product_cols = ["Cakes", "Pies", "Cookies", "Smoothies", "Coffee"]

        # 3️⃣ FEATURE ENGINEERING
        df["Date"] = pd.to_datetime(df["Date"])
        df["Total_Sales"] = df[product_cols].sum(axis=1)
        df["Day_of_Week"] = df["Date"].dt.day_name()
        df["Month"] = df["Date"].dt.month_name()

        # ───────────────────────────────────────────
        # SECTION 1 – Overall Sales Summary
        # ───────────────────────────────────────────
        st.subheader("1️⃣ Overall Sales Summary")
        st.dataframe(df["Total_Sales"].describe().to_frame("Value"))

        # ───────────────────────────────────────────
        # SECTION 2 – Day‑of‑Week Impact
        # ───────────────────────────────────────────
        st.subheader("2️⃣ Average Sales by Day of Week")
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_sales = (
            df.groupby("Day_of_Week")["Total_Sales"]
            .mean()
            .reindex(weekday_order)
        )

        fig1, ax1 = plt.subplots()
        weekday_sales.plot(kind="bar", ax=ax1, color="skyblue", edgecolor="black")
        ax1.set_ylabel("Average Daily Sales")
        ax1.set_xlabel("")
        ax1.set_title("Average Sales per Weekday")
        st.pyplot(fig1)

        # ───────────────────────────────────────────
        # SECTION 3 – Product Seasonality
        # ───────────────────────────────────────────
        st.subheader("3️⃣ Product Seasonality (Monthly Average)")
        months_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        monthly_product_sales = (
            df.groupby("Month")[product_cols]
            .mean()
            .reindex(months_order)
        )

        fig2, ax2 = plt.subplots()
        for col in product_cols:
            ax2.plot(months_order, monthly_product_sales[col], marker="o", label=col)
        ax2.set_ylabel("Average Daily Sales")
        ax2.set_xlabel("")
        ax2.set_title("Monthly Product Sales Pattern")
        ax2.set_xticklabels(months_order, rotation=45)
        ax2.legend()
        st.pyplot(fig2)

        # ───────────────────────────────────────────
        # SECTION 4 – Trend Over Time
        # ───────────────────────────────────────────
        st.subheader("4️⃣ Sales Trend Over Time")
        df_trend = df.set_index("Date")
        fig3, ax3 = plt.subplots()
        df_trend["Total_Sales"].plot(ax=ax3, label="Daily Sales", linewidth=0.8)
        df_trend["Total_Sales"].rolling(30).mean().plot(ax=ax3, label="30‑Day Rolling Mean", linewidth=2)
        ax3.set_ylabel("Sales")
        ax3.set_title("Daily Sales and 30‑Day Rolling Average")
        ax3.legend()
        st.pyplot(fig3)
        df_trend.reset_index(inplace=True)   # restore if needed later

        # ───────────────────────────────────────────
        # SECTION 5 – Promotion Effect
        # ───────────────────────────────────────────
        if "promotion" in df.columns:
            st.subheader("5️⃣ Promotion vs Non‑Promotion Sales")
            promo_sales = df.groupby("promotion")["Total_Sales"].mean()
            promo_sales.index = [
                "Promotion Applied" if str(x).lower().startswith("promo") else "No Promotion"
                for x in promo_sales.index
            ]

            fig4, ax4 = plt.subplots()
            promo_sales.plot(kind="bar", ax=ax4, color="lightgreen", edgecolor="black")
            ax4.set_ylabel("Average Daily Sales")
            ax4.set_xlabel("")
            ax4.set_title("Impact of Promotions on Sales")
            st.pyplot(fig4)

            st.dataframe(
                promo_sales.reset_index().rename(columns={"index": "Promotion Type", "Total_Sales": "Avg Daily Sales"})
            )
        else:
            st.info("No `promotion` column found in the dataset – skipping promotion analysis.")

    except Exception as e:
        st.error(f"⚠️ Error while processing file: {e}")

else:
    st.info("👆 Please upload an Excel file to begin.")
