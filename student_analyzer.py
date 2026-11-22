"""
Student Academic Performance Analyzer
-------------------------------------
Run:
    pip install numpy pandas matplotlib
    python student_analyzer.py
    python student_analyzer.py students.csv

Expected CSV columns:
    Student_ID, Name, Math, Science, English, Computer, History

The application:
- Loads marks from CSV
- Checks missing values and invalid marks
- Calculates average, percentage, grade, and pass/fail status
- Prints class-level insights
- Saves cleaned results and charts in an output/ folder
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SUBJECTS = ["Math", "Science", "English", "Computer", "History"]
PASS_MARK = 35


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Read the CSV and validate its basic structure."""
    df = pd.read_csv(csv_path)

    required = ["Student_ID", "Name"] + SUBJECTS
    missing_columns = [col for col in required if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for subject in SUBJECTS:
        df[subject] = pd.to_numeric(df[subject], errors="coerce")

    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Display a concise data-quality report."""
    print("\n========== DATA QUALITY REPORT ==========")
    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    print("\nMissing values by column:")
    print(df.isna().sum())

    print("\nDuplicate student IDs:", df["Student_ID"].duplicated().sum())

    invalid_counts = {}
    for subject in SUBJECTS:
        invalid_counts[subject] = ((df[subject] < 0) | (df[subject] > 100)).sum()
    print("\nMarks outside 0-100:")
    print(pd.Series(invalid_counts))


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace missing subject marks with that subject's class median.
    Keep original rows and report the replacement through a warning.
    Invalid marks outside 0-100 are treated as missing before imputation.
    """
    result = df.copy()

    for subject in SUBJECTS:
        invalid = (result[subject] < 0) | (result[subject] > 100)
        result.loc[invalid, subject] = np.nan

        missing_count = result[subject].isna().sum()
        if missing_count:
            median_value = result[subject].median()
            if pd.isna(median_value):
                raise ValueError(
                    f"Cannot fill {subject}: all values are missing or invalid."
                )
            print(
                f"Filling {missing_count} missing/invalid {subject} mark(s) "
                f"with class median {median_value:.1f}."
            )
            result[subject] = result[subject].fillna(median_value)

    return result


def assign_grade(percentage: float) -> str:
    """Convert percentage into a simple grade band."""
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    if percentage >= 35:
        return "E"
    return "F"


def calculate_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Add total, average, percentage, grade, and pass/fail columns."""
    result = df.copy()

    result["Total"] = result[SUBJECTS].sum(axis=1)
    result["Average"] = result[SUBJECTS].mean(axis=1).round(2)
    result["Percentage"] = (
        result["Total"] / (len(SUBJECTS) * 100) * 100
    ).round(2)
    result["Grade"] = result["Percentage"].apply(assign_grade)

    # A student passes only if they score at least PASS_MARK in every subject.
    result["Status"] = np.where(
        (result[SUBJECTS] >= PASS_MARK).all(axis=1), "Pass", "Fail"
    )
    return result


def print_insights(results: pd.DataFrame) -> None:
    """Print student-level and class-level findings."""
    print("\n========== STUDENT RESULTS ==========")
    print(
        results[
            ["Student_ID", "Name", "Total", "Average", "Percentage", "Grade", "Status"]
        ].to_string(index=False)
    )

    subject_averages = results[SUBJECTS].mean().round(2)
    top_student = results.loc[results["Percentage"].idxmax()]
    low_student = results.loc[results["Percentage"].idxmin()]
    pass_count = (results["Status"] == "Pass").sum()
    fail_count = (results["Status"] == "Fail").sum()

    print("\n========== CLASS INSIGHTS ==========")
    print("Average marks by subject:")
    print(subject_averages)
    print(f"\nClass average percentage: {results['Percentage'].mean():.2f}%")
    print(f"Pass count: {pass_count}")
    print(f"Fail count: {fail_count}")
    print(
        f"Pass percentage: {pass_count / len(results) * 100:.1f}%"
        if len(results) else "Pass percentage: N/A"
    )
    print(
        f"Top performer: {top_student['Name']} "
        f"({top_student['Percentage']:.2f}%)"
    )
    print(
        f"Needs support: {low_student['Name']} "
        f"({low_student['Percentage']:.2f}%)"
    )
    print(f"Strongest subject: {subject_averages.idxmax()}")
    print(f"Subject needing attention: {subject_averages.idxmin()}")


def create_charts(results: pd.DataFrame, output_dir: Path) -> None:
    """Create and save three basic Matplotlib charts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Average marks in each subject
    plt.figure(figsize=(8, 5))
    results[SUBJECTS].mean().plot(kind="bar")
    plt.title("Average Marks by Subject")
    plt.xlabel("Subject")
    plt.ylabel("Average Marks (out of 100)")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(output_dir / "subject_averages.png", dpi=150)
    plt.close()

    # 2. Distribution of student percentages
    plt.figure(figsize=(8, 5))
    plt.hist(results["Percentage"], bins=8, edgecolor="black")
    plt.title("Distribution of Student Percentages")
    plt.xlabel("Percentage")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.savefig(output_dir / "percentage_distribution.png", dpi=150)
    plt.close()

    # 3. Grade counts
    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = results["Grade"].value_counts().reindex(
        grade_order, fill_value=0
    )
    plt.figure(figsize=(8, 5))
    grade_counts.plot(kind="bar")
    plt.title("Number of Students in Each Grade")
    plt.xlabel("Grade")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.savefig(output_dir / "grade_distribution.png", dpi=150)
    plt.close()

    print(f"\nCharts saved in: {output_dir.resolve()}")


def main() -> None:
    default_csv = Path(__file__).with_name("students.csv")
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_csv

    try:
        print(f"Loading dataset: {csv_path}")
        raw_df = load_dataset(str(csv_path))
        inspect_data(raw_df)

        cleaned_df = clean_data(raw_df)
        results = calculate_performance(cleaned_df)
        print_insights(results)

        output_dir = Path(__file__).with_name("output")
        results.to_csv(output_dir / "student_performance_results.csv", index=False)
        create_charts(results, output_dir)

        print(
            f"Results CSV saved to: "
            f"{(output_dir / 'student_performance_results.csv').resolve()}"
        )

    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_path}")
        print("Place students.csv beside this script or pass a CSV path.")
    except Exception as error:
        print(f"Could not complete analysis: {error}")


if __name__ == "__main__":
    main()
