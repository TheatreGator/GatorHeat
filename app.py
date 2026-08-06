import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
import datetime
import time

st.set_page_config(page_title="Alhambra Interactive Heatmap", layout="wide")

# --- HARDCODED MASTER LAYOUT ---
HARDCODED_LAYOUT = {
    'Boxes': {'D': [1, 2, 3, 4], 'F': [1, 2, 3, 4], 'H': [1, 2, 3, 4], 'K': [1, 2, 3, 4]}, 
    'Dress Circle': {'A': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'B': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'C': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'D': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'E': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'F': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'G': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'H': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'J': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'K': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'L': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]}, 
    'Stalls': {'C': [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], 'D': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], 'E': [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'F': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'G': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'H': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], 'J': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'K': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'L': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'M': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'N': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'P': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'R': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'S': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'T': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'U': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'V': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'W': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], 'X': [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]}, 
    'Stalls Lounge': {'A': [1, 2, 3, 4, 5, 6, 7, 8], 'B': [1, 2, 3, 4, 5, 6, 7]}, 
    'Upper Circle': {'A': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36], 'B': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'C': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'D': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'E': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37], 'F': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'G': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'H': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'J': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'K': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 'L': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]}
}

st.title("🎭 Alhambra Theatre Heatmap & Insights")
st.markdown("Upload your **Sales Data** (CSV or Excel). The theatre layout is built-in automatically.")

# --- Helper Functions ---
def get_col_index(target_name, col_list, has_none=False):
    """Helper to auto-map dropdowns based on column names."""
    try:
        lower_cols = [str(c).lower().strip() for c in col_list]
        idx = lower_cols.index(target_name.lower().strip())
        return idx + 1 if has_none else idx
    except ValueError:
        return 0

@st.cache_data
def load_data(file, pasted=None):
    df = pd.DataFrame()
    try:
        if file is not None:
            if file.name.endswith('.csv'): df = pd.read_csv(file)
            else: df = pd.read_excel(file)
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
    layout = []
    stalls_dict = HARDCODED_LAYOUT.get('Stalls', {})
    max_s = max([max(seats) for seats in stalls_dict.values()]) if stalls_dict else 0
    y = 100
    for r in sorted(stalls_dict.keys()):
        layout.extend(generate_dynamic_row('Stalls', r, stalls_dict[r], y, max_s, spacing=18, curve_factor=0.0004))
        y += 28 
    stalls_bottom_y = y

    lounge_dict = HARDCODED_LAYOUT.get('Stalls Lounge', {})
    for r, seats in lounge_dict.items():
        for s in seats:
            x = 300 - (s*20) if r == 'A' else 700 - (s*20)
            layout.append({'Area': 'Stalls Lounge', 'Row': r, 'Combined_Seat': f"{r}{s}", 'X': x, 'Y': stalls_bottom_y + 40})

    dress_dict = HARDCODED_LAYOUT.get('Dress Circle', {})
    max_d = max([max(seats) for seats in dress_dict.values()]) if dress_dict else 0
    y = stalls_bottom_y + 120
    for r in sorted(dress_dict.keys()):
        layout.extend(generate_dynamic_row('Dress Circle', r, dress_dict[r], y, max_d, spacing=18, curve_factor=0.0003, gap_center=35))
        y += 28
    dress_bottom_y = y

    upper_dict = HARDCODED_LAYOUT.get('Upper Circle', {})
    max_u = max([max(seats) for seats in upper_dict.values()]) if upper_dict else 0
    y = dress_bottom_y + 120
    for r in sorted(upper_dict.keys()):
        layout.extend(generate_dynamic_row('Upper Circle', r, upper_dict[r], y, max_u, spacing=18, curve_factor=0.0003, gap_center=35))
        y += 28
            
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

