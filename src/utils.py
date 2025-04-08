import re

def extract_xml(response_text):
    """
    Extracts the XML content between the <beginning>...</beginning> tags from a string.
    Args:
        response_text (str): The full text returned by the LLM, potentially containing XML.

    Returns:
        str or None: The extracted XML content if found, otherwise None.

    Example:
        extract_xml("Here is your property: <beginning><property>...</property></beginning>")
        '<beginning><property>...</property></beginning>'
    """
    match = re.search(r"<beginning>.*?</beginning>", response_text, re.DOTALL)
    return match.group(0) if match else None