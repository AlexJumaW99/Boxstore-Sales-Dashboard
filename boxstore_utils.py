import pymysql.cursors
import pymysql
from pymysql import Error
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def connect_to_database(host, user, password, database):
    """Connect to the MySQL database."""
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,  # ensures the header names from the DB are brought as well!
        )
        if connection.open:
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None


def fetch_data(connection, query):
    """Fetch data from the database using a SQL query."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            return data
    except Error as e:
        print("Error fetching data from MySQL", e)
        return None


def display_countries(data, title):
    country_counts = data["co_name"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]

    # Create a choropleth map
    fig = px.choropleth(
        country_counts,
        locations="country",
        locationmode="country names",
        color="count",
        hover_name="country",
        hover_data={"count": True},
        color_continuous_scale=px.colors.sequential.Plasma,
        title=title,
    )

    # Update layout for better appearance
    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=False, projection_type="equirectangular"
        ),
        title_x=0.5,
    )
    # return the figure for showing
    return fig


def order_horizontal_barcharts(
    data, x, y, title, xlabel, ylabel, color=None, legend_label=None
):
    fig = px.bar(
        data,
        x=x,
        y=y,
        orientation="h",
        title=title,
        color=color,
        labels={
            f"{x}": f"{xlabel}",
            f"{y}": f"{ylabel}",
            f"{color}": f"{legend_label}",
        },
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending", "dtick": 1})

    return fig


def pie_chart_viz(data, values, names, title, values_label, names_label):
    # Create a Pie Chart using Plotly Express
    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        labels={f"{values}": f"{values_label}", f"{names}": f"{names_label}"},
        hole=0.3,  # Optional: To create a donut chart
    )
    # Update layout for better appearance
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        title_x=0.5,
        annotations=[
            dict(text="Product Categories", x=0.5, y=0.5, font_size=10, showarrow=False)
        ],
    )
    # Show the figure
    return fig


def dataframe_conversion():
    """
    Main function to orchestrate database connection, data fetching, and manipulation.
    """
    # Establish the database connection
    connection = connect_to_database(
        "localhost", "root", "37024013", "aj_0393756_boxstore"
    )

    if not connection:
        return "Failed to connect to the DB!"

    try:
        # Define your SQL query
        people_sql_query = "SELECT * FROM people;"

        # Fetch the data
        data = fetch_data(connection, people_sql_query)

        # Load data into a pandas DataFrame
        people_df = pd.DataFrame(data)
        print("Data loaded into DataFrame successfully!")
        print(people_df.head())

        detailed_people_info_query = """ 
        SELECT p.p_id, p.first_name, p.last_name
             , p.addr, p.addr_code, p.addr_info
             , p.addr_delivery
             , gat.addr_type, gtc.tc_name
             , grg.rg_name
             , gco.co_name

        FROM people p
             JOIN geo_address_type gat ON p.addr_type_id=gat.addr_type_id
             JOIN geo_towncity gtc ON p.tc_id=gtc.tc_id
             JOIN geo_region grg ON gtc.rg_id=grg.rg_id
             JOIN geo_country gco ON grg.co_id=gco.co_id;"""

        data2 = fetch_data(connection, detailed_people_info_query)

        detailed_people_df = pd.DataFrame(data2)
        print("\n")
        print(detailed_people_df.head())

        detailed_employee_info_query = """
        SELECT pe.pe_id
             , e.first_name AS employee_fname, e.last_name 
             , m.first_name, m.last_name
             , pe.pe_hired, pe.pe_salary
             , gtc.tc_name
             , grg.rg_name
             , gco.co_name
             
        FROM people_employee pe 
            JOIN people e ON pe.p_id=e.p_id
            LEFT JOIN people m ON pe.p_id_mgr=m.p_id 
            JOIN geo_towncity gtc ON e.tc_id=gtc.tc_id
            JOIN geo_region grg ON gtc.rg_id=grg.rg_id
            JOIN geo_country gco ON grg.co_id=gco.co_id
            
        WHERE e.active=1 OR m.active=1;
        """

        data3 = fetch_data(connection, detailed_employee_info_query)

        detailed_employee_df = pd.DataFrame(data3)
        print("\n")
        print(detailed_employee_df.head())

        detailed_only_customers_query = """
        SELECT p.p_id, p.first_name, p.last_name
             , p.addr, p.addr_code, p.addr_info
             , p.addr_delivery
             , gat.addr_type, gtc.tc_name
             , grg.rg_name
             , gco.co_name

        FROM people p
             JOIN geo_address_type gat ON p.addr_type_id=gat.addr_type_id
             JOIN geo_towncity gtc ON p.tc_id=gtc.tc_id
             JOIN geo_region grg ON gtc.rg_id=grg.rg_id
             JOIN geo_country gco ON grg.co_id=gco.co_id
             
        WHERE p.employee=0;
        """
        data4 = fetch_data(connection, detailed_only_customers_query)

        detailed_customer_df = pd.DataFrame(data4)
        print("\n")
        print(detailed_customer_df.head())

        orders_join_query = """
        SELECT oi.oi_id, oi.order_id, oi.item_id, oi.oi_qty
             , p.first_name AS cust_first_name, p.last_name AS cust_last_name
             , e.first_name AS emp_first_name, e.last_name AS emp_last_name
             , gco.co_name
             , i.item_id, i.item_name, i.item_modelno, i.item_barcode
             , i.man_id
             , m.man_id, m.man_name
             , i.it_id, it.it_desc
             , ip.item_price
             , (oi.oi_qty * ip.item_price) AS total_price 
             , group_concat(ii.ii_serialno) AS serialno 

        FROM orders__item oi
            JOIN item_inventory ii ON oi.oi_id=ii.oi_id
            JOIN orders o ON oi.order_id=o.order_id
            JOIN people p ON p.p_id=o.p_id_cus
            JOIN people e ON e.p_id=o.p_id_emp
            JOIN geo_towncity gtc ON p.tc_id=gtc.tc_id
            JOIN geo_region grg ON gtc.rg_id=grg.rg_id
            JOIN geo_country gco ON grg.co_id=gco.co_id
            JOIN item i ON oi.item_id=i.item_id
            JOIN item_price ip ON ip.item_id=oi.item_id
            JOIN manufacturer m ON i.man_id=m.man_id
            JOIN item_type it ON i.it_id=it.it_id
     
        WHERE o.order_date BETWEEN ip.ip_beg AND IFNULL(ip.ip_end, CURRENT_TIME)

        GROUP BY oi.oi_id, oi.order_id, oi.item_id, oi.oi_qty
        , i.item_id, i.item_name, i.item_modelno, i.item_barcode
        , i.man_id
        , m.man_id, m.man_name
        , i.it_id, it.it_desc
        , ip.item_price;
        """
        data5 = fetch_data(connection, orders_join_query)

        orders_join_df = pd.DataFrame(data5)
        print("\n")
        print(orders_join_df.head())

        man_rep_query = """SELECT * FROM manufacturer_people_reps;"""
        data6 = fetch_data(connection, man_rep_query)

        man_rep_df = pd.DataFrame(data6)
        print("\n")
        print(man_rep_df.head())

        man_data_query = """
        SELECT m.man_id 
             , m.man_name, m.tc_id, gtc.tc_name
             , grg.rg_name
             , gco.co_name  
             
        FROM manufacturer m
            JOIN geo_towncity gtc ON m.tc_id=gtc.tc_id
            JOIN geo_region grg ON gtc.rg_id=grg.rg_id
            JOIN geo_country gco ON grg.co_id=gco.co_id;
        """
        data7 = fetch_data(connection, man_data_query)

        man_df = pd.DataFrame(data7)
        print("\n")
        print(man_df.head())

        return (
            people_df,
            detailed_people_df,
            detailed_employee_df,
            detailed_customer_df,
            orders_join_df,
            man_rep_df,
            man_df,
        )

    finally:
        # Ensure the connection is closed
        if connection:
            connection.close()
            print("\n")
            print("Connection closed.")
