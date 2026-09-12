import pandas as pd
import json
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

def train_and_export_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "..", "database", "TOP_TIER_RESEARCH_DATASET.xlsx")
    MODEL_OUT_PATH = os.path.join(BASE_DIR, "behavior_model.pkl")
    METRICS_OUT_PATH = os.path.join(BASE_DIR, "model_metrics.json")
    
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_excel(DATA_PATH)
    
    # 1. Define Features and Target
    target = 'final_risk_label'
    
    text_feature = 'text_content'
    categorical_features = ['platform', 'interaction_type', 'topic', 'emotion_label']
    numerical_features = ['likes', 'comments_count', 'shares', 'session_duration', 
                          'toxicity_score', 'avg_sentiment_score', 'posting_frequency', 'late_night_ratio']
    
    # Fill missing values just in case
    df[text_feature] = df[text_feature].fillna('')
    for col in categorical_features:
        df[col] = df[col].fillna('unknown')
    for col in numerical_features:
        df[col] = df[col].fillna(0)
        
    X = df[[text_feature] + categorical_features + numerical_features]
    y = df[target]
    
    # 2. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Build Preprocessing Pipeline
    print("Building preprocessing pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(max_features=5000), text_feature),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ],
        remainder='drop'
    )
    
    # 4. Construct the Full Pipeline with RandomForest
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced'))
    ])
    
    # 5. Train Model
    print("Training model (this may take a moment)...")
    pipeline.fit(X_train, y_train)
    
    # 6. Evaluate Model
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    
    metrics = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "classification_report": report_dict,
        "confusion_matrix": conf_matrix
    }
    
    print(f"Validation Accuracy: {accuracy:.4f}")
    
    # 7. Export Artifacts
    print("Saving model weights and metrics...")
    joblib.dump(pipeline, MODEL_OUT_PATH)
    
    with open(METRICS_OUT_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Model saved to: {MODEL_OUT_PATH}")
    print(f"Metrics saved to: {METRICS_OUT_PATH}")

if __name__ == "__main__":
    train_and_export_model()
