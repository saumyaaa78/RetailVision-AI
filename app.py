import streamlit as st
import pandas as pd
from pathlib import Path

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RetailVision AI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("RetailVision AI Dashboard")


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data
def load_data():
    """
    Load the transaction-level cleaned dataset.

    The project normally stores the file here:
        dataset/cleaned_data.csv

    A fallback to app.py's folder is included so the dashboard
    is easier to run if the CSV is moved beside app.py.
    """
    base_dir = Path(__file__).resolve().parent

    possible_paths = [
        base_dir / "dataset" / "cleaned_data.csv",
        base_dir / "cleaned_data.csv",
    ]

    data_path = next((p for p in possible_paths if p.exists()), None)

    if data_path is None:
        raise FileNotFoundError(
            "cleaned_data.csv was not found. "
            "Please keep it inside the 'dataset' folder beside app.py."
        )

    data = pd.read_csv(data_path, low_memory=False)

    required_columns = [
        "Store",
        "Date",
        "Sales",
        "Customers",
        "Open",
        "Promo",
        "CompetitionDistance",
    ]

    missing = [col for col in required_columns if col not in data.columns]

    if missing:
        raise ValueError(
            "The dataset is missing these required columns: "
            + ", ".join(missing)
        )

    # Numeric conversions
    numeric_columns = [
        "Store",
        "Sales",
        "Customers",
        "Open",
        "Promo",
        "CompetitionDistance",
        "Year",
        "Month",
        "Day",
        "Quarter",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    # Date conversion
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    # Remove rows where the basic analysis fields are invalid
    data = data.dropna(
        subset=["Store", "Date", "Sales", "Customers", "Open", "Promo"]
    ).copy()

    # Store IDs should be integers
    data["Store"] = data["Store"].astype(int)

    # Sales/customer analysis should use open-store days.
    # Closed days have zero sales and should not distort averages.
    data = data[data["Open"] == 1].copy()

    # Competition distance categories
    bins = [-float("inf"), 1000, 5000, 10000, float("inf")]
    labels = [
        "Less than 1 km",
        "1-5 km",
        "5-10 km",
        "10+ km",
    ]

    data["Competition Range"] = pd.cut(
        data["CompetitionDistance"],
        bins=bins,
        labels=labels,
        right=False
    )

    # Ensure stable chronological sorting
    data = data.sort_values("Date").reset_index(drop=True)

    return data


# =========================================================
# LOAD DATA
# =========================================================

try:
    df = load_data()
except Exception as e:
    st.error(f"Unable to load dashboard data: {e}")
    st.stop()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

store_options = ["All Stores"] + [
    str(store)
    for store in sorted(df["Store"].dropna().unique())
]

selected_store = st.sidebar.selectbox(
    "🏬 Select Store",
    store_options
)

promo_options = [
    "All Promotions",
    "Promotion",
    "No Promotion",
]

selected_promo = st.sidebar.selectbox(
    "📢 Promotion Status",
    promo_options
)

competition_options = [
    "All Competition Ranges",
    "Less than 1 km",
    "1-5 km",
    "5-10 km",
    "10+ km",
]

selected_competition = st.sidebar.selectbox(
    "📍 Competition Distance",
    competition_options
)


# =========================================================
# APPLY ALL FILTERS TO THE SAME TRANSACTION DATA
# =========================================================

filtered_df = df.copy()

# Store filter
if selected_store != "All Stores":
    filtered_df = filtered_df[
        filtered_df["Store"] == int(selected_store)
    ].copy()

# Promotion filter
if selected_promo == "Promotion":
    filtered_df = filtered_df[
        filtered_df["Promo"] == 1
    ].copy()

elif selected_promo == "No Promotion":
    filtered_df = filtered_df[
        filtered_df["Promo"] == 0
    ].copy()

# Competition filter
if selected_competition != "All Competition Ranges":
    filtered_df = filtered_df[
        filtered_df["Competition Range"].astype(str)
        == selected_competition
    ].copy()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_sum(series):
    return float(series.sum()) if len(series) else 0.0


def safe_mean(series):
    return float(series.mean()) if len(series) else 0.0


def format_number(value):
    return f"{value:,.0f}"


def format_decimal(value):
    return f"{value:,.2f}"


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

st.subheader("Dashboard Summary")

if filtered_df.empty:
    st.warning("No records match the selected filters.")
else:
    total_records = len(filtered_df)
    total_stores = filtered_df["Store"].nunique()
    total_sales = safe_sum(filtered_df["Sales"])
    average_sales = safe_mean(filtered_df["Sales"])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Records",
            f"{total_records:,}"
        )

    with col2:
        st.metric(
            "Total Stores",
            f"{total_stores:,}"
        )

    with col3:
        st.metric(
            "Total Sales",
            f"{total_sales:,.0f}"
        )

    with col4:
        st.metric(
            "Average Sales",
            f"{average_sales:,.2f}"
        )


