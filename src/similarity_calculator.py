import math

import numpy as np

class SimilarityCalculator():
    def __init__(self, project_frequency_dict, report_frequency_dict, is_xml_report, num_files_to_print):
        self.project_frequency_dict = project_frequency_dict
        self.report_frequency_dict = report_frequency_dict
        self.is_xml_report = is_xml_report
        self.num_files_to_print = num_files_to_print
        if is_xml_report:
            self.final_score_for_reports = self.get_final_score_for_reports(project_frequency_dict, report_frequency_dict)
            self.ranked_documents_for_reports = self.rank_documents_for_reports(self.final_score_for_reports)
            print(self.ranked_documents_for_reports)
        else:
            self.final_score_for_report = self.get_final_score_for_report(project_frequency_dict, report_frequency_dict)
            self.ranked_documents_for_report = self.rank_documents_for_report(self.final_score_for_report)
            print(self.ranked_documents_for_report)

    def get_final_score_for_report(self, project_frequency_dict, report_frequency_dict, xml_report = None, alpha = 0.25):
        rvsm_score_dict = dict()
        simi_score_dict = dict()
        final_score_dict = dict()

        if xml_report:
            for source_dir, source_frequency_dict in project_frequency_dict.items(): # bug instance : bug_id, report_frequency_dict, source_frequency_dict_dict
                rvsm_score_dict[source_dir] = self.rvsm_score(report_frequency_dict, source_frequency_dict)
                simi_score_dict[source_dir] = 0
                for bug_instance in xml_report: # report_frequency_dict == report_info
                    if bug_instance.report_frequency_dict != report_frequency_dict and source_dir in bug_instance.source_frequency_dict_dict.keys():
                        simi_score_dict[source_dir] += self.simi_score(report_frequency_dict, bug_instance.report_frequency_dict) / len(bug_instance.source_frequency_dict_dict)

            for soucre_dir, rvsm_score in rvsm_score_dict.items(): # normalize rVSMScore
                rvsm_score_dict[soucre_dir] = self.normalize(rvsm_score, rvsm_score_dict.values())
            for source_dir, simi_score in simi_score_dict.items(): # normalize SimiScore
                simi_score_dict[source_dir] = self.normalize(simi_score, simi_score_dict.values())
            for source_dir in project_frequency_dict.keys():
                final_score_dict[source_dir] = (1 - alpha) * rvsm_score_dict[source_dir] + alpha * simi_score_dict[source_dir]
            return final_score_dict
        else: # In case where there is no previous bug information
            for source_dir, source_frequency_dict in project_frequency_dict.items(): # bug instance : bug_id, report_frequency_dict, source_frequency_dict_dict
                rvsm_score_dict[source_dir] = self.rvsm_score(report_frequency_dict, source_frequency_dict)

            for soucre_dir, rvsm_score in rvsm_score_dict.items(): # normalize rVSMScore
                rvsm_score_dict[soucre_dir] = self.normalize(rvsm_score, rvsm_score_dict.values())

            for source_dir in project_frequency_dict.keys():
                final_score_dict[source_dir] = rvsm_score_dict[source_dir]
            return final_score_dict

    def get_final_score_for_reports(self, project_frequency_dict, report_frequency_dict):
        final_score_dict_for_reports = dict()
        for bug_instance in report_frequency_dict:
            final_score_dict_for_reports[bug_instance.bug_id] = self.get_final_score_for_report(project_frequency_dict, bug_instance.report_frequency_dict, report_frequency_dict, alpha = 0.25)
        return final_score_dict_for_reports

    def rvsm_score(self, query, document):
        return self.document_length(document) * self.cos(query, document) / (self.norm(query) * self.norm(document))

    def simi_score(self, report_frequency_dict, similar_report_frequency_dict):
        return self.cos(report_frequency_dict, similar_report_frequency_dict) / (self.norm(report_frequency_dict) * self.norm(similar_report_frequency_dict))

    def tfidf(self, term, document):
        return self.tf(term, document) * self.idf(term)

    def tf(self, term, document):
        if document[term] == 0:
            return 0
        return math.log(document[term]) + 1

    def idf(self, term):
        n_t = 0
        for document in self.project_frequency_dict.values(): # {word_1 : word_1_count, word_2 : word_2_count, ...}
            if term in document.keys():
                n_t += 1
        if n_t == 0:
            return 0
        return math.log(len(self.project_frequency_dict) / n_t)

    def document_length(self, document):
        return 1 / (1 + math.exp(- len(document)))

    def cos(self, query, document):
        cos = 0
        terms = set(query.keys()) & set(document.keys())
        for term in terms:
            cos += self.tfidf(term, query) * self.tfidf(term, document)
        return cos

    def norm(self, document):
        norm = 0
        for term in document.keys():
            norm += self.tfidf(term, document) ** 2
        norm = math.sqrt(norm)
        return norm

    def normalize(self, x, x_list):
        if max(x_list) == min(x_list):
            print("Abnormal case")
            return x
        return (x - min(x_list)) / (max(x_list) - min(x_list))

    def rank_documents_for_report(self, final_score_for_report):
        return sorted(final_score_for_report.items(), key = lambda x : x[1], reverse = True)

    def rank_documents_for_reports(self, final_score_for_reports):
        ranked_documents_for_reports = dict()
        for bug_id, final_score_for_report in final_score_for_reports.items():
            ranked_documents_for_reports[bug_id] = sorted(final_score_for_report.items, keys = lambda x : x[1], reverse = True)

    def make_report(self):
        if 
        pass

    def top_n_rank(self, n):
        pass

    def mean_reciprocal_rank(self):
        pass

    def mean_average_precision(self):
        pass