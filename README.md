# AI Debate Platform

English | [中文](README_CN.md)

A Python-based application that enables debates and answer optimization between two AI language models. The platform supports OpenAI models, Anthropic Claude models, and various Chinese AI models like DeepSeek, Moonshot, ChatGLM, Qwen, and ERNIE.

## Features

- **AI Debate Mode**: Pit two AI models against each other in a structured debate format
- **Answer Optimization Mode**: Let one AI model critique and iteratively improve another model's answers
- **Multi-Model Support**: Compatible with:
  - OpenAI models (GPT series)
  - Anthropic Claude models
  - DeepSeek models
  - Moonshot models
  - ChatGLM models
  - Qwen (通义千问) models
  - ERNIE (文心一言) models
- **Custom API Support**: Use self-hosted or alternative API endpoints
- **User-friendly GUI**: Easy-to-use interface built with PyQt5
- **Streaming Output**: Real-time response viewing
- **Comprehensive Logging**: Detailed logs for every conversation
- **Debate Configuration**: Customize the debate parameters, including model temperature settings
- **Export Results**: Save debate or optimization results for future reference

## Requirements

- Python 3.7+
- OpenAI API key (for OpenAI models)
- Additional API keys for other model providers

## Quick Start (Executable Version)

For Windows users, you can download the ready-to-use executable version from the [Releases](https://github.com/yourusername/ai-debate-platform/releases) page. Simply download and run the .exe file - no installation or Python environment required.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-debate-platform.git
cd ai-debate-platform
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Application

Run the GUI application:

```bash
python ai_debate_gui.py
```

1. Enter your API keys for both models
2. Select the debate or optimization mode
3. Choose models for both sides
4. Set the debate topic or question for optimization
5. Configure additional parameters (temperature, number of rounds)
6. Click "Start" to begin the process

### Command Line Interface

The application can also be used from the command line:

```bash
python ai_debate.py --api-key1 YOUR_API_KEY1 --api-key2 YOUR_API_KEY2 --model1 gpt-4 --model2 claude-2 --question "What is the best programming language?"
```

For custom API endpoints:

```bash
python ai_debate.py --api-key1 YOUR_API_KEY1 --api-key2 YOUR_API_KEY2 --model1 custom-model-1 --model2 custom-model-2 --api-base1 http://your-api-endpoint-1 --api-base2 http://your-api-endpoint-2 --question "Your debate topic here"
```

## Configuration Options

### Models
- Select from a variety of AI models from different providers
- Adjust temperature settings for each model (0.0-2.0)

### Debate Parameters
- Set the number of debate rounds
- Specify the debate topic or question for optimization

### Output Options
- Enable/disable streaming output
- Save results to a specific file location

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- This project uses the OpenAI API for GPT models
- Anthropic API for Claude models
- Various Chinese AI model providers for additional models 