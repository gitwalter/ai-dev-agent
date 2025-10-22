"""
Check if the environment has all required dependencies for apps/main.py.
"""

import sys
import importlib

def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"[OK] {package_name} is installed")
        return True
    except ImportError:
        print(f"[X] {package_name} is NOT installed")
        return False

def main():
    print("Environment Check for apps/main.py")
    print("=" * 60)
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print()
    
    print("Checking required packages...")
    print()
    
    # Core packages
    packages = [
        ("google-generativeai", "google.generativeai"),
        ("langchain", "langchain"),
        ("langchain-core", "langchain_core"),
        ("langchain-google-genai", "langchain_google_genai"),
        ("langgraph", "langgraph"),
        ("pydantic", "pydantic"),
    ]
    
    all_installed = True
    missing = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
            missing.append(package_name)
    
    print()
    print("=" * 60)
    
    if all_installed:
        print("[OK] All required packages are installed!")
        print()
        print("You can run the app with:")
        print(f"  {sys.executable} apps/main.py")
    else:
        print("[X] Missing packages detected!")
        print()
        print("To fix this, run:")
        print()
        if "langgraph" in str(sys.executable).lower():
            print(f"  {sys.executable} -m pip install {' '.join(missing)}")
        else:
            print("  # Switch to langgraph environment:")
            print("  C:\\App\\Anaconda\\Scripts\\activate.bat langgraph")
            print()
            print("  # Or install in current environment:")
            print(f"  {sys.executable} -m pip install -r requirements.txt")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()

