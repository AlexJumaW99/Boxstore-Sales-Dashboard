import pymysql 
import pandas 
import streamlit as st

def mysqlconnect(): 
	# To connect MySQL database 
	conn = pymysql.connect( 
		host='localhost', 
		user='root', 
		password = "37024013", 
		db='aj_0393756_boxstore', 
		) 
	
	cur = conn.cursor() 
	
	# Select query 
	cur.execute("select * from people") 
	output = cur.fetchall() 
	
	for i in range(5): 
		print(output[i]) 
	
	# To close the connection 
	conn.close() 

def run_streamlit_app():
    st.title("Boxstore Sales Dashboard") 
    st.markdown("_Prototype v0.0.1_")
    st.cache_data

# Driver Code 
if __name__ == "__main__" : 
	mysqlconnect()
