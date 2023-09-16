""" Modul pro vytváření sémantických embeddingů a dalších funkcí.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from nltk import tokenize


def get_embeddings(text: str, model: SentenceTransformer, sent_tokenize: bool = True) -> np.ndarray:
    """

    :param text:
    :param model:
    :param sent_tokenize:
    :return:
    """
    if sent_tokenize:
        sentences = tokenize.sent_tokenize(text)
        sentence_embeddings = [model.encode(sent) for sent in sentences]
        doc_embedding = np.mean(sentence_embeddings, axis=0)
    else:
        doc_embedding = model.encode(text)

    return doc_embedding