def process_data(filtered_sales, df_layout, area_c, seat_c, count_c, price_c, value_c, band_c):
    agg_dict = {count_c: 'sum'}
    has_r = price_c != "None"
    has_v = value_c != "None"
    has_p = band_c != "None"
    
    if has_r: agg_dict[price_c] = 'sum'
    if has_v: agg_dict[value_c] = 'sum'
    if has_p: agg_dict[band_c] = 'first' 

    df_grouped = filtered_sales.groupby([area_c, seat_c]).agg(agg_dict).reset_index()
    df_grouped.rename(columns={count_c: 'Count'}, inplace=True)
    if has_r:
        df_grouped.rename(columns={price_c: 'Total_Revenue'}, inplace=True)
        df_grouped['Avg_Price'] = (df_grouped['Total_Revenue'] / df_grouped['Count']).fillna(0)
    if has_v: df_grouped.rename(columns={value_c: 'Total_Value'}, inplace=True)
    if has_p: df_grouped.rename(columns={band_c: 'Expected_Price'}, inplace=True)

    def safe_match(layout_area, data, target_col):
        exact = data[data[target_col] == layout_area]
        return exact if not exact.empty else data[data[target_col].apply(lambda x: x in layout_area or layout_area in x)]

    merged_records = []
    for _, layout_row in df_layout.iterrows():
        area = layout_row['Area']
        seat = layout_row['Combined_Seat']
        area_match = safe_match(area, df_grouped, area_c)
        seat_match = area_match[area_match[seat_c] == seat]
        
        count = seat_match['Count'].sum() if not seat_match.empty else 0
        revenue = seat_match['Total_Revenue'].sum() if has_r and not seat_match.empty else 0
        value = seat_match['Total_Value'].sum() if has_v and not seat_match.empty else 0
        avg_price = seat_match['Avg_Price'].mean() if has_r and not seat_match.empty and count > 0 else 0
        reduction_pct = ((value - revenue) / value * 100) if has_r and has_v and value > 0 else 0
        expected_price = seat_match['Expected_Price'].values[0] if has_p and not seat_match.empty else "Unmapped"
            
        merged_records.append({
            'Area': area, 'Combined_Seat': seat, 'X': layout_row['X'], 'Y': layout_row['Y'], 
            'Count': count, 'Total_Revenue': revenue, 'Total_Value': value, 'Avg_Price': avg_price, 
            'Reduction_Pct': reduction_pct, 'Expected_Price': expected_price
        })
    return pd.DataFrame(merged_records), has_r, has_p, has_v

