from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

# Load the model ONCE when the file is imported
# This is the 'starter model' defined in MedMatch v2.2 Section 4.1
logger = logging.getLogger(__name__)

MODEL = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("Embedding model loaded successfully")

def get_embedding(text: str) -> list[float]:
    logger.info(f"Generating embedding for text (length: {len(text)})")
    if not text:
        return []
    embedding = MODEL.encode(text).tolist()
    logger.info(f"Embedding generated: {len(embedding)} dimensions")
    return embedding

def match_score(embedding_a: list, embedding_b: list) -> float:
    """Return similarity percentage (0-100) between two embeddings."""
    if not embedding_a or not embedding_b:
        return 0.0
    
    a = np.array(embedding_a).reshape(1, -1)
    b = np.array(embedding_b).reshape(1, -1)
    score = cosine_similarity(a, b)[0][0]
    return round(float(score) * 100, 2)