# =========================================================
# CUSTOMER & DATE INFORMATION
# =========================================================

st.subheader("Customer & Date Information")

if filtered_df.empty:
    st.info("Customer and date information is not available for the selected filters.")
else:
    total_customers = safe_sum(filtered_df["Customers"])
    start_date = filtered_df["Date"].min()
    end_date = filtered_df["Date"].max()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Customers",
            f"{int(total_customers):,}"
        )

    with col2:
        st.write("**Start Date**")
        st.write(start_date.strftime("%Y-%m-%d"))

    with col3:
        st.write("**End Date**")
        st.write(end_date.strftime("%Y-%m-%d"))


# =========================================================
# DETAILED SUMMARY
# =========================================================

st.subheader("Detailed Summary")

if not filtered_df.empty:
    detailed_summary = pd.DataFrame(
        {
            "Metric": [
                "Total Records",
                "Total Stores",
                "Total Sales",
                "Average Sales",
                "Total Customers",
                "Start Date",
                "End Date",
            ],
            "Value": [
                f"{len(filtered_df):,}",
                f"{filtered_df['Store'].nunique():,}",
                f"{safe_sum(filtered_df['Sales']):,.0f}",
                f"{safe_mean(filtered_df['Sales']):,.2f}",
                f"{int(safe_sum(filtered_df['Customers'])):,}",
                filtered_df["Date"].min().strftime("%Y-%m-%d"),
                filtered_df["Date"].max().strftime("%Y-%m-%d"),
            ],
        }
    )

    st.dataframe(
        detailed_summary,
        width="stretch",
        hide_index=True
    )


# =========================================================
# MONTHLY SALES TREND
# =========================================================

st.subheader("Monthly Sales Trend")

if not filtered_df.empty:
    monthly_df = (
        filtered_df
        .assign(
            Period=filtered_df["Date"].dt.to_period("M").astype(str)
        )
        .groupby("Period", as_index=True)["Sales"]
        .sum()
        .to_frame()
    )

    monthly_df["Sales (Millions)"] = (
        monthly_df["Sales"] / 1_000_000
    )

    st.line_chart(
        monthly_df[["Sales (Millions)"]]
    )
else:
    st.info("No monthly sales data matches the selected filters.")


# =========================================================
# STORE PERFORMANCE
# =========================================================

st.subheader("Store Performance")

