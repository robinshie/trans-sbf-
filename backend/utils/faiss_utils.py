import faiss
import numpy as np

class FaissUtils:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.text_map = {}

    def add_vector(self, vector: np.ndarray):
        """Add a vector to the index."""
        self.index.add(vector)

    def search_vector(self, vector: np.ndarray, k: int = 1):
        """Search for the nearest vectors in the index."""
        distances, indices = self.index.search(vector, k)
        return distances, indices

    def update_vector(self, index: int, new_vector: np.ndarray):
        """Update an existing vector in the index."""
        self.index.remove_ids(faiss.IDSelectorBatch([index]))
        self.add_vector(new_vector)

    def delete_vector(self, index: int):
        """Delete a vector from the index."""
        self.index.remove_ids(faiss.IDSelectorBatch([index]))
    
    def get_vector(self, index: int):
        """Retrieve a vector from the index by its ID."""
        vector = np.zeros((self.index.d,), dtype='float32')  # Create an empty vector with the correct shape
        self.index.reconstruct(index, vector)  # Reconstruct the vector from the index
        return vector

    def get_all_vectors(self):
        """Retrieve all vectors from the index."""
        all_vectors = []
        for i in range(self.index.ntotal):  # Loop through all vectors in the index
            vector = self.get_vector(i)  # Get each vector
            all_vectors.append(vector)
        return all_vectors

    def add_vector_with_text(self, vector, text):
        self.index.add(vector)
        self.text_map[len(self.text_map)] = text
    
    def get_text_by_index(self, index):
        return self.text_map.get(index, "未知文本")