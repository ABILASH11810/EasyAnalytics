import pandas as pd
import streamlit as st
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from utils import enhanced_sanitize_dataframe_for_streamlit

TRANSFORM_OPS = [
    "Mathematical Transformations", "Feature Scaling", "Encoding Categorical Variables",
    "Discretization Binning", "Datetime Transformation", "Column Operations",
    "String Transformations", "Type Conversion", "Create a New Column"
]

def math_transformations(df, operation, columns=None, inplace=True):
    result = df.copy()
    target_cols = columns if columns else result.select_dtypes(include=[np.number]).columns

    for col in target_cols:
        try:
            if operation == 'log':
                transformed = np.log(result[col] + 1)
            elif operation == 'sqrt':
                transformed = np.sqrt(result[col].abs())
            elif operation == 'square':
                transformed = result[col] ** 2
            else:
                continue

            if inplace:
                result[col] = transformed
            else:
                result[f"{operation}_{col}"] = transformed
        except Exception as e:
            st.warning(f"Failed to transform column '{col}': {e}")

    return enhanced_sanitize_dataframe_for_streamlit(result)

def scaling_operations(df, method, columns=None, inplace=True):
    result = df.copy()
    target_cols = columns if columns else result.select_dtypes(include=[np.number]).columns

    if result[target_cols].empty:
        st.warning("No numeric columns found for scaling.")
        return enhanced_sanitize_dataframe_for_streamlit(df)

    if method == 'minmax':
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()

    try:
        scaled_data = scaler.fit_transform(result[target_cols])
        if inplace:
            result[target_cols] = scaled_data
        else:
            for idx, col in enumerate(target_cols):
                result[f"{method}_scaled_{col}"] = scaled_data[:, idx]
    except Exception as e:
        st.warning(f"Scaling failed: {e}")

    return enhanced_sanitize_dataframe_for_streamlit(result)

def create_new_column(df, col1, col2, operation, new_col):
    result = df.copy()

    if not (np.issubdtype(result[col1].dtype, np.number) and np.issubdtype(result[col2].dtype, np.number)):
        st.error("Operation can be performed only between 2 numeric columns")
        return enhanced_sanitize_dataframe_for_streamlit(result)

    try:
        if operation == '+':
            result[new_col] = result[col1] + result[col2]
        elif operation == '-':
            result[new_col] = result[col1] - result[col2]
        elif operation == '*':
            result[new_col] = result[col1] * result[col2]
        elif operation == '/':
            result[new_col] = result[col1] / result[col2]
        else:
            st.error(f"Unsupported operation: {operation}")
    except Exception as e:
        st.error(f"Error while creating new column: {e}")

    return enhanced_sanitize_dataframe_for_streamlit(result)

def convert_str_int_columns(df, columns=None):
    result = df.copy()
    target_cols = columns if columns else result.columns

    for col in target_cols:
        try:
            result[col] = pd.to_numeric(result[col], errors='raise')
        except Exception as e:
            st.warning(f"Column '{col}' could not be converted: {e}")

    return enhanced_sanitize_dataframe_for_streamlit(result)

OP_MAP2={
    "Mathematical Transformations": {
        "Log Transform": lambda df, label="Log Transform": math_transformations(
            df, 'log',
            columns=st.session_state.get("selected_columns", []),
            inplace=st.session_state.get(f"inplace_{label}", True)
        ),
        "Square Root Transform": lambda df, label="Square Root Transform": math_transformations(
            df, 'sqrt',
            columns=st.session_state.get("selected_columns", []),
            inplace=st.session_state.get(f"inplace_{label}", True)
        ),
        "Square Transform": lambda df, label="Square Transform": math_transformations(
            df, 'square',
            columns=st.session_state.get("selected_columns", []),
            inplace=st.session_state.get(f"inplace_{label}", True)
        ),
    },

    "Feature Scaling": {
        "Min-Max Scaling": lambda df, label="Min-Max Scaling": scaling_operations(
            df, 'minmax',
            columns=st.session_state.get("selected_columns", []),
            inplace=st.session_state.get(f"inplace_{label}", True)
        ),
        "Standard Scaling (Z-score)": lambda df, label="Standard Scaling (Z-score)": scaling_operations(
            df, 'standard',
            columns=st.session_state.get("selected_columns", []),
            inplace=st.session_state.get(f"inplace_{label}", True)
        ),
    },

    "Encoding Categorical Variables": {
        "Label Encoding": lambda df: enhanced_sanitize_dataframe_for_streamlit(
            df.select_dtypes(include=['object', 'category']).apply(lambda x: pd.Categorical(x).codes)
        ),
        "One-Hot Encoding": lambda df: enhanced_sanitize_dataframe_for_streamlit(
            pd.get_dummies(df, prefix_sep='_')
        ),
    },

    "Discretization Binning": {
        "Equal-Width Binning": lambda df: enhanced_sanitize_dataframe_for_streamlit(
            df.select_dtypes(include=[np.number]).apply(
                lambda x: pd.cut(x, bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
            )
        ),
        "Quantile Binning": lambda df: enhanced_sanitize_dataframe_for_streamlit(
            df.select_dtypes(include=[np.number]).apply(
                lambda x: pd.qcut(x, q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
            )
        ),
    },

    "Column Operations": {
        "Add Row Index": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.reset_index()),
        "Remove Index": lambda df: enhanced_sanitize_dataframe_for_streamlit(df.reset_index(drop=True)),
    },

    "Datetime Transformation": {
       "Parse Dates": lambda df: enhanced_sanitize_dataframe_for_streamlit(
    df.assign(**{
        col: pd.to_datetime(df[col], errors="ignore")
        for col in df.select_dtypes(include=["object"]).columns
    })),

    "Extract Date Components": lambda df: enhanced_sanitize_dataframe_for_streamlit(
    df.assign(**{
        key: value
        for col in df.select_dtypes(include=["datetime64"]).columns
        for key, value in {
            f"{col}_year": df[col].dt.year,
            f"{col}_month": df[col].dt.month,
            f"{col}_day": df[col].dt.day
        }.items()
    })
)

    },
    "Create a New Column": {
        "Create Custom Column": lambda df: create_new_column(
    df,
    col1=st.session_state.get("col1"),
    col2=st.session_state.get("col2"),
    operation=st.session_state.get("operation"),
    new_col=st.session_state.get("new_col_name")
)

    },

    "Type Conversion": {
        "Convert String Integers to Int": lambda df: convert_str_int_columns(
            df, columns=st.session_state.get("selected_columns", [])
        )
    },

    "String Transformations": {
        "Convert to Uppercase": lambda df: enhanced_sanitize_dataframe_for_streamlit(
            df.select_dtypes(include=['object']).apply(lambda x: x.str.upper())
        ),
        "Convert to Lowercase": lambda df: enhanced_sanitize_dataframe_for_streamlit(
            df.select_dtypes(include=['object']).apply(lambda x: x.str.lower())
        ),
    "Remove Whitespace": lambda df: enhanced_sanitize_dataframe_for_streamlit(
        df.select_dtypes(include=['object']).apply(lambda x: x.str.strip())
    )
}
}
