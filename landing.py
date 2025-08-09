import streamlit as st
from utils import nav, BTN_STYLE

def landing_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title("Easy Analytics.")
    st.subheader("No code analysis platform")
    st.markdown("### ")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Get Started", key="start"):
            nav("upload")
    st.markdown('</div>', unsafe_allow_html=True)