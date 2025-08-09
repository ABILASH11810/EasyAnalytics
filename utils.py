import streamlit as st
import pandas as pd

THEME_PRIMARY = "#007bff"
BTN_STYLE = f"""
<style>
/* target all buttons inside the app container and the common Streamlit wrappers */
section[data-testid="stAppViewContainer"] button,
div.stButton > button,
div.stDownloadButton > button,
div[data-testid="stHorizontalBlock"] button,
button[data-baseweb] {{
    background-color: {THEME_PRIMARY} !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    font-size: 14px !important;
    min-width: 160px !important;  /* ensures minimum width */
    height: 44px !important;      /* fixed height for all buttons */
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    text-align: center !important;
}

/* Make the Streamlit wrapper divs expand so buttons fill their column */
div.stButton,
div.stDownloadButton,
div[data-testid="stHorizontalBlock"] > div {
    width: 100% !important;
}

/* Force the actual <button> to fill wrapper (so columns make them equal) */
div.stButton > button,
div.stDownloadButton > button {
    width: 100% !important;
    max-width: 100% !important;
}

/* When using horizontal blocks, make each child flex equally so columns are same width */
div[data-testid="stHorizontalBlock"] > div {
    flex: 1 1 0px !important;
}

/* hover & disabled */
section[data-testid="stAppViewContainer"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.12);
}
section[data-testid="stAppViewContainer"] button:disabled {
    background-color: #a8c7ff !important;
    cursor: not-allowed;
}
</style>
"""

def nav(next_page):
    st.session_state.page = next_page
    st.rerun()

def back_button(prev_page):
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("Back"):
            nav(prev_page)

def next_button(label, target, disabled=False):
    col1, col2, col3 = st.columns([1, 8, 1])
    with col3:
        if st.button(label, disabled=disabled):
            nav(target)

def enhanced_sanitize_dataframe_for_streamlit(df):
    """
    Enhanced DataFrame sanitization to handle all Arrow incompatibility issues.
    """
    if df is None or df.empty:
        return df
    
    df_clean = df.copy()
    
    # Handle each column individually with comprehensive type checking
    for col in df_clean.columns:
        col_dtype = str(df_clean[col].dtype)
        
        # Handle nullable integer types (Int64, Int32, etc.)
        if col_dtype.startswith('Int') or 'Int' in col_dtype:
            try:
                # Convert to regular float64, handling NaN values
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').astype('float64')
            except:
                df_clean[col] = df_clean[col].astype(str)
        
        # Handle nullable boolean types
        elif col_dtype == 'boolean':
            try:
                # Convert to string to avoid Arrow issues
                df_clean[col] = df_clean[col].astype(str).replace('<NA>', 'Unknown')
            except:
                df_clean[col] = df_clean[col].astype(str)
        
        # Handle string/object columns with mixed types or None values
        elif col_dtype == 'object':
            try:
                # Convert to string and handle various null representations
                series = df_clean[col].astype(str)
                series = series.replace(['nan', 'None', '<NA>', 'null', 'NULL', 'NaN'], '')
                df_clean[col] = series
            except:
                df_clean[col] = 'Error'
        
        # Handle datetime with timezone issues
        elif 'datetime' in col_dtype and 'tz' in col_dtype:
            try:
                df_clean[col] = df_clean[col].dt.tz_localize(None)
            except:
                df_clean[col] = df_clean[col].astype(str)
        
        # Handle category types
        elif col_dtype == 'category':
            try:
                df_clean[col] = df_clean[col].astype(str)
            except:
                df_clean[col] = 'Category'
    
    # Final safety check - ensure no problematic dtypes remain
    for col in df_clean.columns:
        dtype_str = str(df_clean[col].dtype)
        if (dtype_str.startswith('Int') or 
            dtype_str == 'boolean' or 
            'Int' in dtype_str):
            df_clean[col] = df_clean[col].astype(str)
    
    return df_clean

def safe_display_dataframe(df, key=None, **kwargs):
    """Safely display DataFrame in Streamlit with enhanced error handling"""
    try:
        clean_df = enhanced_sanitize_dataframe_for_streamlit(df)
        st.dataframe(clean_df, key=key, **kwargs)
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")
        # Multiple fallback attempts
        try:
            # Try with basic string conversion
            simple_df = df.astype(str)
            st.dataframe(simple_df, key=key, **kwargs)
        except:
            # Ultimate fallback to text display
            st.write("Data preview (text format):")
            st.text(str(df.head()))

def safe_excel_export(df, filename="processed_dataset.xlsx"):
    """
    Safely export DataFrame to Excel with fallback options.
    """
    try:
        from io import BytesIO
        
        # Try to import openpyxl
        try:
            import openpyxl
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Processed Data', index=False)
            return output.getvalue(), "xlsx", " Download as Excel"
        except ImportError:
            # Fallback to CSV if openpyxl not available
            csv_data = df.to_csv(index=False).encode('utf-8')
            return csv_data, "csv", " Download as CSV (Excel not available)"
    except Exception as e:
        # Ultimate fallback
        csv_data = df.to_csv(index=False).encode('utf-8')
        return csv_data, "csv", "Download as CSV (Error occurred)"


    pass

