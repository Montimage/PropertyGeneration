"""
This module handles interaction with a local LLM served by Ollama 
using LangChain. It provides functions to:

- Initialize the LLM with specific generation parameters.
- Generate and validate a formally defined XML property from a natural language description.
"""

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from syntax_validation import XMLValidator
from utils import extract_xml
import os
import time
import pandas as pd


def initialize_llm(model_name, model_config):
    """
    Initializes an LLM using configuration parameters for Ollama.

    Args:
        model_name (str): The name of the model (e.g., "mistral", "gemma3:12b").
        model_config (dict): Configuration dictionary with:
            - "provider": The LLM provider (e.g., "ollama").
            - "temperature" (float): Sampling temperature for generation.
            - "top_p" (float): Nucleus sampling value.
            - "max_tokens" (int): Maximum number of tokens to generate.

    Returns:
        OllamaLLM: An instantiated LangChain LLM object.
    
    Raises:
        ValueError: If an unsupported provider is specified.
    """

    if model_config["provider"] == "ollama":
        llm = OllamaLLM(
            model=model_name,
            temperature=model_config["temperature"],
            top_p=model_config["top_p"],
            num_predict=model_config["max_tokens"]
        )
    else:
        raise ValueError(f"Provider {model_config['provider']} not supported.")
    return llm

def generate_property(llm, prompt, max_iterations=1, store_iterations=False, output_dir=None, stats=None):
    """
    Generates a formally defined XML property using the given LLM and input prompt.

    This function iteratively queries the LLM until a valid XML structure is produced
    or the maximum number of iterations is reached. The response is validated using
    the XMLValidator class to ensure structural correctness.

    Args:
        llm (BaseLanguageModel): An LLM object instantiated via LangChain and Ollama.
        prompt (str): The natural language description to convert into XML.
        max_iterations (int): The maximum number of iterations to attempt generating valid XML.
        store_iterations (bool): Whether to store each iteration's response for analysis.
        output_dir (str or None): Directory to store iteration outputs if store_iterations is True.
        stats (dict or None): Optional dictionary to collect statistics about the generation process. Format should be {"stats_file_path": "path/to/stats.csv", "model_name": "model_name", "prompt_file": "refernce_to_file"}.
    
    Returns:
        Tuple[str or None, bool, str]: A tuple containing:
            - The generated XML string if valid, otherwise None.
            - A boolean indicating whether the XML is valid (True) or not (False).
            - A validation message if invalid.

        If store_iterations is True, each iteration's response will be saved in the specified output directory for further analysis.
        If stats is provided, generation statistics will be collected and saved to the specified CSV file in the format: {prompt_file, model_name, iterations, elapsed_time}.
    """
    validator = XMLValidator()

    iterations = 0
    prompt_text = prompt
    valid_xml = False
    validation_message = ""
    last_xml_candidate = ""

    # Define prompt template
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="User: {question}\nAssistant:"
    )

    # Create LLM chain
    chain = prompt_template | llm

    start_time = time.time()
    while iterations < max_iterations:
        print(f"Iteration {iterations + 1} of {max_iterations}")        
        response = chain.invoke({"question": prompt_text})
        iterations += 1

        # Extract XML from the response
        extracted_xml = extract_xml(response)
        if extracted_xml is None:
            validation_message = "Please return only the XML content, wrapped entirely between <beginning> and </beginning> tags."
            # If store_iterations is True, save the response for analysis
            if store_iterations and output_dir is not None:
                file_path = os.path.join(output_dir, f"iteration_{iterations}_invalid.txt")
                with open(file_path, "w") as file:
                    file.write(response)
            continue
        else:
            last_xml_candidate = extracted_xml
            valid_xml, validation_message = validator.validate_xml(extracted_xml)

            # If valid, stop
            if valid_xml:
                print("Valid XML generated:")
                if store_iterations and output_dir is not None:
                    file_path = os.path.join(output_dir, f"iteration_{iterations}_valid.xml")
                    with open(file_path, "w") as file:
                        file.write(extracted_xml)
                if stats is not None:
                    print(f"Recording stats in file {stats['stats_file_path']}")
                    elapsed_time = time.time() - start_time
                    stats_file_path = stats["stats_file_path"]
                    model_name = stats["model_name"]
                    prompt_file = stats["prompt_file"]
                    save_statistics(stats_file_path, prompt_file, model_name, iterations, True, elapsed_time)
                return extracted_xml, True, ""

            # If invalid, modify prompt and retry
            if store_iterations and output_dir is not None:
                file_path = os.path.join(output_dir, f"iteration_{iterations}_invalid.xml")
                with open(file_path, "w") as file:
                    file.write(extracted_xml)
            print(f"Invalid XML generated: {validation_message}")
        prompt_text += f"\n\n### Validation Feedback:\nThe generated XML is invalid: {validation_message}\nPlease correct and return only a valid XML structure."
    if stats is not None:
        elapsed_time = time.time() - start_time
        stats_file_path = stats["stats_file_path"]
        model_name = stats["model_name"]
        prompt_file = stats["prompt_file"]
        save_statistics(stats_file_path, prompt_file, model_name, iterations, False, elapsed_time)
    return last_xml_candidate, False, validation_message

def save_statistics(stats_file, prompt_file, model_name, iterations, valid_xml, elapsed_time):
    """
    Save the statistics for the current experiment.
    """
    stats_data = {
        "prompt_file": prompt_file,
        "model_name": model_name,
        "iterations": iterations,
        "valid_xml": valid_xml,
        "elapsed_time": elapsed_time
    }
    # Append to CSV
    stats_df = pd.DataFrame([stats_data])
    if os.path.exists(stats_file):
        stats_df.to_csv(stats_file, mode='a', header=False, index=False)
    else:
        stats_df.to_csv(stats_file, index=False)

    print(f"Saved statistics in {stats_file}: {stats_data}")