if not filtered_df.empty:

    store_summary = (
        filtered_df
        .groupby("Store")
        .agg(
            total_sales=("Sales", "sum"),
            average_sales=("Sales", "mean"),
            total_customers=("Customers", "sum"),
            total_records=("Sales", "size"),
        )
        .sort_values("total_sales", ascending=False)
    )

    # =====================================================
    # STORE KPIs
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        if selected_store != "All Stores":
            st.metric(
                "Selected Store",
                f"Store {selected_store}"
            )
        else:
            top_store_id = int(store_summary.index[0])
            st.metric(
                "Top Store",
                f"Store {top_store_id}"
            )

    with col2:
        top_sales = float(store_summary.iloc[0]["total_sales"])

        if selected_store != "All Stores":
            st.metric(
                "Store Sales",
                f"{top_sales / 1_000_000:.2f}M"
            )
        else:
            st.metric(
                "Top Store Sales",
                f"{top_sales / 1_000_000:.2f}M"
            )

    with col3:
        top_customers = int(
            store_summary.iloc[0]["total_customers"]
        )

        if selected_store != "All Stores":
            st.metric(
                "Customers",
                f"{top_customers:,}"
            )
        else:
            st.metric(
                "Top Store Customers",
                f"{top_customers:,}"
            )

    # =====================================================
    # TOP STORES BY SALES
    # =====================================================

    st.markdown("### Top Stores by Sales")

    top_store_chart = store_summary.head(10).copy()

    top_store_chart["Store"] = (
        "Store "
        + top_store_chart.index.astype(int).astype(str)
    )

    top_store_chart = top_store_chart.set_index("Store")

    top_store_chart["Sales (Millions)"] = (
        top_store_chart["total_sales"] / 1_000_000
    )

    st.bar_chart(
        top_store_chart[["Sales (Millions)"]]
    )

    # =====================================================
    # STORE DETAILS
    # =====================================================

    st.markdown("### Store Details")

    display_store = store_summary.reset_index().copy()

    display_store["total_sales"] = display_store[
        "total_sales"
    ].map(lambda x: f"{x:,.0f}")

    display_store["average_sales"] = display_store[
        "average_sales"
    ].map(lambda x: f"{x:,.2f}")

    display_store["total_customers"] = display_store[
        "total_customers"
    ].map(lambda x: f"{x:,.0f}")

    display_store["total_records"] = display_store[
        "total_records"
    ].map(lambda x: f"{x:,.0f}")

    display_store = display_store.rename(
        columns={
            "Store": "Store",
            "total_records": "Total Records",
            "total_sales": "Total Sales",
            "average_sales": "Average Sales",
            "total_customers": "Total Customers",
        }
    )

    st.dataframe(
        display_store[
            [
                "Store",
                "Total Records",
                "Total Sales",
                "Average Sales",
                "Total Customers",
            ]
        ],
        width="stretch",
        hide_index=True
    )

else:
    st.info("No store data matches the selected filters.")


# =========================================================
# PROMO PERFORMANCE
# =========================================================

st.subheader("Promo Performance")

if not filtered_df.empty:

    promo_summary = (
        filtered_df
        .assign(
            Promotion=filtered_df["Promo"].map(
                {
                    1: "Promotion",
                    0: "No Promotion",
                }
            )
        )
        .groupby("Promotion")
        .agg(
            total_records=("Sales", "size"),
            total_sales=("Sales", "sum"),
            average_sales=("Sales", "mean"),
            total_customers=("Customers", "sum"),
        )
        .reindex(["Promotion", "No Promotion"])
        .dropna(how="all")
    )

    # =====================================================
    # SALES COMPARISON
    # =====================================================

    st.markdown("### Sales Comparison")

    sales_chart = promo_summary.copy()

    sales_chart["Total Sales (Millions)"] = (
        sales_chart["total_sales"] / 1_000_000
    )

    st.bar_chart(
        sales_chart[["Total Sales (Millions)"]]
    )

    # =====================================================
    # AVERAGE SALES COMPARISON
    # =====================================================

    st.markdown("### Average Sales Comparison")

    avg_chart_data = promo_summary[
        ["average_sales"]
    ].rename(
        columns={
            "average_sales": "Average Sales"
        }
    ).dropna()

    if not avg_chart_data.empty:
        st.bar_chart(avg_chart_data)

    # =====================================================
    # PROMOTION DETAILS
    # =====================================================

    st.markdown("### Promotion Details")

    display_promo = promo_summary.reset_index().copy()

    display_promo["total_records"] = display_promo[
        "total_records"
    ].map(lambda x: f"{x:,.0f}")

    display_promo["total_sales"] = display_promo[
        "total_sales"
    ].map(lambda x: f"{x:,.0f}")

    display_promo["average_sales"] = display_promo[
        "average_sales"
    ].map(lambda x: f"{x:,.2f}")

    display_promo["total_customers"] = display_promo[
        "total_customers"
    ].map(lambda x: f"{x:,.0f}")

    display_promo = display_promo.rename(
        columns={
            "Promotion": "Promo",
            "total_records": "Total Records",
            "total_sales": "Total Sales",
            "average_sales": "Average Sales",
            "total_customers": "Total Customers",
        }
    )

    st.dataframe(
        display_promo[
            [
                "Promo",
                "Total Records",
                "Total Sales",
                "Average Sales",
                "Total Customers",
            ]
        ],
        width="stretch",
        hide_index=True
    )

