import pandas as pd
import re
import os

def analyze_llm_stats(file_path):
    """
    Analyzes the LLM statistics CSV file and computes:
    - Syntax Validation Rate (SVR): Percentage of properties that were valid on the first attempt.
    - Average Iteration Count (IC): Average number of iterations taken before achieving a valid property.
    - Execution Success Rate (ESR): Percentage of properties that successfully executed in the monitoring tool.

    The results are saved to a CSV file, including the model name in the filename.

    Args:
    file_path (str): Path to the input CSV file containing LLM statistics.

    Returns:
    str: Path to the saved results file.
    """
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Extract model name from the file path
    m = re.search(r'/([^/]+)/[^/]+$', file_path)
    model_name = m.group(1) if m else "unknown_model"

    # Extract number of examples from the 'prompt_file' column
    def extract_examples(prompt_file):
        match = re.search(r'_(\d+)\.txt$', prompt_file)
        return int(match.group(1)) if match else None

    df["num_examples"] = df["prompt_file"].apply(extract_examples)

    # Compute Syntax Validation Rate (SVR)
    def compute_svr(sub_df):
        total = len(sub_df)
        valid_first_try = len(sub_df[(sub_df["iterations"] == 1) & (sub_df["valid_xml"] == True)])  # Count valid first-attempt cases
        return (valid_first_try / total) * 100 if total > 0 else 0

    # Compute Average Iteration Count (IC) (only for valid properties)
    def compute_ic(sub_df):
        valid_cases = sub_df[sub_df["valid_xml"] == True]  # Filter only successfully generated properties
        return valid_cases["iterations"].mean() if len(valid_cases) > 0 else 0  # Compute mean iterations

    # Compute Total Validation Rate (TVR)
    def compute_tvr(sub_df):
        total = len(sub_df)
        total_valid = len(sub_df[sub_df["valid_xml"] == True])
        return (total_valid / total) * 100 if total > 0 else 0

    # Aggregate results by Model and Number of Examples
    results = df.groupby(["model_name", "num_examples"]).agg(
        SVR=("iterations", lambda x: compute_svr(df.loc[x.index])),
        Avg_Iterations=("iterations", lambda x: compute_ic(df.loc[x.index])),
        TVR=("iterations", lambda x: compute_tvr(df.loc[x.index])),
    ).reset_index()

    # Define the output file name with the model name
    output_file = f"llm_evaluation_results_{model_name}.csv"

    # Save results to CSV
    if os.path.exists(output_file):
        results.to_csv(output_file, mode='a', header=False, index=False)
    else:
        results.to_csv(output_file, index=False)

# Usage:
analyze_llm_stats("5G_results/gemma3:12b/stats_gemma3:12b.csv")
analyze_llm_stats("5G_results/llama3.1:8b/stats_llama3.1:8b.csv")
analyze_llm_stats("5G_results/llama3.2:3b/stats_llama3.2:3b.csv")
analyze_llm_stats("5G_results/mistral-nemo:12b/stats_mistral-nemo:12b.csv")
analyze_llm_stats("5G_results/deepseek-coder:6.7b/stats_deepseek-coder:6.7b.csv")