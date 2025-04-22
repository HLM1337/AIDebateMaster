# AI 辩论系统 / AI Debate System

## 项目介绍 / Project Introduction

这是一个AI辩论系统，能够让两个AI模型围绕特定话题进行辩论，并生成综合性结论。系统支持多种大型语言模型，包括OpenAI的GPT系列、Anthropic的Claude系列以及DeepSeek的模型，用户可以自由组合不同模型进行辩论对抗。

This is an AI debate system that allows two AI models to debate on specific topics and generate a comprehensive conclusion. The system supports various large language models, including OpenAI's GPT series, Anthropic's Claude series, and DeepSeek models, allowing users to freely combine different models for debate competitions.

### 主要特性 / Main Features

- **多模型支持** / **Multi-model Support**
  - 支持OpenAI的GPT-3.5/GPT-4系列
  - 支持Anthropic的Claude 3系列
  - 支持DeepSeek的模型
  - Support for OpenAI's GPT-3.5/GPT-4 series
  - Support for Anthropic's Claude 3 series
  - Support for DeepSeek models

- **用户友好的图形界面** / **User-friendly GUI**
  - 简洁明了的设置界面
  - 实时显示辩论过程
  - 辩论结果汇总展示
  - Clear and concise settings interface
  - Real-time display of the debate process
  - Summary display of debate results

- **灵活配置** / **Flexible Configuration**
  - 可自定义辩论主题
  - 可选择不同AI模型作为正反方
  - 可调整温度参数影响创造性
  - 可设置辩论回合数
  - Customizable debate topics
  - Different AI models can be selected for affirmative and negative sides
  - Adjustable temperature parameters to influence creativity
  - Configurable number of debate rounds

- **流式输出** / **Streaming Output**
  - 支持实时流式显示AI回复
  - 提供更好的用户体验
  - Supports real-time streaming display of AI responses
  - Provides better user experience

- **结果保存** / **Result Saving**
  - 自动保存完整对话记录
  - 支持保存辩论结果到JSON文件
  - Automatically saves complete conversation logs
  - Supports saving debate results to JSON files

## 安装要求 / Installation Requirements

- Python 3.8+
- OpenAI API密钥（或DeepSeek API密钥，用于DeepSeek模型）
- 以下Python库:
  - openai>=1.1.0
  - PyQt5>=5.15.0
  - anthropic>=0.18.0 (可选，用于Claude模型)
  - requests>=2.31.0
- Python 3.8+
- OpenAI API key (or DeepSeek API key for DeepSeek models)
- The following Python libraries:
  - openai>=1.1.0
  - PyQt5>=5.15.0
  - anthropic>=0.18.0 (optional, for Claude models)
  - requests>=2.31.0

## 安装指南 / Installation Guide

1. 克隆或下载本仓库 / Clone or download this repository
```bash
git clone https://github.com/yourusername/ai-debate-system.git
cd ai-debate-system
```

2. 安装依赖 / Install dependencies
```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### 图形界面模式 / GUI Mode

启动图形界面应用程序：
Launch the GUI application:

```bash
python ai_debate_gui.py
```

1. 输入您的API密钥
2. 设置辩论主题
3. 选择AI模型和参数
4. 点击"开始辩论"按钮
5. 观看实时辩论过程
6. 查看生成的综合结论

1. Enter your API key
2. Set debate topic
3. Select AI models and parameters
4. Click the "Start Debate" button
5. Watch the real-time debate process
6. View the generated comprehensive conclusion

### 命令行模式 / Command Line Mode

也可以通过命令行直接运行辩论：
You can also run debates directly through the command line:

```bash
python ai_debate.py --api_key YOUR_API_KEY --question "人工智能是否会超越人类智能？" --model1 gpt-4 --model2 deepseek-chat --rounds 3
```

参数说明 / Parameters:
- `--api_key`: API密钥 / API key
- `--question`: 辩论主题 / Debate topic
- `--model1`: 第一个AI模型 / First AI model
- `--model2`: 第二个AI模型 / Second AI model
- `--temp1`: 第一个模型的温度参数 / Temperature parameter for the first model
- `--temp2`: 第二个模型的温度参数 / Temperature parameter for the second model
- `--rounds`: 辩论回合数 / Number of debate rounds
- `--output`: 结果保存文件名 / Result save filename
- `--stream`: 启用流式输出 / Enable streaming output
- `--log`: 日志文件路径 / Log file path
- `--log_level`: 日志级别 / Log level

## 支持的模型 / Supported Models

- **OpenAI**:
  - gpt-4-turbo
  - gpt-4
  - gpt-3.5-turbo

- **Anthropic**:
  - claude-3-opus-20240229
  - claude-3-sonnet-20240229
  - claude-3-haiku-20240307

- **DeepSeek**:
  - deepseek-reasoner
  - deepseek-chat

## 示例输出 / Example Output

一个典型的辩论过程包括以下阶段：
A typical debate process includes the following stages:

1. 各自陈述初始观点 / Initial statements of viewpoints
2. 多轮相互辩论和反驳 / Multiple rounds of debate and rebuttal
3. 生成综合性结论 / Generation of a comprehensive conclusion

## 项目结构 / Project Structure

- `ai_debate.py`: 核心辩论逻辑和命令行接口
- `ai_debate_gui.py`: 图形用户界面
- `requirements.txt`: 项目依赖列表
- `logs/`: 辩论日志和结果保存目录

- `ai_debate.py`: Core debate logic and command line interface
- `ai_debate_gui.py`: Graphical user interface
- `requirements.txt`: Project dependency list
- `logs/`: Directory for debate logs and saved results

## 注意事项 / Notes

- 需要有效的API密钥才能使用
- API调用会产生费用，请注意控制使用量
- 对于DeepSeek模型，系统会自动使用DeepSeek的API
- 对于Claude模型，需要单独配置Anthropic API密钥

- A valid API key is required for use
- API calls will incur costs, please control usage
- For DeepSeek models, the system will automatically use DeepSeek's API
- For Claude models, a separate Anthropic API key needs to be configured

## 许可证 / License

MIT

## 贡献 / Contribution

欢迎提交问题和改进建议！
Issues and improvement suggestions are welcome! 