import streamlit as st
from landing import landing_page
from upload import upload_page
from data_cleaning import cleaning_menu, operation_page
from data_transformation import transform_menu, transform_operation_page
from data_visualization import visualization_page
from export import export_page

st.set_page_config(page_title="Easy Analytics", page_icon="", layout="wide")

# Theme and style
from utils import BTN_STYLE
st.markdown(BTN_STYLE, unsafe_allow_html=True)

# State initialization
if "page" not in st.session_state:
    st.session_state.page = "home"
if "df" not in st.session_state:
    st.session_state.df = None
if "operation_set" not in st.session_state:
    st.session_state.operation_set = None

# Page router
def main():
    page_functions = {
        "home": landing_page,
        "upload": upload_page,
        "cleaning_menu": cleaning_menu,
        "operation": operation_page,
        "transform_menu": transform_menu,
        "transform_operation": transform_operation_page,
        "visualize": visualization_page,
        "export": export_page
    }
    current_page = st.session_state.page
    if current_page in page_functions:
        page_functions[current_page]()
    else:
        st.error("Page not found!")

if __name__ == "__main__":
    main()