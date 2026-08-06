import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Alhambra Interactive Heatmap", layout="wide")

# --- HARDCODED MASTER LAYOUT ---
# This dictionary was extracted directly from your 'Full Seat List.xlsx'
HARDCODED_LAYOUT = {
    'Boxes': {'D': [1, 2, 3, 4], 'F': [1, 2, 3, 4], 'H': [1, 2, 3, 4], 'K': [1, 2, 3, 4]}, 
    'Dress Circle': {'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'B': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'C': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'D': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'E': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'F': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'G': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'H': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'J': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'K': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'L': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]}, 
    'Stalls': {'C': [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], 'D': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], 'E': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'F': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'G': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'H': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'J': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'K': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'L': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'M': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'N': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'P': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'R': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'S': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'T': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'U': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'V': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'W': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'X': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]}, 
    'Stalls Lounge': {'A': [1, 2, 3, 4, 5, 6, 7, 8], 'B': [1, 2, 3, 4, 5, 6, 7]}, 
    'Upper Circle': {'A': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'B': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'C': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'D': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'E': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37], 'F': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'G': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'H': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'J': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'K': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'L': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]}
}

st.title("🎭 Alhambra Theatre Interactive Heatmap")
st.markdown("Upload your **Sales Data**. The theatre layout is built-in automatically.")

# --- Data Input Section ---
col1, col2 = st.columns(2)
with col1:
    sales_file = st.file_uploader("Upload Sales Data (CSV/Excel)", type=["csv", "xlsx", "xls"])
with col2:
    pasted_data = st.text_area("OR Paste Sales Data", height=100)

@st.cache_data
def load_sales(file, pasted=None):
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

def generate_dynamic_row(area, row_letter, valid_seats, base_y, max_seats_in_area, spacing=18, curve_factor=0.0003, gap_center=0):
    row_layout = []
    for seat_num in valid_seats:
        x = 500 + (max_seats_in_area * spacing / 2) - (seat_num * spacing)
        if gap_center > 0:
            if seat_num > max_seats_in_area / 2: x -= gap_center / 2
            else: x += gap_center / 2
        dist_from_center = abs(x - 500)
        y = base_y + (curve_factor * (dist_from_center ** 2))
        row_layout.append({'Area': area, 'Row': row_letter, 'Seat_Num': seat_num, 'Combined_Seat': f"{row_letter}{seat_num}", 'X': x, 'Y': y})
    return row_layout

@st.cache_data
def build_master_layout():
    """Builds the layout using the hardcoded dictionary and improved spacing."""
    layout = []
    
    # 1. STALLS
    stalls_dict = HARDCODED_LAYOUT.get('Stalls', {})
    max_s = max([max(seats) for seats in stalls_dict.values()]) if stalls_dict else 0
    y = 100
    for r in sorted(stalls_dict.keys()):
        layout.extend(generate_dynamic_row('Stalls', r, stalls_dict[r], y, max_s, spacing=18, curve_factor=0.0004))
        y += 28 
    stalls_bottom_y = y

    # 2. STALLS LOUNGE 
    lounge_dict = HARDCODED_LAYOUT.get('Stalls Lounge', {})
    for r, seats in lounge_dict.items():
        for s in seats:
            x = 300 - (s*20) if r == 'A' else 700 - (s*20)
            layout.append({'Area': 'Stalls Lounge', 'Row': r, 'Combined_Seat': f"{r}{s}", 'X': x, 'Y': stalls_bottom_y + 40})

    # 3. DRESS CIRCLE
    dress_dict = HARDCODED_LAYOUT.get('Dress Circle', {})
    max_d = max([max(seats) for seats in dress_dict.values()]) if dress_dict else 0
    y = stalls_bottom_y + 120
    for r in sorted(dress_dict.keys()):
        layout.extend(generate_dynamic_row('Dress Circle', r, dress_dict[r], y, max_d, spacing=18, curve_factor=0.0003, gap_center=35))
        y += 28
    dress_bottom_y = y

    # 4. UPPER CIRCLE 
    upper_dict = HARDCODED_LAYOUT.get('Upper Circle', {})
    max_u = max([max(seats) for seats in upper_dict.values()]) if upper_dict else 0
    y = dress_bottom_y + 120
    for r in sorted(upper_dict.keys()):
        layout.extend(generate_dynamic_row('Upper Circle', r, upper_dict[r], y, max_u, spacing=18, curve_factor=0.0003, gap_center=35))
        y += 28
            
    # 5. BOXES 
    boxes_dict = HARDCODED_LAYOUT.get('Boxes', {})
    boxes_pos = {'C': (140, 90), 'D': (140, 200), 'G': (80, 90), 'H': (80, 200), 'E': (860, 90), 'F': (860, 200), 'J': (920, 90), 'K': (920, 200)}
    for r, seats in boxes_dict.items():
        if r in boxes_pos:
            bx, by = boxes_pos[r]
            for s in seats:
                x_mod = 0 if s % 2 != 0 else -20
                y_mod = 0 if s <= 2 else 20
                layout.append({'Area': 'Boxes', 'Row': r, 'Combined_Seat': f"{r}{s}", 'X': bx + x_mod, 'Y': by + y_mod})

    return pd.DataFrame(layout), stalls_bottom_y, dress_bottom_y

