from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'A Python package for simple but complex computer functions.'
LONG_DESCRIPTION = """
<div align="center">
  <img src="https://github.com/MKM12345/ai_commands/blob/main/logo.png">
</div>

# ai_commands v1.0.0

ai_commands is a Python package designed to simplify common AI-related tasks and perform sentiment analysis on text data.

## Overview

ai_commands provides a collection of functions and utilities to streamline various AI tasks, making it easier for developers to work with artificial intelligence and natural language processing. Whether you need to generate text variations or analyze sentiment in text, ai_commands has you covered.

### Features

- **Text Variation Generation**: Use the `ai_similarise` function to generate text variations by replacing words with synonyms and shuffling sentence structure.
- **Sentiment Analysis**: Employ the `analyze_sentiment` function to perform sentiment analysis on text, providing sentiment labels and scores.

## Installation

You can install ai_commands using pip:
`pip install ai-commands`

## Usage
Here's how you can use ai_commands in your Python projects:

```
import ai_commands

# Generate text variations
original_message = "Sorry, you lost the game!"
similar_message = ai_commands.ai_similarise(original_message)
print("Similar Message:", similar_message)

# Perform sentiment analysis
text_to_analyze = "I love this product. It's fantastic!"
sentiment_result = ai_commands.analyze_sentiment(text_to_analyze)
print("Sentiment Analysis Result:", sentiment_result)
```

## Documentation
For detailed usage instructions and additional functions, please refer to the documentation.

Support and Contributions
ai_commands is an open-source project, and contributions from the community are welcome! If you have ideas for improvements or new features, please check out our contribution guidelines.

License
ai_commands is licensed under the [MIT License](License).

For more information, visit the GitHub repository.
"""

# Setting up
setup(
    name="ai_commands",
    version=VERSION,
    author="MKM12345",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "nltk",
        "textblob",
        "transformers",
        "torch",
        "networkx",
        "langdetect",
        "Pillow",
        "spacy",
        # Add any other dependencies for ai_commands functions here
    ],
    keywords=['python', 'AI', 'sentiment analysis', 'natural language processing'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
