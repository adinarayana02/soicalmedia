import pandas as pd
import sys

def analyze_data():
    file_path = r"C:\Users\Adi Narayana Thota\OneDrive\Desktop\MTECH\social_media\backend\database\TOP_TIER_RESEARCH_DATASET.xlsx"
    out_path = r"C:\Users\Adi Narayana Thota\.gemini\antigravity\brain\04eea5f8-d689-45b0-bc88-d4cafc7bb030\dataset_analysis.md"
    try:
        df = pd.read_excel(file_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("# Dataset Analysis Report\n\n")
            f.write(f"**Shape:** {df.shape[0]} rows, {df.shape[1]} columns\n\n")
            f.write("## Columns\n")
            for col in df.columns:
                f.write(f"- `{col}` (dtype: {df[col].dtype}, nulls: {df[col].isnull().sum()})\n")
            f.write("\n## First 3 Rows\n")
            f.write("```\n")
            f.write(df.head(3).to_string())
            f.write("\n```\n")
            f.write("\n## Summary Statistics\n")
            f.write("```\n")
            f.write(df.describe(include='all').to_string())
            f.write("\n```\n")
        print("Analysis successfully written to dataset_analysis.md")
    except Exception as e:
        print(f"Error loading Excel file: {e}")

if __name__ == "__main__":
    analyze_data()
