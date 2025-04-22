import os
import openai
import time
import argparse
import traceback
import sys
import json
import datetime
from typing import List, Dict, Any

class AIDebate:
    def __init__(self, api_key1: str, api_key2: str, model1: str = "gpt-3.5-turbo", model2: str = "gpt-3.5-turbo", 
                 temperature1: float = 0.7, temperature2: float = 0.7, 
                 stream: bool = False, log_file: str = None, log_level: str = "info",
                 api_base1: str = None, api_base2: str = None):
        """
        初始化AI辩论程序
        
        参数:
            api_key1: 第一个模型的API密钥
            api_key2: 第二个模型的API密钥
            model1: 第一个AI模型名称
            model2: 第二个AI模型名称
            temperature1: 第一个模型的温度参数
            temperature2: 第二个模型的温度参数
            stream: 是否使用流式输出
            log_file: 日志文件路径，如果为None则不记录到文件
            log_level: 日志级别（debug, info, warning, error）
            api_base1: 第一个模型的API基础URL(可选)
            api_base2: 第二个模型的API基础URL(可选)
        """
        self.stream = stream
        self.log_file = log_file
        self.log_level = log_level.lower()
        
        # 初始化日志
        self.init_logging()
        self.log("info", "初始化AI辩论系统")
        self.log("info", f"模型设置: 模型1={model1}, 模型2={model2}, 温度1={temperature1}, 温度2={temperature2}")
        self.log("info", f"流式输出: {'启用' if stream else '禁用'}")
        
        # 记录自定义API基础URL
        if api_base1:
            self.log("info", f"模型1使用自定义API基础URL: {api_base1}")
        if api_base2:
            self.log("info", f"模型2使用自定义API基础URL: {api_base2}")
        
        # 根据模型确定API类型
        self.api_type1, base_url1 = self._determine_api_type(model1, api_base1)
        self.api_type2, base_url2 = self._determine_api_type(model2, api_base2)
        
        # 记录API类型
        self.log("info", f"模型1 API类型: {self.api_type1.upper()}")
        self.log("info", f"模型2 API类型: {self.api_type2.upper()}")
        
        # 保存API密钥
        self.key1 = api_key1
        self.key2 = api_key2
        
        try:
            # 初始化客户端1
            if self.api_type1 == "openai":
                self.client1 = openai.OpenAI(api_key=self.key1)
            else:
                self.client1 = openai.OpenAI(api_key=self.key1, base_url=base_url1)
            
            print(f"模型1 {self.api_type1.upper()} API客户端初始化成功")
            self.log("info", f"模型1 {self.api_type1.upper()} API客户端初始化成功")
            
            # 初始化客户端2
            if self.api_type2 == "openai":
                self.client2 = openai.OpenAI(api_key=self.key2)
            else:
                self.client2 = openai.OpenAI(api_key=self.key2, base_url=base_url2)
            
            print(f"模型2 {self.api_type2.upper()} API客户端初始化成功")
            self.log("info", f"模型2 {self.api_type2.upper()} API客户端初始化成功")
            
        except Exception as e:
            print(f"API客户端初始化失败: {str(e)}")
            self.log("error", f"API客户端初始化失败: {str(e)}")
            traceback.print_exc()
            raise
            
        self.model1 = model1
        self.model2 = model2
        self.temperature1 = temperature1
        self.temperature2 = temperature2
    
    def _determine_api_type(self, model: str, api_base: str = None) -> (str, str):
        """
        根据模型名称和API基础URL确定API类型和基础URL
        
        参数:
            model: 模型名称
            api_base: 自定义API基础URL
            
        返回:
            (api_type, base_url): API类型和基础URL的元组
        """
        # 如果提供了自定义API基础URL，直接使用
        if api_base:
            self.log("info", f"使用自定义API基础URL: {api_base}")
            return "custom", api_base
            
        # 根据模型名称自动识别API类型和基础URL
        if model.startswith("gpt"):
            return "openai", None
        elif model.startswith("deepseek"):
            return "deepseek", "https://api.deepseek.com/v1"
        elif model.startswith("claude"):
            return "anthropic", "https://api.anthropic.com/v1"
        elif model.startswith("moonshot"):
            return "moonshot", "https://api.moonshot.cn/v1"
        elif model.startswith("glm"):
            return "chatglm", "https://open.bigmodel.cn/api/paas/v4"
        elif model.startswith("qwen") or model.startswith("通义"):
            return "qwen", "https://dashscope.aliyuncs.com/api/v1"
        elif model.startswith("ernie") or model.startswith("文心"):
            return "ernie", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1"
        else:
            # 默认使用OpenAI兼容格式
            self.log("warning", f"未知模型类型: {model}，使用OpenAI兼容格式")
            return "openai", None
    
    def init_logging(self):
        """初始化日志系统"""
        if self.log_file:
            # 创建日志文件目录
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 在日志文件开头写入基本信息
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"AI辩论系统日志 - 开始时间: {datetime.datetime.now()}\n")
                f.write(f"日志级别: {self.log_level}\n")
                f.write("-" * 80 + "\n\n")
    
    def log(self, level: str, message: str, data: Any = None):
        """
        记录日志
        
        参数:
            level: 日志级别（debug, info, warning, error）
            message: 日志消息
            data: 可选的额外数据
        """
        level = level.lower()
        # 根据日志级别决定是否记录
        level_priority = {"debug": 0, "info": 1, "warning": 2, "error": 3}
        if level_priority.get(level, 0) < level_priority.get(self.log_level, 1):
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        
        # 如果有额外数据且是debug级别，则记录数据
        if data is not None and level == "debug":
            if isinstance(data, (dict, list)):
                try:
                    data_str = json.dumps(data, ensure_ascii=False, indent=2)
                    log_entry += f"\n{data_str}"
                except:
                    log_entry += f"\n{str(data)}"
            else:
                log_entry += f"\n{str(data)}"
        
        # 写入日志文件
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + "\n\n")
            except Exception as e:
                print(f"写入日志文件失败: {str(e)}")
        
    def generate_response_stream(self, model: str, temp: float, messages: List[Dict[str, str]]) -> str:
        """
        使用流式输出方式生成回复
        
        参数:
            model: 使用的模型名称
            temp: 温度参数
            messages: 消息历史
            
        返回:
            生成的回复文本
        """
        print(f"正在使用模型 {model} 流式生成回复...")
        self.log("info", f"使用模型 {model} 流式生成回复")
        self.log("debug", "请求消息", messages)
        
        try:
            print(f"发送流式请求到API服务器...")
            print(f"请求参数: model={model}, temperature={temp}, stream=True")
            print(f"消息内容: {messages[-1]['content'][:50]}...")
            
            # 根据不同API提供商，可能需要调整请求参数
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temp,
                "stream": True,
            }
            
            # 选择合适的客户端
            if model == self.model1:
                client = self.client1
                api_type = self.api_type1
            else:  # model == self.model2
                client = self.client2
                api_type = self.api_type2
            
            # 特定API的额外参数
            if model.startswith("claude-") and api_type == "anthropic":
                # Anthropic API可能有不同的参数要求
                pass
            elif api_type in ["zhipu", "baidu", "moonshot"]:
                # 这些API可能有特殊参数要求
                pass
            
            stream = client.chat.completions.create(**kwargs)
            
            self.log("info", f"流式请求已发送: model={model}, temperature={temp}")
            
            print("\n--- 开始流式输出 ---")
            sys.stdout.write("回复: ")
            sys.stdout.flush()
            
            # 收集完整回复
            collected_content = []
            
            # 处理流式响应
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    content_chunk = chunk.choices[0].delta.content
                    collected_content.append(content_chunk)
                    # 打印片段
                    sys.stdout.write(content_chunk)
                    sys.stdout.flush()
            
            # 打印一个换行
            sys.stdout.write("\n\n")
            sys.stdout.flush()
            print("--- 流式输出结束 ---\n")
            
            complete_content = "".join(collected_content)
            self.log("info", f"流式回复完成, 长度={len(complete_content)}")
            self.log("debug", "完整回复", complete_content)
            
            return complete_content.strip()
            
        except Exception as e:
            print(f"流式生成回复时出错: {e}")
            self.log("error", f"流式生成回复出错: {str(e)}")
            print("详细错误信息:")
            traceback.print_exc()
            
            # 更详细的错误信息
            if "401" in str(e):
                print("API密钥验证失败！请检查您的API密钥是否正确。")
                self.log("error", "API密钥验证失败")
            elif "429" in str(e):
                print("API调用频率超限！请降低请求频率或等待一段时间后再试。")
                self.log("error", "API调用频率超限")
            elif "500" in str(e) or "502" in str(e) or "503" in str(e):
                print("API服务器错误！请稍后重试。")
                self.log("error", "API服务器错误")
            elif "invalid_request_error" in str(e):
                print("请求格式错误！请检查模型名称等参数是否正确。")
                self.log("error", "请求格式错误")
            
            return f"无法生成回复，请检查API密钥或网络连接。错误详情: {str(e)}"
        
    def generate_response(self, model: str, temp: float, messages: List[Dict[str, str]]) -> str:
        """
        使用指定的模型生成回复
        
        参数:
            model: 使用的模型名称
            temp: 温度参数
            messages: 消息历史
            
        返回:
            生成的回复文本
        """
        # 如果启用了流式输出，使用流式方法
        if self.stream:
            return self.generate_response_stream(model, temp, messages)
            
        print(f"正在使用模型 {model} 生成回复...")
        self.log("info", f"使用模型 {model} 生成回复")
        self.log("debug", "请求消息", messages)
        
        try:
            print(f"发送请求到API服务器...")
            print(f"请求参数: model={model}, temperature={temp}")
            print(f"消息内容: {messages[-1]['content'][:50]}...")
            
            # 根据不同API提供商，可能需要调整请求参数
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temp,
            }
            
            # 选择合适的客户端
            if model == self.model1:
                client = self.client1
                api_type = self.api_type1
            else:  # model == self.model2
                client = self.client2
                api_type = self.api_type2
            
            # 特定API的额外参数
            if model.startswith("claude-") and api_type == "anthropic":
                # Anthropic API可能有不同的参数要求
                pass
            elif api_type in ["zhipu", "baidu", "moonshot"]:
                # 这些API可能有特殊参数要求
                pass
            
            response = client.chat.completions.create(**kwargs)
            
            print(f"API请求成功!")
            self.log("info", "API请求成功")
            
            result = response.choices[0].message.content.strip()
            print(f"收到回复，内容长度: {len(result)} 字符")
            self.log("info", f"收到回复，长度={len(result)}")
            self.log("debug", "回复内容", result)
            
            return result
        except Exception as e:
            print(f"生成回复时出错: {e}")
            self.log("error", f"生成回复出错: {str(e)}")
            print("详细错误信息:")
            traceback.print_exc()
            
            # 更详细的错误信息
            if "401" in str(e):
                print("API密钥验证失败！请检查您的API密钥是否正确。")
                self.log("error", "API密钥验证失败")
            elif "429" in str(e):
                print("API调用频率超限！请降低请求频率或等待一段时间后再试。")
                self.log("error", "API调用频率超限")
            elif "500" in str(e) or "502" in str(e) or "503" in str(e):
                print("API服务器错误！请稍后重试。")
                self.log("error", "API服务器错误")
            elif "invalid_request_error" in str(e):
                print("请求格式错误！请检查模型名称等参数是否正确。")
                self.log("error", "请求格式错误")
            
            return f"无法生成回复，请检查API密钥或网络连接。错误详情: {str(e)}"
    
    def run_debate(self, initial_question: str, rounds: int = 3) -> Dict[str, Any]:
        """
        运行AI之间的辩论
        
        参数:
            initial_question: 初始问题
            rounds: 辩论回合数
            
        返回:
            包含完整对话历史和最终答案的字典
        """
        print(f"初始问题: {initial_question}\n")
        print(f"使用模型: {self.model1} 和 {self.model2}")
        print(f"API类型: {self.api_type1}, {self.api_type2}")
        print(f"流式输出: {'启用' if self.stream else '禁用'}\n")
        
        self.log("info", f"开始辩论，主题: {initial_question}")
        self.log("info", f"辩论回合数: {rounds}")
        
        conversation = []
        
        # 设置AI的角色特性，使其更有辩论性
        ai1_role = f"你是一个具有批判性思维的AI助手，名为'AI 1'。你擅长从多角度思考问题，但倾向于支持主流、传统观点。你应该为自己的观点辩护，同时批判另一个AI可能存在的逻辑漏洞。"
        ai2_role = f"你是一个具有创新思维的AI助手，名为'AI 2'。你擅长提出新颖的想法和视角，倾向于支持非传统、前沿观点。你应该为自己的观点辩护，同时批判另一个AI可能存在的局限性。"
        
        # 第一阶段：各自陈述初始观点
        print("==========================================")
        print("阶段1: 各自陈述初始观点")
        self.log("info", "阶段1: 各自陈述初始观点")
        
        # AI 1 提出初始观点
        messages1 = [
            {"role": "system", "content": ai1_role},
            {"role": "user", "content": f"请对以下问题提出你的观点和论据：{initial_question}。请保持逻辑性和条理性，限制在300字以内。"}
        ]
        
        print(f"\n-- AI 1 ({self.model1}) 陈述观点 --")
        self.log("info", f"AI 1 ({self.model1}) 陈述初始观点")
        ai1_initial = self.generate_response(self.model1, self.temperature1, messages1)
        print(f"AI 1 ({self.model1}) 初始观点:\n{ai1_initial}\n")
        self.log("info", f"AI 1 初始观点已生成，长度={len(ai1_initial)}")
        
        conversation.append({"role": f"AI 1 ({self.model1})", "content": ai1_initial})
        
        # AI 2 提出初始观点
        messages2 = [
            {"role": "system", "content": ai2_role},
            {"role": "user", "content": f"请对以下问题提出你的观点和论据：{initial_question}。尽量提供与主流观点不同的视角，保持逻辑性和条理性，限制在300字以内。"}
        ]
        
        print(f"\n-- AI 2 ({self.model2}) 陈述观点 --")
        self.log("info", f"AI 2 ({self.model2}) 陈述初始观点")
        ai2_initial = self.generate_response(self.model2, self.temperature2, messages2)
        print(f"AI 2 ({self.model2}) 初始观点:\n{ai2_initial}\n")
        self.log("info", f"AI 2 初始观点已生成，长度={len(ai2_initial)}")
        
        conversation.append({"role": f"AI 2 ({self.model2})", "content": ai2_initial})
        
        # 记录当前的观点，用于后续辩论
        ai1_current = ai1_initial
        ai2_current = ai2_initial
        
        # 第二阶段：相互辩论
        for i in range(rounds):
            print(f"==========================================")
            print(f"阶段2: 第 {i+1}/{rounds} 轮辩论")
            self.log("info", f"阶段2: 第 {i+1}/{rounds} 轮辩论")
            
            # AI 1 反驳 AI 2
            print(f"\n-- AI 1 ({self.model1}) 反驳 AI 2 --")
            self.log("info", f"AI 1 ({self.model1}) 反驳 AI 2")
            messages1 = [
                {"role": "system", "content": ai1_role},
                {"role": "user", "content": f"原始问题：{initial_question}\n\n你的观点：\n{ai1_current}\n\n对方观点：\n{ai2_current}\n\n请针对对方观点中的弱点进行反驳，同时强化自己的论点。保持逻辑性和条理性，限制在250字以内。"}
            ]
            
            ai1_response = self.generate_response(self.model1, self.temperature1, messages1)
            print(f"AI 1 ({self.model1}) 反驳:\n{ai1_response}\n")
            self.log("info", f"AI 1 反驳已生成，长度={len(ai1_response)}")
            
            conversation.append({"role": f"AI 1 ({self.model1})", "content": ai1_response})
            ai1_current = ai1_response
            
            # 短暂暂停，避免API限制
            time.sleep(1)
            
            # AI 2 反驳 AI 1
            print(f"\n-- AI 2 ({self.model2}) 反驳 AI 1 --")
            self.log("info", f"AI 2 ({self.model2}) 反驳 AI 1")
            messages2 = [
                {"role": "system", "content": ai2_role},
                {"role": "user", "content": f"原始问题：{initial_question}\n\n你的观点：\n{ai2_current}\n\n对方观点：\n{ai1_response}\n\n请针对对方观点中的弱点进行反驳，同时强化自己的论点。保持逻辑性和条理性，限制在250字以内。"}
            ]
            
            ai2_response = self.generate_response(self.model2, self.temperature2, messages2)
            print(f"AI 2 ({self.model2}) 反驳:\n{ai2_response}\n")
            self.log("info", f"AI 2 反驳已生成，长度={len(ai2_response)}")
            
            conversation.append({"role": f"AI 2 ({self.model2})", "content": ai2_response})
            ai2_current = ai2_response
            
            # 短暂暂停，避免API限制
            time.sleep(1)
        
        # 第三阶段：得出最终综合结论
        print("==========================================")
        print("阶段3: 综合结论")
        self.log("info", "阶段3: 生成综合结论")
        
        # 整合所有对话内容，向第三个AI请求综合
        debate_history = "\n\n".join([
            f"问题: {initial_question}",
            f"AI 1 初始观点: {ai1_initial}",
            f"AI 2 初始观点: {ai2_initial}"
        ])
        
        for i in range(rounds):
            debate_history += f"\n\n第 {i+1} 轮辩论:"
            debate_history += f"\nAI 1 反驳: {conversation[2*i+2]['content']}"
            debate_history += f"\nAI 2 反驳: {conversation[2*i+3]['content']}"
        
        # 使用两个模型中性能更强的一个来生成最终结论
        conclusion_model = self.model1 if self.model1.startswith("gpt-4") or self.model1.startswith("deepseek-reasoner") else self.model2
        
        conclusion_messages = [
            {"role": "system", "content": "你是一个公正、全面的总结者。你的任务是分析两个AI之间的辩论，找出关键洞见，并提供一个平衡、综合的结论。"},
            {"role": "user", "content": f"以下是两个AI围绕问题\"{initial_question}\"进行的辩论。请分析双方的观点和论据，然后提供一个平衡的结论，指出最有价值的见解。不要简单重复双方观点，而是真正整合它们的精华部分。\n\n{debate_history}"}
        ]
        
        print(f"\n-- 生成最终结论 (使用 {conclusion_model}) --")
        self.log("info", f"生成最终结论，使用模型: {conclusion_model}")
        conclusion = self.generate_response(conclusion_model, 0.6, conclusion_messages)
        print(f"最终结论:\n{conclusion}\n")
        self.log("info", f"最终结论已生成，长度={len(conclusion)}")
        
        # 添加到对话历史
        conversation.append({"role": "最终结论", "content": conclusion})
        
        # 日志记录完整对话
        self.log("info", "辩论完成，记录完整对话历史")
        self.create_full_conversation_log(initial_question, conversation)
        
        return {
            "initial_question": initial_question,
            "conversation": conversation,
            "final_answer": conclusion
        }
    
    def create_full_conversation_log(self, question: str, conversation: List[Dict[str, str]]):
        """创建包含完整对话的日志文件"""
        if not self.log_file:
            return
            
        log_dir = os.path.dirname(self.log_file)
        conversation_log = os.path.join(log_dir, f"conversation_{int(time.time())}.txt")
        
        try:
            with open(conversation_log, 'w', encoding='utf-8') as f:
                f.write(f"辩论主题: {question}\n")
                f.write(f"时间: {datetime.datetime.now()}\n")
                f.write(f"模型: {self.model1} 和 {self.model2}\n")
                f.write("-" * 80 + "\n\n")
                
                for msg in conversation:
                    f.write(f"【{msg['role']}】\n")
                    f.write(f"{msg['content']}\n\n")
                    f.write("-" * 40 + "\n\n")
            
            self.log("info", f"完整对话已保存至: {conversation_log}")
            print(f"完整对话日志已保存至: {conversation_log}")
        except Exception as e:
            self.log("error", f"保存对话日志失败: {str(e)}")
            print(f"保存对话日志失败: {str(e)}")
    
    def save_debate(self, debate_result: Dict[str, Any], filename: str = "ai_debate_result.txt"):
        """
        保存辩论结果到文件
        
        参数:
            debate_result: 辩论结果
            filename: 保存的文件名
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"辩论主题: {debate_result['initial_question']}\n\n")
                f.write("===== 辩论过程 =====\n\n")
                
                for i, message in enumerate(debate_result['conversation']):
                    if message['role'] == "最终结论":
                        continue  # 跳过，因为我们会在后面单独输出
                    f.write(f"{message['role']}:\n{message['content']}\n\n")
                    
                f.write("===== 最终结论 =====\n\n")
                f.write(debate_result['final_answer'])
            
            print(f"辩论结果已保存到 {filename}")
            self.log("info", f"辩论结果已保存到 {filename}")
        except Exception as e:
            print(f"保存结果到文件失败: {str(e)}")
            self.log("error", f"保存结果到文件失败: {str(e)}")
            traceback.print_exc()

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

def main():
    parser = argparse.ArgumentParser(description="AI辩论：让两个AI进行辩论并得出综合结论")
    parser.add_argument("--api_key1", type=str, required=True, help="第一个模型的API密钥")
    parser.add_argument("--api_key2", type=str, required=True, help="第二个模型的API密钥")
    parser.add_argument("--question", type=str, default="人工智能是否会超越人类智能？", help="辩论主题/问题")
    parser.add_argument("--rounds", type=int, default=3, help="辩论回合数")
    parser.add_argument("--model1", type=str, default="gpt-3.5-turbo", help="第一个AI模型")
    parser.add_argument("--model2", type=str, default="gpt-3.5-turbo", help="第二个AI模型")
    parser.add_argument("--temp1", type=float, default=0.7, help="第一个AI的温度参数")
    parser.add_argument("--temp2", type=float, default=0.7, help="第二个AI的温度参数")
    parser.add_argument("--output", type=str, default="ai_debate_result.txt", help="输出文件名")
    parser.add_argument("--api_base1", type=str, help="第一个模型的API基础URL")
    parser.add_argument("--api_base2", type=str, help="第二个模型的API基础URL")
    parser.add_argument("--stream", action="store_true", help="启用流式输出")
    parser.add_argument("--log", type=str, default="logs/debate.log", help="日志文件路径")
    parser.add_argument("--log_level", type=str, default="info", choices=["debug", "info", "warning", "error"], help="日志级别")
    
    args = parser.parse_args()
    
    # 检查API密钥
    api_key1 = args.api_key1
    api_key2 = args.api_key2
    
    if not api_key1 or not api_key2:
        # 检查各种可能的API密钥环境变量
        api_key_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "DEEPSEEK_API_KEY",
            "MOONSHOT_API_KEY",
            "ZHIPU_API_KEY",
            "ERNIE_API_KEY",
            "BAIDU_API_KEY"
        ]
        
        if not api_key1:
            for var in api_key_vars:
                api_key1 = os.environ.get(var)
                if api_key1:
                    print(f"使用环境变量 {var} 中的API密钥作为第一个模型的API密钥")
                    break
                    
        if not api_key2:
            for var in api_key_vars:
                api_key2 = os.environ.get(var)
                if api_key2:
                    print(f"使用环境变量 {var} 中的API密钥作为第二个模型的API密钥")
                    break
    
    if not api_key1 or not api_key2:
        print("错误: 请提供两个模型的API密钥，通过--api_key1和--api_key2参数或设置相应的环境变量。")
        print("支持的环境变量: OPENAI_API_KEY, ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, MOONSHOT_API_KEY, ZHIPU_API_KEY, ERNIE_API_KEY, BAIDU_API_KEY")
        return
    
    # 记录API基础URL
    api_base1 = args.api_base1
    if api_base1:
        print(f"使用第一个模型的自定义API基础URL: {api_base1}")
        
    api_base2 = args.api_base2
    if api_base2:
        print(f"使用第二个模型的自定义API基础URL: {api_base2}")
    
    try:
        print(f"初始化AI辩论，模型1: {args.model1}, 模型2: {args.model2}")
        print(f"流式输出: {'启用' if args.stream else '禁用'}")
        print(f"日志记录: 文件={args.log}, 级别={args.log_level}")
        
        # 创建日志目录
        if args.log:
            log_dir = os.path.dirname(args.log)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
        
        debate = AIDebate(
            api_key1=api_key1,
            api_key2=api_key2,
            model1=args.model1,
            model2=args.model2,
            temperature1=args.temp1,
            temperature2=args.temp2,
            stream=args.stream,
            log_file=args.log,
            log_level=args.log_level,
            api_base1=api_base1,
            api_base2=api_base2
        )
        
        print(f"开始辩论，主题: {args.question}")
        result = debate.run_debate(args.question, args.rounds)
        
        print(f"保存结果到文件: {args.output}")
        debate.save_debate(result, args.output)
        
        print("程序成功完成！")
        print(f"完整对话日志可在logs目录中查看")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        traceback.print_exc()
        print("\n请检查以下可能的问题:")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. API服务是否可用")
        print("4. 模型名称是否正确")
        print("5. 是否有足够的API调用额度")
    
if __name__ == "__main__":
    main() 