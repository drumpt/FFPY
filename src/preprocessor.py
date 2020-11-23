import os
import string
import re

import nltk

def report_to_frequency(report_dir):
    f = open(report_dir, "r")
    words = tokenization(f.read())
    words = remove_punctuation(words)
    words = case_normalization(words)
    words = stop_word_filtering(words, report_dir, False)
    words = stemming(words)

    keywords = sorted(set(words))
    frequency = [words.count(word) for word in keywords]
    return keywords, frequency

def source_to_frequency(source_dir, keywords):
    f = open(source_dir, "r")
    words = tokenization(f.read())
    words = remove_punctuation(words)
    words = identifier_normalization(words)
    words = case_normalization(words)
    words = stop_word_filtering(words, source_dir, True)
    words = stemming(words)

    frequency = [words.count(word) for word in keywords]
    return frequency

def tokenization(file):
    return nltk.tokenize.word_tokenize(file)

def remove_punctuation(words):
    return [word for word in words if not word in string.punctuation and not word[0].isdigit()]

def identifier_normalization(words):
    normalized_words = []
    for word in words:
        if snake_case_breakdown(word)[0] != word:
            normalized_words.extend(snake_case_breakdown(word))
        elif word.isalnum() and camel_case_breakdown(word)[0] != word:
            normalized_words.extend(camel_case_breakdown(word))
        else:
            normalized_words.append(word)
    return normalized_words

def case_normalization(words):
    return [word.lower() for word in words]

def stop_word_filtering(words, file_dir, is_source):
    stop_words = nltk.corpus.stopwords.words("english")

    if is_source: # include reserved keywords for programming language
        reserved_keywords = []
        abb_to_fullname = {"c" : "C", "cs" : "C#", "cpp" : "C++", "go" : "Go", 'hs' : "Haskell", 'lhs' : "Haskell", \
                        "java" : "Java", "js" : "JavaScript", "m" : "Objective-C", "mm" : "Objective-C", "C" : "Objective-C", \
                        "py" : "Python", "r" : "R", "sh" : "Shell", "swift" : "Swift"}
        extension = file_dir.split(".")[-1]
        target_file = ""
        for file in os.listdir("../res"):
            if abb_to_fullname.get(extension) and file.startswith(abb_to_fullname[extension]) and file.endswith("ords.md"):
                target_file = os.path.join("../res", file)

        if target_file:
            f = open(target_file, "r")
            lines = f.readlines()
            for line in lines:
                if line.rstrip().startswith("  -"):
                    reserved_keyword = line.split("-")[1].strip().lower()
                    reserved_keywords.append(reserved_keyword)
        stop_words += reserved_keywords
        # print(stop_words)
    return [word for word in words if not word in stop_words]

def stemming(words):
    snowball = nltk.stem.SnowballStemmer("english")
    return [snowball.stem(word) for word in words]

def snake_case_breakdown(identifier):
    return identifier.split("_")

def camel_case_breakdown(identifier):
    idx = list(map(str.isupper, identifier))
    l = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:  # "Ul"
            l.append(i)
        elif not x and y:  # "lU"
            l.append(i+1)
    l.append(len(identifier))
    return [identifier[x:y] for x, y in zip(l, l[1:]) if x < y]