def generate_smart_insights(merged_df, total_capacity):
    """Algorithmic 'AI' Data Analyst"""
    st.markdown("### 🤖 Smart Insights")
    
    sold_df = merged_df[merged_df['Count'] > 0]
    total_sales = sold_df['Count'].sum()
    sell_through = (len(sold_df) / total_capacity) * 100 if total_capacity > 0 else 0
    
    if sold_df.empty:
        st.info("Upload sales data to generate insights.")
        return
        
    busiest_area = sold_df.groupby('Area')['Count'].sum().idxmax()
    busiest_area_sales = sold_df.groupby('Area')['Count'].sum().max()
    top_seat = sold_df.loc[sold_df['Count'].idxmax()]
    
    summary_text = (
        f"**Sales Overview:** You have processed a total of **{int(total_sales)} ticket sales** across **{len(sold_df)} unique seats**. "
        f"This accounts for a **{sell_through:.1f}% sell-through rate** of the available venue capacity.\n\n"
        f"**Trending Patterns:** The most popular section by volume is the **{busiest_area}**, which accounts for {int(busiest_area_sales)} of your total sales. "
        f"The single most popular seat is **{top_seat['Area']} - {top_seat['Combined_Seat']}**, which has been sold {int(top_seat['Count'])} times. "
    )
    
    st.info(summary_text)

# --- Main Logic ---
df_sales = load_sales(sales_file, pasted_data)
df_layout, stalls_bottom, dress_bottom = build_master_layout()
df_layout['Area'] = df_layout['Area'].astype(str).str.title()
TOTAL_VENUE_CAPACITY = len(df_layout)

