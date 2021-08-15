# Fault Finder by Python(FFPY)
## Description
Implementation of IR-based Fault Localization based on `Where Should the Bugs Be Fixed?` paper. You can visit my [blog](https://drumpt.github.io/category/FFPY/) to see the detailed information.

## Usage
```
python3 main.py --project_dir [PROJECT_DIR] --report_dir [REPORT_DIR] --num_files_to_print [NUM_FILES]
```
- PROJECT_DIR : software project directory which contains files where errors can exist
- REPORT_DIR : xml file which contains bug reports from users and corresponding source code files to fix bugs
- NUM_FILES : number of top-ranked files believed that a fault exists  

For now, it just supports these four cases:
| PROJECT_DIR | REPORT_DIR |
| --- | --- |
| ../data/JodaTime | ../data/JodaTime/JodaTimeBugRepository.xml |
| ../data/SWT/swt-3.1/src | ../data/SWT/SWTBugRepository.xml |
| ../data/ZXing | ../data/ZXing/ZXingBugRepository.xml |
| ../data/Rhino | ../data/Rhino/RhinoBugRepository.xml |

## Experimental Results

| Program | Top 1 | Top 5 | Top 10 | MRR | MAP |
| :---: | :---: | :---: | :---: | :---: | :---: |
| JodaTime | 0.375 | 0.875 | 0.875 | 0.604 | 0.604 |
| SWT | 0.112 | 0.449 | 0.561 | 0.311 | 0.223 |
| ZXing | 0.000 | 0.150 | 0.250 | 0.096 | 0.077 |
| Rhino | 0.094 | 0.344 | 0.406 | 0.236 | 0.147 |

## References
- Jian Zhou, Hongyu Zhang. [Where Should the Bugs Be Fixed?](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6227210) IEEE Internation Conference on Software Engineering, 2012.  
- Shin Yoo. 9. [Fault Localisation](https://coinse.kaist.ac.kr/assets/files/teaching/2020/cs453/cs453slide09.pdf)
