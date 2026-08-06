import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io

st.set_page_config(page_title="Alhambra Theatre Heatmap", layout="wide")

st.title("🎭 Alhambra Theatre Seating Heatmap")
st.markdown("This app reads your visual **Seating Diagram.xlsx** to build a coordinate map, then overlays your sales data.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Sales Data")
    sales_file = st.file_uploader("Upload Sales (CSV/Excel)", type=["csv", "xlsx", "xls"])
    st.info("Your data must have a column for Row (e.g., A) and a column for Seat (e.g., 6).")

with col2:
    st.subheader("2. Upload Map Layout")
    map_file = st.file_uploader("Upload 'Seating Diagram.xlsx'", type=["xlsx", "xls"])

# --- Helper Functions ---
@st.cache_data
def load_sales(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    return pd.read_excel(file)

@st.cache_data
def build_coordinate_map(map_file):
    """
    Parses the visual Excel layout to find the X, Y coordinates of every seat.
    Assumes row letters (A, B, C) are on the far left or right, and numbers are the seats.
    """
    # Read without headers to treat it as a pure grid
    df_map = pd.read_excel(map_file, header=None)
    
    seat_coordinates = []
    
    # Iterate through the excel grid
    for y, row in df_map.iterrows():
        row_label = None
        
        # Try to find the row label (usually a string like 'A', 'B', 'AA' on the left/right)
        for val in row.dropna():
            if isinstance(val, str) and len(val.strip()) <= 2 and val.strip().isalpha():
                row_label = val.strip()
                break # Found the row letter
                
        if not row_label:
            continue # Skip empty rows or rows without a letter
            
        # Now find all the seat numbers in this row
        for x, val in enumerate(row):
            if pd.notna(val) and isinstance(val, (int, float)):
                try:
                    seat_num = int(float(val))
                    seat_coordinates.append({
                        'Row': row_label,
                        'Seat': seat_num,
                        'X': x,
                        'Y': y
                    })
                except ValueError:
                    pass
                    
    return pd.DataFrame(seat_coordinates)

# --- Main Logic ---
if sales_file and map_file:
    df_sales = load_sales(sales_file)
    df_coords = build_coordinate_map(map_file)
    
    st.success("Files loaded! We mapped {} seats from your Excel layout.".format(len(df_coords)))
    
    st.markdown("---")
    st.subheader("3. Map Your Columns")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        sales_row_col = st.selectbox("Sales Data: ROW Column (e.g., A)", df_sales.columns)
    with c2:
        sales_seat_col = st.selectbox("Sales Data: SEAT Column (e.g., 6)", df_sales.columns)
    with c3:
        sales_count_col = st.selectbox("Sales Data: COUNT/SOLD Column", df_sales.columns)

    if st.button("Generate Heatmap"):
        # Standardize data types to ensure matching
        df_sales[sales_row_col] = df_sales[sales_row_col].astype(str).str.strip()
        df_sales[sales_seat_col] = pd.to_numeric(df_sales[sales_seat_col], errors='coerce').fillna(-1).astype(int)
        
        # Merge the Map Coordinates with the Sales Data
        merged_df = pd.merge(
            df_coords, 
            df_sales, 
            how='left', 
            left_on=['Row', 'Seat'], 
            right_on=[sales_row_col, sales_seat_col]
        )
        
        # Fill unsold seats with 0
        merged_df[sales_count_col] = merged_df[sales_count_col].fillna(0)
        
        max_sales = merged_df[sales_count_col].max()
        
        # --- Plotting the Heatmap ---
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # Plot unsold seats in light grey
        unsold = merged_df[merged_df[sales_count_col] == 0]
        ax.scatter(unsold['X'], unsold['Y'], c='#e0e0e0', s=100, label='Unsold/House')
        
        # Plot sold seats with heatmap colors
        sold = merged_df[merged_df[sales_count_col] > 0]
        if not sold.empty:
            scatter = ax.scatter(
                sold['X'], sold['Y'], 
                c=sold[sales_count_col], 
                cmap='YlOrRd', 
                s=100,
                vmin=0, vmax=max_sales
            )
            plt.colorbar(scatter, ax=ax, label='Times Sold')
            
        # Formatting to make it look like a theatre map
        ax.invert_yaxis() # Stage is at the top (lowest Y in excel)
        ax.set_facecolor('white')
        ax.axis('off') # Hide the grid lines and axes
        
        # Add Row Labels to the left side
        for _, row in df_coords.drop_duplicates(subset=['Row']).iterrows():
            ax.text(row['X'] - 1.5, row['Y'], row['Row'], va='center', ha='right', fontsize=9, fontweight='bold')
            
        plt.title("Alhambra Theatre Seating Heatmap", fontsize=16, pad=20)
        
        st.pyplot(fig)
        
        st.info("Note: Any house seats, wheelchair spaces, or company seats represented in the Excel file by non-numbers were automatically excluded. If they appear in your sales data, they will only map if they have a standard row/seat number in the Excel layout.")
