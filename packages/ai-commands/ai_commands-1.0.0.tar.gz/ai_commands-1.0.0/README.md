# ai_commands

![Package Logo](https://github.com/MKM12345/ai_commands/blob/main/logo.png)

[![Python Version](https://img.shields.io/badge/Python-%3E%3D%203.7-blue?style=plastic.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/badge/pypi%20package-0.1.0-4DC71F?style=plastic.svg)](https://pypi.org/project/ai_commands/)
[![First Timer Friendly](https://img.shields.io/badge/first%20timer-friendly-4DC71F?style=plastic.svg)](https://github.com/MKM12345/ai_commands/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
[![Tests](https://img.shields.io/badge/tests-all%20passing-4DC71F?style=plastic.svg)](https://github.com/MKM12345/ai_commands/actions)

## Overview

`ai_commands` is a Python package designed to simplify common AI-related tasks such as performing sentiment analysis on text data. It provides a collection of functions and utilities to streamline various AI tasks, making it easier for developers to work with artificial intelligence and natural language processing.

### Features

- **Text Variation Generation**: Use the `ai_similarise` function to generate text variations by replacing words with synonyms and shuffling sentence structure.
- **Sentiment Analysis**: Employ the `analyze_sentiment` function to perform sentiment analysis on text, providing sentiment labels and scores.

## Installation

You can install `ai_commands` using pip:
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

## Support and Contributions
ai_commands is an open-source project, and contributions from the community are welcome! If you have ideas for improvements or new features, please check out our contribution guidelines.

## License
ai_commands is licensed under the MIT License.
