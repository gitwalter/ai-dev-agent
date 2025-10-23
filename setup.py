"""Setup file to make ai-dev-agent installable as a package."""

from setuptools import setup, find_packages

setup(
    name="ai-dev-agent",
    version="0.1.0",
    packages=find_packages(include=["agents*", "models*", "utils*", "apps*", "prompts*"]),
    python_requires=">=3.11",
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
)
