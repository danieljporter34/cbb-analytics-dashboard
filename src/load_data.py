from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def fetch_torvik_team_data(season: int = 2027) -> pd.DataFrame:
  """Fetches BartTorvik efficiency and Four Factors data, merging into a single parquet."""
  # 1. Base results & efficiency (no header row)
  base_url = f"https://barttorvik.com/{season}_team_results.csv"
  base_cols = [
      "rank",
      "team",
      "conf",
      "record",
      "adj_o",
      "adj_o_rk",
      "adj_d",
      "adj_d_rk",
      "barthag",
      "barthag_rk",
      "eff_margin",
      "record_conf",
      "wins",
      "losses",
      "games",
      "adj_tempo",
      "adj_tempo_rk",
  ]

  print(f"Fetching {season} BartTorvik team results...")
  base_df = pd.read_csv(
      base_url, header=None, usecols=range(len(base_cols)), names=base_cols
  )

# 2. Four Factors (use header=None so row 0 isn't dropped during the active season)
  ff_url = f"https://barttorvik.com/{season}_fffinal.csv"
  print(f"Fetching {season} BartTorvik four factors...")

  ff_indices = [0, 1, 3, 5, 7, 9, 11, 13, 15]
  ff_names = [
      "team",
      "off_efg",
      "def_efg",
      "off_ftr",
      "def_ftr",
      "off_orb",
      "def_orb",
      "off_to",
      "def_to",
  ]
  ff_df = pd.read_csv(
      ff_url, header=None, usecols=ff_indices, names=ff_names
  )
  ff_df = ff_df[ff_df["team"] != "TeamName"]  # Safely drop header if present

  # Clean strings before merging
  base_df["team"] = base_df["team"].astype(str).str.strip()
  base_df["conf"] = base_df["conf"].astype(str).str.strip()
  ff_df["team"] = ff_df["team"].astype(str).str.strip()

  merged_df = pd.merge(base_df, ff_df, on="team", how="inner")

  # Convert all numeric metrics to floats/ints
  numeric_cols = [
      "rank",
      "adj_o",
      "adj_o_rk",
      "adj_d",
      "adj_d_rk",
      "barthag",
      "barthag_rk",
      "eff_margin",
      "wins",
      "losses",
      "games",
      "adj_tempo",
      "adj_tempo_rk",
      "off_efg",
      "def_efg",
      "off_to",
      "def_to",
      "off_orb",
      "def_orb",
      "off_ftr",
      "def_ftr",
  ]
  for col in numeric_cols:
    merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")

  processed_path = DATA_DIR / f"torvik_teams_{season}.parquet"
  merged_df.to_parquet(processed_path, index=False)
  print(f"Successfully processed {len(merged_df)} teams to {processed_path}")

  return merged_df


if __name__ == "__main__":
  fetch_torvik_team_data(season=2027)