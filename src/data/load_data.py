import pandas as pd

EXPECTED_COLUMNS = [
    "Text",
    "Sentiment",
    "Timestamp",
    "User",
    "Platform",
    "Hashtags",
    "Retweets",
    "Likes",
    "Country",
    "Year",
    "Month",
    "Day",
    "Hour",
]


def load_and_validate(path: str, verbose: bool = True):
    df = pd.read_csv(path)

    # Drop unwanted columns 
    df = df.drop(
        columns=[c for c in df.columns if c.startswith("Unnamed")], errors="ignore"
    )

    # Parse Timestamp explicitly (not plaintext)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    report = {}

    # --- Schema check ---
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    report["missing_columns"] = missing_cols

    # --- Missing values check ---
    nulls = df.isnull().sum()
    report["null_counts"] = nulls[nulls > 0].to_dict()

    # --- Duplicates check ---
    report["duplicate_rows"] = int(df.duplicated().sum())
    report["duplicate_text_values"] = int(df["Text"].duplicated().sum())

    # --- Whitespace / label consistency check ---
    report["sentiment_raw_unique"] = int(df["Sentiment"].nunique())
    report["sentiment_stripped_unique"] = int(df["Sentiment"].str.strip().nunique())
    report["platform_raw_values"] = df["Platform"].unique().tolist()
    report["platform_stripped_values"] = df["Platform"].str.strip().unique().tolist()

    # --- Timestamp consistency vs Year/Month/Day/Hour columns ---
    if "Timestamp" in df.columns and "Year" in df.columns:
        mismatch = (df["Timestamp"].dt.year != df["Year"]).sum()
        report["timestamp_year_mismatches"] = int(mismatch)
        report["unparseable_timestamps"] = int(df["Timestamp"].isnull().sum())

    # --- Numeric sanity checks ---
    for col in ["Retweets", "Likes"]:
        if col in df.columns:
            report[f"{col}_negative_count"] = int((df[col] < 0).sum())
            report[f"{col}_range"] = (float(df[col].min()), float(df[col].max()))

    if verbose:
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Missing expected columns: {report['missing_columns'] or 'none'}")
        print(f"Null values: {report['null_counts'] or 'none'}")
        print(f"Duplicate rows: {report['duplicate_rows']}")
        print(f"Duplicate Text values: {report['duplicate_text_values']}")
        print(
            f"Sentiment labels: {report['sentiment_raw_unique']} raw -> "
            f"{report['sentiment_stripped_unique']} after trimming whitespace"
        )
        print(
            f"Platform values: {report['platform_raw_values']} -> "
            f"{report['platform_stripped_values']}"
        )
        print(f"Timestamp/Year mismatches: {report.get('timestamp_year_mismatches')}")

    return df, report


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sentimentdataset.csv"
    load_and_validate(path)
