import streamlit as st
from utils import back_button, next_button, nav
from cleaning_operations import CLEANING_OPS, OP_MAP1

def cleaning_menu():
    back_button("upload")
    st.title("Data Cleaning")
    n_cols = 3
    rows = [CLEANING_OPS[i:i + n_cols] for i in range(0, len(CLEANING_OPS), n_cols)]
    for row in rows:
        cols = st.columns(n_cols)
        for idx, btn in enumerate(row):
            if idx < len(row):
                with cols[idx]:
                    if st.button(btn, key=f"clean_{btn}"):
                        st.session_state.operation_set = btn
                        nav("operation")
    st.markdown("---")
    next_button("Next", "transform_menu")

def operation_page():
    from utils import enhanced_sanitize_dataframe_for_streamlit, safe_display_dataframe
    df = st.session_state.df.copy()
    op_group = st.session_state.operation_set
    back_button("cleaning_menu")
    st.title(op_group)

    if op_group not in OP_MAP1:
        st.error("Operation not found!")
        return

    operations = OP_MAP1[op_group]
    st.subheader("Select an operation:")

    DISPLAY_OPS = {
        "Handling Missing Values": ["Show Missing Values", "Count Missing Values", "Show Non-Missing ", "Show Missing Values by Column"],
        "Fixing Data Types": ["View Data Types"],
        "Renaming Columns": ["View Current Column Names"],
        "Removing Duplicates": ["Show Duplicates"],
        "Handling Categorical Data": ["View Unique Values"]
    }

    for op_label, func in operations.items():
        is_display_op = op_label in DISPLAY_OPS.get(op_group, [])

        with st.expander(op_label, expanded=True):
            requires_columns = any(keyword in op_label.lower() for keyword in [
                "fill", "missing", "string", "category", "replace", "convert", "fix", "strip", "lower", "upper"
            ]) and not is_display_op

            if requires_columns:
                all_columns = list(df.columns)
                selected_columns = st.multiselect("Select columns", options=all_columns, default=[], key=f"cols_{op_label}")
                st.session_state.selected_columns = selected_columns

            if st.button(op_label, key=f"op_{op_group}_{op_label}"):
                try:
                    with st.spinner(f"Applying {op_label}..."):
                        df_result = func(df)
                        df_result = enhanced_sanitize_dataframe_for_streamlit(df_result)

                        if is_display_op:
                            st.session_state.last_result = df_result
                            st.success(f"Output generated for '{op_label}'")
                            st.subheader("Result Preview")
                            safe_display_dataframe(df_result)
                        else:
                            st.session_state.df = df_result
                            st.success(f"Operation '{op_label}' applied successfully!")
                            st.subheader("Updated Data Preview")
                            safe_display_dataframe(df_result)
                            if df_result.shape != df.shape:
                                st.info(f"Data shape changed: {df.shape} → {df_result.shape}")
                except Exception as e:
                    st.error(f"Error applying operation: {str(e)}")

    st.markdown("---")
    st.subheader(" Run Custom Python Code")

    st.info("""You can interact with your current dataset using the variable df. Any changes to df will update the main dataset.""")

    user_code = st.text_area("Enter your Python code below:", height=100, key="user_code_input_cleaning")

    if st.button("Run Code", key="run_code_cleaning"):
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
            st.error(" Error while executing your code:")
            st.code(str(e))
