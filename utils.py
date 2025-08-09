import streamlit as st
import pandas as pd

THEME_PRIMARY = "#007bff"
BTN_STYLE = f"""
<style>
div.stButton > button {{
    background-color:{THEME_PRIMARY};
    color:white;
    font-weight:bold;
    border-radius:8px;
    width:100%;
    border: none;
    padding: 0.5rem 1rem;
}}
div.stButton > button:hover {{
    background-color:#0056b3;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}}
div.stButton > button:disabled {{
    background-color:#8abaf8;
    color:white;
}}
div[data-testid="stHorizontalBlock"] {{
    gap:1rem;
}}
h1, h2, h3 {{
    color:black;
    text-align:center;
}}
.main-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}}
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