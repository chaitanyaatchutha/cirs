import pandas as pd
import re
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. FILE PATHS
# ============================================================

TRAIN_FILE = "CIRS_Train.csv"
TEST_FILE = "CIRS_Test.csv"

MODEL_FILE = "model.pkl"
VECTORIZER_FILE = "vectorizer.pkl"


# ============================================================
# 2. LOAD DATASETS
# ============================================================

print("Loading training dataset...")

train_data = pd.read_csv(TRAIN_FILE)

print("Loading testing dataset...")

test_data = pd.read_csv(TEST_FILE)


# ============================================================
# 3. CLEAN COLUMN NAMES
# ============================================================

train_data.columns = train_data.columns.str.strip()
test_data.columns = test_data.columns.str.strip()


# ============================================================
# 4. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = ["Complaint", "Department"]

for column in required_columns:

    if column not in train_data.columns:
        raise ValueError(
            f"'{column}' column is missing from training dataset."
        )

    if column not in test_data.columns:
        raise ValueError(
            f"'{column}' column is missing from testing dataset."
        )


# ============================================================
# 5. TEXT CLEANING
# ============================================================

def clean_text(text):

    text = str(text).lower().strip()

    # Keep letters and numbers.
    # Numbers can contain useful information such as room numbers.
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


train_data["Complaint"] = train_data["Complaint"].apply(clean_text)
test_data["Complaint"] = test_data["Complaint"].apply(clean_text)


# ============================================================
# 6. REMOVE EMPTY COMPLAINTS
# ============================================================

train_data = train_data[train_data["Complaint"] != ""].copy()
test_data = test_data[test_data["Complaint"] != ""].copy()


# ============================================================
# 7. REMOVE DUPLICATES
# ============================================================

train_data = train_data.drop_duplicates(
    subset=["Complaint"]
).reset_index(drop=True)

test_data = test_data.drop_duplicates(
    subset=["Complaint"]
).reset_index(drop=True)


# ============================================================
# 8. PREPARE X AND Y
# ============================================================

X_train = train_data["Complaint"]
y_train = train_data["Department"]

X_test = test_data["Complaint"]
y_test = test_data["Department"]


print("\n========================================")
print("DATASET INFORMATION")
print("========================================")

print("Training samples :", len(X_train))
print("Testing samples  :", len(X_test))

print("\nDepartments:")
print(sorted(y_train.unique()))


# ============================================================
# 9. SHOW TRAINING DISTRIBUTION
# ============================================================

print("\n========================================")
print("TRAINING DATA DISTRIBUTION")
print("========================================")

print(y_train.value_counts())


# ============================================================
# 10. TF-IDF VECTORIZER
# ============================================================

print("\n========================================")
print("CREATING TF-IDF FEATURES")
print("========================================")

vectorizer = TfidfVectorizer(

    # Single words + two-word combinations
    ngram_range=(1, 2),

    # Ignore extremely rare words
    min_df=1,

    # Ignore extremely common words
    max_df=0.95,

    # Limit vocabulary size for efficiency
    max_features=10000,

    # Normalize text vectors
    sublinear_tf=True
)


# IMPORTANT:
# fit_transform ONLY on training data

X_train_vec = vectorizer.fit_transform(X_train)


# IMPORTANT:
# ONLY transform test data.
# DO NOT fit again.

X_test_vec = vectorizer.transform(X_test)


print("Training feature shape :", X_train_vec.shape)
print("Testing feature shape  :", X_test_vec.shape)


# ============================================================
# 11. TRAIN LOGISTIC REGRESSION
# ============================================================

print("\n========================================")
print("TRAINING MODEL")
print("========================================")

model = LogisticRegression(

    max_iter=1000,

    # Helps when classes have slightly different sizes
    class_weight="balanced",

    # Stable solver for TF-IDF text classification
    solver="lbfgs",

    random_state=42
)

model.fit(X_train_vec, y_train)


print("Model training completed!")


# ============================================================
# 12. PREDICTION
# ============================================================

print("\n========================================")
print("TESTING MODEL")
print("========================================")

y_pred = model.predict(X_test_vec)


# ============================================================
# 13. ACCURACY
# ============================================================

accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:")
print(f"{accuracy * 100:.2f}%")


# ============================================================
# 14. CLASSIFICATION REPORT
# ============================================================

print("\n========================================")
print("CLASSIFICATION REPORT")
print("========================================")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ============================================================
# 15. CONFUSION MATRIX
# ============================================================

print("\n========================================")
print("CONFUSION MATRIX")
print("========================================")

labels = sorted(y_train.unique())

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=labels
)

cm_df = pd.DataFrame(
    cm,
    index=labels,
    columns=labels
)

print(cm_df)


# ============================================================
# 16. SAVE MODEL
# ============================================================

print("\n========================================")
print("SAVING MODEL")
print("========================================")

joblib.dump(model, MODEL_FILE)

joblib.dump(
    vectorizer,
    VECTORIZER_FILE
)

print(f"Model saved as      : {MODEL_FILE}")
print(f"Vectorizer saved as : {VECTORIZER_FILE}")


# ============================================================
# 17. TEST NEW COMPLAINTS
# ============================================================

print("\n========================================")
print("TESTING NEW COMPLAINTS")
print("========================================")


samples = [

    "The ceiling fan in our classroom suddenly stopped working",

    "The Arduino board is not detected",

    "The computer in the lab is not starting",

    "The hostel water supply is not working",

    "The library book cannot be issued",

    "The classroom floor is very dirty",

    "The hostel door is broken",

    "I cannot download my hall ticket",

    "The tube light is flickering",

    "The oscilloscope is not working"

]


# Clean samples
clean_samples = [
    clean_text(sample)
    for sample in samples
]


# Convert using the SAME trained vectorizer
sample_vectors = vectorizer.transform(clean_samples)


# Predictions
predictions = model.predict(sample_vectors)


# Probabilities
probabilities = model.predict_proba(sample_vectors)


for i in range(len(samples)):

    predicted_department = predictions[i]

    confidence = max(probabilities[i]) * 100

    print("\nComplaint:")
    print(samples[i])

    print("Predicted Department:")
    print(predicted_department)

    print(f"Confidence: {confidence:.2f}%")


# ============================================================
# 18. FINISHED
# ============================================================

print("\n========================================")
print("TRAINING COMPLETE")
print("========================================")

print("Your model is ready to use.")
print(f"Model      : {MODEL_FILE}")
print(f"Vectorizer : {VECTORIZER_FILE}")