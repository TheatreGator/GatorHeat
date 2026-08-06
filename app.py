import streamlit as st
import pandas as pd
import math
import base64
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import io

st.set_page_config(page_title="Alhambra Theatre Heatmap", layout="wide")

# --- UI Header ---
st.title("🎭 Alhambra Theatre Seating Heatmap")
st.markdown("Upload or paste your sales data below. The app will mathematically generate the curved seating layout and overlay it directly onto the Alhambra SVG background.")

# --- Data Input Section ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Sales Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

with col2:
    st.subheader("OR Paste Data")
    pasted_data = st.text_area("Paste tabular data (Area, Row, Seat, Count)", height=150)

# --- Helper Functions ---
@st.cache_data
def load_data(file, pasted):
    df = pd.DataFrame()
    try:
        if file is not None:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        elif pasted:
            # Reads tab or comma separated pasted data
            df = pd.read_csv(io.StringIO(pasted), sep=r'\t|,', engine='python')
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return df

def get_heatmap_color(count, max_count):
    if count == 0:
        return "#e0e0e0" # Default grey for unsold seats
    cmap = cm.get_cmap('YlOrRd')
    norm = mcolors.Normalize(vmin=0, vmax=max_count)
    rgba = cmap(norm(count))
    return mcolors.to_hex(rgba)

# --- Geometry Generator ---
def generate_curved_row(area, row_letter, num_seats, center_x, center_y, radius, start_angle, end_angle):
    """Calculates X/Y coordinates for an arc of seats."""
    seats = []
    angle_step = (end_angle - start_angle) / (num_seats - 1) if num_seats > 1 else 0
    
    for i in range(num_seats):
        seat_num = i + 1
        angle_deg = start_angle + (i * angle_step)
        angle_rad = math.radians(angle_deg)
        
        # Calculate coordinates
        x = center_x + (radius * math.cos(angle_rad))
        y = center_y + (radius * math.sin(angle_rad))
        
        seats.append({
            'Area': area,
            'Row': row_letter,
            'Seat': seat_num,
            'x': x,
            'y': y
        })
    return seats

def build_theatre_layout():
    """
    Hardcodes the physical layout of the theatre using geometric arcs.
    You can adjust the center_x, center_y, and radius values to align 
    perfectly with your specific SVG background file.
    """
    layout = []
    
    # 1. STALLS
    stalls_center_x = 400
    stalls_center_y = 100 
    
    stalls_rows = [
        ('A', 22), ('B', 24), ('C', 26), ('D', 28), ('E', 30), ('F', 32), ('G', 34),
        ('H', 34), ('J', 36), ('K', 36), ('L', 38), ('M', 38), ('N', 40), ('P', 40),
        ('R', 42), ('S', 42), ('T', 44), ('U', 44), ('V', 44), ('W', 40), ('X', 30)
    ]
    
    current_radius = 150
    for row_letter, num_seats in stalls_rows:
        layout.extend(generate_curved_row(
            area='Stalls', row_letter=row_letter, num_seats=num_seats,
            center_x=stalls_center_x, center_y=stalls_center_y, 
            radius=current_radius, start_angle=60, end_angle=120
        ))
        current_radius += 18 

    # 2. DRESS CIRCLE 
    dress_center_y = 350
    dress_rows = [
        ('A', 30), ('B', 32), ('C', 34), ('D', 36), ('E', 38), ('F', 38),
        ('G', 40), ('H', 40), ('J', 42), ('K', 42), ('L', 44)
    ]
    
    current_radius = 200
    for row_letter, num_seats in dress_rows:
        half_seats = num_seats // 2
        # Left Block
        layout.extend(generate_curved_row('Dress Circle', row_letter, half_seats, stalls_center_x, dress_center_y, current_radius, 130, 95))
        # Right Block 
        right_block = generate_curved_row('Dress Circle', row_letter, half_seats, stalls_center_x, dress_center_y, current_radius, 85, 50)
        for i, seat in enumerate(right_block):
            seat['Seat'] = half_seats + i + 1
        layout.extend(right_block)
        current_radius += 18

    return pd.DataFrame(layout)

# --- Main Application ---
df_sales = load_data(uploaded_file, pasted_data)

if not df_sales.empty:
    st.success("Data loaded successfully!")
    st.write("Data Preview:", df_sales.head(3))
    
    st.markdown("---")
    st.subheader("2. Map Your Columns")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        area_col = st.selectbox("Area Column (e.g., Stalls)", df_sales.columns, index=0)
    with c2:
        row_col = st.selectbox("Row Column (e.g., A)", df_sales.columns, index=1 if len(df_sales.columns) > 1 else 0)
    with c3:
        seat_col = st.selectbox("Seat Column (e.g., 6)", df_sales.columns, index=2 if len(df_sales.columns) > 2 else 0)
    with c4:
        count_col = st.selectbox("Sales Count Column", df_sales.columns, index=3 if len(df_sales.columns) > 3 else 0)

    if st.button("Generate Overlay Heatmap"):
        # 1. Clean sales data to ensure matching
        df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.title()
        df_sales[row_col] = df_sales[row_col].astype(str).str.strip().str.upper()
        df_sales[seat_col] = pd.to_numeric(df_sales[seat_col], errors='coerce').fillna(0).astype(int)
        
        # 2. Get the physical coordinate layout
        df_layout = build_theatre_layout()
        
        # 3. Merge layout with sales data
        merged_df = pd.merge(
            df_layout, df_sales,
            how='left',
            left_on=['Area', 'Row', 'Seat'],
            right_on=[area_col, row_col, seat_col]
        )
        merged_df[count_col] = merged_df[count_col].fillna(0)
        max_sales = merged_df[count_col].max() if not merged_df.empty else 0
        
        # 4. Inject Seats into the SVG
        svg_file_path = "Alhambra Lounge Extras.svg"
        try:
            with open(svg_file_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Create the SVG circle tags
            circles_svg = ""
            for _, seat in merged_df.iterrows():
                color = get_heatmap_color(seat[count_col], max_sales)
                circles_svg += f'<circle cx="{seat["x"]}" cy="{seat["y"]}" r="5" fill="{color}" stroke="#999" stroke-width="0.5" />\n'
            
            # Insert the circles right before the closing </svg> tag
            modified_svg = svg_content.replace('</svg>', f'<g id="heatmap_seats">\n{circles_svg}</g>\n</svg>')
            
            # Display it
            b64_svg = base64.b64encode(modified_svg.encode('utf-8')).decode('utf-8')
            html_code = f'<div style="text-align: center;"><img src="data:image/svg+xml;base64,{b64_svg}" style="max-width: 100%; height: auto;"></div>'
            
            st.components.v1.html(html_code, height=900, scrolling=True)
            
            st.download_button("Download Merged SVG", data=modified_svg, file_name="Alhambra_Overlay.svg", mime="image/svg+xml")
            
        except FileNotFoundError:
            st.error(f"Could not find `{svg_file_path}`. Make sure it is in the same folder.")
else:
    st.info("Awaiting data input to generate the heatmap.")
