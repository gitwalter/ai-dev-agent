#!/usr/bin/env python
"""
AI-Dev-Agent Setup Configuration

Legacy setup.py for backward compatibility with older pip versions.
Modern configuration is in pyproject.toml
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure Python 3.9+
if sys.version_info < (3, 9):
    raise RuntimeError("AI-Dev-Agent requires Python 3.9 or later")

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle version specifiers
                    if "==" in line:
                        requirements.append(line.replace("==", ">="))
                    else:
                        requirements.append(line)
    except FileNotFoundError:
        # Fallback to minimal requirements
        requirements = [
            "streamlit>=1.28.2",
            "pydantic>=2.5.0",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "click>=8.1.7",
            "rich>=13.7.0",
        ]
    return requirements

setup(
    name="ai-dev-agent",
    version="1.0.0",
    author="AI-Dev-Agent Team",
    author_email="team@ai-dev-agent.org",
    description="Conscious AI development organisms in the noble tradition of mathematical beauty and software craftsmanship",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ai-dev-agent/ai-dev-agent",
    project_urls={
        "Bug Tracker": "https://github.com/ai-dev-agent/ai-dev-agent/issues",
        "Documentation": "https://ai-dev-agent.readthedocs.io",
        "Source Code": "https://github.com/ai-dev-agent/ai-dev-agent",
    },
    packages=find_packages(include=[
        "agents*", "apps*", "context*", "demo*", 
        "models*", "monitoring*", "utils*", "workflow*"
    ]),
    include_package_data=True,
    package_data={
        "": ["*.md", "*.yaml", "*.yml", "*.json", "*.toml"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "ai": [
            "google-generativeai>=0.3.2",
            "openai>=1.3.7",
        ],
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "bandit>=1.7.5",
            "safety>=2.3.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-dev-agent=apps.main:main",
            "ai-agent-demo=demo.ai_agent_demo_system:main",
            "ai-prompt-manager=apps.prompt_manager_app:main",
        ],
    },
    zip_safe=False,
)
