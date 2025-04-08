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

def generate_property(llm, prompt, max_iterations=1):
    """
    Generates a formally defined XML property using the given LLM and input prompt.

    This function iteratively queries the LLM until a valid XML structure is produced
    or the maximum number of iterations is reached. The response is validated using
    the XMLValidator class to ensure structural correctness.

    Args:
        llm (BaseLanguageModel): An LLM object instantiated via LangChain and Ollama.
        prompt (str): The natural language description to convert into XML.
        max_iterations (int): The maximum number of iterations to attempt generating valid XML.
    
    Returns:
        Tuple[str or None, bool]: A tuple containing:
            - The generated XML string if valid, otherwise None.
            - A boolean indicating whether the XML is valid (True) or not (False).
    """
    validator = XMLValidator()

    iterations = 0
    prompt_text = prompt
    valid_xml = False
    validation_message = ""

    # Define prompt template
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="User: {question}\nAssistant:"
    )

    # Create LLM chain
    chain = prompt_template | llm

    while iterations < max_iterations:
        print(f"Iteration {iterations + 1} of {max_iterations}")        
        response = chain.invoke({"question": prompt_text})
        iterations += 1

        # Extract XML from the response
        extracted_xml = extract_xml(response)
        if extracted_xml is None:
            validation_message = "Please return only the XML content, wrapped entirely between <beginning> and </beginning> tags."
            continue

        else:
            valid_xml, validation_message = validator.validate_xml(extracted_xml)

            # If valid, stop
            if valid_xml:
                print("Valid XML generated:")
                print(extracted_xml)
                return extracted_xml, True

            # If invalid, modify prompt and retry
            print(f"Invalid XML generated: {validation_message}")
        prompt_text += f"\n\n### Validation Feedback:\nThe generated XML is invalid: {validation_message}\nPlease correct and return only a valid XML structure."
    return None, False