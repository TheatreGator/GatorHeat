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
st.markdown("Upload your sales data or paste it below to generate a heatmap of sold seats on the Alhambra seating diagram.")

# --- Data Input Section ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Sales Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])

with col2:
    st.subheader("OR Paste Data")
    pasted_data = st.text_area("Paste tabular data (Section, Row, Seat Number)", height=150)

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
            # Read tab/comma separated pasted data
            df = pd.read_csv(io.StringIO(pasted), sep=r'\t|,', engine='python')
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return df

def generate_color(heat_value, max_value):
    """Generates a hex color from a colormap based on the heat value."""
    if max_value == 0:
        return "#d3d3d3" # Default grey for unsold
    
    # Using a Yellow-Orange-Red colormap for the heat
    cmap = cm.get_cmap('YlOrRd')
    norm = mcolors.Normalize(vmin=0, vmax=max_value)
    rgba = cmap(norm(heat_value))
    return mcolors.to_hex(rgba)

# --- Main Logic ---
df_sales = load_data(uploaded_file, pasted_data)

if not df_sales.empty:
    st.success("Sales data loaded successfully!")
    st.write("Data Preview:", df_sales.head())
    
    # ---------------------------------------------------------
    # IMPORTANT: Map your dataset columns here.
    # The app assumes you have columns that identify a seat.
    # Adjust these variables to match your actual column names.
    # ---------------------------------------------------------
    seat_id_col = st.selectbox("Select the column that represents the Seat ID (e.g., 'A1', 'Stalls-A-1')", df_sales.columns)
    
    if st.button("Generate Heatmap"):
        # Aggregate data to count how many times each seat was sold
        seat_counts = df_sales[seat_id_col].value_counts().to_dict()
        max_sales = max(seat_counts.values()) if seat_counts else 0
        
        st.write(f"**Maximum sales for a single seat:** {max_sales}")

        # --- SVG Manipulation ---
        svg_file_path = "Alhambra Lounge Extras.svg"
        
        try:
            with open(svg_file_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
                
            soup = BeautifulSoup(svg_content, 'xml')
            
            # Find all circles (representing seats) in the SVG
            circles = soup.find_all('circle')
            
            matched_seats = 0
            for circle in circles:
                # Assuming the circle's ID corresponds to the seat ID in your data
                # e.g., <circle id="A1" ... />
                circle_id = circle.get('id') 
                
                if circle_id in seat_counts:
                    sales_count = seat_counts[circle_id]
                    heat_color = generate_color(sales_count, max_sales)
                    circle['fill'] = heat_color
                    matched_seats += 1
                else:
                    # Ignore price colors and default to a standard unfilled/grey seat
                    circle['fill'] = "#e0e0e0" 
            
            st.info(f"Matched {matched_seats} seats from your data to the SVG diagram.")
            
            # --- Render the modified SVG ---
            modified_svg = str(soup)
            
            # Encode SVG to display in Streamlit
            b64_svg = base64.b64encode(modified_svg.encode('utf-8')).decode('utf-8')
            html_code = f'<img src="data:image/svg+xml;base64,{b64_svg}" width="100%">'
            
            st.markdown("### Heatmap Result")
            st.components.v1.html(html_code, height=800, scrolling=True)
            
            # Provide a download button for the modified SVG
            st.download_button(
                label="Download Heatmap SVG",
                data=modified_svg,
                file_name="Alhambra_Heatmap.svg",
                mime="image/svg+xml"
            )
            
        except FileNotFoundError:
            st.error(f"Could not find `{svg_file_path}`. Please ensure it is in the same folder as this script.")
        except Exception as e:
            st.error(f"An error occurred while processing the SVG: {e}")
else:
    st.info("Awaiting data input to generate the heatmap.")
