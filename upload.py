import streamlit as st
import pandas as pd
from utils import back_button, next_button, nav, enhanced_sanitize_dataframe_for_streamlit, safe_display_dataframe

def upload_page():
    back_button("home")
    st.title("Upload your dataset")
    uploaded = st.file_uploader("Choose your dataset", type=["csv", "xlsx"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            df = enhanced_sanitize_dataframe_for_streamlit(df)
            st.session_state.df = df.copy()
            st.success(f"Dataset loaded successfully! Shape: {df.shape}")
            st.subheader("Dataset Preview")
            safe_display_dataframe(df.head(10))
            st.subheader("Dataset Info")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Rows:** {df.shape[0]}")
                st.write(f"**Columns:** {df.shape[1]}")
            with col2:
                st.write("**Column Types:**")
                st.write(df.dtypes.value_counts())
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    next_button("Next", "cleaning_menu", disabled=st.session_state.df is None)