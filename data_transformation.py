import streamlit as st
from utils import back_button, next_button, nav
from transforming_operations import TRANSFORM_OPS, OP_MAP2

def transform_menu():
    back_button("cleaning_menu")
    st.title("Data Transformation")
    n_cols = 3
    rows = [TRANSFORM_OPS[i:i + n_cols] for i in range(0, len(TRANSFORM_OPS), n_cols)]
    for row in rows:
        cols = st.columns(n_cols)
        for idx, btn in enumerate(row):
            if idx < len(row):
                with cols[idx]:
                    if st.button(btn, key=f"trans_{btn}"):
                        st.session_state.operation_set = btn
                        st.write(f"Debug: Setting operation_set to: {btn}") 
                        nav("transform_operation")
    st.markdown("---")
    next_button("Next", "visualize")

def transform_operation_page():
    from utils import enhanced_sanitize_dataframe_for_streamlit, safe_display_dataframe

    if "operation_set" not in st.session_state:
        st.error("No operation selected. Please go back and select an operation.")
        st.write("Available session state keys:", list(st.session_state.keys()))
        back_button("transform_menu")
        return

    if "df" not in st.session_state:
        st.error("No dataframe found. Please load data first.")
        back_button("transform_menu")
        return

    df = st.session_state.df.copy()
    op_group = st.session_state.operation_set

    back_button("transform_menu")
    st.title(op_group)

    if op_group not in OP_MAP2:
        st.error("Operation not found!")
        st.warning(f"'{op_group}' is not a valid key in OP_MAP2")
        from difflib import get_close_matches
        matches = get_close_matches(op_group, OP_MAP2.keys(), n=3, cutoff=0.6)
        if matches:
            st.info("Did you mean one of these?")
            for match in matches:
                if st.button(f"Use '{match}' instead", key=f"fallback_{match}"):
                    st.session_state.operation_set = match
                    st.rerun()
        else:
            st.info("Available operations:")
            for key in OP_MAP2.keys():
                st.write(f"- {key}")
        return

    operations = OP_MAP2[op_group]
    st.subheader("Select an operation:")

    column_select_ops = [
        "Mathematical Transformations", "Feature Scaling",
        "Encoding Categorical Variables", "String Transformations",
        "Discretization Binning", "Datetime Transformation",
        "Type Conversion", "Create a New Column"
    ]

    for op_label, func in operations.items():
        needs_columns = op_group in column_select_ops

        if op_label == "Create Custom Column":
            with st.expander(f"{op_label}", expanded=True):
                all_columns = list(df.columns)
                col1 = st.selectbox("Select first column", all_columns, key="col1")
                col2 = st.selectbox("Select second column", all_columns, key="col2")
                operation = st.selectbox("Select operation", ["+", "-", "*", "/"], key="operation")
                new_col_name = st.text_input("Enter name for new column", key="new_col_name")

                if st.button(op_label, key=f"op_{op_label}"):
                    if not col1 or not col2 or not operation or not new_col_name:
                        st.warning("Please fill in all the required fields.")
                    else:
                        try:
                            with st.spinner("Creating new column..."):
                                df_result = func(df)
                                df_result = enhanced_sanitize_dataframe_for_streamlit(df_result)
                                st.session_state.df = df_result
                                st.success(f"Custom column '{new_col_name}' created successfully!")
                                st.subheader("Updated Data Preview")
                                safe_display_dataframe(df_result)
                        except Exception as e:
                            st.error(f"Error applying operation: {str(e)}")
                            st.write("**Error details:**", e)

        elif needs_columns:
            with st.expander(f"{op_label}", expanded=True):
                all_columns = list(df.columns)
                selected_columns = st.multiselect(
                    f"Select columns for {op_label}", 
                    options=all_columns, 
                    default=None, 
                    key=f"cols_{op_label}",
                    help="Choose which columns to apply this transformation to"
                )

                inplace = st.toggle(f"Apply inplace for '{op_label}'", value=True, key=f"inplace_{op_label}")

                if st.button(op_label, key=f"op_{op_label}"):
                    if not selected_columns:
                        st.warning("Please select at least one column before applying the operation.")
                    else:
                        st.session_state.selected_columns = selected_columns

                        try:
                            with st.spinner(f"Applying {op_label}..."):
                                df_result = func(df)
                                df_result = enhanced_sanitize_dataframe_for_streamlit(df_result)
                                st.session_state.df = df_result
                                st.success(f"Operation '{op_label}' applied successfully!")
                                st.subheader("Updated Data Preview")
                                safe_display_dataframe(df_result)
                                if df_result.shape != df.shape:
                                    st.info(f"Data shape changed: {df.shape} → {df_result.shape}")
                        except Exception as e:
                            st.error(f" Error applying operation: {str(e)}")
                            st.write("**Error details:**", e)

        else:
            if st.button(op_label, key=f"op_{op_label}"):
                try:
                    with st.spinner(f"Applying {op_label}..."):
                        df_result = func(df)
                        df_result = enhanced_sanitize_dataframe_for_streamlit(df_result)
                        st.session_state.df = df_result
                        st.success(f"Operation '{op_label}' applied successfully!")
                        st.subheader("Updated Data Preview")
                        safe_display_dataframe(df_result)
                        if df_result.shape != df.shape:
                            st.info(f" Data shape changed: {df.shape} → {df_result.shape}")
                except Exception as e:
                    st.error(f"Error applying operation: {str(e)}")
                    st.write("**Error details:**", e)

    # Custom Python interpreter
    st.markdown("---")
    st.subheader(" Run Custom Python Code")

    user_code = st.text_area("Enter your Python code below:", height=100, key="user_code_input")
    st.info("""You can interact with your current dataset using the variable df. Any changes to df will update the main dataset.""")

    if st.button("Run Code"):
        try:
            local_vars = {"df": st.session_state.df.copy()}
            exec(user_code, {}, local_vars)
            if "df" in local_vars:
                st.session_state.df = enhanced_sanitize_dataframe_for_streamlit(local_vars["df"])
                st.success("Code executed successfully! DataFrame updated.")
                st.subheader("Updated Data Preview")
                safe_display_dataframe(st.session_state.df)
            else:
                st.info("Code executed, but 'df' was not modified.")
        except Exception as e:
            st.error("Error while executing your code:")
            st.code(str(e))