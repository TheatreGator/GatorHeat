import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Alhambra Interactive Heatmap", layout="wide")

st.title("🎭 Alhambra Theatre Interactive Heatmap")
st.markdown("Upload your **Sales Data**. The app will automatically generate the true structural layout of the Alhambra and map your sales directly to the seats.")

# --- Data Input Section ---
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("1. Upload Sales Data (CSV/Excel)", type=["csv", "xlsx", "xls"])

with col2:
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

def generate_row(area, row_letter, seat_list, base_y, center_x=500, spacing=14, curve_factor=0.0003, gap_center=0):
    """Generates X/Y coordinates for a specific row, placing low numbers on the right."""
    layout = []
    total_seats_est = max(seat_list) if seat_list else 0
    
    for seat_num in seat_list:
        # X position: Base it so seat 1 is far right (High X), max seat is far left (Low X)
        x = center_x + (total_seats_est * spacing / 2) - (seat_num * spacing)
        
        # Apply center aisle gap if necessary
        if gap_center > 0:
            if seat_num > total_seats_est / 2:
                x -= gap_center / 2 # Push left block further left
            else:
                x += gap_center / 2 # Push right block further right
                
        # Y position: Base height + a gentle curve mapping the distance from center
        dist_from_center = abs(x - center_x)
        y = base_y + (curve_factor * (dist_from_center ** 2))
        
        layout.append({
            'Area': area, 'Row': row_letter, 'Seat_Num': seat_num, 
            'Combined_Seat': f"{row_letter}{seat_num}", 'X': x, 'Y': y
        })
    return layout

@st.cache_data
def build_mathematical_layout():
    """Generates the true physical structure of the Alhambra."""
    layout = []
    
    # 1. STALLS
    stalls_seats = {
        'A': range(1, 25), 'B': range(1, 27), 'C': range(1, 33), 'D': range(1, 33),
        'E': range(1, 35), 'F': range(1, 35), 'G': range(1, 35), 'H': range(1, 35),
        'J': range(1, 37), 'K': range(1, 37), 'L': range(1, 37), 'M': range(1, 37),
        'N': range(1, 37), 'P': range(1, 37), 'R': range(1, 37), 'S': range(1, 37),
        'T': range(1, 37), 'U': range(1, 37), 'V': range(1, 37), 'W': range(1, 37),
        'X': range(1, 35)
    }
    y = 100
    for r, seats in stalls_seats.items():
        layout.extend(generate_row('Stalls', r, seats, y, curve_factor=0.0004))
        y += 18 
    
    stalls_bottom_y = y

    # 2. STALLS LOUNGE (Behind Stalls, split into Left and Right)
    # Lounge A (Left side - Row A in data)
    for i in range(1, 9):
        layout.append({'Area': 'Stalls Lounge', 'Row': 'A', 'Combined_Seat': f"A{i}", 'X': 320 - (i*16), 'Y': stalls_bottom_y + 30})
    # Lounge B (Right side - Row B in data)
    for i in range(1, 8):
        layout.append({'Area': 'Stalls Lounge', 'Row': 'B', 'Combined_Seat': f"B{i}", 'X': 680 - (i*16), 'Y': stalls_bottom_y + 30})

    # 3. DRESS CIRCLE (Split down the middle)
    y += 100
    dress_seats = {l: range(1, 37) for l in ['B','C','D','E','F','G','H','J','K','L']}
    dress_seats['A'] = range(1, 39)
    for r, seats in dress_seats.items():
        layout.extend(generate_row('Dress Circle', r, seats, y, curve_factor=0.0003, gap_center=24))
        y += 18

    # 4. UPPER CIRCLE (With Control Booth Gap)
    y += 100
    upper_seats = {'A': range(1, 37), 'B': range(1, 39), 'C': range(1, 39), 'D': range(1, 39), 'E': range(1, 39)}
    for l in ['F','G','H','J','K','L']:
        upper_seats[l] = list(range(1, 17)) + list(range(23, 39)) # Excludes seats 17-22 to form the gap
        
    for r, seats in upper_seats.items():
        layout.extend(generate_row('Upper Circle', r, seats, y, curve_factor=0.0003, gap_center=24))
        y += 18
        
    # 5. BOXES (2x2 Grids on the sides)
    boxes_pos = {
        'G': (100, 100), 'C': (160, 100), 'H': (100, 160), 'D': (160, 160), # Left Side
        'E': (840, 100), 'J': (900, 100), 'F': (840, 160), 'K': (900, 160)  # Right Side
    }
    for box, (bx, by) in boxes_pos.items():
        for i in range(1, 5):
            x_mod = 0 if i % 2 != 0 else -16 # Seats 1,3 right; 2,4 left
            y_mod = 0 if i <= 2 else 16      # Seats 1,2 top; 3,4 bottom
            layout.append({
                'Area': 'Boxes', 'Row': box, 'Combined_Seat': f"{box}{i}",
                'X': bx + x_mod, 'Y': by + y_mod
            })

    return pd.DataFrame(layout)

