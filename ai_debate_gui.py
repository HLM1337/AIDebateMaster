#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, 
                            QSpinBox, QDoubleSpinBox, QGroupBox, QFileDialog, QProgressBar,
                            QCheckBox, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor

# 导入AI辩论模块
try:
    from ai_debate import AIDebate
except ImportError:
    print("错误: 无法导入 AI 辩论模块。请确保 ai_debate.py 文件位于当前目录中。")
    sys.exit(1)

class Translator:
    """多语言支持类"""
    def __init__(self):
        self.current_lang = 'zh'  # 默认使用中文
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """加载所有可用的翻译文件"""
        locales_dir = 'locales'
        if not os.path.exists(locales_dir):
            os.makedirs(locales_dir)
            
        for file in os.listdir(locales_dir):
            if file.endswith('.json'):
                lang = file[:-5]  # 移除.json后缀
                with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
    
    def set_language(self, lang):
        """设置当前语言"""
        if lang in self.translations:
            self.current_lang = lang
            return True
        return False
    
    def get_text(self, key, *args):
        """获取翻译文本，支持格式化参数"""
        # 支持使用点号访问嵌套的翻译键
        keys = key.split('.')
        text = self.translations.get(self.current_lang, {})
        
        for k in keys:
            if isinstance(text, dict):
                text = text.get(k, key)
            else:
                return key
        
        if isinstance(text, str) and args:
            try:
                return text.format(*args)
            except:
                return text
        return text

# 创建全局翻译器实例
translator = Translator()

