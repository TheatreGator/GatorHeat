import streamlit as st
import pandas as pd
import io
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from bs4 import BeautifulSoup
import base64

st.set_page_config(page_title="Alhambra Theatre Seat Heatmap", layout="wide")

# --- UI Header ---
st.title("🎭 Alhambra Theatre Seating Heatmap")
st.markdown("Upload your sales data to generate a heatmap of sold seats on the Alhambra seating diagram.")

# --- Data Input Section ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Sales Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

with col2:
    st.subheader("OR Paste Data")
    pasted_data = st.text_area("Paste tabular data here", height=150)

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
            df = pd.read_csv(io.StringIO(pasted), sep=r'\t|,', engine='python')
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return df

def generate_color(heat_value, max_value):
    if max_value == 0:
        return "#e0e0e0" 
    
    cmap = cm.get_cmap('YlOrRd')
    norm = mcolors.Normalize(vmin=0, vmax=max_value)
    rgba = cmap(norm(heat_value))
    return mcolors.to_hex(rgba)

# --- Main Logic ---
df_sales = load_data(uploaded_file, pasted_data)

if not df_sales.empty:
    st.success("Sales data loaded successfully!")
    st.write("Data Preview:", df_sales.head())
    
    st.markdown("---")
    st.subheader("2. Map Your Columns")
    
    # Map the specific 3 columns you mentioned
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        area_col = st.selectbox("Area Column", df_sales.columns, index=0)
    with col_b:
        seat_col = st.selectbox("Seat Number Column (e.g., A6)", df_sales.columns, index=1 if len(df_sales.columns) > 1 else 0)
    with col_c:
        count_col = st.selectbox("Count/Sold Column", df_sales.columns, index=2 if len(df_sales.columns) > 2 else 0)

    # Allow tweaking how the ID is formed to match the SVG
    st.markdown("### 3. Match SVG Formatting")
    id_format = st.radio(
        "How should we combine your data to match the SVG's seat IDs?",
        ["Use Seat Number only (e.g., 'A6')", 
         "Combine Area and Seat Number with a hyphen (e.g., 'Stalls-A6')",
         "Combine Area and Seat Number with an underscore (e.g., 'Stalls_A6')"]
    )

    if st.button("Generate Heatmap"):
        # Format the IDs based on user selection
        if "hyphen" in id_format:
            df_sales['Generated_ID'] = df_sales[area_col].astype(str) + "-" + df_sales[seat_col].astype(str)
        elif "underscore" in id_format:
            df_sales['Generated_ID'] = df_sales[area_col].astype(str) + "_" + df_sales[seat_col].astype(str)
        else:
            df_sales['Generated_ID'] = df_sales[seat_col].astype(str)

        # Create dictionary of {Seat_ID: Count}
        seat_counts = dict(zip(df_sales['Generated_ID'], df_sales[count_col]))
        
        # Ensure counts are treated as numbers
        seat_counts = {str(k).strip(): float(v) for k, v in seat_counts.items()}
        max_sales = max(seat_counts.values()) if seat_counts else 0
        
        svg_file_path = "Alhambra Lounge Extras.svg"
        
        try:
            with open(svg_file_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
                
            soup = BeautifulSoup(svg_content, 'xml')
            circles = soup.find_all('circle')
            
            matched_seats = 0
            unmatched_svg_ids = []

            for circle in circles:
                circle_id = circle.get('id', '')
                
                if circle_id in seat_counts:
                    sales_count = seat_counts[circle_id]
                    heat_color = generate_color(sales_count, max_sales)
                    circle['fill'] = heat_color
                    matched_seats += 1
                else:
                    circle['fill'] = "#e0e0e0"
                    if circle_id:
                        unmatched_svg_ids.append(circle_id)
            
            if matched_seats > 0:
                st.success(f"Successfully matched {matched_seats} seats!")
            else:
                st.error("0 seats matched. Check the debug tool below to see what IDs your SVG is using.")

            # --- Render SVG ---
            modified_svg = str(soup)
            b64_svg = base64.b64encode(modified_svg.encode('utf-8')).decode('utf-8')
            html_code = f'<img src="data:image/svg+xml;base64,{b64_svg}" width="100%">'
            
            st.components.v1.html(html_code, height=800, scrolling=True)
            
            st.download_button(
                label="Download Heatmap SVG",
                data=modified_svg,
                file_name="Alhambra_Heatmap.svg",
                mime="image/svg+xml"
            )

            # --- DEBUGGING TOOL ---
            with st.expander("🛠️ Debug: See available SVG IDs"):
                st.write("If you matched 0 seats, it's because your data (e.g., 'A6') doesn't exactly match the IDs embedded in the SVG file. Here is a list of the first 50 actual IDs found inside your SVG's `<circle>` tags:")
                st.write(unmatched_svg_ids[:50] if unmatched_svg_ids else "No IDs found on the circles in your SVG!")
                
        except FileNotFoundError:
            st.error(f"Could not find `{svg_file_path}`.")
else:
    st.info("Awaiting data input to generate the heatmap.")
  
