import numpy as np
import PyPDF2
from transformers import AutoTokenizer, AutoModel
import torch
from faiss_utils import FaissUtils

# Load a pre-trained model and tokenizer for text vectorization
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def read_pdf_and_add_to_faiss(file_path: str, faiss_utils: FaissUtils):
    """Read a PDF file and add its content to the Faiss index."""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_number, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Vectorize the entire text
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                outputs = model(**inputs)
                vector = outputs.last_hidden_state.mean(dim=1).detach().numpy()  # Mean of the last hidden state
                faiss_utils.add_vector_with_text(vector.astype('float32'), f"Page {page_number + 1}: {text}")
    print("Added PDF content to the Faiss index.")
    return faiss_utils

def search_text_in_faiss(faiss_utils: FaissUtils, input_text: str):
    """Search for a given input text in the Faiss index and return the closest matching text."""
    # Vectorize the input text
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    vector = outputs.last_hidden_state.mean(dim=1).detach().numpy()  # Mean of the last hidden state

    # Search for the nearest vector in the Faiss index
    distances, indices = faiss_utils.search_vector(vector.astype('float32'))

    # Normalize distances to range 0-100
    if distances.size > 0:
        min_distance = distances.min()
        max_distance = distances.max()
        normalized_distances = 100 * (distances - min_distance) / (max_distance - min_distance + 1e-8)
    else:
        normalized_distances = distances

    if len(indices) > 0 and normalized_distances[0][0] < 50:  # Adjust threshold as needed
        return faiss_utils.get_text_by_index(indices[0][0])
    return "No matching text found"

def main():
    # Initialize FaissUtils with vector dimension 768 (BERT output dimension)
    faiss_utils = FaissUtils(dimension=768)

    # Read a PDF file and add its content to Faiss index
    pdf_path = "C:/Users/Robin/Desktop/trest/out/建设工程合同纠纷首次执行通知书.pdf"  # Update with actual PDF path
    faiss_utils = read_pdf_and_add_to_faiss(pdf_path, faiss_utils)

    # Input a sentence and find the closest match in the vector database
    input_text = "限公司依据西安仲裁委员会西仲调字（ 2024）第1514号仲裁裁"  # Replace with the sentence you want to match
    matched_text = search_text_in_faiss(faiss_utils, input_text)
    print(f"Matched Text: {matched_text}")

if __name__ == '__main__':
    main()