class DebateWorker(QThread):
    """处理AI辩论的工作线程，防止UI冻结"""
    # 定义信号
    update_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True
    
    def stop(self):
        self.running = False
    
    def run(self):
        """运行辩论或优化进程"""
        try:
            if not (self.config.get('api_key1') and self.config.get('api_key2')):
                self.error_signal.emit(translator.get_text("error.api_keys_required"))
                return
                
            if not self.config['question']:
                self.error_signal.emit(translator.get_text("error.topic_required"))
                return
            
            # 检测模型类型和需要的API
            model1 = self.config['model1']
            model2 = self.config['model2']
            work_mode = self.config.get('mode', 'debate')  # 默认为辩论模式
            
            # 检测是否使用自定义API
            is_custom_api = 'api_base1' in self.config and 'api_base2' in self.config
            
            if is_custom_api:
                self.update_signal.emit(translator.get_text("ui.custom_api_label") + "\n")
                self.update_signal.emit(translator.get_text("ui.model1_api", self.config['api_base1']) + "\n")
                self.update_signal.emit(translator.get_text("ui.model2_api", self.config['api_base2']) + "\n")
                self.update_signal.emit(translator.get_text("ui.model1_name", model1) + "\n")
                self.update_signal.emit(translator.get_text("ui.model2_name", model2) + "\n")
            else:
                # 检测模型类型
                models_info = []
                
                if model1.startswith("deepseek-") or model2.startswith("deepseek-"):
                    models_info.append(translator.get_text("models.deepseek"))
                
                if model1.startswith("claude-") or model2.startswith("claude-"):
                    models_info.append(translator.get_text("models.claude"))
                
                if model1.startswith("moonshot-") or model2.startswith("moonshot-"):
                    models_info.append(translator.get_text("models.moonshot"))
                
                if model1.startswith("glm-") or model2.startswith("glm-"):
                    models_info.append(translator.get_text("models.chatglm"))
                    
                if model1.startswith("qwen-") or model2.startswith("qwen-"):
                    models_info.append(translator.get_text("models.qwen"))
                    
                if model1.startswith("ernie-") or model2.startswith("ernie-"):
                    models_info.append(translator.get_text("models.ernie"))
                
                if models_info:
                    self.update_signal.emit(translator.get_text("ui.detected_models", ", ".join(models_info)) + "\n")
            
            self.update_signal.emit(translator.get_text("ui.configuring") + "\n")
            self.update_signal.emit(translator.get_text("ui.work_mode", 
                translator.get_text("mode.debate") if work_mode == 'debate' else translator.get_text("mode.optimization")) + "\n")
            self.update_signal.emit(translator.get_text("ui.model_info", "1", model1, self.config['temperature1']) + "\n")
            self.update_signal.emit(translator.get_text("ui.model_info", "2", model2, self.config['temperature2']) + "\n")
            
            if work_mode == 'debate':
                self.update_signal.emit(translator.get_text("ui.debate_rounds", self.config['rounds']) + "\n")
            else:
                self.update_signal.emit(translator.get_text("ui.optimization_iterations", self.config['rounds']) + "\n")
                
            self.update_signal.emit(translator.get_text("ui.streaming", 
                translator.get_text("ui.enabled") if self.config.get('stream', True) else translator.get_text("ui.disabled")) + "\n")
            
            self.update_signal.emit("\n")  # 添加空行分隔
            
            # 创建辩论包装类的实例
            debate_kwargs = {
                'api_key1': self.config['api_key1'],
                'api_key2': self.config['api_key2'],
                'model1': model1,
                'model2': model2,
                'temperature1': self.config['temperature1'],
                'temperature2': self.config['temperature2'],
                'update_signal': self.update_signal,
                'progress_signal': self.progress_signal,
                'stream': self.config.get('stream', True)
            }
            
            # 如果使用自定义API基础URL
            if 'api_base1' in self.config:
                debate_kwargs['api_base1'] = self.config['api_base1']
            if 'api_base2' in self.config:
                debate_kwargs['api_base2'] = self.config['api_base2']
            
            debate = AIDebateWrapper(**debate_kwargs)
            
            # 运行指定模式
            if work_mode == 'debate':
                # 辩论模式
                self.update_signal.emit(translator.get_text("ui.debate_start") + "\n")
                self.update_signal.emit(translator.get_text("ui.topic", self.config['question']) + "\n")
                self.update_signal.emit(translator.get_text("ui.affirmative", model1, self.config['temperature1']) + "\n")
                self.update_signal.emit(translator.get_text("ui.negative", model2, self.config['temperature2']) + "\n")
                self.update_signal.emit("-" * 50 + "\n\n")
                
                # 运行辩论
                result = debate.run_debate(
                    question=self.config['question'],
                    rounds=self.config['rounds']
                )
            else:
                # 问题优化模式
                self.update_signal.emit(translator.get_text("ui.optimization_start") + "\n")
                self.update_signal.emit(translator.get_text("ui.question", self.config['question']) + "\n")
                self.update_signal.emit(translator.get_text("ui.analyst", model1, self.config['temperature1']) + "\n")
                self.update_signal.emit(translator.get_text("ui.optimizer", model2, self.config['temperature2']) + "\n")
                self.update_signal.emit("-" * 50 + "\n\n")
                
                # 运行问题优化
                result = debate.run_optimization(
                    question=self.config['question'],
                    iterations=self.config['rounds']
                )
            
            # 保存日志
            if self.config.get('log_file'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.config['log_file']
                
                # 确保日志目录存在
                log_dir = os.path.dirname(filename)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                self.update_signal.emit("\n" + translator.get_text("ui.save_result", filename) + "\n")
            
            # 辩论结束，发送结果信号
            self.finished_signal.emit(result)
            
        except Exception as e:
            error_msg = translator.get_text("error.process", str(e))
            print(f"错误详情: {str(e)}")
            import traceback
            traceback.print_exc()
            self.error_signal.emit(error_msg)


class AIDebateWrapper(AIDebate):
    """AIDebate类的包装器，重定向输出到GUI"""
    
    def __init__(self, api_key1, api_key2, model1, model2, temperature1, temperature2, update_signal, progress_signal, 
                 stream=True, api_base1=None, api_base2=None):
        # 创建logs目录
        if not os.path.exists("logs"):
            os.makedirs("logs")
        super().__init__(api_key1, api_key2, model1, model2, temperature1, temperature2, 
                        stream=stream, log_file="logs/debate.log", 
                        api_base1=api_base1, api_base2=api_base2)
        self.update_signal = update_signal
        self.progress_signal = progress_signal
        self.current_round = 0
        self.total_rounds = 0
    
    def run_debate(self, question, rounds):
        """运行辩论并更新UI"""
        self.current_round = 0
        self.total_rounds = rounds
        
        # 替换原始的print输出，重定向到GUI
        original_print = print
        def custom_print(*args, **kwargs):
            # 将print内容发送到GUI
            text = " ".join(str(arg) for arg in args)
            # 为每条print消息添加换行，确保格式正确
            if not text.endswith("\n"):
                text += "\n"
            self.update_signal.emit(text)
            # 也保留原始print功能以便调试
            original_print(*args, **kwargs)
        
        # 替换全局print函数
        import builtins
        builtins.print = custom_print
        
        try:
            # 调用父类方法运行辩论
            result = super().run_debate(question, rounds)
            # 恢复原始print函数
            builtins.print = original_print
            return result
        except Exception as e:
            self.update_signal.emit(f"错误: {str(e)}\n")
            # 确保恢复原始print函数
            builtins.print = original_print
            raise
    
    def run_optimization(self, question, iterations):
        """运行问题优化并更新UI"""
        self.current_round = 0
        self.total_rounds = iterations
        
        # 替换原始的print输出，重定向到GUI
        original_print = print
        def custom_print(*args, **kwargs):
            # 将print内容发送到GUI
            text = " ".join(str(arg) for arg in args)
            # 为每条print消息添加换行，确保格式正确
            if not text.endswith("\n"):
                text += "\n"
            self.update_signal.emit(text)
            # 也保留原始print功能以便调试
            original_print(*args, **kwargs)
        
        # 替换全局print函数
        import builtins
        builtins.print = custom_print
        
        try:
            # 调用父类方法运行问题优化
            result = super().run_optimization(question, iterations)
            # 恢复原始print函数
            builtins.print = original_print
            return result
        except Exception as e:
            self.update_signal.emit(f"错误: {str(e)}\n")
            # 确保恢复原始print函数
            builtins.print = original_print
            raise
    
    # 移除旧的generate_response方法，因为它与父类接口不匹配
    # 实现新的方法重写父类的generate_response_stream以实现进度更新
    def generate_response_stream(self, model, temp, messages):
        """重写流式生成响应方法，实现真正的GUI流式输出"""
        self.update_signal.emit(f"\n正在使用模型 {model} 流式生成回复...\n")
        self.update_signal.emit("回复: ")
        
        try:
            # 选择合适的客户端
            if model == self.model1:
                client = self.client1
            else:
                client = self.client2
                
            # 获取客户端
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                stream=True,
            )
            
            # 收集完整回复
            collected_content = []
            
            # 处理流式响应
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    content_chunk = chunk.choices[0].delta.content
                    collected_content.append(content_chunk)
                    # 关键：将每个块实时发送到GUI
                    self.update_signal.emit(content_chunk)
            
            # 发送一个换行，完成当前响应
            self.update_signal.emit("\n\n")
            
            complete_content = "".join(collected_content)
            
            # 更新进度
            self.current_round += 0.5  # 每个回应算半个回合
            progress = int((self.current_round / (self.total_rounds * 2)) * 100)
            self.progress_signal.emit(progress)
            
            return complete_content
        except Exception as e:
            self.update_signal.emit(f"\n生成回复出错: {str(e)}\n")
            raise


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.debate_worker = None
        self.initUI()
        self.statusBar().showMessage("准备就绪", 2000)
    
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle("AI辩论与问题优化系统")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(main_widget)
        
        # 添加语言选择器
        lang_layout = QHBoxLayout()
        lang_label = QLabel('Language/语言:')
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', '简体中文'])
        self.lang_combo.setCurrentText('简体中文')  # 默认选中中文
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)
        
        # 创建设置组
        self.settings_group = QGroupBox("系统设置")
        settings_layout = QVBoxLayout()
        
        # 工作模式选择
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel("工作模式:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["辩论模式", "问题优化模式"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_combo)
        settings_layout.addLayout(mode_layout)
        
        # API密钥设置框
        api_group = QGroupBox("API密钥设置")
        api_group_layout = QVBoxLayout()
        
        # 自定义API基础URL选项
        self.custom_api_check = QCheckBox("使用自定义API基础URL")
        self.custom_api_check.stateChanged.connect(self.toggle_custom_api)
        api_group_layout.addWidget(self.custom_api_check)
        
        # 正方API设置框
        aff_api_box = QGroupBox("模型1 API设置")
        aff_api_box_layout = QVBoxLayout()
        
        # 正方API基础URL输入框
        aff_api_url_layout = QHBoxLayout()
        self.api_base1_label = QLabel("API基础URL:")
        self.aff_api_url_input = QLineEdit()
        self.aff_api_url_input.setPlaceholderText("例如: http://localhost:1234/v1")
        self.aff_api_url_input.setEnabled(False)
        aff_api_url_layout.addWidget(self.api_base1_label)
        aff_api_url_layout.addWidget(self.aff_api_url_input)
        aff_api_box_layout.addLayout(aff_api_url_layout)
        
        # 正方自定义模型名称
        aff_model_name_layout = QHBoxLayout()
        aff_model_name_label = QLabel("自定义模型名称:")
        self.aff_model_name_input = QLineEdit()
        self.aff_model_name_input.setPlaceholderText("例如: llama3 或 qwen-max")
        self.aff_model_name_input.setEnabled(False)
        aff_model_name_layout.addWidget(aff_model_name_label)
        aff_model_name_layout.addWidget(self.aff_model_name_input)
        aff_api_box_layout.addLayout(aff_model_name_layout)
        
        # 正方API密钥
        aff_api_layout = QHBoxLayout()
        self.api_key1_label = QLabel("API密钥:")
        self.aff_api_key_input = QLineEdit()
        self.aff_api_key_input.setEchoMode(QLineEdit.Password)
        aff_api_layout.addWidget(self.api_key1_label)
        aff_api_layout.addWidget(self.aff_api_key_input)
        aff_api_box_layout.addLayout(aff_api_layout)
        
        aff_api_box.setLayout(aff_api_box_layout)
        api_group_layout.addWidget(aff_api_box)
        
        # 反方API设置框
        neg_api_box = QGroupBox("模型2 API设置")
        neg_api_box_layout = QVBoxLayout()
        
        # 反方API基础URL输入框
        neg_api_url_layout = QHBoxLayout()
        self.api_base2_label = QLabel("API基础URL:")
        self.neg_api_url_input = QLineEdit()
        self.neg_api_url_input.setPlaceholderText("例如: http://localhost:5678/v1")
        self.neg_api_url_input.setEnabled(False)
        neg_api_url_layout.addWidget(self.api_base2_label)
        neg_api_url_layout.addWidget(self.neg_api_url_input)
        neg_api_box_layout.addLayout(neg_api_url_layout)
        
        # 反方自定义模型名称
        neg_model_name_layout = QHBoxLayout()
        neg_model_name_label = QLabel("自定义模型名称:")
        self.neg_model_name_input = QLineEdit()
        self.neg_model_name_input.setPlaceholderText("例如: mistral-medium 或 gemma-7b")
        self.neg_model_name_input.setEnabled(False)
        neg_model_name_layout.addWidget(neg_model_name_label)
        neg_model_name_layout.addWidget(self.neg_model_name_input)
        neg_api_box_layout.addLayout(neg_model_name_layout)
        
        # 反方API密钥
        neg_api_layout = QHBoxLayout()
        self.api_key2_label = QLabel("API密钥:")
        self.neg_api_key_input = QLineEdit()
        self.neg_api_key_input.setEchoMode(QLineEdit.Password)
        neg_api_layout.addWidget(self.api_key2_label)
        neg_api_layout.addWidget(self.neg_api_key_input)
        neg_api_box_layout.addLayout(neg_api_layout)
        
        neg_api_box.setLayout(neg_api_box_layout)
        api_group_layout.addWidget(neg_api_box)
        
        api_group.setLayout(api_group_layout)
        settings_layout.addWidget(api_group)
        
        # API提供商提示
        api_provider_info = QLabel("注意: 系统将根据模型名称自动选择对应的API提供商，或使用您指定的自定义API服务器")
        api_provider_info.setStyleSheet("color: blue;")
        settings_layout.addWidget(api_provider_info)
        
        # 辩论主题设置
        topic_layout = QHBoxLayout()
        self.topic_label = QLabel("辩论问题:")
        self.topic_input = QLineEdit()
        topic_layout.addWidget(self.topic_label)
        topic_layout.addWidget(self.topic_input)
        settings_layout.addLayout(topic_layout)
        
        # 创建模型选择组
        self.model_settings_group = QGroupBox("模型设置")
        model_layout = QHBoxLayout()
        
        # 可用的AI模型
        self.available_models = [
            # OpenAI模型
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4",
            "gpt-3.5-turbo",
            # Claude模型
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            # DeepSeek模型
            "deepseek-chat",
            "deepseek-reasoner",
            # Moonshot模型
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k",
            # ChatGLM模型
            "glm-4",
            "glm-3-turbo",
            # 通义千问模型
            "qwen-turbo",
            "qwen-plus",
            "qwen-max",
            # 文心一言模型
            "ernie-bot-4",
            "ernie-bot-turbo"
        ]
        
        # 添加API提供商分组
        self.api_providers = {
            "gpt-": "OpenAI",
            "claude-": "Anthropic",
            "deepseek-": "DeepSeek",
            "moonshot-": "Moonshot",
            "glm-": "智谱AI",
            "qwen-": "阿里云通义千问",
            "ernie-": "百度文心一言"
        }
        
        # 模型1设置
        aff_layout = QVBoxLayout()
        self.model1_label = QLabel("正方模型:")
        self.model1_combo = QComboBox()
        self.model1_combo.addItems(self.available_models)
        self.model1_combo.setCurrentIndex(0)  # 默认选择第一个模型
        self.model1_combo.currentTextChanged.connect(self.on_model_changed)
        aff_layout.addWidget(self.model1_label)
        aff_layout.addWidget(self.model1_combo)
        
        # 模型1温度设置
        temp1_layout = QHBoxLayout()
        self.temp1_label = QLabel("温度:")
        self.temp1_spin = QDoubleSpinBox()
        self.temp1_spin.setRange(0.0, 2.0)
        self.temp1_spin.setSingleStep(0.1)
        self.temp1_spin.setValue(0.7)
        temp1_layout.addWidget(self.temp1_label)
        temp1_layout.addWidget(self.temp1_spin)
        aff_layout.addLayout(temp1_layout)
        
        # 模型2设置
        neg_layout = QVBoxLayout()
        self.model2_label = QLabel("反方模型:")
        self.model2_combo = QComboBox()
        self.model2_combo.addItems(self.available_models)
        self.model2_combo.setCurrentIndex(1)  # 默认选择第二个模型
        self.model2_combo.currentTextChanged.connect(self.on_model_changed)
        neg_layout.addWidget(self.model2_label)
        neg_layout.addWidget(self.model2_combo)
        
        # 模型2温度设置
        temp2_layout = QHBoxLayout()
        self.temp2_label = QLabel("温度:")
        self.temp2_spin = QDoubleSpinBox()
        self.temp2_spin.setRange(0.0, 2.0)
        self.temp2_spin.setSingleStep(0.1)
        self.temp2_spin.setValue(0.7)
        temp2_layout.addWidget(self.temp2_label)
        temp2_layout.addWidget(self.temp2_spin)
        neg_layout.addLayout(temp2_layout)
        
        # 添加到模型布局
        model_layout.addLayout(aff_layout)
        model_layout.addLayout(neg_layout)
        self.model_settings_group.setLayout(model_layout)
        
        # 创建轮数和保存设置组
        rounds_group = QGroupBox("其他设置")
        rounds_layout = QHBoxLayout()
        
        # 轮数设置
        self.rounds_label = QLabel("辩论轮数:")
        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 10)
        self.rounds_spin.setValue(3)
        rounds_layout.addWidget(self.rounds_label)
        rounds_layout.addWidget(self.rounds_spin)
        
        # 流式输出设置
        self.stream_check = QCheckBox("流式输出")
        self.stream_check.setChecked(True)
        rounds_layout.addWidget(self.stream_check)
        
        # 保存设置
        self.save_check = QCheckBox("保存结果")
        self.save_check.setChecked(True)
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_save_path)
        self.save_path = "logs/result.json"
        
        rounds_layout.addWidget(self.save_check)
        rounds_layout.addWidget(self.browse_button)
        rounds_group.setLayout(rounds_layout)
        
        # 添加设置到主布局
        settings_layout.addWidget(self.model_settings_group)
        settings_layout.addWidget(rounds_group)
        self.settings_group.setLayout(settings_layout)
        main_layout.addWidget(self.settings_group)
        
        # 创建控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_process)
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_process)
        self.stop_button.setEnabled(False)
        self.clear_button = QPushButton("清除输出")
        self.clear_button.clicked.connect(self.clear_output)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)
        
        # 创建进度条
        progress_layout = QHBoxLayout()
        progress_label = QLabel("进度:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)
        
        # 创建分割器，分隔辩论过程和结论
        splitter = QSplitter(Qt.Vertical)
        
        # 创建输出区域
        self.output_settings_group = QGroupBox("处理过程")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 10))
        # 启用自动滚动
        self.output_text.document().blockCountChanged.connect(self.scroll_to_bottom)
        output_layout.addWidget(self.output_text)
        self.output_settings_group.setLayout(output_layout)
        
        # 创建结论显示区域
        self.conclusion_group = QGroupBox("最终答案与观点")
        conclusion_layout = QVBoxLayout()
        self.conclusion_text = QTextEdit()
        self.conclusion_text.setReadOnly(True)
        self.conclusion_text.setFont(QFont("Courier New", 10))
        conclusion_layout.addWidget(self.conclusion_text)
        self.conclusion_group.setLayout(conclusion_layout)
        
        # 添加到分割器
        splitter.addWidget(self.output_settings_group)
        splitter.addWidget(self.conclusion_group)
        splitter.setSizes([500, 200])
        
        # 添加到主布局
        main_layout.addWidget(splitter)
        
        # 初始化模式相关UI
        self.on_mode_changed(0)  # 默认为辩论模式
    
    def on_mode_changed(self, index):
        """当工作模式变化时更新UI"""
        mode = "debate" if index == 0 else "optimization"
        
        # 更新标签文本
        if mode == "debate":
            self.topic_label.setText(translator.get_text("ui.topic_label"))
            self.model1_label.setText(translator.get_text("ui.affirmative_model"))
            self.model2_label.setText(translator.get_text("ui.negative_model"))
            self.rounds_label.setText(translator.get_text("ui.debate_rounds_label"))
            self.conclusion_group.setTitle(translator.get_text("ui.final_opinions"))
            self.start_button.setText(translator.get_text("ui.start_debate"))
        else:
            self.topic_label.setText(translator.get_text("ui.question_label"))
            self.model1_label.setText(translator.get_text("ui.analyst_model"))
            self.model2_label.setText(translator.get_text("ui.optimizer_model"))
            self.rounds_label.setText(translator.get_text("ui.optimization_iterations_label"))
            self.conclusion_group.setTitle(translator.get_text("ui.final_answer"))
            self.start_button.setText(translator.get_text("ui.start_optimization"))
        
        # 更新状态栏
        if mode == "debate":
            self.statusBar().showMessage(translator.get_text("ui.status_debate_mode"), 3000)
        else:
            self.statusBar().showMessage(translator.get_text("ui.status_optimization_mode"), 3000)
    
    def browse_save_path(self):
        """浏览保存路径对话框"""
        options = QFileDialog.Options()
        # 根据当前模式设置默认文件名
        mode = "debate" if self.mode_combo.currentIndex() == 0 else "optimization"
        default_filename = "debate_result.json" if mode == "debate" else "optimization_result.json"
        file_name, _ = QFileDialog.getSaveFileName(
            self, "选择保存路径", os.path.join("logs", default_filename),
            "JSON文件 (*.json);;所有文件 (*)", options=options
        )
        if file_name:
            self.save_path = file_name
            # 显示简短的文件名
            short_name = os.path.basename(file_name)
            self.browse_button.setText(f".../{short_name}")
    
    def toggle_custom_api(self, state):
        """切换是否使用自定义API设置"""
        enabled = (state == Qt.Checked)
        
        # 启用/禁用正方API基础URL和模型名称输入框
        self.aff_api_url_input.setEnabled(enabled)
        self.aff_model_name_input.setEnabled(enabled)
        
        # 启用/禁用反方API基础URL和模型名称输入框
        self.neg_api_url_input.setEnabled(enabled)
        self.neg_model_name_input.setEnabled(enabled)
        
        # 启用/禁用模型选择
        self.model1_combo.setEnabled(not enabled)
        self.model2_combo.setEnabled(not enabled)
        
        if enabled:
            self.statusBar().showMessage("已启用自定义API设置，模型选择将被禁用", 5000)
            
            # 清空自定义字段，提示用户必须填写
            self.aff_model_name_input.setPlaceholderText("必填：请输入模型名称")
            self.aff_model_name_input.setStyleSheet("background-color: #FFEEEE;")
            self.neg_model_name_input.setPlaceholderText("必填：请输入模型名称")
            self.neg_model_name_input.setStyleSheet("background-color: #FFEEEE;")
        else:
            self.statusBar().showMessage("已禁用自定义API设置，将根据模型名称自动选择API服务器", 5000)
            self.aff_model_name_input.setPlaceholderText("例如: llama3 或 qwen-max")
            self.aff_model_name_input.setStyleSheet("")
            self.neg_model_name_input.setPlaceholderText("例如: mistral-medium 或 gemma-7b")
            self.neg_model_name_input.setStyleSheet("")
    
    def start_process(self):
        """启动辩论或优化进程"""
        # 获取当前模式
        mode = "debate" if self.mode_combo.currentIndex() == 0 else "optimization"
        
        # 检查必要条件
        if not (self.aff_api_key_input.text() and self.neg_api_key_input.text()):
            QMessageBox.warning(self, "缺少API密钥", f"请为{'正方和反方' if mode == 'debate' else '分析师和优化师'}分别输入API密钥")
            return
            
        if not self.topic_input.text():
            QMessageBox.warning(self, "缺少内容", f"请输入{'辩论主题' if mode == 'debate' else '待优化问题'}")
            return
            
        # 检查如果使用自定义URL但没有输入模型名称
        if self.custom_api_check.isChecked():
            if not self.aff_api_url_input.text():
                QMessageBox.warning(self, "缺少API基础URL", "使用自定义API时，必须输入模型1的API基础URL")
                return
                
            if not self.neg_api_url_input.text():
                QMessageBox.warning(self, "缺少API基础URL", "使用自定义API时，必须输入模型2的API基础URL")
                return
                
            if not self.aff_model_name_input.text():
                QMessageBox.warning(self, "缺少模型名称", "使用自定义API基础URL时，必须输入模型1的自定义模型名称")
                return
                
            if not self.neg_model_name_input.text():
                QMessageBox.warning(self, "缺少模型名称", "使用自定义API基础URL时，必须输入模型2的自定义模型名称")
                return
        
        # 准备配置
        config = {
            'mode': mode,
            'use_separate_api': True,
            'api_key1': self.aff_api_key_input.text(),
            'api_key2': self.neg_api_key_input.text(),
            'temperature1': self.temp1_spin.value(),
            'temperature2': self.temp2_spin.value(),
            'question': self.topic_input.text(),
            'rounds': self.rounds_spin.value(),
            'stream': self.stream_check.isChecked()
        }
        
        # 如果使用自定义API
        if self.custom_api_check.isChecked():
            config['api_base1'] = self.aff_api_url_input.text()
            config['api_base2'] = self.neg_api_url_input.text()
            config['custom_model1'] = self.aff_model_name_input.text()
            config['custom_model2'] = self.neg_model_name_input.text()
            config['model1'] = self.aff_model_name_input.text()  # 使用自定义模型名称
            config['model2'] = self.neg_model_name_input.text()  # 使用自定义模型名称
        else:
            config['model1'] = self.model1_combo.currentText()
            config['model2'] = self.model2_combo.currentText()
        
        # 如果选择了保存，添加日志文件路径
        if self.save_check.isChecked():
            # 根据模式设置默认保存文件名
            if not self.save_path or self.save_path == "logs/result.json":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if mode == "debate":
                    self.save_path = f"logs/debate_result_{timestamp}.json"
                else:
                    self.save_path = f"logs/optimization_result_{timestamp}.json"
            
            config['log_file'] = self.save_path
        
        # 清除之前的输出
        self.output_text.clear()
        self.conclusion_text.clear()
        self.progress_bar.setValue(0)
        
        # 创建工作线程并启动
        self.debate_worker = DebateWorker(config)
        self.debate_worker.update_signal.connect(self.update_output)
        self.debate_worker.progress_signal.connect(self.progress_bar.setValue)
        self.debate_worker.finished_signal.connect(self.process_finished)
        self.debate_worker.error_signal.connect(self.show_error)
        self.debate_worker.start()
        
        # 更新按钮状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
    
    def stop_process(self):
        """停止辩论或优化进程"""
        if self.debate_worker and self.debate_worker.isRunning():
            self.debate_worker.stop()
            self.debate_worker.wait()
            mode = "辩论" if self.mode_combo.currentIndex() == 0 else "优化"
            self.update_output(f"\n{mode}已停止\n")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    @pyqtSlot(str)
    def update_output(self, text):
        """更新输出文本框"""
        # 直接追加文本，不添加额外换行
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.output_text.setTextCursor(cursor)
        
        # 实时更新UI，确保每个token都能立即显示
        # 强制立即重绘
        self.output_text.viewport().update()
        QApplication.processEvents()
        
        # 确保文本框滚动到最新位置
        self.scroll_to_bottom()
    
    @pyqtSlot(dict)
    def process_finished(self, result):
        """处理完成时的处理"""
        # 在结论区域显示结果
        self.conclusion_text.clear()
        
        # 获取当前模式
        mode = "debate" if self.mode_combo.currentIndex() == 0 else "optimization"
        
        # 根据模式调整显示逻辑
        initial_question = result.get('initial_question', '')
        if mode == "debate":
            conclusion_text = f"问题: {initial_question}\n\n"
            
            # 获取对话历史并显示
            conversation = result.get('conversation', [])
            if conversation:
                conclusion_text += "观点汇总:\n\n"
                for i, entry in enumerate(conversation):
                    role = entry.get('role', '未知')
                    content = entry.get('content', '')
                    if role != "最终结论":  # 最终结论单独展示
                        conclusion_text += f"【{role}】\n{content}\n\n"
                        conclusion_text += "-" * 40 + "\n\n"
            
            # 显示最终结论（如果有）
            if 'final_answer' in result:
                conclusion_text += f"最终答案:\n{result.get('final_answer', '')}\n"
        else:
            # 优化模式的显示逻辑
            conclusion_text = f"问题: {initial_question}\n\n"
            
            # 获取优化过程并显示
            conversation = result.get('conversation', [])
            if conversation:
                conclusion_text += "答案优化过程:\n\n"
                for i, entry in enumerate(conversation):
                    role = entry.get('role', '未知')
                    content = entry.get('content', '')
                    if role != "最终优化答案":  # 最终结果单独展示
                        conclusion_text += f"【{role}】\n{content}\n\n"
                        conclusion_text += "-" * 40 + "\n\n"
            
            # 显示最终优化结果（如果有）
            if 'final_result' in result:
                conclusion_text += f"最终优化答案:\n{result.get('final_result', '')}\n"
        
        self.conclusion_text.setText(conclusion_text)
        
        # 更新按钮状态
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 更新进度条为100%
        self.progress_bar.setValue(100)
        
        # 通知用户已完成
        process_name = "辩论" if mode == "debate" else "答案优化"
        self.update_output(f"\n{process_name}已完成! 您的问题已得到答案，请查看下方的结果区域。\n")
    
    @pyqtSlot(str)
    def show_error(self, error_message):
        """显示错误消息"""
        QMessageBox.critical(self, translator.get_text("error.title", "Error"), error_message)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def on_model_changed(self, model_name):
        """当模型选择改变时调用"""
        # 根据模型前缀识别API提供商
        for prefix, provider in self.api_providers.items():
            if model_name.startswith(prefix):
                self.statusBar().showMessage(f"已选择{provider}模型，将使用{provider} API接口", 5000)
                break
    
    def clear_output(self):
        """清除输出区域"""
        self.output_text.clear()
        self.conclusion_text.clear()
        self.progress_bar.setValue(0)

    def scroll_to_bottom(self):
        """滚动到文本框底部"""
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

    def change_language(self, lang_text):
        """切换界面语言"""
        lang = 'en' if lang_text == 'English' else 'zh'
        if translator.set_language(lang):
            self.update_ui_texts()
    
    def update_ui_texts(self):
        """更新界面上的所有文本"""
        # 更新窗口标题
        self.setWindowTitle(translator.get_text("ui.window_title"))
        
        # 更新设置组
        self.settings_group.setTitle(translator.get_text("ui.settings"))
        
        # 更新模式选择
        self.mode_label.setText(translator.get_text("ui.mode_label"))
        mode_items = [
            translator.get_text("mode.debate"),
            translator.get_text("mode.optimization")
        ]
        current_index = self.mode_combo.currentIndex()
        self.mode_combo.clear()
        self.mode_combo.addItems(mode_items)
        self.mode_combo.setCurrentIndex(current_index)
        
        # 更新API设置组
        api_boxes = self.settings_group.findChildren(QGroupBox)
        for box in api_boxes:
            if box.title() == "API密钥设置":
                box.setTitle(translator.get_text("ui.api_settings"))
            elif box.title() == "模型1 API设置":
                box.setTitle(translator.get_text("ui.model1_api_settings"))
            elif box.title() == "模型2 API设置":
                box.setTitle(translator.get_text("ui.model2_api_settings"))
        
        # 更新模型设置组
        self.model_settings_group.setTitle(translator.get_text("ui.model_settings"))
        
        # 更新其他设置组
        other_settings = self.settings_group.findChildren(QGroupBox)
        for box in other_settings:
            if box.title() == "其他设置":
                box.setTitle(translator.get_text("ui.other_settings"))
        
        # 更新模型1设置
        # 这里不更新model1_label和model2_label，因为它们在on_mode_changed中处理
        self.temp1_label.setText(translator.get_text("ui.temperature"))
        self.api_key1_label.setText(translator.get_text("ui.api_key"))
        
        # 更新模型2设置
        self.temp2_label.setText(translator.get_text("ui.temperature"))
        self.api_key2_label.setText(translator.get_text("ui.api_key"))
        
        # 更新自定义API设置
        self.custom_api_check.setText(translator.get_text("ui.custom_api"))
        if hasattr(self, 'api_base1_label'):
            self.api_base1_label.setText(translator.get_text("ui.api_base_url"))
        if hasattr(self, 'api_base2_label'):
            self.api_base2_label.setText(translator.get_text("ui.api_base_url"))
            
        # 更新API提示信息
        api_info_labels = self.settings_group.findChildren(QLabel)
        for label in api_info_labels:
            if "注意:" in label.text():
                label.setText(translator.get_text("ui.api_provider_note"))
        
        # 更新回合数设置 - 根据模式在on_mode_changed中处理
        
        # 更新主题/问题输入 - 根据模式在on_mode_changed中处理
        self.topic_input.setPlaceholderText(translator.get_text("ui.topic_placeholder"))
        
        # 更新输出设置组
        self.output_settings_group.setTitle(translator.get_text("ui.processing"))
        self.stream_check.setText(translator.get_text("ui.stream_output"))
        self.save_check.setText(translator.get_text("ui.save_to_file"))
        self.browse_button.setText(translator.get_text("ui.browse"))
        
        # 更新控制按钮 - 开始按钮根据模式在on_mode_changed中处理
        self.stop_button.setText(translator.get_text("ui.stop"))
        self.clear_button.setText(translator.get_text("ui.clear"))
        
        # 更新进度相关文本
        progress_labels = self.findChildren(QLabel)
        for label in progress_labels:
            if label.text() == "进度:":
                label.setText(translator.get_text("ui.progress"))
        
        # 再次调用on_mode_changed来更新与模式相关的文本
        self.on_mode_changed(self.mode_combo.currentIndex())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建窗口并显示
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_()) 