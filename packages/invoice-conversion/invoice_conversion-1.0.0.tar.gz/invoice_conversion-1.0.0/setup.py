from setuptools import setup, find_packages

setup(
    name="invoice_conversion",
    version="1.0.0",
    packages=find_packages(),
    description="A simple utility to convert Excel-based invoices to PDF format.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lionel Tchami",
    author_email="lionel@apotitech.com",
    url="https://github.com/apotitech/invoice_conversion",  # Replace with your project's repository URL
    install_requires=[
        "pandas>=1.0.0",
        "fpdf>=1.7",
        "openpyxl"  # Needed to read .xlsx files with pandas
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",  # Adjust if you're using a different license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",  # For example, adjust if you're targeting a specific Python version
    ],
    keywords=["excel", "pdf", "invoice", "invoice converter", "invoice conversion"],
    project_urls={
        "Bug Reports": "https://github.com/apotitech/invoice_conversion/issues",
        "Source": "https://github.com/apotitech/invoice_conversion",
    },
)
