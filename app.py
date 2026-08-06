import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Alhambra Interactive Heatmap", layout="wide")

st.title("🎭 Alhambra Theatre Interactive Heatmap")
st.markdown("Upload your **Seating Diagram Excel map** and your **Sales Data**. Hover over the generated seats to see sales counts.")

# --- Data Input Section ---
st.subheader("1. Upload Files & Data")
col1, col2, col3 = st.columns(3)

with col1:
    map_file = st.file_uploader("Upload Map Layout (Seating Diagram_2.xlsx)", type=["xlsx", "xls"])
    
with col2:
    uploaded_file = st.file_uploader("Upload Sales Data (CSV/Excel)", type=["csv", "xlsx", "xls"])

with col3:
    pasted_data = st.text_area("OR Paste Sales Data (e.g., Stalls, L28, 1)", height=100)

# --- Helper Functions ---
@st.cache_data
def load_sales(file, pasted):
    df = pd.DataFrame()
    try:
        if file is not None:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        elif pasted:
            df = pd.read_csv(io.StringIO(pasted), sep=r'\t|,', engine='python')
    except Exception as e:
        st.error(f"Error loading sales data: {e}")
    return df

@st.cache_data
def build_coordinate_map(map_file):
    """Parses the visual Excel layout to find the X, Y coordinates of every seat."""
    df_map = pd.read_excel(map_file, header=None)
    seat_coordinates = []
    
    for y, row in df_map.iterrows():
        row_label = None
        
        # Find the row letter (looks for a short alpha string like 'A', 'AA', 'L')
        for val in row.dropna():
            if isinstance(val, str) and val.strip().isalpha() and len(val.strip()) <= 2:
                row_label = val.strip().upper()
                break 
                
        if not row_label:
            continue 
            
        # Find all seat numbers in this row based on Excel column index (x)
        for x, val in enumerate(row):
            if pd.notna(val) and isinstance(val, (int, float)):
                try:
                    seat_num = int(float(val))
                    seat_coordinates.append({
                        'Row': row_label,
                        'Seat_Num': seat_num,
                        'Combined_Seat': f"{row_label}{seat_num}",
                        'X': x,
                        'Y': y
                    })
                except ValueError:
                    pass
                    
    return pd.DataFrame(seat_coordinates)

# --- Main Logic ---
df_sales = load_sales(uploaded_file, pasted_data)

if map_file is not None and not df_sales.empty:
    st.success("Both Map and Sales data loaded successfully!")
    
    st.markdown("---")
    st.subheader("2. Map Your Sales Columns")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        area_col = st.selectbox("Area Column (e.g., Stalls)", df_sales.columns, index=0)
    with c2:
        seat_col = st.selectbox("Seat Column (e.g., L28)", df_sales.columns, index=1 if len(df_sales.columns) > 1 else 0)
    with c3:
        count_col = st.selectbox("Sales Count Column", df_sales.columns, index=2 if len(df_sales.columns) > 2 else 0)

    if st.button("Generate Interactive Heatmap"):
        # 1. Clean sales data to ensure perfect matching
        df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.title()
        df_sales[seat_col] = df_sales[seat_col].astype(str).str.strip().str.upper()
        df_sales[count_col] = pd.to_numeric(df_sales[count_col], errors='coerce').fillna(0)
        
        # 2. Aggregate Duplicate Sales Data (e.g., sum up multiple "L28" entries)
        df_grouped = df_sales.groupby([area_col, seat_col])[count_col].sum().reset_index()
        
        # 3. Build the Map Grid from Excel
        df_layout = build_coordinate_map(map_file)
        df_layout['Combined_Seat'] = df_layout['Combined_Seat'].astype(str)
        
        # 4. Merge Layout with Aggregated Sales
        merged_df = pd.merge(
            df_layout, df_grouped,
            how='left',
            left_on='Combined_Seat',
            right_on=seat_col
        )
        merged_df[count_col] = merged_df[count_col].fillna(0)
        
        # Separate into Sold and Unsold for better plotting control
        unsold_df = merged_df[merged_df[count_col] == 0]
        sold_df = merged_df[merged_df[count_col] > 0]
        
        # --- Build Interactive Plotly Chart ---
        fig = go.Figure()

        # Add Unsold Seats (Grey)
        if not unsold_df.empty:
            fig.add_trace(go.Scatter(
                x=unsold_df['X'], y=unsold_df['Y'],
                mode='markers',
                marker=dict(size=12, color='#e0e0e0', line=dict(width=1, color='DarkSlateGrey')),
                name="Unsold",
                text=unsold_df['Combined_Seat'],
                hovertemplate="<b>Seat: %{text}</b><br>Times Sold: 0<extra></extra>"
            ))

        # Add Sold Seats (Heatmap Colors)
        if not sold_df.empty:
            fig.add_trace(go.Scatter(
                x=sold_df['X'], y=sold_df['Y'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=sold_df[count_col],
                    colorscale='YlOrRd',
                    showscale=True,
                    colorbar=dict(title="Times Sold"),
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name="Sold",
                text=sold_df['Combined_Seat'],
                customdata=sold_df[count_col],
                hovertemplate="<b>Seat: %{text}</b><br>Times Sold: %{customdata}<extra></extra>"
            ))

        # Add Row Labels to the sides (based on the first seat of each row)
        row_labels = df_layout.groupby('Row').first().reset_index()
        fig.add_trace(go.Scatter(
            x=row_labels['X'] - 1.5, y=row_labels['Y'],
            mode='text',
            text=row_labels['Row'],
            textfont=dict(size=14, color='black'),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Formatting the chart to look like a theatre layout
        fig.update_layout(
            title="Interactive Alhambra Seating Heatmap",
            plot_bgcolor='white',
            width=1200,
            height=900,
            yaxis=dict(
                autorange='reversed', # Ensure the stage is at the top
                showgrid=False, zeroline=False, visible=False
            ),
            xaxis=dict(
                showgrid=False, zeroline=False, visible=False
            ),
            hovermode="closest"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Tip: You can zoom in, pan around, and hover your mouse over any seat to see its data. Double-click the chart to reset the zoom.")

else:
    st.info("Please upload both the Map Layout (Excel) and your Sales Data to generate the chart.")
