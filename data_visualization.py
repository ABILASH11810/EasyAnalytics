import streamlit as st
from utils import back_button, next_button, safe_display_dataframe
import plotly.express as px
import numpy as np

def visualization_page():
    back_button("transform_menu")
    st.title("Data Visualization")
    if st.session_state.df is None:
        st.error("No dataset loaded. Please upload data first.")
        return
    df = st.session_state.df

    chart_types = [
        "Line", "Bar", "Histogram", "Box", "Scatter", "Pie", 
        "Heatmap", "Area", "Violin", "Strip", "Sunburst", "Treemap", "Funnel"
    ]
    
    chart_type = st.selectbox("Select Chart Type", chart_types)
   
    tab1, tab2, tab3, tab4 = st.tabs([" Basic", "Styling", "Layout", "Interactive"])
  
    params = {}
    
    with tab1:
        st.subheader("Data Mapping")
  
        if chart_type in ["Line", "Bar", "Area"]:
            params['x'] = st.selectbox("X-axis", df.columns, key="x_basic")
            params['y'] = st.selectbox("Y-axis", df.columns, key="y_basic")
        elif chart_type == "Scatter":
            params['x'] = st.selectbox("X-axis", df.columns, key="x_scatter")
            params['y'] = st.selectbox("Y-axis", df.columns, key="y_scatter")
        elif chart_type == "Histogram":
            params['x'] = st.selectbox("Column to analyze", df.columns, key="x_hist")
        elif chart_type in ["Box", "Violin", "Strip"]:
            params['x'] = st.selectbox("Category (X-axis)", df.columns, key="x_box")
            params['y'] = st.selectbox("Values (Y-axis)", df.columns, key="y_box")
        elif chart_type == "Pie":
            params['names'] = st.selectbox("Categories", df.columns, key="pie_names")
            params['values'] = st.selectbox("Values", df.columns, key="pie_values")
        elif chart_type == "Heatmap":
            st.info("Heatmap will use correlation matrix of numerical columns")
        elif chart_type in ["Sunburst", "Treemap"]:
            params['path'] = st.multiselect("Hierarchical Path", df.columns, key="path_hier")
            params['values'] = st.selectbox("Values", df.columns, key="values_hier")
        elif chart_type == "Funnel":
            params['x'] = st.selectbox("Values", df.columns, key="funnel_x")
            params['y'] = st.selectbox("Categories", df.columns, key="funnel_y")
        
        # Additional mappings
        st.subheader("Additional Mappings")
        
        color_col = st.selectbox("Color by (optional)", [None] + list(df.columns), key="color_mapping")
        if color_col:
            params['color'] = color_col
            
        if chart_type == "Scatter":
            size_col = st.selectbox("Size by (optional)", [None] + list(df.columns), key="size_mapping")
            if size_col:
                params['size'] = size_col
            
            symbol_col = st.selectbox("Symbol by (optional)", [None] + list(df.columns), key="symbol_mapping")
            if symbol_col:
                params['symbol'] = symbol_col
        
        # Faceting
        facet_col = st.selectbox("Facet by (optional)", [None] + list(df.columns), key="facet_mapping")
        if facet_col:
            params['facet_col'] = facet_col
        
        facet_row = st.selectbox("Facet rows (optional)", [None] + list(df.columns), key="facet_row_mapping")
        if facet_row:
            params['facet_row'] = facet_row
    
    with tab2:
        st.subheader("Color Configuration")
        
        if 'color' in params:
            if df[params['color']].dtype in ['object', 'category']:
                color_discrete = st.selectbox("Color Palette", 
                    ['plotly', 'Set1', 'Set2', 'Set3', 'Pastel1', 'Pastel2', 'Dark2'], key="color_discrete")
                params['color_discrete_sequence'] = getattr(px.colors.qualitative, color_discrete, None)
            else:
                color_continuous = st.selectbox("Color Scale", 
                    ['Viridis', 'Plasma', 'Blues', 'Reds', 'YlOrRd'], key="color_continuous")
                params['color_continuous_scale'] = color_continuous
        
        
        # Chart-specific styling
        if chart_type == "Line":
            line_shape = st.selectbox("Line Shape", 
                ['linear', 'spline', 'vh', 'hv', 'vhv', 'hvh'], key="line_shape")
            params['line_shape'] = line_shape
            
            show_markers = st.checkbox("Show Markers", key="show_markers")
            if show_markers:
                params['markers'] = True
        
        elif chart_type == "Bar":
            orientation = st.selectbox("Orientation", ['vertical', 'horizontal'], key="bar_orientation")
            if orientation == 'horizontal':
                params['orientation'] = 'h'
        
        elif chart_type == "Histogram":
            nbins = st.number_input("Number of Bins", 1, 100, 20, key="hist_bins")
            params['nbins'] = nbins
            
            histnorm = st.selectbox("Normalization", 
                [None, 'percent', 'probability', 'density'], key="hist_norm")
            if histnorm:
                params['histnorm'] = histnorm
        
        elif chart_type == "Scatter":
            size_max = st.slider("Maximum Marker Size", 5, 50, 20, key="size_max")
            params['size_max'] = size_max
        
        # Error bars
        if chart_type in ["Bar", "Scatter", "Line"]:
            st.subheader("Error Bars")
            error_x = st.selectbox("X Error (optional)", [None] + list(df.columns), key="error_x")
            if error_x:
                params['error_x'] = error_x
                
            error_y = st.selectbox("Y Error (optional)", [None] + list(df.columns), key="error_y")
            if error_y:
                params['error_y'] = error_y
    
    with tab3:
        st.subheader("Titles and Labels")
        
        title = st.text_input("Chart Title", f"{chart_type} Chart", key="chart_title")
        params['title'] = title
        
        if 'x' in params:
            x_label = st.text_input("X-axis Label", params['x'], key="x_label")
            params['labels'] = params.get('labels', {})
            params['labels']['x'] = x_label
        
        if 'y' in params:
            y_label = st.text_input("Y-axis Label", params['y'], key="y_label")
            params['labels'] = params.get('labels', {})
            params['labels']['y'] = y_label
        
        st.subheader("Chart Dimensions")
        
        width = st.number_input("Width (pixels)", 400, 2000, 800, key="chart_width")
        height = st.number_input("Height (pixels)", 300, 1500, 600, key="chart_height")
        params['width'] = width
        params['height'] = height
        
        st.subheader("Axis Configuration")
        
        if chart_type != "Heatmap":
            log_x = st.checkbox("Logarithmic X-axis", key="log_x")
            if log_x:
                params['log_x'] = True
                
            log_y = st.checkbox("Logarithmic Y-axis", key="log_y")
            if log_y:
                params['log_y'] = True
        
        st.subheader("Theme")
        template = st.selectbox("Chart Template", 
            ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white'], 
            key="template")
        params['template'] = template
    
    with tab4:
        st.subheader("Animation")
        
        animation_frame = st.selectbox("Animation Frame (optional)", 
            [None] + list(df.columns), key="animation_frame")
        if animation_frame:
            params['animation_frame'] = animation_frame
            
        animation_group = st.selectbox("Animation Group (optional)", 
            [None] + list(df.columns), key="animation_group")
        if animation_group:
            params['animation_group'] = animation_group
        
        if chart_type == "Scatter":
            st.subheader("Marginal Plots")
            marginal_x = st.selectbox("Marginal X Plot", 
                [None, 'histogram', 'box', 'violin', 'rug'], key="marginal_x")
            if marginal_x:
                params['marginal_x'] = marginal_x
                
            marginal_y = st.selectbox("Marginal Y Plot", 
                [None, 'histogram', 'box', 'violin', 'rug'], key="marginal_y")
            if marginal_y:
                params['marginal_y'] = marginal_y
            
            st.subheader("Trendline")
            trendline = st.selectbox("Trendline Type", 
                [None, 'ols', 'lowess'], key="trendline")
            if trendline:
                params['trendline'] = trendline
        
        if chart_type == "Line":
            line_group = st.selectbox("Line Group (optional)", 
                [None] + list(df.columns), key="line_group")
            if line_group:
                params['line_group'] = line_group
    

    if st.button(" Generate Chart", key="generate_chart"):
        try:
            with st.spinner("Generating chart..."):
                fig = create_chart(df, chart_type, params)
                st.plotly_chart(fig, use_container_width=True)
                

                with st.expander("View Parameters Used"):
                    st.json(params)
                    
        except Exception as e:
            st.error(f"Error generating chart: {str(e)}")
    
    next_button("Next", "export")