def build_figure(merged_df, view_filter, metric_choice, marker_size, stalls_bottom, dress_bottom, has_r, has_p, has_v, title_override=None):
    map_df = merged_df[merged_df['Area'] == view_filter] if view_filter != "All Areas" else merged_df
    fig = go.Figure()
    
    if metric_choice == "Price Band" and has_p:
        unique_bands = map_df['Expected_Price'].unique()
        color_seq = px.colors.qualitative.Pastel + px.colors.qualitative.Set3
        for i, band in enumerate(unique_bands):
            b_df = map_df[map_df['Expected_Price'] == band]
            marker_color = '#e0e0e0' if str(band) == "Unmapped" else color_seq[i % len(color_seq)]
            fig.add_trace(go.Scatter(
                x=b_df['X'], y=b_df['Y'], mode='markers',
                marker=dict(size=marker_size, color=marker_color, line=dict(width=1, color='DarkSlateGrey')),
                name=str(band), text=b_df['Area'] + " - " + b_df['Combined_Seat'],
                customdata=b_df[['Expected_Price', 'Count']], hovertemplate="<b>%{text}</b><br>Band: %{customdata[0]}<br>Times Sold: %{customdata[1]}<extra></extra>"
            ))
    else:
        unsold_df = map_df[map_df['Count'] == 0]
        sold_df = map_df[map_df['Count'] > 0]
        metric_col = 'Count' if metric_choice == "Sales Count" else 'Total_Revenue'
        color_title = "Times Sold" if metric_choice == "Sales Count" else "Revenue (£)"
        
        if not unsold_df.empty:
            fig.add_trace(go.Scatter(
                x=unsold_df['X'], y=unsold_df['Y'], mode='markers',
                marker=dict(size=marker_size, color='#e0e0e0', line=dict(width=1, color='white')),
                name="Unsold", text=unsold_df['Area'] + " - " + unsold_df['Combined_Seat'],
                hovertemplate="<b>%{text}</b><br>Times Sold: 0<br>Revenue: £0.00<extra></extra>"
            ))

        if not sold_df.empty:
            hover_temp = "<b>%{text}</b><br>Times Sold: %{customdata[0]}"
            custom_cols = ['Count']
            
            if has_r:
                hover_temp += "<br>Total Revenue: £%{customdata[1]:.2f}<br>Avg Price/Seat: £%{customdata[2]:.2f}"
                custom_cols.extend(['Total_Revenue', 'Avg_Price'])
                if has_v:
                    hover_temp += "<br>Total Value: £%{customdata[3]:.2f}<br>Reduction: %{customdata[4]:.1f}%"
                    custom_cols.extend(['Total_Value', 'Reduction_Pct'])
            if has_p:
                custom_cols.append('Expected_Price')
                hover_temp += f"<br>Price Band: %{{customdata[{len(custom_cols)-1}]}}"
                
            hover_temp += "<extra></extra>"
            fig.add_trace(go.Scatter(
                x=sold_df['X'], y=sold_df['Y'], mode='markers',
                marker=dict(size=marker_size, color=sold_df[metric_col], colorscale='YlOrRd', showscale=True, colorbar=dict(title=color_title), line=dict(width=1, color='DarkRed')),
                name="Sold", text=sold_df['Area'] + " - " + sold_df['Combined_Seat'], customdata=sold_df[custom_cols], hovertemplate=hover_temp
            ))
        
    if view_filter in ["All Areas", "Stalls"]: fig.add_annotation(x=500, y=70, text="<b>STALLS</b>", showarrow=False, font=dict(size=18, color="black"))
    if view_filter in ["All Areas", "Dress Circle"]: fig.add_annotation(x=500, y=stalls_bottom + 80, text="<b>DRESS CIRCLE</b>", showarrow=False, font=dict(size=18, color="black"))
    if view_filter in ["All Areas", "Upper Circle"]: fig.add_annotation(x=500, y=dress_bottom + 80, text="<b>UPPER CIRCLE</b>", showarrow=False, font=dict(size=18, color="black"))
    if view_filter in ["All Areas", "Boxes"]:
        for label, (lx, ly) in {'C': (140, 70), 'D': (140, 180), 'G': (80, 70), 'H': (80, 180), 'E': (860, 70), 'F': (860, 180), 'J': (920, 70), 'K': (920, 180)}.items():
             fig.add_annotation(x=lx-10, y=ly-15, text=f"Box {label}", showarrow=False, font=dict(size=12, color="gray"))
    if view_filter in ["All Areas", "Stalls Lounge"]:
        fig.add_annotation(x=220, y=stalls_bottom + 60, text="Lounge A", showarrow=False, font=dict(size=14, color="gray"))
        fig.add_annotation(x=620, y=stalls_bottom + 60, text="Lounge B", showarrow=False, font=dict(size=14, color="gray"))

    fig.update_layout(plot_bgcolor='white', width=1200, height=1100, yaxis=dict(autorange='reversed', showgrid=False, zeroline=False, visible=False), xaxis=dict(showgrid=False, zeroline=False, visible=False), hovermode="closest", showlegend=(metric_choice == "Price Band"))
    
    if title_override: fig.update_layout(title=title_override, title_x=0.5, title_font=dict(size=24))
    return fig

