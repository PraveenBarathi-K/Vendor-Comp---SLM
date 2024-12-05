import torch
from transformers import AlbertTokenizer, AlbertForSequenceClassification
import nltk
import re
import pandas as pd


nltk.download('punkt')

# Load products list
mobile_phones_df = pd.read_csv('vendor_comparison_dataset-final.csv')
products = mobile_phones_df['mobile_name'].tolist()

# Load tokenizer and model
tokenizer = AlbertTokenizer.from_pretrained('albert-base-v2')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AlbertForSequenceClassification.from_pretrained('model', num_labels=5)
model.to(device)

# Preprocess query
def preprocess_query(query):
    tokens = nltk.word_tokenize(query)
    return ' '.join(tokens)

# Extract mobile name from query
def extract_mobile_name(query, products):
    for product in products:
        if re.search(r'\b' + re.escape(product) + r'\b', query, re.IGNORECASE):
            return product
    return None

# Predict label and extract mobile name
def predict_and_extract(query, model, tokenizer, products):
    processed_query = preprocess_query(query)
    inputs = tokenizer(processed_query, return_tensors='pt', truncation=True, padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_label = torch.argmax(outputs.logits, dim=1).item()
    mobile_name = extract_mobile_name(query, products)

    return predicted_label, mobile_name