def create_chart(df, chart_type, params):
    """Create chart based on type and parameters"""

    clean_params = {k: v for k, v in params.items() if v is not None and v != ""}
    
    if chart_type == "Line":
        return px.line(df, **clean_params)
    elif chart_type == "Bar":
        return px.bar(df, **clean_params)
    elif chart_type == "Histogram":
        return px.histogram(df, **clean_params)
    elif chart_type == "Box":
        return px.box(df, **clean_params)
    elif chart_type == "Scatter":
        return px.scatter(df, **clean_params)
    elif chart_type == "Pie":
        return px.pie(df, **clean_params)
    elif chart_type == "Heatmap":
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            st.warning("No numeric columns found for correlation heatmap.")
            return px.scatter(x=[0], y=[0], title="No numeric data available")
        corr_matrix = numeric_df.corr()
        return px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                        title=clean_params.get('title', 'Correlation Heatmap'))
    elif chart_type == "Area":
        return px.area(df, **clean_params)
    elif chart_type == "Violin":
        return px.violin(df, **clean_params)
    elif chart_type == "Strip":
        return px.strip(df, **clean_params)
    elif chart_type == "Sunburst":
        return px.sunburst(df, **clean_params)
    elif chart_type == "Treemap":
        return px.treemap(df, **clean_params)
    elif chart_type == "Funnel":
        return px.funnel(df, **clean_params)