# --- Main Logic ---
df_sales = load_sales(uploaded_file, pasted_data)

if not df_sales.empty:
    st.success("Sales data loaded successfully!")
    
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
        # 1. Clean data to ensure perfect matching
        df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.title()
        df_sales[seat_col] = df_sales[seat_col].astype(str).str.strip().str.upper()
        df_sales[count_col] = pd.to_numeric(df_sales[count_col], errors='coerce').fillna(0)
        
        # 2. Aggregate Duplicate Sales Data 
        df_grouped = df_sales.groupby([area_col, seat_col])[count_col].sum().reset_index()
        
        # 3. Build the Geometric Layout
        df_layout = build_mathematical_layout()
        df_layout['Area'] = df_layout['Area'].astype(str).str.title()
        
        # 4. Safe Merging function 
        def match_area(layout_area, sales_data):
            exact_match = sales_data[sales_data[area_col] == layout_area]
            if not exact_match.empty:
                return exact_match
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
                'Area': area,
                'Combined_Seat': seat,
                'X': layout_row['X'],
                'Y': layout_row['Y'],
                'Row': layout_row['Row'],
                'Count': count
            })
            
        merged_df = pd.DataFrame(merged_records)
        
        # Separate into Sold and Unsold
        unsold_df = merged_df[merged_df['Count'] == 0]
        sold_df = merged_df[merged_df['Count'] > 0]
        
        # --- Build Interactive Plotly Chart ---
        fig = go.Figure()

        # Add Unsold Seats (Grey)
        if not unsold_df.empty:
            fig.add_trace(go.Scatter(
                x=unsold_df['X'], y=unsold_df['Y'],
                mode='markers',
                marker=dict(size=12, color='#e0e0e0', line=dict(width=1, color='white')),
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
                    line=dict(width=1, color='DarkRed')
                ),
                name="Sold",
                text=sold_df['Area'] + " - " + sold_df['Combined_Seat'],
                customdata=sold_df['Count'],
                hovertemplate="<b>%{text}</b><br>Times Sold: %{customdata}<extra></extra>"
            ))
            
        # Add Text Labels for the Boxes to make them readable
        box_labels = {'C': (160, 90), 'D': (160, 190), 'G': (100, 90), 'H': (100, 190),
                      'E': (840, 90), 'F': (840, 190), 'J': (900, 90), 'K': (900, 190)}
        for label, (lx, ly) in box_labels.items():
             fig.add_annotation(x=lx-8, y=ly-10, text=f"Box {label}", showarrow=False, font=dict(size=10, color="gray"))
             
        # Add Text Labels for Lounges
        fig.add_annotation(x=250, y=360, text="Lounge A", showarrow=False, font=dict(size=12, color="gray"))
        fig.add_annotation(x=620, y=360, text="Lounge B", showarrow=False, font=dict(size=12, color="gray"))

        # Formatting the chart
        fig.update_layout(
            title="Interactive Alhambra Seating Heatmap",
            plot_bgcolor='white',
            width=1200,
            height=1000,
            yaxis=dict(
                autorange='reversed', 
                showgrid=False, zeroline=False, visible=False
            ),
            xaxis=dict(
                showgrid=False, zeroline=False, visible=False
            ),
            hovermode="closest",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please upload your Sales Data to generate the chart.")
