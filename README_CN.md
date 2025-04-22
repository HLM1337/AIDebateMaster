# AI辩论平台

[English](README.md) | 中文

这是一个基于Python的应用程序，支持两个AI语言模型之间的辩论和答案优化。该平台支持OpenAI模型、Anthropic Claude模型以及各种中文AI模型，如DeepSeek、Moonshot、ChatGLM、通义千问和文心一言等。

## 功能特点

- **AI辩论模式**：让两个AI模型在结构化的辩论格式中相互对决
- **答案优化模式**：让一个AI模型批评并逐步改进另一个模型的回答
- **多模型支持**：兼容以下模型：
  - OpenAI模型（GPT系列）
  - Anthropic Claude模型
  - DeepSeek模型
  - Moonshot模型
  - ChatGLM模型
  - 通义千问模型
  - 文心一言模型
- **自定义API支持**：使用自托管或替代API端点
- **用户友好的GUI**：基于PyQt5构建的易用界面
- **流式输出**：实时查看AI响应
- **全面的日志记录**：对每次对话进行详细记录
- **辩论配置**：自定义辩论参数，包括模型温度设置
- **导出结果**：保存辩论或优化结果以供将来参考

## 系统要求

- Python 3.7+
- OpenAI API密钥（用于OpenAI模型）
- 其他模型提供商的API密钥

## 快速开始（可执行文件版本）

对于Windows用户，您可以从[Releases](https://github.com/HLM1337/AIDebateMaster/releases)页面下载即用型可执行文件版本。只需下载并运行.exe文件 - 无需安装或Python环境。

## 安装方法

1. 克隆此仓库：
```bash
git clone https://github.com/HLM1337/AIDebateMaster.git
cd AIDebateMaster
```

2. 安装所需依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 图形界面应用

运行图形界面应用：

```bash
python ai_debate_gui.py
```

1. 输入两个模型的API密钥
2. 选择辩论或优化模式
3. 为双方选择模型
4. 设置辩论主题或待优化问题
5. 配置其他参数（温度、回合数）
6. 点击"开始"启动过程

### 命令行界面

该应用程序也可以通过命令行使用：

```bash
python ai_debate.py --api-key1 你的API密钥1 --api-key2 你的API密钥2 --model1 gpt-4 --model2 claude-2 --question "什么是最好的编程语言？"
```

对于自定义API端点：

```bash
python ai_debate.py --api-key1 你的API密钥1 --api-key2 你的API密钥2 --model1 custom-model-1 --model2 custom-model-2 --api-base1 http://你的API端点1 --api-base2 http://你的API端点2 --question "你的辩论主题"
```

## 配置选项

### 模型
- 从不同提供商选择各种AI模型
- 调整每个模型的温度设置（0.0-2.0）

### 辩论参数
- 设置辩论回合数
- 指定辩论主题或待优化问题

### 输出选项
- 启用/禁用流式输出
- 将结果保存到特定文件位置

## 许可证

本项目是开源的，根据[MIT许可证](LICENSE)提供。

## 致谢

- 本项目使用OpenAI API访问GPT模型
- 使用Anthropic API访问Claude模型
- 使用各种中文AI模型提供商的API访问其他模型 