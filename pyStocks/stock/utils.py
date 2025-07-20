import re


def split_camel_case(name: str) -> str:
    """
    Turn CamelCase strings into human-readable words separated by spaces.

    Examples
    --------
    >>> split_camel_case("MarketCap")
    'Market Cap'
    >>> split_camel_case("EnterpriseValueEBITDARatio")
    'Enterprise Value EBITDA Ratio'

    Parameters
    ----------
    name : str
        CamelCase or mixed-case identifier.

    Returns
    -------
    str
        The input string split into words at uppercase boundaries.
    """
    # 1) Split acronym+TitleCase boundaries: "EBITDARatio" -> "EBITDA Ratio"
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', name)
    # 2) Split lower->upper or digit->upper: "MarketCap" -> "Market Cap"
    name = re.sub(r'([a-z\d])([A-Z])', r'\1 \2', name)
    return name
