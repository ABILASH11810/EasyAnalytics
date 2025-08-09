import streamlit as st
from utils import back_button, safe_display_dataframe, safe_excel_export

def export_page():
    back_button("visualize")
    st.title("Export Report")
    if st.session_state.df is None:
        st.error("No dataset to export!")
        return
    df = st.session_state.df
    st.subheader("Dataset Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    st.subheader("Final Dataset")
    safe_display_dataframe(df)
    st.subheader("Export Options")
    col1, col2 = st.columns(2)
    with col1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name="processed_dataset.csv",
            mime="text/csv"
        )
    with col2:
        excel_data, file_type, button_label = safe_excel_export(df)
        if file_type == "xlsx":
            st.download_button(
                label=button_label,
                data=excel_data,
                file_name="processed_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.download_button(
                label=button_label,
                data=excel_data,
                file_name="processed_dataset.csv",
                mime="text/csv"
            )
            if "not available" in button_label:
                st.warning(" Install openpyxl for Excel export: `pip install openpyxl`")