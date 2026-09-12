import pandas as pd

def analyze_data():
    file_path = r"C:\Users\Adi Narayana Thota\OneDrive\Desktop\MTECH\social_media\backend\database\TOP_TIER_RESEARCH_DATASET.xlsx"
    try:
        print("Loading dataset...")
        df = pd.read_excel(file_path)
        print("Dataset Shape:", df.shape)
        print("\nColumns:")
        for col in df.columns:
            print(f"- {col} (dtype: {df[col].dtype}, nulls: {df[col].isnull().sum()})")
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
        
        print("\nSummary Statistics:")
        print(df.describe(include='all').to_string())
    except Exception as e:
        print(f"Error loading Excel file: {e}")

if __name__ == "__main__":
    analyze_data()
