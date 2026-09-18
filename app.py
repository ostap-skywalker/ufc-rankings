import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC AI Rankings", page_icon="🏆", layout="wide")
st.title("ELO UFC Rankings")
st.markdown("Global, Strike, and Grapple Elo ratings")

@st.cache_data
def load_data():
    df = pd.read_csv("rankings_light.csv")
    return df

roster = load_data()

filt_c1, filt_c2, filt_c3 = st.columns(3)
with filt_c1: weight_filter = st.selectbox("Ranking Category", [
    "Pound-for-Pound (All)", "Best Strikers (Strike Elo)", "Best Grapplers (Grapple Elo)", 
    "Flyweight", "Bantamweight", "Featherweight", "Lightweight", "Welterweight", 
    "Middleweight", "Light Heavyweight", "Heavyweight", "Strawweight"
])
with filt_c2: era_filter = st.selectbox("Roster Era", ["Active Fighters", "All-Time Roster"])
with filt_c3: state_filter = st.selectbox("Fighter State", ["Current Rating", "Absolute Peak (Prime)"])

df_rank = roster.copy()
if era_filter == "Active Fighters":
    cutoff = pd.to_datetime('today') - pd.Timedelta(days=730)
    df_rank['last_fight_date'] = pd.to_datetime(df_rank['last_fight_date'], errors='coerce')
    df_rank = df_rank[df_rank['last_fight_date'] >= cutoff]

is_peak = (state_filter == "Absolute Peak (Prime)")
sort_col = "peak_elo" if is_peak else "global_elo"

if weight_filter == "Pound-for-Pound (All)":
    df_rank = df_rank.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
    display_cols = ['name', 'fights_in_ufc', 'stance', 'strike_elo', 'grapple_elo', sort_col]
    col_names = ['Fighter', 'UFC Fights', 'Stance', 'Strike Elo', 'Grapple Elo', 'P4P Elo']
elif "Best Strikers" in weight_filter:
    df_rank = df_rank.sort_values(by="strike_elo", ascending=False).reset_index(drop=True)
    display_cols = ['name', 'fights_in_ufc', 'stance', 'strike_elo', 'grapple_elo', sort_col]
    col_names = ['Fighter', 'UFC Fights', 'Stance', 'Strike Elo', 'Grapple Elo', 'Global Elo']
elif "Best Grapplers" in weight_filter:
    df_rank = df_rank.sort_values(by="grapple_elo", ascending=False).reset_index(drop=True)
    display_cols = ['name', 'fights_in_ufc', 'stance', 'grapple_elo', 'strike_elo', sort_col]
    col_names = ['Fighter', 'UFC Fights', 'Stance', 'Grapple Elo', 'Strike Elo', 'Global Elo']
else:
    
    div_clean = weight_filter
    if 'weight_class' in df_rank.columns:
        df_rank = df_rank[df_rank['weight_class'].astype(str).str.contains(div_clean, case=False, na=False)]
        
    df_rank = df_rank.sort_values(by=sort_col, ascending=False).reset_index(drop=True)
    display_cols = ['name', 'fights_in_ufc', 'stance', 'strike_elo', 'grapple_elo', sort_col]
    col_names = ['Fighter', 'UFC Fights', 'Stance', 'Strike Elo', 'Grapple Elo', f'{div_clean} Elo']

df_display = df_rank.head(100)[display_cols].copy()
for col in display_cols[3:]:
    df_display[col] = df_display[col].apply(lambda x: f"{float(x):.1f}" if pd.notna(x) else "1000.0")
df_display.columns = col_names
df_display.insert(0, '#', range(1, len(df_display) + 1))

st.dataframe(df_display, use_container_width=True, hide_index=True)
