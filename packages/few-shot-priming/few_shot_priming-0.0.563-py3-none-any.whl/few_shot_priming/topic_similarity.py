import math

import nltk
import os

import numpy as np
from contextualized_topic_models.models.ctm import CombinedTM
from contextualized_topic_models.utils.data_preparation import TopicModelDataPreparation
from contextualized_topic_models.utils.preprocessing import WhiteSpacePreprocessingStopwords
from contextualized_topic_models.evaluation.measures import CoherenceNPMI,InvertedRBO
from nltk.corpus import stopwords as stop_words
from few_shot_priming.prompting_stance import *
from few_shot_priming.experiment import *
from scipy.spatial.distance import cosine

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def preprocess_dataset(df):
    stopwords = list(stop_words.words("english"))
    documents = list(df["text"])
    #documents = list(df.groupby("claims.article.rawFile", as_index = False).agg({"claims.claimCorrectedText": "\n".join})["claims.claimCorrectedText"])
    sp = WhiteSpacePreprocessingStopwords(documents, stopwords_list=stopwords)
    preprocessed_documents, unpreprocessed_corpus, vocab, retained_indices = sp.preprocess()
    return preprocessed_documents, unpreprocessed_corpus, vocab, retained_indices


def create_topic_model(df_test, topic_model_params):
    """
    Create a contexutlaized topic model and save it in mode-path as saved in conf.yaml
    :param df_test:
    :param topic_count: count of dimensions of the topic model
    :param epcohs: count of iterations to train the topic model for
    :return:
    """
    preprocessed_documents, unpreprocessed_corpus, vocab, retained_indices = preprocess_dataset(df_test)
    tp = TopicModelDataPreparation("all-mpnet-base-v2")
    training_dataset = tp.fit(text_for_contextual=unpreprocessed_corpus, text_for_bow=preprocessed_documents)
    #training_dataset = tp.transform(text_for_contextual=unpreprocessed_corpus, text_for_bow=preprocessed_documents)
    bow_size = len(tp.vocab)
    ctm = CombinedTM(bow_size=bow_size, **topic_model_params)
    ctm.fit(training_dataset)
    return ctm, bow_size

def dump_model(model,  topic_model_path):
    model.save(models_dir=topic_model_path)

def load_topic_model(topic_model_params, bow_size, topic_model_path):
    ctm = CombinedTM(bow_size=bow_size, **topic_model_params)
    models_dirs = os.listdir(topic_model_path)
    if len(models_dirs)>1:
        raise Exception("there are multiple saved models delete all but the one you want")
    ctm.load(os.path.join(topic_model_path,models_dirs[0]), epoch=topic_model_params["num_epochs"]-1)
    return ctm

def load_similarities(experiment, experiment_type):
    path_similarities = get_similarities_path(experiment, experiment_type)
    return np.genfromtxt(path_similarities)

def save_similarities(experiment, experiment_type, similarities):
    path_similarities = get_similarities_path(experiment, experiment_type)
    np.savetxt(path_similarities, similarities)

def evaluate_model(experiment, arguments_to_check):
    """
    :param model: contextual topic model to be evaluated

    """
    similarities = load_similarities(experiment, "validation")
    splits = load_splits(experiment, oversample=False)
    df_validation = splits["validation"]
    df_training = splits["training"]
    all_similar_examples = []
    for i in range(0, arguments_to_check):
        i = np.random.randint(0,len(df_validation))
        examples_sorted = sample_similar(i, similarities, df_training, df_training.shape[0])
        queries = [df_validation["text"].iloc[i] for _ in range(0,len(df_training))]
        queries_topic = [df_validation["topic"].iloc[i] for _ in range(0,len(df_training))]
        examples_sorted["query-text"] = queries
        examples_sorted["query-topic"] = queries_topic
        all_similar_examples.append(examples_sorted)

    df_sorted_examples = pd.concat(all_similar_examples)
    df_sorted_examples.to_csv("~/contexutal_topic_model_evaluation.csv", sep="\t", columns=["query-text", "query-topic", "text", "topic"])



def calc_all_similarity(df_train, df_test, model):
    df_all = pd.concat([df_test, df_train])
    preprocessed_all_documents, unpreprocessed_all_corpus, _, _= preprocess_dataset(df_all)
    preprocessed_test_documents, unpreprocessed_test_corpus,_, _= preprocess_dataset(df_test)
    tp = TopicModelDataPreparation("all-mpnet-base-v2")
    tp.fit(text_for_contextual=unpreprocessed_test_corpus, text_for_bow=preprocessed_test_documents)
    dataset = tp.transform(text_for_contextual=unpreprocessed_all_corpus, text_for_bow=preprocessed_all_documents)
    vectors = model.get_doc_topic_distribution(dataset, n_samples=20)
    test_vectors = vectors[:df_test.shape[0]]
    training_vectors = vectors[df_test.shape[0]:]
    similarities = np.zeros(((len(test_vectors)), len(training_vectors)))
    for i, test_vector in enumerate(test_vectors):
        for j, training_vector in enumerate(training_vectors):
            similarities[i,j] = cosine(test_vector, training_vector)
    return similarities

def sample_similar(test_index, similarities, df_training, few_shot_size):
    indices = np.argsort(similarities[test_index, :])
    return df_training.iloc[indices[:few_shot_size]]

def sample_diverse(test_index, similarities, df_training, few_shot_size):
    indices = np.argsort(similarities[test_index, :])
    all_training_size = len(indices)
    step = math.floor(all_training_size/few_shot_size)
    indices_of_indices = range(0,all_training_size,step)
    diverse_indices = indices[indices_of_indices]
    diverse_indices = diverse_indices[:few_shot_size]
    return df_training.iloc[diverse_indices]

