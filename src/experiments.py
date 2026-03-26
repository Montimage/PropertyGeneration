"""
Experiments module per model
"""
from llm_interaction import initialize_llm, generate_property
import os

LLM_MODELS = {
    "gemma3:12b": {"provider": "ollama", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
    "llama3.1:8b": {"provider": "ollama", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
    "llama3.2:3b": {"provider": "ollama", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
    "mistral-nemo:12b": {"provider": "ollama", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
    "deepseek-coder:6.7b": {"provider": "ollama", "temperature": 0.3, "top_p": 0.8, "max_tokens": 2048},
    "gpt-4-turbo": {"provider": "openai", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
    "gpt-3.5-turbo": {"provider": "openai", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024},
    "gpt-oss": {"provider": "ollama", "temperature": 0.7, "top_p": 0.9, "max_tokens": 1024}, # 20b parameters
}

PROMPTS_FOLDER = "5G_prompts/"
RESULTS_FOLDER = "5G_results/"

def run_experiment(model_name, prompts_folder=PROMPTS_FOLDER):

    if model_name not in LLM_MODELS:
        raise ValueError(f"Model {model_name} not found in configuration.")
    
    model = initialize_llm(model_name, LLM_MODELS[model_name])

    # iterate through prompts in the folder 
    for prompt_file in os.listdir(prompts_folder):
        if prompt_file.endswith(".txt"):
            with open(os.path.join(prompts_folder, prompt_file), "r") as file:
                prompt_text = file.read()

                prompt_file_name_without_ext = os.path.splitext(prompt_file)[0]
                print(f"Running experiment for model {model_name} with prompt {prompt_file_name_without_ext}")
                OUTPUTDIR = f"{RESULTS_FOLDER}{model_name}/{prompt_file_name_without_ext}/"
                os.makedirs(OUTPUTDIR, exist_ok=True)

                STATS_DIR = f"{RESULTS_FOLDER}{model_name}/stats_{model_name}.csv"

                stats_config = {
                    "stats_file_path": STATS_DIR,
                    "model_name": model_name,
                    "prompt_file": prompt_file
                }
                generate_property(model, prompt_text, max_iterations=5, store_iterations=True, output_dir=OUTPUTDIR, stats=stats_config)

if __name__ == "__main__":
    model_name = "gemma3:12b"  # Change this to the desired model
    run_experiment(model_name)