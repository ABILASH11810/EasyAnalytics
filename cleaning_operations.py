import pandas as pd
import streamlit as st
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from utils import enhanced_sanitize_dataframe_for_streamlit

def handle_missing_values(df, method, columns=None):
    result = df.copy()
    target_cols = columns if columns else result.columns

    if method == "isnull":
        result = result[target_cols].isnull()
    elif method == "isnull_sum":
        result = pd.DataFrame(result[target_cols].isnull().sum(), columns=['Missing_Count'])
    elif method == "notnull":
        result = result[target_cols].notnull()
    else:
        result = df

    return enhanced_sanitize_dataframe_for_streamlit(result)

def remove_missing_values(df, method='default', **kwargs):
    if method == 'default':
        result = df.dropna()
    elif method == 'axis1':
        result = df.dropna(axis=1)
    elif method == 'all':
        result = df.dropna(how='all')
    else:
        result = df

    return enhanced_sanitize_dataframe_for_streamlit(result)

def fill_missing_values(df, method='zero', value=None, columns=None):
    result = df.copy()
    target_cols = columns if columns else result.columns

    if method == 'zero':
        result[target_cols] = result[target_cols].fillna(0)
    elif method == 'ffill':
        result[target_cols] = result[target_cols].ffill()
    elif method == 'bfill':
        result[target_cols] = result[target_cols].bfill()
    elif method == 'mean':
        numeric_cols = result[target_cols].select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            result[col] = result[col].fillna(result[col].mean())
    elif method == 'unknown':
        result[target_cols] = result[target_cols].fillna("Unknown")

    return enhanced_sanitize_dataframe_for_streamlit(result)

def string_operations(df, operation, columns=None):
    result = df.copy()
    string_cols = columns if columns else df.select_dtypes(include=['object']).columns

    if operation == 'lower':
        for col in string_cols:
            result[col] = result[col].astype(str).str.lower()
    elif operation == 'upper':
        for col in string_cols:
            result[col] = result[col].astype(str).str.upper()
    elif operation == 'strip':
        for col in string_cols:
            result[col] = result[col].astype(str).str.strip()

    return enhanced_sanitize_dataframe_for_streamlit(result)

def data_type_operations(df, operation, columns=None):
    result = df.copy()
    target_cols = columns if columns else result.columns

    if operation == 'fix_numeric':
        for col in target_cols:
            if result[col].dtype == 'object':
                try:
                    numeric_col = pd.to_numeric(result[col], errors='ignore')
                    if not numeric_col.equals(result[col]):
                        result[col] = numeric_col
                except:
                    pass

    return enhanced_sanitize_dataframe_for_streamlit(result)

def categorical_operations(df, operation, columns=None):
    result = df.copy()
    target_cols = columns if columns else result.columns

    if operation == 'to_category':
        string_cols = result[target_cols].select_dtypes(include=['object']).columns
        for col in string_cols:
            result[col] = result[col].astype('category')

    return enhanced_sanitize_dataframe_for_streamlit(result)


CLEANING_OPS = [
    "Handling Missing Values", "Removing Missing Values", "Filling Missing Values",
    "Removing Duplicates", "Renaming Columns", "Fixing Data Types",
    "String Cleaning", "Handling Categorical Data", "Replacing Values"
]

OP_MAP1 = {
   "Handling Missing Values": {
    "Show Missing Values": lambda df: handle_missing_values(df, "isnull", columns=st.session_state.get("selected_columns", [])),
    "Count Missing Values": lambda df: handle_missing_values(df, "isnull_sum", columns=st.session_state.get("selected_columns", [])),
    "Show Non-Missing ": lambda df: handle_missing_values(df, "notnull", columns=st.session_state.get("selected_columns", [])),
    "Show Missing Values by Column": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame(df.isnull().sum(), columns=['Missing_Count'])),
    },
    "Removing Missing Values": {
        "Drop All Missing ": lambda df: remove_missing_values(df, 'default'),
        "Drop Empty Columns": lambda df: remove_missing_values(df, 'axis1'),
        "Drop All-Missing Rows": lambda df: remove_missing_values(df, 'all'),
    },
    "Filling Missing Values": {
    "Fill with 0": lambda df: fill_missing_values(df, 'zero', columns=st.session_state.get("selected_columns", [])),
    "Forward Fill": lambda df: fill_missing_values(df, 'ffill', columns=st.session_state.get("selected_columns", [])),
    "Backward Fill": lambda df: fill_missing_values(df, 'bfill', columns=st.session_state.get("selected_columns", [])),
    "Fill with Mean": lambda df: fill_missing_values(df, 'mean', columns=st.session_state.get("selected_columns", [])),
    "Fill with 'Unknown'": lambda df: fill_missing_values(df, 'unknown', columns=st.session_state.get("selected_columns", [])),
    },
    "Removing Duplicates": {
        "Show Duplicates": lambda df: enhanced_sanitize_dataframe_for_streamlit(df[df.duplicated()]),
        "Remove Duplicates": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.drop_duplicates()),
    },
    "Renaming Columns": {
        "View Current Column Names": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame(list(df.columns), columns=['Column_Names'])),
        "Lowercase Column Names": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.rename(columns={col: col.lower() for col in df.columns})),
        "Remove Spaces from Columns": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.rename(columns={col: col.replace(' ', '_') for col in df.columns})),
    },
    "Fixing Data Types": {
    "Auto-Fix Numeric Types": lambda df: data_type_operations(df, 'fix_numeric', columns=st.session_state.get("selected_columns", [])),
    "View Data Types": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame(df.dtypes, columns=['Data_Type'])),
},
    "String Cleaning": {
    "Convert to Lowercase": lambda df: string_operations(df, 'lower', columns=st.session_state.get("selected_columns", [])),
    "Convert to Uppercase": lambda df: string_operations(df, 'upper', columns=st.session_state.get("selected_columns", [])),
    "Strip Whitespace": lambda df: string_operations(df, 'strip', columns=st.session_state.get("selected_columns", [])),
   }, 
    "Handling Categorical Data": {
    "Convert to Category": lambda df: categorical_operations(df, 'to_category', columns=st.session_state.get("selected_columns", [])),
    "View Unique Values": lambda df: enhanced_sanitize_dataframe_for_streamlit(pd.DataFrame([f"{col}: {df[col].nunique()} unique" for col in df.columns], columns=['Unique_Counts'])),
},
    "Replacing Values": {
    "Replace Zero with NaN": lambda df: enhanced_sanitize_dataframe_for_streamlit(df[st.session_state.get("selected_columns", df.columns)].replace(0, np.nan)),
    "Replace Negative with NaN": lambda df: enhanced_sanitize_dataframe_for_streamlit(df[st.session_state.get("selected_columns", df.columns)].applymap(lambda x: np.nan if (isinstance(x, (int, float)) and x < 0) else x)),
},
}