import streamlit as st

st.set_page_config(page_title="Velor Trading Journal", layout="wide")

with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:20px;'>
            <img src='assets/logo.png' style='width:90px; border-radius:6px;' />
        </div>
        <h3>Velor Journal</h3>
        """,
        unsafe_allow_html=True
    )

st.title("Welcome to Velor Trading Journal")
st.write("Select a page on the left to start.")