else:
    st.info("No promotion data matches the selected filters.")


# =========================================================
# COMPETITION PERFORMANCE
# =========================================================

st.subheader("Competition Performance")

if not filtered_df.empty:

    competition_summary = (
        filtered_df
        .dropna(subset=["Competition Range"])
        .groupby("Competition Range", observed=True)
        .agg(
            total_records=("Sales", "size"),
            total_sales=("Sales", "sum"),
            average_sales=("Sales", "mean"),
        )
        .reindex(
            [
                "Less than 1 km",
                "1-5 km",
                "5-10 km",
                "10+ km",
            ]
        )
        .dropna(how="all")
    )

    # =====================================================
    # SALES BY COMPETITION RANGE
    # =====================================================

    st.markdown("### Sales by Competition Distance")

    competition_sales_chart = competition_summary.copy()

    competition_sales_chart["Sales (Millions)"] = (
        competition_sales_chart["total_sales"] / 1_000_000
    )

    st.bar_chart(
        competition_sales_chart[["Sales (Millions)"]]
    )

    # =====================================================
    # AVERAGE SALES BY COMPETITION RANGE
    # =====================================================

    st.markdown("### Average Sales by Competition Distance")

    competition_avg_chart = competition_summary[
        ["average_sales"]
    ].rename(
        columns={
            "average_sales": "Average Sales"
        }
    ).dropna()

    if not competition_avg_chart.empty:
        st.bar_chart(competition_avg_chart)

    # =====================================================
    # COMPETITION DETAILS
    # =====================================================

    st.markdown("### Competition Details")

    display_competition = competition_summary.reset_index().copy()

    display_competition["total_records"] = display_competition[
        "total_records"
    ].map(lambda x: f"{x:,.0f}")

    display_competition["total_sales"] = display_competition[
        "total_sales"
    ].map(lambda x: f"{x:,.0f}")

    display_competition["average_sales"] = display_competition[
        "average_sales"
    ].map(lambda x: f"{x:,.2f}")

    display_competition = display_competition.rename(
        columns={
            "Competition Range": "Competition Range",
            "total_records": "Total Records",
            "total_sales": "Total Sales",
            "average_sales": "Average Sales",
        }
    )

    st.dataframe(
        display_competition[
            [
                "Competition Range",
                "Total Records",
                "Total Sales",
                "Average Sales",
            ]
        ],
        width="stretch",
        hide_index=True
    )

else:
    st.info("No competition data matches the selected filters.")


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

st.subheader("Business Insights")

insight_col1, insight_col2 = st.columns(2)


# =========================================================
# PROMOTION INSIGHT
# =========================================================

