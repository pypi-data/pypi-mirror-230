import pandas as pd
from sentence_transformers import SentenceTransformer, util


def calc_similarity_sentence_transformer(df_test, df_training):
    model = SentenceTransformer('"all-mpnet-base-v2"')
    test_text = df_test["text"]
    training_text = df_training["text"]
    test_embeddings = model.encode(test_text)
    training_embeddings = model.encode(training_text)
    cosine_scores = util.cos_sim(test_embeddings, training_embeddings)
    return cosine_scores

