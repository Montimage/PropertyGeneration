from generate_prompt import generate_prompt
from llm_interaction import generate_property, initialize_llm

# Config is set here directly
DEFAULT_MODEL_NAME = "mistral"
DEFAULT_MODEL_CONFIG = {
    "provider": "ollama",
    "temperature": 0.3,
    "top_p": 0.9,
    "max_tokens": 1024
}

# Load once
llm = initialize_llm(DEFAULT_MODEL_NAME, DEFAULT_MODEL_CONFIG)


def generate_property_from_text(scenario: str, protocols: list[str]) -> str:
    """
    Generates a valid XML property from a natural language description.
    Returns either the valid XML string or a warning message
    """
    try:
        full_prompt = generate_prompt(
            scenario=scenario,
            protocol_list=protocols,
            num_examples=1
        )

        xml_candidate, is_valid, feedback = generate_property(llm, full_prompt)
        return {
            "success": True,
            "xml": xml_candidate,
            "is_valid": is_valid,
            "validation_feedback": feedback,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "xml": None,
            "is_valid": None,
            "validation_feedback": None,
            "error": str(e)
        }