import streamlit as st

st.set_page_config(
    page_title="ClickZetta Low Touch Tool",
    page_icon="👋",
)

st.write("# Welcome to ClickZetta Low Touch Tool! 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    ClickZetta Low Touch Tool is a tool that integrates SQL translation, connection testing, and data verification.
    
    
    - Unify Page: unify db connection testing and sql translation, data verification for single query.
    - Connection Testing Page: db connection testing.
    - SQL Translation Page: sql translation for batch queries.
    - Data Verification Page: data verification for batch queries.
    
    **👈 Select a page from the sidebar** to reach your desired purpose.
    
"""
)