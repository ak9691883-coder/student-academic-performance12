# Student Academic Performance Analyzer

A beginner-friendly Python project using NumPy, Pandas, and Matplotlib.

## Setup
```bash
pip install numpy pandas matplotlib
```

## Run
Keep `student_analyzer.py` and `students.csv` in the same folder:
```bash
python student_analyzer.py
```
Or provide your own CSV:
```bash
python student_analyzer.py path/to/your_students.csv
```

## Required CSV columns
`Student_ID`, `Name`, `Math`, `Science`, `English`, `Computer`, `History`

Marks should be between 0 and 100. Missing or out-of-range marks are filled with the subject median for this demonstration. For real academic reporting, verify missing marks against the source rather than assuming they represent average performance.

## Grade criteria
| Percentage | Grade |
|---|---|
| 90-100 | A+ |
| 80-89.99 | A |
| 70-79.99 | B |
| 60-69.99 | C |
| 50-59.99 | D |
| 35-49.99 | E |
| Below 35 | F |

A student passes only when they score at least 35 in every subject.

## Output
The program creates an `output/` folder with the analyzed CSV and three charts:
- `student_performance_results.csv`
- `subject_averages.png`
- `percentage_distribution.png`
- `grade_distribution.png`

## Concepts
- NumPy: `np.where()` for pass/fail classification
- Pandas: CSV loading, missing-value checks, median imputation, aggregation, export
- Matplotlib: bar chart and histograms
