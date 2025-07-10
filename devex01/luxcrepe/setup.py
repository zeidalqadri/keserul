"""
Setup configuration for LuxCrepe package
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(this_directory, "README.md")
    
    if os.path.exists(readme_path):
        with open(readme_path, encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from package
def read_version():
    import luxcrepe
    return luxcrepe.__version__

# Core dependencies
install_requires = [
    "requests>=2.25.0",
    "beautifulsoup4>=4.9.0",
    "lxml>=4.6.0",
    "numpy>=1.20.0",
]

# ML dependencies (optional)
ml_requires = [
    "torch>=1.9.0",
    "transformers>=4.10.0",
    "scikit-learn>=1.0.0",
    "Pillow>=8.0.0",
    "opencv-python>=4.5.0",
]

# Development dependencies
dev_requires = [
    "pytest>=6.0.0",
    "pytest-cov>=2.12.0",
    "black>=21.0.0",
    "flake8>=3.9.0",
    "mypy>=0.910",
    "isort>=5.9.0",
]

# Documentation dependencies
docs_requires = [
    "sphinx>=4.0.0",
    "sphinx-rtd-theme>=0.5.0",
    "myst-parser>=0.15.0",
]

setup(
    name="luxcrepe",
    version=read_version(),
    author="LuxCrepe Team",
    author_email="team@luxcrepe.com",
    description="ML-Enhanced Universal E-commerce Product Scraper",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/luxcrepe/luxcrepe",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "ml": ml_requires,
        "dev": dev_requires,
        "docs": docs_requires,
        "all": ml_requires + dev_requires + docs_requires,
    },
    entry_points={
        "console_scripts": [
            "luxcrepe=luxcrepe.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "luxcrepe": [
            "ml/models/*.json",
            "ml/models/*.pkl",
            "data/*.json",
        ],
    },
    zip_safe=False,
    keywords="web-scraping, machine-learning, e-commerce, product-data, luxury-brands",
    project_urls={
        "Bug Reports": "https://github.com/luxcrepe/luxcrepe/issues",
        "Source": "https://github.com/luxcrepe/luxcrepe",
        "Documentation": "https://luxcrepe.readthedocs.io/",
    },
)