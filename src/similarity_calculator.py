import math

import numpy as np
from prettytable import PrettyTable

class SimilarityCalculator:
    def __init__(self, project_frequency_dict, report_frequency_dict, xml_report, num_files_to_print):
        self.project_frequency_dict = project_frequency_dict
        self.report_frequency_dict = report_frequency_dict
        self.xml_report = xml_report
        self.num_files_to_print = num_files_to_print
        if self.xml_report:
            self.final_score_for_reports = self.get_final_score_for_reports(project_frequency_dict, xml_report)
            self.ranked_documents_for_reports = self.rank_documents_for_reports(self.final_score_for_reports)
        else:
            self.final_score_for_report = self.get_final_score_for_report(project_frequency_dict, report_frequency_dict, xml_report)
            self.ranked_documents_for_report = self.rank_documents_for_report(self.final_score_for_report)
        self.print_result()

    ### Calculate final scores ###

    def get_final_score_for_report(self, project_frequency_dict, report_frequency_dict, xml_report, alpha = 0.25):
        rvsm_score_dict, simi_score_dict, final_score_dict = dict(), dict(), dict()

        if xml_report:
            for source_dir, source_frequency_dict in project_frequency_dict.items(): # bug instance : bug_id, report_frequency_dict, related_sources
                rvsm_score_dict[source_dir] = self.rvsm_score(report_frequency_dict, source_frequency_dict)
                simi_score_dict[source_dir] = 0
                for bug_instance in xml_report: # report_frequency_dict == report_info
                    if bug_instance.report_frequency_dict != report_frequency_dict and source_dir in bug_instance.related_sources:
                        simi_score_dict[source_dir] += self.simi_score(report_frequency_dict, bug_instance.report_frequency_dict) / len(bug_instance.related_sources)

            for soucre_dir, rvsm_score in rvsm_score_dict.items(): # normalize rVSMScore
                rvsm_score_dict[soucre_dir] = self.normalize(rvsm_score, rvsm_score_dict.values())
            for source_dir, simi_score in simi_score_dict.items(): # normalize SimiScore
                simi_score_dict[source_dir] = self.normalize(simi_score, simi_score_dict.values())
            for source_dir in project_frequency_dict.keys():
                final_score_dict[source_dir] = (1 - alpha) * rvsm_score_dict[source_dir] + alpha * simi_score_dict[source_dir]
            return final_score_dict
        else: # In case where there is no previous bug information
            for source_dir, source_frequency_dict in project_frequency_dict.items():
                rvsm_score_dict[source_dir] = self.rvsm_score(report_frequency_dict, source_frequency_dict)

            for soucre_dir, rvsm_score in rvsm_score_dict.items(): # normalize rVSMScore
                rvsm_score_dict[soucre_dir] = self.normalize(rvsm_score, rvsm_score_dict.values())

            for source_dir in project_frequency_dict.keys():
                final_score_dict[source_dir] = rvsm_score_dict[source_dir]
            return final_score_dict

    def get_final_score_for_reports(self, project_frequency_dict, xml_report):
        final_score_dict_for_reports = dict()
        for bug_instance in xml_report:
            final_score_dict_for_reports[bug_instance.bug_id] = self.get_final_score_for_report(project_frequency_dict, bug_instance.report_frequency_dict, xml_report, alpha = 0.25)
        return final_score_dict_for_reports

    ### Calculate rVSMScore, SimiScore ###

    def rvsm_score(self, query, document):
        if self.norm(query) * self.norm(document) == 0:
            return 0
        return self.document_length(document) * self.cos(query, document) / (self.norm(query) * self.norm(document))

    def simi_score(self, report_frequency_dict, similar_report_frequency_dict):
        if self.norm(report_frequency_dict) * self.norm(similar_report_frequency_dict) == 0:
            return 0
        return self.cos(report_frequency_dict, similar_report_frequency_dict) / (self.norm(report_frequency_dict) * self.norm(similar_report_frequency_dict))

    ### Functions needed to calculate rVSMScore, SimiScore ###

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
            return x
        return (x - min(x_list)) / (max(x_list) - min(x_list))

    ### Sort source codes based on their scores ###

    def rank_documents_for_report(self, final_score_for_report):
        return sorted(final_score_for_report.items(), key = lambda x : x[1], reverse = True)

    def rank_documents_for_reports(self, final_score_for_reports):
        ranked_documents_for_reports = dict()
        for bug_id, final_score_for_report in final_score_for_reports.items():
            ranked_documents_for_reports[bug_id] = sorted(final_score_for_report.items(), key = lambda x : x[1], reverse = True)
        return ranked_documents_for_reports

    ### Evaluation metrics ###

    def top_n_rank(self, n):
        ranked_bug_files = 0
        for bug_id, ranked_document_for_report in self.ranked_documents_for_reports.items():
            for bug_instance in self.xml_report:
                if bug_instance.bug_id == bug_id and set([final_score_for_report[0] for final_score_for_report in ranked_document_for_report][: n]) & set(bug_instance.related_sources) != set():
                    ranked_bug_files += 1
        return ranked_bug_files / len(self.xml_report)

    def mean_reciprocal_rank(self):
        reciprocal_rank = 0
        for bug_instance in self.xml_report:
            for i, final_score_for_report in enumerate(self.ranked_documents_for_reports[bug_instance.bug_id]):
                if final_score_for_report[0] in bug_instance.related_sources:
                    reciprocal_rank += 1 / (i + 1)
        return reciprocal_rank / len(self.xml_report)

    def mean_average_precision(self):
        total_average_precision = 0
        for bug_instance in self.xml_report:
            average_precision = 0
            for i, final_score_for_report in enumerate(self.ranked_documents_for_reports[bug_instance.bug_id]):
                if final_score_for_report[0] in bug_instance.related_sources:
                    precision = len(set(list(zip(*self.ranked_documents_for_reports[bug_instance.bug_id]))[0][: i + 1]) & set(bug_instance.related_sources)) / (i + 1)
                    average_precision += precision / len(bug_instance.related_sources)
            total_average_precision += average_precision
        return total_average_precision / len(self.xml_report)

    ### Print result ###

    def print_result(self):
        if self.xml_report:
            table = PrettyTable()
            table.field_names = ['Top 1', 'Top 5', 'Top 10', 'MRR', 'MAP']
            table.align["Top 1"] = "c"
            table.align["Top 5"] = "c"
            table.align["Top 10"] = "c"
            table.align["MRR"] = "c"
            table.align["MAP"] = "c"

            row = ["%.3f" % self.top_n_rank(n = 1), "%.3f" % self.top_n_rank(n = 5), "%.3f" % self.top_n_rank(n = 10), "%.3f" % self.mean_reciprocal_rank(), "%.3f" % self.mean_average_precision()]
            table.add_row(row)
            print(table)
        else:
            table = PrettyTable()
            table.field_names = ['ranking', 'source file', 'score']
            table.align["ranking"] = "c"
            table.align['source file'] = "l"
            table.align['score'] = "r"

            for i, final_score_for_report in enumerate(self.ranked_documents_for_report):
                if i >= self.num_files_to_print:
                    break
                row = [i + 1, final_score_for_report[0], "%.3f" % final_score_for_report[1]]
                table.add_row(row)
            print(table)