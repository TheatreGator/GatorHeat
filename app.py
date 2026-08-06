import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Alhambra Interactive Heatmap", layout="wide")

st.title("🎭 Alhambra Theatre Interactive Heatmap")
st.markdown("Upload your **Full Seat List** (to build the physical layout) and your **Sales Data** (to color the heatmap).")

# --- Data Input Section ---
st.subheader("1. Upload Files")
col1, col2, col3 = st.columns(3)

with col1:
    master_file = st.file_uploader("Upload Full Seat List (Excel)", type=["xlsx", "xls"])
with col2:
    sales_file = st.file_uploader("Upload Sales Data (CSV/Excel)", type=["csv", "xlsx", "xls"])
with col3:
    pasted_data = st.text_area("OR Paste Sales Data", height=100)

# --- Helper Functions ---
@st.cache_data
def load_data(file, pasted=None):
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
        st.error(f"Error loading data: {e}")
    return df

def generate_dynamic_row(area, row_letter, valid_seats, base_y, max_seats_in_area, spacing=14, curve_factor=0.0003, gap_center=0):
    """Generates X/Y coordinates ONLY for valid seats in the Master List."""
    row_layout = []
    
    for seat_num in valid_seats:
        # X position: Base it so seat 1 is far right (High X), max seat is far left (Low X)
        x = 500 + (max_seats_in_area * spacing / 2) - (seat_num * spacing)
        
        # Apply center aisle gap if necessary
        if gap_center > 0:
            if seat_num > max_seats_in_area / 2: x -= gap_center / 2
            else: x += gap_center / 2
                
        # Y position: Base height + a gentle curve mapping the distance from center
        dist_from_center = abs(x - 500)
        y = base_y + (curve_factor * (dist_from_center ** 2))
        
        row_layout.append({
            'Area': area, 'Row': row_letter, 'Seat_Num': seat_num, 
            'Combined_Seat': f"{row_letter}{seat_num}", 'X': x, 'Y': y
        })
    return row_layout

@st.cache_data
def build_master_layout(df_master):
    """Builds the physical structure precisely matching the Full Seat List."""
    layout = []
    
    # 1. STALLS
    stalls = df_master[df_master['Area'] == 'Stalls']
    if not stalls.empty:
        max_s = stalls['Seat Number'].max()
        y = 100
        for r in sorted(stalls['Row'].unique()):
            seats = stalls[stalls['Row'] == r]['Seat Number'].tolist()
            layout.extend(generate_dynamic_row('Stalls', r, seats, y, max_s, curve_factor=0.0004))
            y += 18 
        stalls_bottom_y = y
    else: stalls_bottom_y = 500

    # 2. STALLS LOUNGE (Behind Stalls, split into Left and Right)
    lounges = df_master[df_master['Area'] == 'Stalls Lounge']
    if not lounges.empty:
        for _, row in lounges.iterrows():
            r = row['Row']
            s = row['Seat Number']
            # Lounge A (Left side - Row A in data), Lounge B (Right side - Row B in data)
            x = 320 - (s*16) if r == 'A' else 680 - (s*16)
            layout.append({'Area': 'Stalls Lounge', 'Row': r, 'Combined_Seat': f"{r}{s}", 'X': x, 'Y': stalls_bottom_y + 30})

    # 3. DRESS CIRCLE
    dress = df_master[df_master['Area'] == 'Dress Circle']
    if not dress.empty:
        max_d = dress['Seat Number'].max()
        y = stalls_bottom_y + 100
        for r in sorted(dress['Row'].unique()):
            seats = dress[dress['Row'] == r]['Seat Number'].tolist()
            layout.extend(generate_dynamic_row('Dress Circle', r, seats, y, max_d, curve_factor=0.0003, gap_center=24))
            y += 18
        dress_bottom_y = y
    else: dress_bottom_y = stalls_bottom_y + 300

    # 4. UPPER CIRCLE 
    upper = df_master[df_master['Area'] == 'Upper Circle']
    if not upper.empty:
        max_u = upper['Seat Number'].max()
        y = dress_bottom_y + 100
        for r in sorted(upper['Row'].unique()):
            seats = upper[upper['Row'] == r]['Seat Number'].tolist()
            layout.extend(generate_dynamic_row('Upper Circle', r, seats, y, max_u, curve_factor=0.0003, gap_center=24))
            y += 18
            
    # 5. BOXES (2x2 Grids on the sides)
    boxes_df = df_master[df_master['Area'] == 'Boxes']
    if not boxes_df.empty:
        boxes_pos = {
            'C': (160, 90), 'D': (160, 190), 'G': (100, 90), 'H': (100, 190), # Left Side
            'E': (840, 90), 'F': (840, 190), 'J': (900, 90), 'K': (900, 190)  # Right Side
        }
        for _, row in boxes_df.iterrows():
            r = row['Row']
            s = row['Seat Number']
            if r in boxes_pos:
                bx, by = boxes_pos[r]
                x_mod = 0 if s % 2 != 0 else -16 # Seats 1,3 right; 2,4 left
                y_mod = 0 if s <= 2 else 16      # Seats 1,2 top; 3,4 bottom
                layout.append({'Area': 'Boxes', 'Row': r, 'Combined_Seat': f"{r}{s}", 'X': bx + x_mod, 'Y': by + y_mod})

    return pd.DataFrame(layout), stalls_bottom_y, dress_bottom_y

