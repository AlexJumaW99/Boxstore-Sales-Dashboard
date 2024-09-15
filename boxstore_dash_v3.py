import pymysql.cursors
import pymysql
from pymysql import Error
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import altair as alt
from boxstore_utils import (
    connect_to_database,
    fetch_data,
    display_countries,
    order_horizontal_barcharts,
    pie_chart_viz,
    dataframe_conversion,
)


def main():
    p_df, dp_df, de_df, dc_df, oj_df, mr_df, m_df = dataframe_conversion()

    st.set_page_config(
        page_title="Boxstore Sales Dashboard",
        page_icon="🏂",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    alt.themes.enable("dark")

    page_bg_image = """
    <style>

    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);
    }

    [data-testid="stToolbar"] {
        right: 2rem;
    }

    [data-testid="stSidebar"] {
        background-image: url("https://images.unsplash.com/photo-1698414786771-0fa24cabcd0b?auto=format&fit=crop&q=80&w=3024&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-position: center;
    }
    </style>

    """

    # inject CSS tag and add unsafe_allow_html
    st.markdown(page_bg_image, unsafe_allow_html=True)

    st.title("Boxstore Sales Dashboard")
    # st.audio("audio_files/Song Audio Final.MP3")
    # st.markdown("_Prototype v0.0.1_")
    # st.cache_data

    total_revenue = float(oj_df["total_price"].sum())

    all_people_country_count = display_countries(dp_df, "Count of People by Country")
    only_employees_country_count = display_countries(
        de_df, "Count of Employees by Country"
    )
    only_customers_country_count = display_countries(
        dc_df, "Count of Customers by Country"
    )
    man_reps_country_count = display_countries(
        mr_df, "Count of Manufacturer Reps by Country"
    )

    man_country_count = display_countries(m_df, "Count of Manufacturers by Country")

    # top_10_items_sold_by_qty = top_items_sold_qty(oj_df)

    oj_df["cust_fullname"] = oj_df["cust_first_name"] + " " + oj_df["cust_last_name"]
    oj_df["emp_fullname"] = oj_df["emp_first_name"] + " " + oj_df["emp_last_name"]

    big_spenders_df = (
        oj_df.groupby("cust_fullname")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    biggest_spender_name = big_spenders_df.iloc[0]["cust_fullname"]
    biggest_spender_amount = big_spenders_df.iloc[0]["total_price"]

    best_customers = order_horizontal_barcharts(
        big_spenders_df.head(10),
        "total_price",
        "cust_fullname",
        "Top 10 Biggest Spenders",
        "Total Spending",
        "Customer Name",
    )

    best_salesmen_df = (
        oj_df.groupby("emp_fullname")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    best_salesman_name = best_salesmen_df.iloc[0]["emp_fullname"]
    best_salesman_amount = best_salesmen_df.iloc[0]["total_price"]

    best_salesmen = order_horizontal_barcharts(
        best_salesmen_df.head(10),
        "total_price",
        "emp_fullname",
        "Top 10 Best Salesmen",
        "Total Sales",
        "Employee Name",
    )

    top_10_quantity = (
        oj_df.groupby("item_name")["oi_qty"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    top_10_items_sold_by_qty = order_horizontal_barcharts(
        top_10_quantity,
        "oi_qty",
        "item_name",
        "Most Sold Items by Quantity",
        "Number of Items Sold",
        "Item Sold",
    )

    # top_10_items_sold_by_tprice = top_items_sold_tprice(oj_df)
    oj_df.total_price = oj_df.total_price.astype(float).fillna(0.0)
    top_10_total_price = (
        oj_df.groupby("item_name")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    top_10_items_sold_by_tprice = order_horizontal_barcharts(
        top_10_total_price,
        "total_price",
        "item_name",
        "Most Items Sold by Price",
        "Total Monetary Value gained from Sales",
        "Item Sold",
    )

    top_10_manu_sales = (
        oj_df.groupby("man_name")["total_price"]
        .sum()
        .reset_index()
        .sort_values(by="total_price", ascending=False)
    )
    top_10_manu_by_sales = order_horizontal_barcharts(
        top_10_manu_sales,
        "total_price",
        "man_name",
        "Bestselling Manufacturers",
        "Total Sales",
        "Manufacturer",
    )

    man_category_sales_df = (
        oj_df.groupby(["man_name", "it_desc"])["total_price"].sum().reset_index()
    )
    top_category_sales_by_manu = order_horizontal_barcharts(
        data=man_category_sales_df,
        x="total_price",
        y="man_name",
        color="it_desc",
        title="Best Selling Product Categories for Each Manufacturer",
        xlabel="Total Sales",
        ylabel="Manufacturer",
        legend_label="Product Category",
    )

    man_category_qty_df = (
        oj_df.groupby(["man_name", "it_desc"])["oi_qty"].sum().reset_index()
    )
    top_category_by_qty_manu = order_horizontal_barcharts(
        data=man_category_qty_df,
        x="oi_qty",
        y="man_name",
        color="it_desc",
        title="Most Selling Product Categories for Each Manufacturer by Quantity",
        xlabel="Total Quantity Sold",
        ylabel="Manufacturer",
        legend_label="Product Category",
    )

    man_sales_by_country_df = (
        oj_df.groupby(["man_name", "co_name"])["total_price"].sum().reset_index()
    )

    sales_by_country = order_horizontal_barcharts(
        data=man_sales_by_country_df,
        x="total_price",
        y="man_name",
        color="co_name",
        title="Best Selling Manufacturers by Country",
        xlabel="Total Sales",
        ylabel="Manufacturer",
        legend_label="Country",
    )

    # Aggregate the total sales by product category
    category_sales_dist = oj_df.groupby("it_desc")["total_price"].sum().reset_index()
    category_sales_pie_chart = pie_chart_viz(
        data=category_sales_dist,
        values="total_price",
        names="it_desc",
        title="Sales Distribution by Product Category",
        values_label="Total Sales",
        names_label="Product Category",
    )

    category_qty_dist = oj_df.groupby("it_desc")["oi_qty"].sum().reset_index()
    category_qty_pie_chart = pie_chart_viz(
        data=category_qty_dist,
        values="oi_qty",
        names="it_desc",
        title="Distribution of Qty Sold by Product Category",
        values_label="Total Qty Sold",
        names_label="Product Category",
    )

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        # st.markdown("Total Revenue")
        st.metric("Total Revenue 💰", f"${total_revenue}", "0%")
        # st.subheader("Geographical Distribution")

    with col2:
        st.metric(
            f"Biggest Spender ➡️ {biggest_spender_name}",
            f"${biggest_spender_amount}",
            "0%",
        )
        # st.selectbox(
        #     "Check out the geographical distribution of different fields:",
        #     ("People", "Employees", "Customers", "Manufacturers"),
        # )

    with col3:
        st.metric(
            f"Best Salesman ➡️ {best_salesman_name}", f"${best_salesman_amount}", "0%"
        )

    column1, column2 = st.columns([2, 2])
    st.sidebar.subheader("User Focus")
    user_options_tup = (
        "Customer",
        "Salesman",
    )
    user_options = st.sidebar.selectbox(
        "Would you like to focus on customer data or salesman data:", user_options_tup
    )

    if user_options == user_options_tup[0]:
        column1.plotly_chart(best_customers)

    elif user_options == user_options_tup[1]:
        column1.plotly_chart(best_salesmen)

    st.sidebar.subheader("Geographical Distribution")
    options_tup = (
        "All People",
        "Employees",
        "Customers",
        "Manufacturer Reps",
        "Manufacturers",
    )
    geo_option = st.sidebar.selectbox(
        "Check out the geographical distribution of different fields:", options_tup
    )

    if geo_option == options_tup[0]:
        column2.plotly_chart(all_people_country_count)
    elif geo_option == options_tup[1]:
        column2.plotly_chart(only_employees_country_count)
    elif geo_option == options_tup[2]:
        column2.plotly_chart(only_customers_country_count)
    elif geo_option == options_tup[3]:
        column2.plotly_chart(man_reps_country_count)
    elif geo_option == options_tup[4]:
        column2.plotly_chart(man_country_count)

    colu1, colu2 = st.columns([2, 2], gap="medium")

    st.sidebar.subheader("Visual Filter")
    vf_options_tup = (
        "Sales",
        "Quantity",
    )
    vf_options = st.sidebar.selectbox("Visual Filter:", vf_options_tup)

    if vf_options == "Sales":
        colu1.plotly_chart(top_10_items_sold_by_tprice)
        colu2.plotly_chart(sales_by_country)
        colu1.plotly_chart(top_10_manu_by_sales)
        colu2.plotly_chart(top_category_sales_by_manu)
        colu1.plotly_chart(category_sales_pie_chart)

    elif vf_options == "Quantity":
        colu1.plotly_chart(top_10_items_sold_by_qty)
        colu2.plotly_chart(top_category_by_qty_manu)
        colu1.plotly_chart(category_qty_pie_chart)

    # colu1.plotly_chart(top_10_items_sold_by_qty)

    # st.plotly_chart(top_10_manu_by_sales)

    # st.plotly_chart(sales_by_country)
    # st.plotly_chart(top_category_sales_by_manu)

    # st.plotly_chart(category_sales_pie_chart)
    # st.plotly_chart(category_qty_pie_chart)


if __name__ == "__main__":
    main()
