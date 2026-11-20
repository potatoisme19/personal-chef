from langchain_core.tools import tool


@tool
def scale_quantity(quantity: float, original_servings: int, target_servings: int) -> float:
    """Scale an ingredient quantity to a new serving count."""
    if original_servings < 1 or target_servings < 1:
        raise ValueError("Serving counts must be positive")
    return round(quantity * target_servings / original_servings, 3)


@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert an oven temperature between Celsius and Fahrenheit."""
    source, target = from_unit.strip().lower(), to_unit.strip().lower()
    if source in {"c", "celsius"} and target in {"f", "fahrenheit"}:
        return round(value * 9 / 5 + 32, 1)
    if source in {"f", "fahrenheit"} and target in {"c", "celsius"}:
        return round((value - 32) * 5 / 9, 1)
    if source == target or (source[:1] == target[:1] and source[:1] in {"c", "f"}):
        return value
    raise ValueError("Units must be Celsius (C) or Fahrenheit (F)")


QUANTITY_TOOLS = [scale_quantity, convert_temperature]