# --- Main Logic ---
if master_file is not None:
    df_master = load_data(master_file)
    df_sales = load_data(sales_file, pasted_data)
    
    if not df_sales.empty:
        st.success("Master Layout and Sales data loaded successfully!")
        st.markdown("---")
        
        # Determine layout Y-anchors for text labels
        df_layout, stalls_bottom, dress_bottom = build_master_layout(df_master)
        df_layout['Area'] = df_layout['Area'].astype(str).str.title()
        
        # 1. Clean data to ensure perfect matching
        area_col = st.selectbox("Select Area Column (from Sales Data)", df_sales.columns, index=0)
        seat_col = st.selectbox("Select Seat Column (from Sales Data)", df_sales.columns, index=1 if len(df_sales.columns) > 1 else 0)
        count_col = st.selectbox("Select Count Column (from Sales Data)", df_sales.columns, index=2 if len(df_sales.columns) > 2 else 0)
        
        df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.title()
        df_sales[seat_col] = df_sales[seat_col].astype(str).str.strip().str.upper()
        df_sales[count_col] = pd.to_numeric(df_sales[count_col], errors='coerce').fillna(0)
        
        # 2. Aggregate Duplicate Sales Data 
        df_grouped = df_sales.groupby([area_col, seat_col])[count_col].sum().reset_index()
        
        # 3. Safe Merging function 
        def match_area(layout_area, sales_data):
            exact_match = sales_data[sales_data[area_col] == layout_area]
            if not exact_match.empty: return exact_match
            partial_match = sales_data[sales_data[area_col].apply(lambda x: x in layout_area or layout_area in x)]
            return partial_match

        merged_records = []
        for _, layout_row in df_layout.iterrows():
            area = layout_row['Area']
            seat = layout_row['Combined_Seat']
            
            area_match = match_area(area, df_grouped)
            seat_match = area_match[area_match[seat_col] == seat]
            
            count = seat_match[count_col].sum() if not seat_match.empty else 0
            
            merged_records.append({
                'Area': area, 'Combined_Seat': seat, 'X': layout_row['X'], 'Y': layout_row['Y'], 'Count': count
            })
            
        merged_df = pd.DataFrame(merged_records)
        
        # --- VIEW TOGGLE ---
        st.subheader("3. Interactive View")
        view_filter = st.radio(
            "Isolate Area:",
            ["All Areas", "Stalls", "Dress Circle", "Upper Circle", "Boxes", "Stalls Lounge"],
            horizontal=True
        )
        
        if view_filter != "All Areas":
            merged_df = merged_df[merged_df['Area'] == view_filter]

        # Separate into Sold and Unsold
        unsold_df = merged_df[merged_df['Count'] == 0]
        sold_df = merged_df[merged_df['Count'] > 0]
        
        # --- Build Interactive Plotly Chart ---
        fig = go.Figure()

        # Add Unsold Seats (Grey)
        if not unsold_df.empty:
            fig.add_trace(go.Scatter(
                x=unsold_df['X'], y=unsold_df['Y'], mode='markers',
                marker=dict(size=12, color='#e0e0e0', line=dict(width=1, color='white')),
                name="Unsold", text=unsold_df['Area'] + " - " + unsold_df['Combined_Seat'],
                hovertemplate="<b>%{text}</b><br>Times Sold: 0<extra></extra>"
            ))

        # Add Sold Seats (Heatmap Colors)
        if not sold_df.empty:
            fig.add_trace(go.Scatter(
                x=sold_df['X'], y=sold_df['Y'], mode='markers',
                marker=dict(
                    size=12, color=sold_df['Count'], colorscale='YlOrRd',
                    showscale=True, colorbar=dict(title="Times Sold"), line=dict(width=1, color='DarkRed')
                ),
                name="Sold", text=sold_df['Area'] + " - " + sold_df['Combined_Seat'],
                customdata=sold_df['Count'],
                hovertemplate="<b>%{text}</b><br>Times Sold: %{customdata}<extra></extra>"
            ))
            
        # Add Text Labels (Only display if "All Areas" or the specific area is selected)
        if view_filter in ["All Areas", "Stalls"]:
            fig.add_annotation(x=500, y=70, text="<b>STALLS</b>", showarrow=False, font=dict(size=16, color="black"))
            
        if view_filter in ["All Areas", "Dress Circle"]:
            fig.add_annotation(x=500, y=stalls_bottom + 70, text="<b>DRESS CIRCLE</b>", showarrow=False, font=dict(size=16, color="black"))
            
        if view_filter in ["All Areas", "Upper Circle"]:
            fig.add_annotation(x=500, y=dress_bottom + 70, text="<b>UPPER CIRCLE</b>", showarrow=False, font=dict(size=16, color="black"))

        if view_filter in ["All Areas", "Boxes"]:
            box_labels = {'C': (160, 90), 'D': (160, 190), 'G': (100, 90), 'H': (100, 190),
                          'E': (840, 90), 'F': (840, 190), 'J': (900, 90), 'K': (900, 190)}
            for label, (lx, ly) in box_labels.items():
                 fig.add_annotation(x=lx-8, y=ly-10, text=f"Box {label}", showarrow=False, font=dict(size=10, color="gray"))
                 
        if view_filter in ["All Areas", "Stalls Lounge"]:
            fig.add_annotation(x=250, y=stalls_bottom + 60, text="Lounge A", showarrow=False, font=dict(size=12, color="gray"))
            fig.add_annotation(x=620, y=stalls_bottom + 60, text="Lounge B", showarrow=False, font=dict(size=12, color="gray"))

        # Formatting the chart
        fig.update_layout(
            plot_bgcolor='white',
            width=1200,
            height=1000,
            yaxis=dict(autorange='reversed', showgrid=False, zeroline=False, visible=False),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            hovermode="closest",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please upload your Sales Data to populate the chart.")
else:
    st.warning("Please upload the **Full Seat List (Excel)** first to build the theatre layout.")
