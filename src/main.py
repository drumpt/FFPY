import os
import argparse

import preprocessor
import similarity_calculator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_dir", type = str, required = True)
    parser.add_argument("--report_dir", type = str, required = True)
    parser.add_argument("--num_files_to_print", type = int, required = False, default = 20)
    args = parser.parse_args()

    project_dir = args.project_dir
    report_dir = args.report_dir
    num_files_to_print = args.num_files_to_print

    project_dir = "../data/ZXing"
    report_dir = "../data/ZXing/ZXingBugRepository.xml"

    project_report_info = preprocessor.Preprocessor(project_dir, report_dir)
    similarity_info = similarity_calculator.SimilarityCalculator(
        project_report_info.project_frequency_dict,
        project_report_info.report_frequency_dict,
        project_report_info.xml_report,
        num_files_to_print
    )

    project_dir = "../data/Rhino"
    report_dir = "../data/Rhino/RhinoBugRepository.xml"

    project_report_info = preprocessor.Preprocessor(project_dir, report_dir)
    similarity_info = similarity_calculator.SimilarityCalculator(
        project_report_info.project_frequency_dict,
        project_report_info.report_frequency_dict,
        project_report_info.xml_report,
        num_files_to_print
    )

    project_dir = "../data/JodaTime/"
    report_dir = "../data/JodaTime/JodaTimeBugRepository.xml"

    project_report_info = preprocessor.Preprocessor(project_dir, report_dir)
    similarity_info = similarity_calculator.SimilarityCalculator(
        project_report_info.project_frequency_dict,
        project_report_info.report_frequency_dict,
        project_report_info.xml_report,
        num_files_to_print
    )

if __name__ == "__main__":
    main()