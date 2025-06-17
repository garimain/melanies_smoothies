# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

import requests


cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(f"Custimze Your Smoothie! :balloon: {st.__version__}")
st.write(
  """Customize the fruits you want in your Smoothie
  And if you're new to **Streamlit**, check
  out our easy-to-follow guides at
  [docs.streamlit.io](https://docs.streamlit.io).
  """
)

customer_name = st.text_input("Please enter your name", "enter your name")
st.write("customer name", customer_name)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    "What are your favorite fruits?",
    my_dataframe, max_selections=5
)
if ingredients_list:
    st.write(ingredients_list)
    st.text(ingredients_list)
    ingredients_string=''
    for fruit in ingredients_list:
        ingredients_string += fruit + ' '
        search_on =pd_df.loc[pd_df['FRUIT_NAME']==fruit, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit, 'is ', search_on, '.')
        st.subheader(fruit + " Nutrition Information")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
        #st.text(smoothiefroot_response.json())
        sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #st.write("ingredient string ", ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + customer_name + """')"""

    st.write(my_insert_stmt)   
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered ! ', icon="✅")
