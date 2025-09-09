"""Setup script for WorkFlowy MCP Server."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="workflowy-mcp",
    version="0.1.0",
    author="Vlad Arbatov",
    author_email="vlad@arbatov.dev",
    description="MCP server for WorkFlowy integration with LLM applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vladzima/workflowy-mcp",
    project_urls={
        "Bug Reports": "https://github.com/vladzima/workflowy-mcp/issues",
        "Source": "https://github.com/vladzima/workflowy-mcp",
        "Documentation": "https://github.com/vladzima/workflowy-mcp/wiki",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=0.1.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "workflowy-mcp=workflowy_mcp.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)