if not df_sales.empty:
    st.success("Sales data loaded successfully!")
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    with c1: area_col = st.selectbox("Area Column", df_sales.columns, index=0)
    with c2: seat_col = st.selectbox("Seat Column", df_sales.columns, index=1 if len(df_sales.columns) > 1 else 0)
    with c3: count_col = st.selectbox("Count Column", df_sales.columns, index=2 if len(df_sales.columns) > 2 else 0)
    
    # Clean data
    df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.title()
    df_sales[seat_col] = df_sales[seat_col].astype(str).str.strip().str.upper()
    df_sales[count_col] = pd.to_numeric(df_sales[count_col], errors='coerce').fillna(0)
    df_grouped = df_sales.groupby([area_col, seat_col])[count_col].sum().reset_index()
    
    def match_area(layout_area, sales_data):
        exact = sales_data[sales_data[area_col] == layout_area]
        if not exact.empty: return exact
        return sales_data[sales_data[area_col].apply(lambda x: x in layout_area or layout_area in x)]

    merged_records = []
    for _, layout_row in df_layout.iterrows():
        area = layout_row['Area']
        seat = layout_row['Combined_Seat']
        area_match = match_area(area, df_grouped)
        seat_match = area_match[area_match[seat_col] == seat]
        count = seat_match[count_col].sum() if not seat_match.empty else 0
        merged_records.append({'Area': area, 'Combined_Seat': seat, 'X': layout_row['X'], 'Y': layout_row['Y'], 'Count': count})
        
    merged_df = pd.DataFrame(merged_records)
    
    # Display AI Insights
    generate_smart_insights(merged_df, TOTAL_VENUE_CAPACITY)
    st.markdown("---")
    
    # --- VIEW TOGGLE ---
    st.subheader("Interactive Heatmap")
    view_filter = st.radio("Isolate Area:", ["All Areas", "Stalls", "Dress Circle", "Upper Circle", "Boxes", "Stalls Lounge"], horizontal=True)
    
    # DYNAMIC DOT SIZING
    marker_size = 14 if view_filter == "All Areas" else 24
    
    if view_filter != "All Areas":
        merged_df = merged_df[merged_df['Area'] == view_filter]

    unsold_df = merged_df[merged_df['Count'] == 0]
    sold_df = merged_df[merged_df['Count'] > 0]
    
    fig = go.Figure()
    if not unsold_df.empty:
        fig.add_trace(go.Scatter(
            x=unsold_df['X'], y=unsold_df['Y'], mode='markers',
            marker=dict(size=marker_size, color='#e0e0e0', line=dict(width=1, color='white')),
            name="Unsold", text=unsold_df['Area'] + " - " + unsold_df['Combined_Seat'],
            hovertemplate="<b>%{text}</b><br>Times Sold: 0<extra></extra>"
        ))

    if not sold_df.empty:
        fig.add_trace(go.Scatter(
            x=sold_df['X'], y=sold_df['Y'], mode='markers',
            marker=dict(size=marker_size, color=sold_df['Count'], colorscale='YlOrRd', showscale=True, colorbar=dict(title="Times Sold"), line=dict(width=1, color='DarkRed')),
            name="Sold", text=sold_df['Area'] + " - " + sold_df['Combined_Seat'],
            customdata=sold_df['Count'], hovertemplate="<b>%{text}</b><br>Times Sold: %{customdata}<extra></extra>"
        ))
        
    if view_filter in ["All Areas", "Stalls"]:
        fig.add_annotation(x=500, y=70, text="<b>STALLS</b>", showarrow=False, font=dict(size=18, color="black"))
    if view_filter in ["All Areas", "Dress Circle"]:
        fig.add_annotation(x=500, y=stalls_bottom + 80, text="<b>DRESS CIRCLE</b>", showarrow=False, font=dict(size=18, color="black"))
    if view_filter in ["All Areas", "Upper Circle"]:
        fig.add_annotation(x=500, y=dress_bottom + 80, text="<b>UPPER CIRCLE</b>", showarrow=False, font=dict(size=18, color="black"))
    if view_filter in ["All Areas", "Boxes"]:
        box_labels = {'C': (140, 70), 'D': (140, 180), 'G': (80, 70), 'H': (80, 180), 'E': (860, 70), 'F': (860, 180), 'J': (920, 70), 'K': (920, 180)}
        for label, (lx, ly) in box_labels.items():
             fig.add_annotation(x=lx-10, y=ly-15, text=f"Box {label}", showarrow=False, font=dict(size=12, color="gray"))
    if view_filter in ["All Areas", "Stalls Lounge"]:
        fig.add_annotation(x=220, y=stalls_bottom + 60, text="Lounge A", showarrow=False, font=dict(size=14, color="gray"))
        fig.add_annotation(x=620, y=stalls_bottom + 60, text="Lounge B", showarrow=False, font=dict(size=14, color="gray"))

    fig.update_layout(plot_bgcolor='white', width=1200, height=1100, yaxis=dict(autorange='reversed', showgrid=False, zeroline=False, visible=False), xaxis=dict(showgrid=False, zeroline=False, visible=False), hovermode="closest", showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Waiting for Sales Data upload to generate the heatmap and insights...")
