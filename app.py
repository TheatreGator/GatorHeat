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
    """Parses the visual Excel layout to find the Area, Row, Seat, and X, Y coordinates."""
    df_map = pd.read_excel(map_file, header=None)
    seat_coordinates = []
    
    current_area = "MAIN" # Default fallback
    
    for y, row in df_map.iterrows():
        row_label = None
        
        # 1. Scan the row for Area Headings and Row Labels
        for val in row.dropna():
            if isinstance(val, str):
                val_clean = val.strip().upper()
                
                # If it's a word longer than 2 letters (e.g., "STALLS", "DRESS CIRCLE")
                if len(val_clean) > 2 and not val_clean.isnumeric():
                    current_area = val_clean
                
                # If it's a 1-2 letter code (e.g., "A", "AA", "L")
                elif val_clean.isalpha() and len(val_clean) <= 2:
                    if not row_label:
                        row_label = val_clean
                        
        # 2. Find all seat numbers in this row based on Excel column index (x)
        if row_label:
            for x, val in enumerate(row):
                if pd.notna(val) and isinstance(val, (int, float)):
                    try:
                        seat_num = int(float(val))
                        seat_coordinates.append({
                            'Area': current_area,
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
        # 1. Clean data to ensure perfect matching (converting both to uppercase)
        df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.upper()
        df_sales[seat_col] = df_sales[seat_col].astype(str).str.strip().str.upper()
        df_sales[count_col] = pd.to_numeric(df_sales[count_col], errors='coerce').fillna(0)
        
        # 2. Aggregate Duplicate Sales Data 
        df_grouped = df_sales.groupby([area_col, seat_col])[count_col].sum().reset_index()
        
        # 3. Build the Map Grid from Excel
        df_layout = build_coordinate_map(map_file)
        
        # 4. Merge Layout with Aggregated Sales ON BOTH AREA AND SEAT
        # We use a custom function to handle slight area name mismatches (e.g., "Dress" vs "DRESS CIRCLE")
        def match_area(layout_area, sales_data):
            # Try exact match first
            exact_match = sales_data[sales_data[area_col] == layout_area]
            if not exact_match.empty:
                return exact_match
            # Fallback to partial match (e.g., "DRESS" is inside "DRESS CIRCLE")
            partial_match = sales_data[sales_data[area_col].apply(lambda x: x in layout_area or layout_area in x)]
            return partial_match

        # Manual merge to ensure safety across Areas
        merged_records = []
        for _, layout_row in df_layout.iterrows():
            area = layout_row['Area']
            seat = layout_row['Combined_Seat']
            
            # Find the matching data
            area_match = match_area(area, df_grouped)
            seat_match = area_match[area_match[seat_col] == seat]
            
            count = seat_match[count_col].sum() if not seat_match.empty else 0
            
            merged_records.append({
                'Area': area,
                'Combined_Seat': seat,
                'X': layout_row['X'],
                'Y': layout_row['Y'],
                'Row': layout_row['Row'],
                'Count': count
            })
            
        merged_df = pd.DataFrame(merged_records)
        
        # Separate into Sold and Unsold for better plotting control
        unsold_df = merged_df[merged_df['Count'] == 0]
        sold_df = merged_df[merged_df['Count'] > 0]
        
        # --- Build Interactive Plotly Chart ---
        fig = go.Figure()

        # Add Unsold Seats (Grey)
        if not unsold_df.empty:
            fig.add_trace(go.Scatter(
                x=unsold_df['X'], y=unsold_df['Y'],
                mode='markers',
                marker=dict(size=12, color='#e0e0e0', line=dict(width=1, color='DarkSlateGrey')),
                name="Unsold",
                text=unsold_df['Area'] + " - " + unsold_df['Combined_Seat'],
                hovertemplate="<b>%{text}</b><br>Times Sold: 0<extra></extra>"
            ))

        # Add Sold Seats (Heatmap Colors)
        if not sold_df.empty:
            fig.add_trace(go.Scatter(
                x=sold_df['X'], y=sold_df['Y'],
                mode='markers',
                marker=dict(
                    size=12,
                    color=sold_df['Count'],
                    colorscale='YlOrRd',
                    showscale=True,
                    colorbar=dict(title="Times Sold"),
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name="Sold",
                text=sold_df['Area'] + " - " + sold_df['Combined_Seat'],
                customdata=sold_df['Count'],
                hovertemplate="<b>%{text}</b><br>Times Sold: %{customdata}<extra></extra>"
            ))

        # Add Row Labels to the sides (based on the first seat of each row)
        row_labels = df_layout.groupby(['Area', 'Row']).first().reset_index()
        fig.add_trace(go.Scatter(
            x=row_labels['X'] - 1.5, y=row_labels['Y'],
            mode='text',
            text=row_labels['Row'],
            textfont=dict(size=14, color='black'),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Formatting the chart
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

else:
    st.info("Please upload both the Map Layout (Excel) and your Sales Data to generate the chart.")
