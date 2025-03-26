from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="pii-redactor",
    version="1.0.0",
    author="Montu",
    author_email="info@montu.com",
    description="A service to redact Personally Identifiable Information (PII) from text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pii-redactor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pii-redactor=pii_redactor.__main__:main",
            "pii-redactor-api=pii_redactor.service.api:start_server",
        ],
    },
)
