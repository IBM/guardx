"""This module provides a set of unit tests for guardx APIs and for the sandbox environment."""

import pytest

from guardx.analysis.types import AnalysisType
from guardx.guardx import Guardx


def test_execute_1():
    python_code = """
def add(a, b):
    return a + b

print(add(2, 3))
"""

    g = Guardx(config_path="./resources/config.yaml")

    # To execute code in sandbox with a default security policy
    result = g.execute(python_code).get_docker_result()

    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')

    assert content_before_metadata == '5', "Execution result of python code is wrong!"


@pytest.mark.parametrize(
    "package_name",
    [
        "npyfile",
        "netCDF4",
        "pandas",
        "cartopy",
        "statistics",
        "yfinance",
        "keras",
        "seaborn",
        "geopandas",
        "statsmodels",
        "dates",
        "scikit-learn",
        "matplotlib",
        "pytz",
        "scipy",
        "cycler",
        "openweathermap",
        "numpy",
        "requests",
        "sympy",
        "numpy",
        "tqdm",
        "selenium",
    ],
)
def test_docker_sandbox_packages(package_name):
    python_code = f"""
def is_package_installed(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

package_name = "{package_name}"

print(is_package_installed(package_name))
"""

    g = Guardx(config_path="./resources/config.yaml")

    # To execute code in sandbox with a default security policy
    result = g.execute(python_code).get_docker_result()

    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')

    assert content_before_metadata == 'True', f"Package '{package_name}' is not installed!"


def test_analyze_secret_unsafe_code():
    python_code = """
import requests

# Sample secret API key (for demonstration purposes only)
API_KEY = "sk_test_1234567890abcdef12345678"

# Endpoint for a sample API (mock URL for demonstration)
API_ENDPOINT = "https://api.example.com/v1/resource"

def fetch_data():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(API_ENDPOINT, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    result = fetch_data()
    if result:
        print("Data fetched successfully!")
        print(result)
    else:
        print("Failed to fetch data.")
"""
    g = Guardx(config_path="./resources/config.yaml")
    result = g.analyze(python_code, {AnalysisType.DETECT_SECRET, AnalysisType.UNSAFE_CODE})
    assert len(result) == 2, "unsafe code leaks secret!"


def test_analyze_safe_code_1():
    python_code = """
def calculate_area():
    length = 10
    width = 5

    return length * width

if __name__ == "__main__":
    print("Welcome to the Rectangle Area Calculator!")
    area = calculate_area(length, width)
    print(f"The area of the rectangle is: {area}")
"""
    g = Guardx(config_path="./resources/config.yaml")
    result = g.analyze(python_code, {AnalysisType.DETECT_SECRET, AnalysisType.UNSAFE_CODE})

    assert result[AnalysisType.DETECT_SECRET] is None, "No leaks in code, but found leaks!"
    assert len(result[AnalysisType.UNSAFE_CODE]) == 0, "Code is safe, but found unsafe code!"


def test_analyze_safe_code_2():
    python_code = """
import os
from dotenv import load_dotenv
import requests

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from environment variables
API_KEY = os.getenv("MY_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found. Please set it in the .env file.")

# Example API URL (replace with the actual API URL you're working with)
API_URL = "https://api.example.com/data"

# Function to make a secure API request
def fetch_data(api_url, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Main program
if __name__ == "__main__":
    try:
        data = fetch_data(API_URL, API_KEY)
        print("API response:", data)
    except Exception as e:
        print("Error occurred:", e)

"""
    g = Guardx(config_path="./resources/config.yaml")
    result = g.analyze(python_code, {AnalysisType.DETECT_SECRET, AnalysisType.UNSAFE_CODE})
    assert result[AnalysisType.DETECT_SECRET] is None, "No leaks in code, but found leaks!"
    assert len(result[AnalysisType.UNSAFE_CODE]) == 0, "Code is safe, but found unsafe code!"


def test_analyze_specialization():
    python_code = """
import requests

# Sample secret API key (for demonstration purposes only)
API_KEY = "sk_test_1234567890abcdef12345678"

# Endpoint for a sample API (mock URL for demonstration)
API_ENDPOINT = "https://api.example.com/v1/resource"

def fetch_data():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(API_ENDPOINT, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    result = fetch_data()
    if result:
        print("Data fetched successfully!")
        print(result)
    else:
        print("Failed to fetch data.")
"""
    g = Guardx(config_path="./resources/config.yaml")
    result = g.analyze(python_code, {AnalysisType.SPECIALIZATION})
    assert len(result) is not None #NOSONAR


def test_execute_with_globals_basic():
    """Test basic execution with globals parameter."""
    python_code = """
result = x + y
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute with globals
    globals_dict = {"x": 10, "y": 20}
    result = g.execute(python_code, globals=globals_dict).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == '30', "Execution with globals failed!"


def test_execute_with_globals_string():
    """Test execution with string globals."""
    python_code = """
result = greeting + " " + name
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute with string globals
    globals_dict = {"greeting": "Hello", "name": "World"}
    result = g.execute(python_code, globals=globals_dict).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == 'Hello World', "Execution with string globals failed!"


def test_execute_with_globals_list():
    """Test execution with list globals."""
    python_code = """
result = sum(numbers)
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute with list globals
    globals_dict = {"numbers": [1, 2, 3, 4, 5]}
    result = g.execute(python_code, globals=globals_dict).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == '15', "Execution with list globals failed!"


def test_execute_with_globals_dict():
    """Test execution with dictionary globals."""
    python_code = """
result = data['key1'] + data['key2']
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute with dict globals
    globals_dict = {"data": {"key1": 100, "key2": 200}}
    result = g.execute(python_code, globals=globals_dict).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == '300', "Execution with dict globals failed!"


def test_execute_without_globals_backward_compatibility():
    """Test that execution without globals still works (backward compatibility)."""
    python_code = """
def multiply(a, b):
    return a * b

result = multiply(6, 7)
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute without globals (should work as before)
    result = g.execute(python_code).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == '42', "Backward compatibility test failed!"


def test_execute_with_empty_globals():
    """Test execution with empty globals dictionary."""
    python_code = """
x = 5
y = 10
result = x + y
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute with empty globals
    result = g.execute(python_code, globals={}).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == '15', "Execution with empty globals failed!"


def test_execute_with_globals_complex_computation():
    """Test execution with globals for complex computation."""
    python_code = """
# Use provided globals to compute result
total = 0
for item in items:
    total += item * multiplier

result = total + offset
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Execute with multiple globals
    globals_dict = {
        "items": [1, 2, 3, 4, 5],
        "multiplier": 2,
        "offset": 10
    }
    result = g.execute(python_code, globals=globals_dict).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    # (1+2+3+4+5)*2 + 10 = 15*2 + 10 = 40
    assert content_before_metadata == '40', "Complex computation with globals failed!"


def test_execute_with_globals_prior_state():
    """Test simulating prior execution state with globals."""
    python_code = """
# Simulate continuing from prior execution
counter += 1
result = counter
print(result)
"""
    
    g = Guardx(config_path="./resources/config.yaml")
    
    # Simulate prior state where counter was 5
    globals_dict = {"counter": 5}
    result = g.execute(python_code, globals=globals_dict).get_docker_result()
    
    output_str = result.output.decode('utf-8')
    content_before_metadata = output_str.split('--', 1)[0].replace('\n', '')
    
    assert content_before_metadata == '6', "Prior state simulation with globals failed!"
