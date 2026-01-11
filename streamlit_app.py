# --------------------------------
# Import python packages
# --------------------------------
import streamlit as st
import pandas as pd
import requests

from snowflake.snowpark.context import get_active_session
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
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------------
# Snowflake session (SiS ONLY)
# --------------------------------
session = get_active_session()

# --------------------------------
# Load fruit options
# --------------------------------
fruit_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

pd_df = fruit_df.to_pandas()
# Optional debug view
st.dataframe(pd_df, use_container_width=True)
# --------------------------------
# Multiselect
# --------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)
# --------------------------------
# Process selection
# --------------------------------
if ingredients_list:

    # ✅ Deterministic, clean string
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            f"The search value for **{fruit_chosen}** is **{search_on}**"
        )

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # --------------------------------
        # Safe API call (SiS-friendly)
        # --------------------------------
        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}",
                timeout=5
            )

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning("Nutrition API returned no data.")

        except Exception as e:
            st.warning("External API unavailable in this environment.")

    # --------------------------------
    # Insert order
    # --------------------------------
    insert_sql = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (?, ?)
    """

    st.code(ingredients_string)

    if st.button("Submit Order"):
        session.sql(
            insert_sql,
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success("Your Smoothie is ordered! ✅")
