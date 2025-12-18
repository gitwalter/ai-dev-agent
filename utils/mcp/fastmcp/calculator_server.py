"""calculator_server.py

FastMCP server providing advanced calculation tools.
Useful for mathematical, statistical, and unit conversion operations.
"""
from fastmcp import FastMCP
import math

mcp = FastMCP("Calculator")


@mcp.tool()
def calculate_expression(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: Math expression (e.g., "2 + 3 * 4", "sqrt(16)", "sin(pi/2)")
        
    Returns:
        Result of the calculation
    """
    # Safe math functions
    safe_functions = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "floor": math.floor,
        "ceil": math.ceil,
    }
    
    try:
        # Only allow safe operations
        result = eval(expression, {"__builtins__": {}}, safe_functions)
        return f"Expression: {expression}\nResult: {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between common units.
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., "km", "miles", "celsius", "kg")
        to_unit: Target unit (e.g., "miles", "km", "fahrenheit", "lbs")
        
    Returns:
        Converted value with units
    """
    # Conversion factors to base units
    conversions = {
        # Length (base: meters)
        "m": 1, "meter": 1, "meters": 1,
        "km": 1000, "kilometer": 1000, "kilometers": 1000,
        "cm": 0.01, "centimeter": 0.01,
        "mm": 0.001, "millimeter": 0.001,
        "mi": 1609.34, "mile": 1609.34, "miles": 1609.34,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
        
        # Weight (base: kg)
        "kg": 1, "kilogram": 1, "kilograms": 1,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "mg": 0.000001, "milligram": 0.000001,
        "lb": 0.453592, "lbs": 0.453592, "pound": 0.453592, "pounds": 0.453592,
        "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
    }
    
    from_lower = from_unit.lower()
    to_lower = to_unit.lower()
    
    # Handle temperature separately
    if from_lower in ["c", "celsius"] and to_lower in ["f", "fahrenheit"]:
        result = (value * 9/5) + 32
        return f"{value} Celsius = {result:.2f} Fahrenheit"
    elif from_lower in ["f", "fahrenheit"] and to_lower in ["c", "celsius"]:
        result = (value - 32) * 5/9
        return f"{value} Fahrenheit = {result:.2f} Celsius"
    elif from_lower in ["c", "celsius"] and to_lower in ["k", "kelvin"]:
        result = value + 273.15
        return f"{value} Celsius = {result:.2f} Kelvin"
    elif from_lower in ["k", "kelvin"] and to_lower in ["c", "celsius"]:
        result = value - 273.15
        return f"{value} Kelvin = {result:.2f} Celsius"
    
    # Standard conversions
    if from_lower not in conversions:
        return f"Unknown unit: {from_unit}"
    if to_lower not in conversions:
        return f"Unknown unit: {to_unit}"
    
    # Convert to base, then to target
    base_value = value * conversions[from_lower]
    result = base_value / conversions[to_lower]
    
    return f"{value} {from_unit} = {result:.4f} {to_unit}"


@mcp.tool()
def calculate_statistics(numbers: str) -> str:
    """
    Calculate statistics for a list of numbers.
    
    Args:
        numbers: Comma-separated list of numbers (e.g., "1, 2, 3, 4, 5")
        
    Returns:
        Mean, median, mode, std dev, min, max
    """
    try:
        # Parse numbers
        nums = [float(x.strip()) for x in numbers.split(",")]
        if not nums:
            return "No numbers provided"
        
        n = len(nums)
        
        # Mean
        mean = sum(nums) / n
        
        # Median
        sorted_nums = sorted(nums)
        if n % 2 == 0:
            median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
        else:
            median = sorted_nums[n//2]
        
        # Variance and Std Dev
        variance = sum((x - mean) ** 2 for x in nums) / n
        std_dev = math.sqrt(variance)
        
        # Min/Max
        min_val = min(nums)
        max_val = max(nums)
        
        return (
            f"Statistics for {n} numbers:\n"
            f"  Mean: {mean:.4f}\n"
            f"  Median: {median:.4f}\n"
            f"  Std Dev: {std_dev:.4f}\n"
            f"  Variance: {variance:.4f}\n"
            f"  Min: {min_val}\n"
            f"  Max: {max_val}\n"
            f"  Sum: {sum(nums):.4f}\n"
            f"  Range: {max_val - min_val:.4f}"
        )
    except Exception as e:
        return f"Error calculating statistics: {e}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8003)

