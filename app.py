import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Alhambra Interactive Heatmap", layout="wide")

st.title("🎭 Alhambra Theatre Interactive Heatmap")
st.markdown("Upload your **Sales Data (CSV/Excel)**. The app will automatically generate the beautiful curved layout of the Alhambra and map your sales directly to the seats.")

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

def generate_curved_row(area, row_letter, num_seats, center_x, center_y, radius, start_angle, end_angle):
    """Calculates X/Y coordinates for an arc of seats."""
    seats = []
    angle_step = (end_angle - start_angle) / (num_seats - 1) if num_seats > 1 else 0
    
    for i in range(num_seats):
        seat_num = i + 1
        angle_deg = start_angle + (i * angle_step)
        angle_rad = math.radians(angle_deg)
        
        x = center_x + (radius * math.cos(angle_rad))
        y = center_y + (radius * math.sin(angle_rad))
        
        seats.append({
            'Area': area,
            'Row': row_letter,
            'Combined_Seat': f"{row_letter}{seat_num}",
            'X': x,
            'Y': y
        })
    return seats

@st.cache_data
def build_mathematical_layout():
    """Generates the physical curves of the Stalls, Dress, and Upper Circle."""
    layout = []
    center_x = 400
    center_y = 100 
    
    # 1. STALLS
    stalls_rows = [
        ('A', 22), ('B', 24), ('C', 26), ('D', 28), ('E', 30), ('F', 32), ('G', 34),
        ('H', 34), ('J', 36), ('K', 36), ('L', 38), ('M', 38), ('N', 40), ('P', 40),
        ('R', 42), ('S', 42), ('T', 44), ('U', 44), ('V', 44), ('W', 40), ('X', 30)
    ]
    r = 150
    for r_letter, n in stalls_rows:
        layout.extend(generate_curved_row('Stalls', r_letter, n, center_x, center_y, r, 120, 60))
        r += 16 

    # 2. DRESS CIRCLE 
    dress_rows = [
        ('A', 30), ('B', 32), ('C', 34), ('D', 36), ('E', 38), ('F', 38),
        ('G', 40), ('H', 40), ('J', 42), ('K', 42), ('L', 44)
    ]
    r = 520
    for r_letter, n in dress_rows:
        half = n // 2
        layout.extend(generate_curved_row('Dress Circle', r_letter, half, center_x, center_y, r, 125, 95))
        right_block = generate_curved_row('Dress Circle', r_letter, half, center_x, center_y, r, 85, 55)
        for i, seat in enumerate(right_block):
            seat['Combined_Seat'] = f"{r_letter}{half + i + 1}"
        layout.extend(right_block)
        r += 16

    # 3. UPPER CIRCLE
    upper_rows = [
        ('A', 32), ('B', 34), ('C', 36), ('D', 38), ('E', 40), ('F', 40),
        ('G', 42), ('H', 42), ('J', 44), ('K', 44), ('L', 46)
    ]
    r = 720
    for r_letter, n in upper_rows:
        half = n // 2
        layout.extend(generate_curved_row('Upper Circle', r_letter, half, center_x, center_y, r, 125, 95))
        right_block = generate_curved_row('Upper Circle', r_letter, half, center_x, center_y, r, 85, 55)
        for i, seat in enumerate(right_block):
            seat['Combined_Seat'] = f"{r_letter}{half + i + 1}"
        layout.extend(right_block)
        r += 16
        
    # 4. STALLS LOUNGE 
    lounge_y = 485
    for i in range(25):
        layout.append({'Area': 'Stalls Lounge', 'Row': 'Lounge', 'Combined_Seat': f"Lounge{i+1}", 'X': 200 + (i*16.5), 'Y': lounge_y})

    # 5. BOXES (Positioned on the left and right sides)
    boxes = {
        'C': (90, 150), 'D': (90, 250), 'G': (40, 150), 'H': (40, 250),    # Left side Boxes
        'E': (690, 150), 'F': (690, 250), 'J': (740, 150), 'K': (740, 250) # Right side Boxes
    }
    
    for box_letter, (base_x, base_y) in boxes.items():
        for i in range(4): # 4 seats per box in a 2x2 grid
            layout.append({
                'Area': 'Boxes',
                'Row': box_letter,
                'Combined_Seat': f"{box_letter}{i+1}",
                'X': base_x + (i % 2) * 16,  # 16px horizontal spacing
                'Y': base_y + (i // 2) * 16  # 16px vertical spacing
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
            
        # Add Text Labels for the Boxes
        box_labels = {'C': (90, 140), 'D': (90, 240), 'G': (40, 140), 'H': (40, 240),
                      'E': (690, 140), 'F': (690, 240), 'J': (740, 140), 'K': (740, 240)}
        for label, (lx, ly) in box_labels.items():
             fig.add_annotation(x=lx+8, y=ly-10, text=f"Box {label}", showarrow=False, font=dict(size=10, color="gray"))

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
