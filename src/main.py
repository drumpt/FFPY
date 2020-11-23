import os
import argparse

import preprocessor
import similarity_calculator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_dir", type = str, required = True)
    parser.add_argument("--report_dir", type = str, required = True)
    args = parser.parse_args()

    project_dir = args.project_dir
    report_dir = args.report_dir

    keywords, report_frequency = preprocessor.report_to_frequency(report_dir)
    frequencies_for_sources = dict()
    for root, _, files in os.walk(project_dir):
        for file in files:
            try:
                source_dir = os.path.join(root, file)
                frequencies_for_sources[source_dir] = preprocessor.source_to_frequency(source_dir, keywords)
            except Exception as e:
                continue

    print(keywords)

    frequencies_for_sources_and_report = {**frequencies_for_sources, report_dir : report_frequency}

    vector_for_sources_and_report = dict()
    for source_dir in frequencies_for_sources_and_report.keys():
       vector_for_sources_and_report[source_dir] = similarity_calculator.frequency_to_vector(keywords, frequencies_for_sources_and_report[source_dir], frequencies_for_sources_and_report.values())

    ranked_documents = similarity_calculator.rank_documents(vector_for_sources_and_report, vector_for_sources_and_report[source_dir])
    print(*ranked_documents[:20], sep = "\n")

if __name__ == "__main__":
    main()