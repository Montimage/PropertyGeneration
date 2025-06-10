"""
This module builds a prompt for few-shot LLM prompting, combining:
- MMT property context (static rules/format guidance)
- A scenario description (user-defined)
- Protocol attribute definitions
- Example XML properties retrieved from a database

It returns a full prompt string suitable for input to an LLM.
"""

from langchain.prompts import PromptTemplate
from retrieve_data import retrieve_examples, retrieve_protocol_context
from pathlib import Path

template = """
You are an AI that generates XML properties for deep packet inspection.

### MMT Property Context:
{mmt_context}

## Scenario Description:
{scenario_description}

## Protocol Context:
{protocol_context}

## Example XML Properties:
{xml_examples}

### Task:
Generate a new XML property that matches the scenario and adheres to the protocol(s) context.
"""

prompt = PromptTemplate(
    input_variables=["mmt_context", "scenario_description", "protocol_context", "xml_examples"],
    template=template,
)

def format_prompt(examples_data, scenario_description, protocol_data, mmt_context):
    """
    Formats the final prompt by injecting example XML properties, protocol information, and scenario context.

    Args:
        examples_data (List[dict]): A list of example entries, eah with 'description', 'protocol', and 'xml_content'.
        scenario_description (str): The user-defined natural language description of the scenario.
        protocol_data (List[dict]): A list of protocol definitions, each with 'protocol_name' and 'protocol_attributes'.
        mmt_context (str): Text that describes the MMT rule format.
    
    Returns:
        str: The formatted prompt string ready for LLM input.
    """

    # Format protocol descriptions
    protocol_context = "\n\n".join(
        f"Protocol: {proto['protocol_name']}\nAttributes: {proto['protocol_attributes']['attributes']}"
        for proto in protocol_data
    )

    xml_examples = "\n\n".join(
        f"### Example {i+1}:\n"
        f"**Description:** {ex['description']}\n"
        f"**Protocol(s):** {ex['protocol']}\n"
        f"**XML Property:**\n{ex['xml_content']}"
        for i, ex in enumerate(examples_data)
    )

    return prompt.format(
        mmt_context=mmt_context,
        scenario_description=scenario_description,
        protocol_context=protocol_context,
        xml_examples=xml_examples
    )

def load_mmt_context():
    context_path = Path(__file__).parent / "data" / "mmt-property-context.txt"
    return context_path.read_text()

def generate_prompt(scenario, protocol_list, num_examples=1):
    """
    Retrieves the necessary context and builds a prompt suitable for few-show XML property generation.

    Args:
        scenario (str): The user-defined scenario description.
        protocol_list (List[str]): A list of protocol names relevant to the scenario.
        num_examples (int): Number of example XML properties to include. Defaults to 1.
    
    Returns:
        str: The formatted prompt string.
    """

    mmt_context = load_mmt_context()
    protocol_data = retrieve_protocol_context(protocol_list)  # Retrieve protocol context from PostgreSQL
    examples = retrieve_examples(scenario, num_examples=num_examples)  # Retrieve examples from PostgreSQL

    prompt = format_prompt(examples, scenario, protocol_data, mmt_context)
    return prompt