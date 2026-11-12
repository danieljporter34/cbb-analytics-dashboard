from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.markdown(
    """
<style>
    /* Style all st.container(border=True) boxes */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, #162032 0%, #0F172A 100%);
        border: 1px solid #2A3950 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        padding: 1.25rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FF6B35 !important;
    }

    /* Style all st.metric(..., border=True) KPI cards */
    [data-testid="stMetric"] {
        background-color: #131C2E;
        border: 1px solid #2A3950 !important;
        border-left: 4px solid #FF6B35 !important; /* Basketball orange accent stripe */
        border-radius: 8px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
    }
</style>
""",
    unsafe_allow_html=True,
)

st.set_page_config(page_title="CBB Efficiency Dashboard", layout="wide")


# Cache data loading so it only loads once into memory
@st.cache_data
def load_data():
  data_path = Path("data/torvik_teams_2026.parquet")
  if not data_path.exists():
    from src.load_data import fetch_torvik_team_data

    return fetch_torvik_team_data(2026)
  return pd.read_parquet(data_path)


df = load_data()

st.title("🏀 College Basketball Efficiency Analytics (2025–26)")

# --- Sidebar Filters ---
st.sidebar.header("Navigation & Filters")

# Conference filter
all_confs = ["All"] + sorted(df["conf"].unique().tolist())
selected_conf = st.sidebar.selectbox("Conference", all_confs)

filtered_df = df if selected_conf == "All" else df[df["conf"] == selected_conf]

# Team filter
selected_team = st.sidebar.selectbox(
    "Select Team", sorted(filtered_df["team"].unique().tolist())
)
team_row = df[df["team"] == selected_team].iloc[0]

# --- Top-Level KPI Cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("National Rank", f"#{int(team_row['rank'])}", border=True)
col2.metric(
    "Adj. Offense (AdjO)",
    f"{team_row['adj_o']:.1f}",
    help="Points scored per 100 possessions (adjusted)", border=True
)
col3.metric(
    "Adj. Defense (AdjD)",
    f"{team_row['adj_d']:.1f}",
    help="Points allowed per 100 possessions (lower is better)", border=True
)
col4.metric(
    "Adj. Tempo", f"{team_row['adj_tempo']:.1f}", help="Possessions per 40 mins", border=True
)

st.divider()

# --- Scatter Plot: Offensive vs Defensive Efficiency ---
st.subheader("Division I Efficiency Landscape")

# Color the selected team differently to make them stand out
plot_df = filtered_df.copy()
plot_df["Highlight"] = plot_df["team"].apply(
    lambda x: "Selected Team" if x == selected_team else "Other Teams"
)

fig = px.scatter(
    plot_df,
    x="adj_o",
    y="adj_d",
    hover_name="team",
    color="Highlight",
    color_discrete_map = ({"Selected Team": "#FF4B4B", "Other Teams": "rgba(241, 245, 249, 0.45)"}),
    labels={"adj_o": "Adjusted Offense (Points / 100 Poss)", "adj_d": "Adjusted Defense (Points Allowed / 100 Poss)"},
)

# Inverted Y axis because lower defense is better in basketball
fig.update_yaxes(autorange="reversed")
fig.update_layout(
    dragmode="pan",)

fig.update_traces(
    selector=dict(name="Other Teams"),
    marker=dict(size=7),
)
fig.update_traces(
    selector=dict(name="Selected Team"),
    marker=dict(size=14, line=dict(width=2, color="#FFFFFF")),
)

st.plotly_chart(fig, width="stretch", config={"scrollZoom": True})

import plotly.graph_objects as go

# --- Dean Oliver's Four Factors Section ---
st.subheader("Dean Oliver's Four Factors Breakdown")
st.caption(
    "Comparison of team offensive and defensive execution relative to Division"
    " I national medians."
)

# Calculate Division I Medians for benchmarking
nat_medians = {
    "eFG%": (df["off_efg"].median(), df["def_efg"].median()),
    "TO%": (df["off_to"].median(), df["def_to"].median()),
    "ORB%": (df["off_orb"].median(), df["def_orb"].median()),
    "FTR": (df["off_ftr"].median(), df["def_ftr"].median()),
}

f1, f2, f3, f4 = st.columns(4)

with f1:
  st.markdown("##### Effective FG% (eFG%)")
  st.metric(
      "Offense",
      f"{team_row['off_efg']:.1f}%",
      delta=f"{team_row['off_efg'] - nat_medians['eFG%'][0]:.1f}% vs D1 Avg",
  )
  st.metric(
      "Defense",
      f"{team_row['def_efg']:.1f}%",
      delta=f"{nat_medians['eFG%'][1] - team_row['def_efg']:.1f}% vs D1 Avg",
      help="Lower opponent eFG% is better",
  )

with f2:
  st.markdown("##### Turnover% (TO%)")
  st.metric(
      "Offense",
      f"{team_row['off_to']:.1f}%",
      delta=f"{nat_medians['TO%'][0] - team_row['off_to']:.1f}% vs D1 Avg",
      help="Lower offensive TO% is better",
  )
  st.metric(
      "Defense",
      f"{team_row['def_to']:.1f}%",
      delta=f"{team_row['def_to'] - nat_medians['TO%'][1]:.1f}% vs D1 Avg",
      help="Higher defensive TO% forced is better",
  )

with f3:
  st.markdown("##### Off. Rebound% (ORB%)")
  st.metric(
      "Offense",
      f"{team_row['off_orb']:.1f}%",
      delta=f"{team_row['off_orb'] - nat_medians['ORB%'][0]:.1f}% vs D1 Avg",
  )
  st.metric(
      "Defense",
      f"{team_row['def_orb']:.1f}%",
      delta=f"{nat_medians['ORB%'][1] - team_row['def_orb']:.1f}% vs D1 Avg",
      help="Lower opponent ORB% allowed is better",
  )

with f4:
  st.markdown("##### Free Throw Rate (FTR)")
  st.metric(
      "Offense",
      f"{team_row['off_ftr']:.1f}",
      delta=f"{team_row['off_ftr'] - nat_medians['FTR'][0]:.1f} vs D1 Avg",
  )
  st.metric(
      "Defense",
      f"{team_row['def_ftr']:.1f}",
      delta=f"{nat_medians['FTR'][1] - team_row['def_ftr']:.1f} vs D1 Avg",
      help="Lower opponent FTR allowed is better",
  )