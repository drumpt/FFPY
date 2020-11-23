import math

import numpy as np

def frequency_to_vector(keywords, frequency_for_source, frequencies_for_sources_and_report):
    vector = np.zeros(len(keywords))
    for i in range(len(keywords)):
        vector[i] = tfidf(i, frequency_for_source, frequencies_for_sources_and_report)
    return vector

def tfidf(term_index, frequency_for_source, frequencies_for_sources_and_report):
    return tf(term_index, frequency_for_source) * idf(term_index, frequencies_for_sources_and_report)

def tf(term_index, frequency_for_source):
    return math.log(frequency_for_source[term_index])

def idf(term_index, frequencies_for_sources_and_report):
    return math.log(len(frequencies_for_sources_and_report) / len([frequency_for_source for frequency_for_source in frequencies_for_sources_and_report if frequency_for_source[term_index] > 0]))

def rank_documents(vector_for_sources, vector_for_report): # vector_for_sources : dict, vector_for_report : vector
    similarities_for_sources = dict()
    for source, vector in vector_for_sources.items():
        similarities_for_sources[source] = cosine_distance(vector, vector_for_report)
    return sorted(similarities_for_sources.items(), key = lambda x : x[1], reverse = True)

def cosine_distance(v1, v2):
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0
    else:
        return np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1)