with insight_col1:

    st.markdown("### 📢 Promotion Insight")

    if (
        selected_promo == "All Promotions"
        and not filtered_df.empty
    ):

        promotion_rows = filtered_df[
            filtered_df["Promo"] == 1
        ]

        no_promotion_rows = filtered_df[
            filtered_df["Promo"] == 0
        ]

        if (
            not promotion_rows.empty
            and not no_promotion_rows.empty
        ):

            promotion_avg = safe_mean(
                promotion_rows["Sales"]
            )

            no_promotion_avg = safe_mean(
                no_promotion_rows["Sales"]
            )

            if no_promotion_avg != 0:
                difference_pct = (
                    (promotion_avg - no_promotion_avg)
                    / no_promotion_avg
                ) * 100
            else:
                difference_pct = 0

            if promotion_avg > no_promotion_avg:

                st.success(
                    f"Stores with promotions have higher "
                    f"average sales ({promotion_avg:,.2f}) "
                    f"than stores without promotions "
                    f"({no_promotion_avg:,.2f}), "
                    f"a difference of {difference_pct:.2f}%."
                )

            elif promotion_avg < no_promotion_avg:

                st.warning(
                    f"Stores without promotions have higher "
                    f"average sales ({no_promotion_avg:,.2f}) "
                    f"than stores with promotions "
                    f"({promotion_avg:,.2f}), "
                    f"a difference of {abs(difference_pct):.2f}%."
                )

            else:

                st.info(
                    "Average sales are the same for "
                    "promotion and non-promotion stores."
                )

        else:

            st.info(
                "Promotion comparison data is not available "
                "for the selected store/competition filter."
            )

    elif selected_promo != "All Promotions":

        st.info(
            "Select 'All Promotions' to compare "
            "promotion vs no-promotion performance."
        )

    else:

        st.info("Promotion data is not available.")


# =========================================================
# COMPETITION INSIGHT
# =========================================================

with insight_col2:

    st.markdown("### 📍 Competition Insight")

    if not filtered_df.empty:

        valid_competition = (
            filtered_df
            .dropna(subset=["Competition Range", "Sales"])
            .groupby("Competition Range", observed=True)["Sales"]
            .mean()
            .dropna()
        )

        if not valid_competition.empty:

            best_range = valid_competition.idxmax()
            lowest_range = valid_competition.idxmin()

            best_value = float(valid_competition.max())
            lowest_value = float(valid_competition.min())

            if selected_competition == "All Competition Ranges":

                st.info(
                    f"The highest average sales are recorded "
                    f"when competition is {best_range} "
                    f"({best_value:,.2f}). The lowest average "
                    f"sales are recorded for {lowest_range} "
                    f"({lowest_value:,.2f})."
                )

            else:

                selected_value = float(
                    valid_competition.iloc[0]
                )

                st.info(
                    f"The selected competition range "
                    f"({selected_competition}) has average "
                    f"sales of {selected_value:,.2f}."
                )

        else:

            st.info(
                "Competition comparison data is not available."
            )

    else:

        st.info("Competition data is not available.")


# =========================================================
# STORE PERFORMANCE INSIGHT
# =========================================================

st.markdown("### 🏆 Store Performance Insight")

if not filtered_df.empty:

    store_insight = (
        filtered_df
        .groupby("Store")
        .agg(
            total_sales=("Sales", "sum"),
            total_customers=("Customers", "sum"),
        )
        .sort_values("total_sales", ascending=False)
    )

    top_store = store_insight.iloc[0]
    top_store_id = int(store_insight.index[0])

    if selected_store == "All Stores":

        st.success(
            f"Store {top_store_id} is the top-performing "
            f"store in the current filtered dataset, with "
            f"total sales of {float(top_store['total_sales']):,.0f} "
            f"and {int(top_store['total_customers']):,} customers."
        )

    else:

        st.success(
            f"Store {top_store_id} has total sales of "
            f"{float(top_store['total_sales']):,.0f} and "
            f"{int(top_store['total_customers']):,} customers "
            f"under the selected filters."
        )

else:

    st.info("Store performance data is not available.")


# =========================================================
# FOOTER / FILTER STATUS
# =========================================================

st.divider()

st.caption(
    "RetailVision AI Dashboard • "
    f"{len(filtered_df):,} records currently match the selected filters."
)