def generate_smart_insights(merged_df, total_capacity, num_performances, has_r, has_p, has_v):
    st.markdown("### 🤖 Smart Insights")
    sold_df = merged_df[merged_df['Count'] > 0]
    total_sales = sold_df['Count'].sum()
    total_inventory = total_capacity * num_performances
    sell_through = (total_sales / total_inventory) * 100 if total_inventory > 0 else 0
    
    if sold_df.empty:
        st.info("No sales data available for the currently selected dates/filters.")
        return
        
    busiest_area = sold_df.groupby('Area')['Count'].sum().idxmax()
    top_seat = sold_df.loc[sold_df['Count'].idxmax()]
    
    summary_text = f"**Capacity Overview:** You have sold **{int(total_sales)} tickets**. With a venue capacity of {total_capacity} over {num_performances} performance(s), your total inventory is {total_inventory}. This represents a true **{sell_through:.1f}% sell-through rate**.\n\n"
    summary_text += f"**Volume Trends:** The highest volume section is the **{busiest_area}**. Your most frequently sold seat is **{top_seat['Area']} - {top_seat['Combined_Seat']}** ({int(top_seat['Count'])} sold)."

    if has_r:
        total_rev = sold_df['Total_Revenue'].sum()
        highest_yield_area = sold_df.groupby('Area')['Total_Revenue'].sum().idxmax()
        summary_text += f"\n\n**Financial Yield:** Total mapped revenue is **£{total_rev:,.2f}**. Highest yielding section: **{highest_yield_area}**."
        
        if has_v:
            total_val = sold_df['Total_Value'].sum()
            if total_val > 0:
                overall_reduction = ((total_val - total_rev) / total_val) * 100
                summary_text += f" The total actual value of these tickets was **£{total_val:,.2f}**, representing an overall **discount/reduction of {overall_reduction:.1f}%** from full price."

    if has_p:
        band_sales = sold_df.groupby('Expected_Price')['Count'].sum()
        band_capacity = merged_df.groupby('Expected_Price')['Count'].count() * num_performances
        st.markdown(summary_text)
        st.markdown("**Pricing Strategy Performance:**")
        
        band_metrics = pd.DataFrame({'Total Available Tickets': band_capacity, 'Tickets Sold': band_sales}).fillna(0)
        band_metrics['Sell-Through %'] = (band_metrics['Tickets Sold'] / band_metrics['Total Available Tickets']) * 100
        st.dataframe(band_metrics.sort_index(ascending=True), use_container_width=True, column_config={"Sell-Through %": st.column_config.NumberColumn(format="%.1f%%")})
    else:
        st.info(summary_text)

# --- Data Input Section ---
col1, col2 = st.columns(2)
with col1: sales_file = st.file_uploader("Upload Sales Data", type=["csv", "xlsx", "xls"])
with col2: pasted_data = st.text_area("OR Paste Sales Data", height=100)

df_sales = load_data(sales_file, pasted_data)
df_layout, stalls_bottom, dress_bottom = build_master_layout()
df_layout['Area'] = df_layout['Area'].astype(str).str.title()
TOTAL_VENUE_CAPACITY = len(df_layout)

