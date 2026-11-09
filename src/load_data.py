from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def fetch_torvik_team_data(season: int = 2026) -> pd.DataFrame:
  """Fetches BartTorvik efficiency and Four Factors data, merging into a single parquet."""
  # 1. Base results & efficiency
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

  # 2. Four Factors
  ff_url = f"https://barttorvik.com/{season}_fffinal.csv"
  # Standard column positions in Torvik's fffinal table
  # cols: team, conf, games, o_efg, d_efg, o_to, d_to, o_orb, d_orb, o_ftr, d_ftr
  ff_cols = [
      "team",
      "conf_ff",
      "games_ff",
      "off_efg",
      "def_efg",
      "off_to",
      "def_to",
      "off_orb",
      "def_orb",
      "off_ftr",
      "def_ftr",
  ]

  print(f"Fetching {season} BartTorvik four factors...")
  ff_df = pd.read_csv(
      ff_url, header=None, usecols=range(len(ff_cols)), names=ff_cols
  )

  # Clean strings before merging
  base_df["team"] = base_df["team"].astype(str).str.strip()
  base_df["conf"] = base_df["conf"].astype(str).str.strip()
  ff_df["team"] = ff_df["team"].astype(str).str.strip()

  # Drop duplicate team column before merge
  ff_df = ff_df[
      [
          "team",
          "off_efg",
          "def_efg",
          "off_to",
          "def_to",
          "off_orb",
          "def_orb",
          "off_ftr",
          "def_ftr",
      ]
  ]

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
  fetch_torvik_team_data(season=2026)