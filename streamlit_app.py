# Import python packages
import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# --------------------------------
# App Title
# --------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------
# Name on order
# --------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

# --------------------------------
# Snowflake connection
# --------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------
# Bring FRUIT_NAME + SEARCH_ON
# --------------------------------
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# --------------------------------
# Convert to Pandas DataFrame
# --------------------------------
pd_df = my_dataframe.to_pandas()

# (Optional – uncomment if you want to see the table)
# st.dataframe(pd_df, use_container_width=True)

# --------------------------------
# Multiselect (uses FRUIT_NAME only)
# --------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

# --------------------------------
# Process selection
# --------------------------------
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build ingredients string for DB insert
        ingredients_string += fruit_chosen + " "

        # 🔑 Get SEARCH_ON value using pandas
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on,
            "."
        )

        # --------------------------------
        # Call SmoothieFroot API
        # --------------------------------
        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            smoothiefroot_response.json(),
            use_container_width=True
        )

    # --------------------------------
    # Insert order into Snowflake
    # --------------------------------
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