if not df_sales.empty:
    st.success("Sales data loaded successfully!")
    st.markdown("---")
    
    st.markdown("#### Map Your Columns")
    c1, c2, c3 = st.columns(3)
    with c1: area_col = st.selectbox("Area Column", df_sales.columns, index=get_col_index("Area", df_sales.columns))
    with c2: seat_col = st.selectbox("Seat Column", df_sales.columns, index=get_col_index("Seat", df_sales.columns) or (1 if len(df_sales.columns) > 1 else 0))
    with c3: count_col = st.selectbox("Count Column", df_sales.columns, index=get_col_index("Count", df_sales.columns) or (2 if len(df_sales.columns) > 2 else 0))
    
    c4, c5, c6 = st.columns(3)
    with c4: price_col = st.selectbox("Revenue/Price Paid (Optional)", ["None"] + list(df_sales.columns), index=get_col_index("Sum of Price", df_sales.columns, has_none=True))
    with c5: value_col = st.selectbox("Total Value (Optional)", ["None"] + list(df_sales.columns), index=get_col_index("Original Price", df_sales.columns, has_none=True))
    with c6: band_col = st.selectbox("Price Band (Optional)", ["None"] + list(df_sales.columns), index=get_col_index("Band", df_sales.columns, has_none=True))
    
    c7, c8, _ = st.columns(3)
    with c7: date_col = st.selectbox("Date of Purchase (Optional for Animation)", ["None"] + list(df_sales.columns), index=get_col_index("Date Confirmed", df_sales.columns, has_none=True))
    with c8: num_performances = st.number_input("Total Performances", min_value=1, value=1, step=1, help="Multiply capacity by this number to get an accurate sell-through rate.")
    
    insights_placeholder = st.container()
    st.markdown("---")
    
    # Clean Core Data
    df_sales[area_col] = df_sales[area_col].astype(str).str.strip().str.title()
    df_sales[seat_col] = df_sales[seat_col].astype(str).str.strip().str.upper()
    df_sales[count_col] = pd.to_numeric(df_sales[count_col], errors='coerce').fillna(0)
    if price_col != "None": df_sales[price_col] = pd.to_numeric(df_sales[price_col], errors='coerce').fillna(0)
    if value_col != "None": df_sales[value_col] = pd.to_numeric(df_sales[value_col], errors='coerce').fillna(0)
    if date_col != "None": df_sales[date_col] = pd.to_datetime(df_sales[date_col], errors='coerce')
    
    min_date, max_date = None, None
    if date_col != "None" and not df_sales[date_col].dropna().empty:
        min_date = df_sales[date_col].dropna().min().date()
        max_date = df_sales[date_col].dropna().max().date()
    
    tab_map, tab_data, tab_forecast = st.tabs(["🗺️ Interactive Heatmap", "💷 Revenue Data", "📈 What-If Forecast"])
    
    with tab_map:
        selected_date = max_date
        if date_col != "None" and max_date is not None:
            st.markdown("#### ⏳ Time-Based Sales Tracking")
            selected_date = st.slider("Drag to view the venue fill up over time:", min_value=min_date, max_value=max_date, value=max_date, format="YYYY-MM-DD")
            play_btn = st.button("▶️ Play Week-by-Week Animation")
        else:
            play_btn = False
            
        c_left, c_right = st.columns([2, 1])
        with c_left: view_filter = st.radio("Isolate Area:", ["All Areas", "Stalls", "Dress Circle", "Upper Circle", "Boxes", "Stalls Lounge"], horizontal=True)
        with c_right:
            metric_options = ["Sales Count"]
            if price_col != "None": metric_options.append("Total Revenue")
            if band_col != "None": metric_options.append("Price Band")
            metric_choice = st.radio("Heatmap Color Metric:", metric_options, horizontal=True)
            
        marker_size = 14 if view_filter == "All Areas" else 24
        map_placeholder = st.empty()
        
        if date_col != "None":
            df_filtered = df_sales[(df_sales[date_col].dt.date <= selected_date) | (df_sales[date_col].isna())]
        else:
            df_filtered = df_sales
            
        merged_df, has_r, has_p, has_v = process_data(df_filtered, df_layout, area_col, seat_col, count_col, price_col, value_col, band_col)
        
        if play_btn and min_date and max_date:
            curr_d = min_date
            while curr_d <= max_date:
                t_df = df_sales[(df_sales[date_col].dt.date <= curr_d) | (df_sales[date_col].isna())]
                t_merged, _, _, _ = process_data(t_df, df_layout, area_col, seat_col, count_col, price_col, value_col, band_col)
                t_fig = build_figure(t_merged, view_filter, metric_choice, marker_size, stalls_bottom, dress_bottom, has_r, has_p, has_v, title_override=f"Sales up to: {curr_d.strftime('%Y-%m-%d')}")
                map_placeholder.plotly_chart(t_fig, use_container_width=True)
                time.sleep(0.2) 
                curr_d += datetime.timedelta(days=7)
            t_fig = build_figure(merged_df, view_filter, metric_choice, marker_size, stalls_bottom, dress_bottom, has_r, has_p, has_v, title_override=f"Sales up to: {max_date.strftime('%Y-%m-%d')}")
            map_placeholder.plotly_chart(t_fig, use_container_width=True)
            
        else:
            fig = build_figure(merged_df, view_filter, metric_choice, marker_size, stalls_bottom, dress_bottom, has_r, has_p, has_v)
            map_placeholder.plotly_chart(fig, use_container_width=True)

    with insights_placeholder:
        generate_smart_insights(merged_df, TOTAL_VENUE_CAPACITY, num_performances, has_r, has_p, has_v)
        
    with tab_data:
        st.subheader("Seat-by-Seat Data")
        display_cols = ['Area', 'Combined_Seat', 'Count']
        if has_r: display_cols.extend(['Total_Revenue', 'Avg_Price'])
        if has_r and has_v: display_cols.extend(['Total_Value', 'Reduction_Pct'])
        if has_p: display_cols.append('Expected_Price')
            
        display_df = merged_df[display_cols].copy()
        rename_map = {'Combined_Seat': 'Seat', 'Total_Revenue': 'Total Revenue (£)', 'Avg_Price': 'Avg Price (£)', 'Total_Value': 'Total Value (£)', 'Reduction_Pct': 'Reduction (%)'}
        if has_p: rename_map['Expected_Price'] = 'Price Band'
        display_df.rename(columns=rename_map, inplace=True)
        
        st.dataframe(
            display_df.sort_values(by='Total Revenue (£)' if has_r else 'Count', ascending=False),
            use_container_width=True,
            column_config={
                "Total Revenue (£)": st.column_config.NumberColumn(format="£%.2f"),
                "Avg Price (£)": st.column_config.NumberColumn(format="£%.2f"),
                "Total Value (£)": st.column_config.NumberColumn(format="£%.2f"),
                "Reduction (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "Count": st.column_config.NumberColumn("Times Sold")
            }
        )
        
    with tab_forecast:
        if has_p and has_r:
            st.subheader("What-If Revenue Forecasting")
            st.markdown("Adjust the hypothetical price for each band below. The app will calculate how much more (or less) revenue you would have generated assuming the exact same volume of ticket sales.")
            
            sold_for_forecast = merged_df[merged_df['Count'] > 0]
            if not sold_for_forecast.empty:
                band_stats = sold_for_forecast.groupby('Expected_Price').agg({'Count': 'sum', 'Total_Revenue': 'sum'}).reset_index()
                band_stats['Current_Avg_Price'] = (band_stats['Total_Revenue'] / band_stats['Count']).fillna(0)
                
                col_bands, col_results = st.columns([2, 1])
                
                with col_bands:
                    new_prices = {}
                    for _, row in band_stats.iterrows():
                        band = row['Expected_Price']
                        if band == "Unmapped": continue
                        new_prices[band] = st.number_input(f"Band '{band}' Price (£) - (Currently averaging £{row['Current_Avg_Price']:.2f} across {int(row['Count'])} tickets)", value=float(row['Current_Avg_Price']), step=1.0)
                
                with col_results:
                    st.markdown("#### Forecast Results")
                    forecast_revenue, base_revenue = 0, 0
                    
                    for _, row in band_stats.iterrows():
                        band = row['Expected_Price']
                        if band == "Unmapped":
                            forecast_revenue += row['Total_Revenue']
                            base_revenue += row['Total_Revenue']
                        else:
                            base_revenue += row['Total_Revenue']
                            forecast_revenue += row['Count'] * new_prices[band]
                    
                    st.metric("Current Base Revenue", f"£{base_revenue:,.2f}")
                    st.metric("Forecasted Revenue", f"£{forecast_revenue:,.2f}", delta=f"£{forecast_revenue - base_revenue:,.2f}")
            else:
                st.info("No sales data available for forecasting based on the current filters.")
        else:
            st.warning("⚠️ To use the Forecasting tool, you must map both a **Revenue/Price Paid Column** and a **Price Band Column**.")
else:
    st.info("Waiting for Sales Data upload to generate the heatmap and insights...")
