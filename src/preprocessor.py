import os
import string
import re

import nltk
from xml.etree.ElementTree import parse

import constants as c

class Bug():
    def __init__(self, bug_id = None, report_frequency_dict = dict(), source_frequency_dict_dict = dict()):
        self.bug_id = bug_id # distinct bug id
        self.report_frequency_dict = report_frequency_dict # {word : word_count}
        self.source_frequency_dict_dict = source_frequency_dict_dict # {{source_dir_1 : {word : word_count}}, {source_dir_2 : {word : word_count}}
    
    def __str__(self):
        bug_string = "\n\n"
        bug_string += f"bug id : {self.bug_id}\n"
        bug_string += f"report frequency dict : {self.report_frequency_dict}\n"
        for k, v in self.source_frequency_dict_dict.items():
            bug_string += f"{k} : {v}\n\n"
        return bug_string

    def set_id(self, bug_id):
        self.bug_id = bug_id

    def set_report_frequency_dict(self, report_frequency_dict):
        self.report_frequency_dict = report_frequency_dict
    
    def add_source_frequency_dict(self, source_dir, source_frequency_dict):
        if source_frequency_dict != dict():
            self.source_frequency_dict_dict[source_dir] = source_frequency_dict

class Preprocessor():
    def __init__(self, project_dir, report_dir):
        self.project_dir = project_dir
        self.report_dir = report_dir
        self.is_xml_report = report_dir.split(".")[-1].lower() == "xml"
        self.project_frequency_dict = dict()
        for source_dir in self.get_sources_from_project_dir(project_dir):
            if self.source_to_frequency_dict(source_dir) != dict():
                self.project_frequency_dict[source_dir] = self.source_to_frequency_dict(source_dir)
        if self.is_xml_report:
            self.report_frequency_dict = self.parse_xml_report(report_dir)
        else:
            self.report_frequency_dict = {report_dir : self.report_to_frequency_dict(report_dir)}

    def get_real_file_dir(self, project_dir, file_dir):
        if os.path.relpath(project_dir) == os.path.relpath("../data/ZXing"):
            file_dir = os.path.join("ZXing-1.6/android/src", file_dir)
        elif os.path.relpath(project_dir) == os.path.relpath("../data/SWT"):
            file_dir = os.path.join("swt-3.1/src", file_dir)
        elif os.path.relpath(project_dir) == os.path.relpath("../data/Rhino"):
            file_dir = file_dir.replace("mozilla/js/", "")
        elif os.path.relpath(project_dir) == os.path.relpath("../data/JodaTime"):
            file_dir = file_dir
        else: # Eclipse, AspectJ, ...
            file_dir = file_dir
        print(os.path.join(project_dir, file_dir))
        return os.path.join(project_dir, file_dir)

    def get_sources_from_project_dir(self, project_dir):
        sources = []
        for root, _, files in os.walk(project_dir):
            for file in files:
                try:
                    sources.append(os.path.join(root, file))
                except Exception as e:
                    pass
        return sources

    def parse_xml_report(self, report_dir):
        report_info = []
        for bug in parse(report_dir).findall("bug"):
            bug_instance = Bug(bug_id = bug.attrib["id"])
            try: # first xml case
                bug_instance.set_report_frequency_dict(self.report_to_frequency_dict(bug.find("bugreport").text, is_string = True))
                try:
                    for file in bug.find("fixedfiles").findall("file"):
                        if len(os.path.splitext(file.attrib["name"])) == 2:
                            file.text = os.path.splitext(file.attrib["name"])[0].replace(".", "/") + os.path.splitext(file.attrib["name"])[1]
                        source_dir = self.get_real_file_dir(self.project_dir, file.attrib["name"])
                        bug_instance.add_source_frequency_dict(source_dir, self.source_to_frequency_dict(source_dir))
                except Exception as e:
                    print(e)
                    # pass
                try:
                    for file in bug.find("fixedFiles").findall("file"):
                        if len(os.path.splitext(file.attrib["name"])) == 2:
                            file.text = os.path.splitext(file.attrib["name"])[0].replace(".", "/") + os.path.splitext(file.attrib["name"])[1]
                        source_dir = self.get_real_file_dir(self.project_dir, file.attrib["name"])
                        bug_instance.add_source_frequency_dict(source_dir, self.source_to_frequency_dict(source_dir))
                except Exception as e:
                    pass
            except Exception as e:
                pass
            try: # second xml case
                bug_instance.set_report_frequency_dict(self.report_to_frequency_dict(bug.find("buginformation").find("description").text, is_string = True))
                for file in bug.find("fixedFiles").findall("file"):
                    if len(os.path.splitext(file.text)) == 2:
                        file.text = os.path.splitext(file.text)[0].replace(".", "/") + os.path.splitext(file.text)[1]
                    source_dir = self.get_real_file_dir(self.project_dir, file.text)
                    bug_instance.add_source_frequency_dict(source_dir, self.source_to_frequency_dict(source_dir))
            except Exception as e:
                print(e)
                # pass
            report_info.append(bug_instance)
            print(bug_instance)
        return report_info

    def source_to_frequency_dict(self, source):
        try:
            f = open(source, "r")
            words = self.tokenization(f.read())
            words = self.remove_punctuation(words)
            words = self.identifier_normalization(words)
            words = self.case_normalization(words)
            words = self.stop_word_filtering(words, source, is_source = True)
            words = self.stemming(words)

            keywords = sorted(set(words))
            frequency_dict = {word : words.count(word) for word in keywords}
            return frequency_dict
        except Exception as e:
            return dict()

    def report_to_frequency_dict(self, report, is_string = False):
        if is_string:
            words = self.tokenization(report)
            words = self.remove_punctuation(words)
            words = self.case_normalization(words)
            words = self.stop_word_filtering(words, "", is_source = False)
            words = self.stemming(words)
        else:
            f = open(report, "r")
            words = self.tokenization(f.read())
            words = self.remove_punctuation(words)
            words = self.case_normalization(words)
            words = self.stop_word_filtering(words, report, is_source = False)
            words = self.stemming(words)

        keywords = sorted(set(words))
        frequency_dict = {word : words.count(word) for word in keywords}
        return frequency_dict

    def tokenization(self, file):
        return nltk.tokenize.word_tokenize(file)

    def remove_punctuation(self, words):
        return [word for word in words if not word in string.punctuation and not word[0].isdigit()]

    def identifier_normalization(self, words):
        normalized_words = []
        for word in words:
            if self.snake_case_breakdown(word)[0] != word:
                normalized_words.extend(self.snake_case_breakdown(word))
            elif word.isalnum() and self.camel_case_breakdown(word)[0] != word:
                normalized_words.extend(self.camel_case_breakdown(word))
            else:
                normalized_words.append(word)
        return normalized_words

    def case_normalization(self, words):
        return [word.lower() for word in words]

    def stop_word_filtering(self, words, file_dir, is_source):
        stop_words = nltk.corpus.stopwords.words("english")

        if is_source: # include reserved keywords for programming language
            reserved_keywords = []
            extension = file_dir.split(".")[-1]
            target_file = ""
            for file in os.listdir(c.RESERVED_WORDS):
                if c.ABB_TO_FULLNAME.get(extension) and file.startswith(c.ABB_TO_FULLNAME[extension]) and file.endswith("ords.md"):
                    target_file = os.path.join(c.RESERVED_WORDS, file)

            if target_file:
                f = open(target_file, "r")
                lines = f.readlines()
                for line in lines:
                    if line.rstrip().startswith("  -"):
                        reserved_keyword = line.split("-")[1].strip().lower()
                        reserved_keywords.append(reserved_keyword)
            stop_words += reserved_keywords
        return [word for word in words if not word in stop_words]

    def stemming(self, words):
        snowball = nltk.stem.SnowballStemmer("english")
        return [snowball.stem(word) for word in words]

    def snake_case_breakdown(self, identifier):
        return identifier.split("_")

    def camel_case_breakdown(self, identifier):
        idx = list(map(str.isupper, identifier))
        l = [0]
        for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
            if x and not y: # "Ul"
                l.append(i)
            elif not x and y: # "lU"
                l.append(i+1)
        l.append(len(identifier))
        return [identifier[x:y] for x, y in zip(l, l[1:]) if x < y]