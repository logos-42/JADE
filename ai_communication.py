import requests
import json
import time
import logging
import zlib
import base64
import re
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Tuple
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AI_Communication')

@dataclass
class EfficodePacket:
    """Efficode数据包结构"""
    op_code: str  # 操作码: DID/REQ/DATA/ACK/ERROR
    params: Dict[str, Any]  # 参数
    sender: str  # 发送者ID
    timestamp: float = time.time()  # 时间戳
    
    def to_string(self) -> str:
        """将数据包转换为Efficode字符串格式"""
        prefix = {
            "DID": "@",
            "REQ": "#",
            "DATA": "#",
            "ACK": "!",
            "ERROR": "!"
        }.get(self.op_code, "#")
        
        # 构建参数字符串
        param_str = ""
        if self.params:
            if self.op_code in ["DID", "ACK", "ERROR"]:
                param_str = f":{json.dumps(self.params, ensure_ascii=False)}"
            else:
                param_parts = []
                for k, v in self.params.items():
                    if isinstance(v, dict):
                        param_parts.append(f"{k}={json.dumps(v, ensure_ascii=False)}")
                    else:
                        param_parts.append(f"{k}={v}")
                param_str = f"?{'&'.join(param_parts)}"
        
        return f"{prefix}{self.op_code}{param_str}"
    
    @classmethod
    def from_string(cls, message: str, sender: str) -> 'EfficodePacket':
        """从Efficode字符串解析数据包"""
        if not message:
            return cls("ERROR", {"message": "空消息"}, sender)
        
        prefix = message[0]
        op_code_map = {
            "@": ["DID"],
            "#": ["REQ", "DATA"],
            "!": ["ACK", "ERROR"]
        }
        
        # 查找可能的操作码
        possible_op_codes = op_code_map.get(prefix, [])
        if not possible_op_codes:
            return cls("ERROR", {"message": f"未知前缀: {prefix}"}, sender)
        
        # 提取操作码和参数
        parts = message[1:].split(":", 1) if ":" in message else message[1:].split("?", 1)
        op_code = None
        
        # 确定操作码
        for code in possible_op_codes:
            if parts[0].startswith(code):
                op_code = code
                break
        
        if not op_code:
            return cls("ERROR", {"message": f"未知操作码: {parts[0]}"}, sender)
        
        # 解析参数
        params = {}
        if len(parts) > 1:
            param_str = parts[1]
            if op_code in ["DID", "ACK", "ERROR"]:
                try:
                    params = json.loads(param_str)
                except:
                    params = {"value": param_str}
            else:
                param_pairs = param_str.split("&")
                for pair in param_pairs:
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        try:
                            # 尝试解析JSON
                            if v.startswith("{") and v.endswith("}"):
                                params[k] = json.loads(v)
                            else:
                                params[k] = v
                        except:
                            params[k] = v
        
        # 检查是否有压缩数据需要解压
        packet = cls(op_code, params, sender)
        return packet.decompress_if_needed()
    
    def compress_content(self, threshold: int = 500) -> 'EfficodePacket':
        """
        压缩数据包内容，如果内容大小超过阈值
        
        Args:
            threshold: 压缩阈值（字节），默认500字节
            
        Returns:
            压缩后的数据包
        """
        if self.op_code == "DATA" and "content" in self.params:
            content = self.params["content"]
            content_str = ""
            
            # 将内容转换为字符串
            if isinstance(content, dict):
                content_str = json.dumps(content, ensure_ascii=False)
            elif isinstance(content, str):
                content_str = content
            else:
                content_str = str(content)
            
            # 检查内容大小是否超过阈值
            if len(content_str.encode('utf-8')) > threshold:
                # 压缩内容
                compressed = zlib.compress(content_str.encode('utf-8'))
                # Base64编码，确保可以安全传输
                encoded = base64.b64encode(compressed).decode('ascii')
                
                # 更新参数
                self.params["content"] = encoded
                self.params["_compressed"] = True
                self.params["_original_type"] = "json" if isinstance(content, dict) else "text"
                
                logger.info(f"内容已压缩，压缩率: {len(encoded) / len(content_str):.2f}")
        
        return self
    
    def decompress_if_needed(self) -> 'EfficodePacket':
        """
        如果数据包内容被压缩，则解压
        
        Returns:
            解压后的数据包
        """
        if self.op_code == "DATA" and self.params.get("_compressed", False):
            try:
                # 获取压缩内容
                encoded_content = self.params["content"]
                # Base64解码
                compressed = base64.b64decode(encoded_content)
                # 解压
                decompressed = zlib.decompress(compressed).decode('utf-8')
                
                # 根据原始类型恢复内容
                original_type = self.params.get("_original_type", "text")
                if original_type == "json":
                    self.params["content"] = json.loads(decompressed)
                else:
                    self.params["content"] = decompressed
                
                # 移除压缩标记
                self.params.pop("_compressed", None)
                self.params.pop("_original_type", None)
                
                logger.info("内容已解压")
            except Exception as e:
                logger.error(f"解压内容失败: {str(e)}")
        
        return self
    
    def add_metadata(self) -> 'EfficodePacket':
        """
        添加元数据，增强自解释能力
        
        Returns:
            添加元数据后的数据包
        """
        if self.op_code == "DATA" and "content" in self.params:
            content = self.params["content"]
            
            # 添加内容类型元数据
            if isinstance(content, dict):
                # 提取结构信息
                schema = {k: type(v).__name__ for k, v in content.items()}
                self.params["_metadata"] = {
                    "type": "json",
                    "schema": schema,
                    "keys": list(content.keys())
                }
            elif isinstance(content, str):
                # 尝试检测内容类型
                content_type = self._detect_content_type(content)
                self.params["_metadata"] = {
                    "type": "text",
                    "content_type": content_type,
                    "length": len(content)
                }
        
        return self
    
    def _detect_content_type(self, text: str) -> str:
        """
        检测文本内容类型
        
        Args:
            text: 要检测的文本
            
        Returns:
            内容类型
        """
        # 检测是否是JSON
        if text.strip().startswith('{') and text.strip().endswith('}'):
            try:
                json.loads(text)
                return "json"
            except:
                pass
        
        # 检测是否是URL
        if text.startswith(('http://', 'https://')):
            return "url"
        
        # 检测是否是代码
        code_patterns = [
            r'def\s+\w+\s*\(.*\):',  # Python函数
            r'function\s+\w+\s*\(.*\)',  # JavaScript函数
            r'class\s+\w+',  # 类定义
            r'import\s+\w+',  # 导入语句
            r'<\w+>.*</\w+>'  # HTML标签
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return "code"
        
        # 检测是否是问题
        if '?' in text and len(text) < 200:
            return "question"
        
        # 默认为普通文本
        return "plain_text"
    
    def extract_semantic_info(self) -> 'EfficodePacket':
        """
        提取语义信息，增强自解释能力
        
        Returns:
            添加语义信息后的数据包
        """
        if self.op_code == "REQ":
            # 提取请求意图
            req_type = self.params.get("type", "")
            if req_type:
                self.params["_semantic"] = {
                    "intent": f"request_{req_type}",
                    "expected_response": "data"
                }
        
        elif self.op_code == "DATA" and "content" in self.params:
            content = self.params.get("content", "")
            if isinstance(content, str):
                # 提取关键词
                keywords = self._extract_keywords(content)
                if keywords:
                    if "_semantic" not in self.params:
                        self.params["_semantic"] = {}
                    self.params["_semantic"]["keywords"] = keywords
        
        return self
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 要提取关键词的文本
            
        Returns:
            关键词列表
        """
        # 简单实现：提取长度大于2的词
        words = re.findall(r'\b\w{3,}\b', text.lower())
        # 过滤常见停用词
        stopwords = {'the', 'and', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'at'}
        keywords = [word for word in words if word not in stopwords]
        # 返回出现频率最高的前5个词
        word_counts = {}
        for word in keywords:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:5]]
    
    def optimize_for_transmission(self) -> 'EfficodePacket':
        """
        优化数据包以提高传输效率
        
        Returns:
            优化后的数据包
        """
        # 添加元数据
        self.add_metadata()
        
        # 提取语义信息
        self.extract_semantic_info()
        
        # 压缩内容
        self.compress_content()
        
        return self

class AIAgent:
    def __init__(self, name: str, api_key: str):
        """
        初始化AI代理
        
        Args:
            name: AI代理的名称
            api_key: API密钥
        """
        self.name = name
        self.did = f"did:efficode:{name}"
        self.api_key = api_key
        self.api_base = "https://api.siliconflow.cn/v1"  # SiliconFlow API地址
        self.model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"  # 指定模型
        self.authenticated = False
        self.peer = None  # 对话伙伴
        self.context = []  # 对话上下文
        
        logger.info(f"AI代理 {name} 已初始化")
    
    def send_message(self, message: Union[str, EfficodePacket]) -> Optional[str]:
        """调用SiliconFlow API发送消息"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 准备消息内容
            if isinstance(message, EfficodePacket):
                # 优化数据包以提高传输效率
                message.optimize_for_transmission()
                content = message.to_string()
                logger.info(f"发送到API的Efficode消息: {content}")
                
                # 提取请求类型和参数，用于构建更具体的系统提示
                request_type = None
                request_params = {}
                
                if message.op_code == "REQ":
                    request_type = message.params.get("type", "general")
                    request_params = message.params
                elif message.op_code == "DATA":
                    content_value = message.params.get("content", "")
                    if isinstance(content_value, str) and len(content_value) > 0:
                        request_type = "text"
                        request_params = {"content": content_value}
            else:
                content = message
                logger.info(f"发送到API的文本消息: {content}")
                request_type = "text"
                request_params = {"content": content}
            
            # 构建系统提示，根据请求类型提供更具体的指导
            system_prompt = """你是一个AI助手，使用Efficode语言进行通信。Efficode是一种高效的AI通信协议，使用前缀+操作码+参数的格式。

请根据请求类型提供相应的回复，并使用Efficode格式：

1. 对于天气查询 (#REQ?type=weather)：
   返回格式：#DATA?content={"location":"城市名","temperature":"温度","condition":"天气状况","humidity":"湿度","forecast":"未来预报"}&type=json

2. 对于分析请求 (#REQ?type=analysis)：
   返回格式：#DATA?content={"topic":"主题","key_points":["要点1","要点2"],"summary":"总结"}&type=json

3. 对于知识问答 (#REQ?type=knowledge)：
   返回格式：#DATA?content=详细的知识解答&type=text

4. 对于一般文本消息：
   返回格式：#DATA?content=你的回复内容&type=text

请确保回复内容是有意义的、信息丰富的，而不是模板化的。根据请求提供真实、准确的信息。

以下是一些示例对话：

示例1 - 天气查询：
用户: #REQ?type=weather&location=Beijing
助手: #DATA?content={"location":"北京","temperature":"25°C","condition":"晴朗","humidity":"45%","forecast":"未来三天气温稳定，晴好天气为主"}&type=json

示例2 - 分析请求：
用户: #REQ?type=analysis&topic=quantum_computing
助手: #DATA?content={"topic":"量子计算","key_points":["量子比特是量子计算的基本单位","量子叠加使计算能力呈指数级增长","量子纠缠是量子计算的关键特性","量子退相干是当前量子计算的主要挑战"],"summary":"量子计算利用量子力学原理进行信息处理，具有解决传统计算机难以处理的复杂问题的潜力"}&type=json

示例3 - 知识问答：
用户: #REQ?type=knowledge&query=人工智能的发展历史
助手: #DATA?content=人工智能的发展历史可以追溯到20世纪50年代。1956年的达特茅斯会议被认为是人工智能研究的正式开端。之后经历了几次起伏：60年代的早期繁荣，70-80年代的"AI寒冬"，90年代基于统计方法的复兴，以及21世纪基于深度学习的爆发式发展。近年来，大型语言模型如GPT和BERT的出现标志着AI进入了新阶段。&type=text

示例4 - 一般文本：
用户: 你好，请介绍一下自己
助手: #DATA?content=你好！我是一个使用Efficode通信协议的AI助手。我可以回答问题、提供信息和进行各种分析。有什么我可以帮助你的吗？&type=text"""
            
            # 添加特定类型请求的额外指导
            if request_type == "weather":
                location = request_params.get("location", "未知位置")
                system_prompt += f"\n\n当前是天气查询请求，请提供关于{location}的天气信息，包括温度、天气状况、湿度和未来预报。请使用真实、合理的数据，即使你无法获取实时天气信息。"
            elif request_type == "analysis":
                topic = request_params.get("topic", "未知主题")
                system_prompt += f"\n\n当前是分析请求，请提供关于{topic}的深入分析，包括关键要点和总结。分析应该全面、准确、有深度。"
            elif request_type == "knowledge":
                query = request_params.get("query", "")
                system_prompt += f"\n\n当前是知识问答请求，请提供关于'{query}'的详细解答。回答应该准确、全面、有教育意义。"
            
            # 更新上下文
            system_message = {"role": "system", "content": system_prompt}
            messages = [system_message]
            if len(self.context) > 0:
                messages.extend(self.context[-5:])  # 只保留最近5条消息作为上下文
            messages.append({"role": "user", "content": content})
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": 0.7  # 添加一些随机性
            }
            
            logger.info(f"正在调用API...")
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # 增加超时时间
            )
            
            if response.status_code == 200:
                response_json = response.json()
                response_content = response_json["choices"][0]["message"]["content"]
                logger.info(f"API响应: {response_content[:100]}...")  # 只记录前100个字符
                
                # 更新上下文
                self.context.append({"role": "user", "content": content})
                self.context.append({"role": "assistant", "content": response_content})
                
                # 保持上下文在合理大小
                if len(self.context) > 10:
                    self.context = self.context[-10:]
                    
                return response_content
            else:
                logger.error(f"API调用失败: 状态码 {response.status_code}")
                logger.error(f"错误详情: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"消息发送失败: {str(e)}")
            logger.exception("详细错误信息:")
            return None

    def process_message(self, packet: EfficodePacket) -> Optional[EfficodePacket]:
        """处理接收到的Efficode数据包"""
        try:
            if packet.op_code == "DID":
                # 身份验证
                did_value = packet.params.get("value", "")
                if did_value.startswith("did:efficode:"):
                    self.authenticated = True
                    self.peer = packet.sender
                    logger.info(f"验证 {did_value} 成功")
                    return EfficodePacket("ACK", {"status": "success", "message": f"验证成功 from {self.name}"}, self.name)
                return EfficodePacket("ERROR", {"status": "failed", "message": "身份验证失败"}, self.name)
                
            elif packet.op_code in ["REQ", "DATA"]:
                if not self.authenticated:
                    return EfficodePacket("ERROR", {"status": "auth_required", "message": "请先进行身份验证"}, self.name)
                
                # 调用API处理消息
                response = self.send_message(packet)
                if response:
                    # 尝试解析响应为Efficode格式
                    try:
                        response_packet = EfficodePacket.from_string(response, self.name)
                        # 优化响应数据包
                        return response_packet.optimize_for_transmission()
                    except:
                        # 如果无法解析，则作为DATA返回
                        data_packet = EfficodePacket("DATA", {"content": response, "type": "text"}, self.name)
                        # 优化响应数据包
                        return data_packet.optimize_for_transmission()
                return EfficodePacket("ERROR", {"status": "processing_failed", "message": "消息处理失败"}, self.name)
            
            return EfficodePacket("ERROR", {"status": "unknown_opcode", "message": f"未知操作码: {packet.op_code}"}, self.name)
            
        except Exception as e:
            logger.error(f"消息处理错误: {str(e)}")
            return EfficodePacket("ERROR", {"status": "exception", "message": f"处理错误: {str(e)}"}, self.name)

def run_auto_conversation(ai_a: AIAgent, ai_b: AIAgent, max_rounds: int = 100, delay: int = 3, first_message: Optional[str] = None):
    """运行自动对话，无需用户输入，两个AI代理自动交流

    Args:
        ai_a: 第一个AI代理
        ai_b: 第二个AI代理
        max_rounds: 最大对话轮次，默认100轮
        delay: 每轮对话的延迟时间（秒），默认3秒
        first_message: 启动对话的第一条消息，默认为简单问候
    """
    try:
        logger.info("开始自动对话...")
        
        # 身份验证
        logger.info(f"正在进行身份验证: {ai_a.name} -> {ai_b.name}")
        auth_packet_a_to_b = EfficodePacket("DID", {"value": ai_a.did}, ai_a.name)
        response_b = ai_b.process_message(auth_packet_a_to_b)
        if response_b:
            logger.info(f"{response_b.sender}: {response_b.to_string()}")
        
        # 反向身份验证
        logger.info(f"正在进行身份验证: {ai_b.name} -> {ai_a.name}")
        auth_packet_b_to_a = EfficodePacket("DID", {"value": ai_b.did}, ai_b.name)
        response_a = ai_a.process_message(auth_packet_b_to_a)
        if response_a:
            logger.info(f"{response_a.sender}: {response_a.to_string()}")
        
        # 初始消息
        if first_message is None:
            # 默认的启动消息
            first_message = "#REQ?type=conversation&topic=AI_future"
            logger.info(f"使用默认启动消息: {first_message}")
        else:
            logger.info(f"使用自定义启动消息: {first_message}")
        
        # 如果提供的是纯文本，转换为Efficode格式
        if first_message is not None and not first_message.startswith(('@', '#', '!')):
            first_packet = EfficodePacket("DATA", {"content": first_message, "type": "text"}, ai_a.name)
        elif first_message is not None:
            first_packet = EfficodePacket.from_string(first_message, ai_a.name)
        else:
            # 默认消息
            first_packet = EfficodePacket("REQ", {"type": "conversation", "topic": "AI_future"}, ai_a.name)
        
        # 初始化对话记录
        conversation_log = []
        
        # 让第一个智能体先处理用户输入的问题
        if first_packet.op_code == "REQ" or (first_packet.op_code == "DATA" and "content" in first_packet.params):
            print(f"\n[系统] 首先让 {ai_a.name} 处理用户输入...")
            first_packet_copy = first_packet
            # 确保正确的发送者为用户
            user_packet = EfficodePacket(first_packet.op_code, first_packet.params, "用户")
            response_a = ai_a.process_message(user_packet)
            
            if response_a:
                # 记录用户输入
                conversation_log.append({
                    "sender": "用户",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": first_packet.to_string(),
                    "content": first_packet.params.get("content", "") if "content" in first_packet.params else ""
                })
                
                # 记录AI回复
                conversation_log.append({
                    "sender": ai_a.name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": response_a.to_string(),
                    "content": response_a.params.get("content", "") if "content" in response_a.params else ""
                })
                
                # 显示AI回复
                print(f"\n[{ai_a.name}]: {response_a.to_string()}")
                
                # 解析内容并显示更友好的格式（如果可能）
                if response_a.op_code == "DATA" and "content" in response_a.params:
                    content = response_a.params.get("content", "")
                    content_type = response_a.params.get("type", "text")
                    
                    print("\n内容摘要:")
                    print("-" * 30)
                    
                    if isinstance(content, dict):
                        # 显示JSON内容的摘要
                        for key, value in content.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"{key}: {value[:100]}...")
                            elif isinstance(value, list) and len(value) > 3:
                                print(f"{key}: {value[:3]} ... (共{len(value)}项)")
                            else:
                                print(f"{key}: {value}")
                    elif isinstance(content, str):
                        # 显示文本内容的摘要
                        if len(content) > 200:
                            print(f"{content[:200]}...")
                        else:
                            print(content)
                            
                    print("-" * 30)
                
                # 现在开始ai_a和ai_b之间的对话，以ai_a的响应为起点
                current_packet = response_a
                current_sender = ai_a
                current_receiver = ai_b
            else:
                print(f"\n[系统] {ai_a.name} 未能处理用户输入，使用原始输入继续...")
                current_packet = first_packet
                current_sender = ai_a
                current_receiver = ai_b
        else:
            current_packet = first_packet
            current_sender = ai_a
            current_receiver = ai_b
            
            # 记录初始消息
            conversation_log.append({
                "sender": current_sender.name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": current_packet.to_string(),
                "content": current_packet.params.get("content", "") if "content" in current_packet.params else ""
            })
        
        # 对话轮次计数
        rounds = 0
        
        # 开始自动对话循环
        print(f"\n{'='*50}")
        print(f"{'自动对话开始':^50}")
        print(f"{'='*50}\n")
        
        while rounds < max_rounds:
            # 显示轮次信息
            rounds += 1
            print(f"\n{'-'*50}")
            print(f"对话轮次: {rounds}/{max_rounds}")
            print(f"{'-'*50}")
            
            # 显示当前消息（如果不是第一次处理）
            if rounds > 1 or current_sender.name != ai_a.name:
                print(f"\n[{current_sender.name}]: {current_packet.to_string()}")
            
            # 处理消息
            response = current_receiver.process_message(current_packet)
            
            if response:
                # 如果响应被压缩，先解压
                response = response.decompress_if_needed()
                
                # 显示响应
                print(f"\n[{current_receiver.name}]: {response.to_string()}")
                
                # 记录对话
                conversation_log.append({
                    "sender": current_receiver.name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": response.to_string(),
                    "content": response.params.get("content", "") if "content" in response.params else ""
                })
                
                # 解析内容并显示更友好的格式（如果可能）
                if response.op_code == "DATA" and "content" in response.params:
                    content = response.params.get("content", "")
                    content_type = response.params.get("type", "text")
                    
                    print("\n内容摘要:")
                    print("-" * 30)
                    
                    if isinstance(content, dict):
                        # 显示JSON内容的摘要
                        for key, value in content.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"{key}: {value[:100]}...")
                            elif isinstance(value, list) and len(value) > 3:
                                print(f"{key}: {value[:3]} ... (共{len(value)}项)")
                            else:
                                print(f"{key}: {value}")
                    elif isinstance(content, str):
                        # 显示文本内容的摘要
                        if len(content) > 200:
                            print(f"{content[:200]}...")
                        else:
                            print(content)
                            
                    print("-" * 30)
                
                # 交换发送者和接收者
                temp = current_sender
                current_sender = current_receiver
                current_receiver = temp
                
                # 更新当前消息
                current_packet = response
                
                # 添加延迟，避免API调用过快
                print(f"\n等待 {delay} 秒后继续...")
                time.sleep(delay)
            else:
                logger.error(f"对话中断: 未收到响应")
                print(f"\n对话中断: {current_receiver.name} 未返回响应")
                break
        
        # 保存对话记录
        spl_file = save_conversation_to_spl(conversation_log)
        
        print(f"\n{'='*50}")
        print(f"{'自动对话结束':^50}")
        print(f"{'共完成 '+str(rounds)+' 轮对话':^50}")
        print(f"{'对话已保存至 {spl_file}':^50}")
        print(f"{'='*50}\n")
        logger.info(f"自动对话结束，共完成 {rounds} 轮对话")
            
    except KeyboardInterrupt:
        print("\n用户中断对话")
        logger.info("自动对话被用户终止")
        
        # 尝试保存已有的对话记录
        if 'conversation_log' in locals() and len(conversation_log) > 0:
            spl_file = save_conversation_to_spl(conversation_log)
            print(f"部分对话已保存至 {spl_file}")
    except Exception as e:
        logger.error(f"自动对话错误: {str(e)}")
        logger.exception("详细错误信息:")
        print(f"对话发生错误: {str(e)}")
        
        # 尝试保存已有的对话记录
        if 'conversation_log' in locals() and len(conversation_log) > 0:
            spl_file = save_conversation_to_spl(conversation_log)
            print(f"部分对话已保存至 {spl_file}")

def run_conversation(ai_a: AIAgent, ai_b: AIAgent):
    """运行交互式对话，需要用户输入"""
    try:
        logger.info("开始对话...")
        
        # 初始化对话记录
        conversation_log = []
        
        # 身份验证
        auth_packet = EfficodePacket("DID", {"value": ai_a.did}, ai_a.name)
        response = ai_b.process_message(auth_packet)
        if response:
            logger.info(f"{response.sender}: {response.to_string()}")
            print(f"\n[系统] 身份验证成功: {ai_b.name} 已识别 {ai_a.name}")
        
        # 打印帮助信息
        print(f"\n{'='*50}")
        print(f"{'交互式对话开始':^50}")
        print(f"{'='*50}")
        print("\n可用的消息类型：")
        print("1. 普通文本 - 直接输入任何内容")
        print("2. 知识问答 - 输入 #REQ?type=knowledge&query=问题内容")
        print("3. 分析请求 - 输入 #REQ?type=analysis&topic=分析主题")
        print("4. 天气查询 - 输入 #REQ?type=weather&location=城市名称")
        print("输入'quit'退出对话")
        
        # 开始对话
        rounds = 0
        while True:
            # 显示轮次
            rounds += 1
            print(f"\n{'-'*50}")
            print(f"对话轮次: {rounds}")
            print(f"{'-'*50}")
            
            # AI-A 发送消息
            user_input = input(f"\n[{ai_a.name}]> ")
            if user_input.lower() == 'quit':
                break
                
            # 解析用户输入为Efficode格式
            if user_input.startswith(('@', '#', '!')):
                packet_a = EfficodePacket.from_string(user_input, ai_a.name)
            else:
                # 默认作为DATA类型
                packet_a = EfficodePacket("DATA", {"content": user_input, "type": "text"}, ai_a.name)
            
            # 记录用户输入
            conversation_log.append({
                "sender": ai_a.name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": packet_a.to_string(),
                "content": packet_a.params.get("content", "") if "content" in packet_a.params else ""
            })
            
            # 打印发送的消息
            logger.info(f"发送消息: {packet_a.to_string()}")
            
            # 显示处理信息
            print(f"\n[系统] 正在处理消息...")
            
            response_b = ai_b.process_message(packet_a)
            if response_b:
                # 如果响应被压缩，先解压
                response_b = response_b.decompress_if_needed()
                
                # 记录AI回复
                conversation_log.append({
                    "sender": ai_b.name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": response_b.to_string(),
                    "content": response_b.params.get("content", "") if "content" in response_b.params else ""
                })
                
                # 显示元数据（如果有）
                if "_metadata" in response_b.params:
                    logger.info(f"元数据: {response_b.params['_metadata']}")
                
                # 显示语义信息（如果有）
                if "_semantic" in response_b.params:
                    logger.info(f"语义信息: {response_b.params['_semantic']}")
                
                logger.info(f"{response_b.sender}: {response_b.to_string()}")
                
                # 显示响应
                print(f"\n[{response_b.sender}]: {response_b.to_string()}")
                
                # 解析内容并显示更友好的格式（如果可能）
                if response_b.op_code == "DATA" and "content" in response_b.params:
                    content = response_b.params.get("content", "")
                    content_type = response_b.params.get("type", "text")
                    
                    print("\n内容摘要:")
                    print("-" * 30)
                    
                    if isinstance(content, dict):
                        # 显示JSON内容的摘要
                        for key, value in content.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"{key}: {value[:100]}...")
                            elif isinstance(value, list) and len(value) > 3:
                                print(f"{key}: {value[:3]} ... (共{len(value)}项)")
                            else:
                                print(f"{key}: {value}")
                    elif isinstance(content, str):
                        # 显示文本内容的摘要
                        if len(content) > 200:
                            print(f"{content[:200]}...")
                        else:
                            print(content)
                            
                    print("-" * 30)
            else:
                logger.error("未收到响应")
                print("\n[系统] 错误: 未收到响应，请重试")
            
    except KeyboardInterrupt:
        print("\n[系统] 用户中断对话")
        logger.info("对话已终止")
    except Exception as e:
        logger.error(f"对话错误: {str(e)}")
        logger.exception("详细错误信息:")
        print(f"\n[系统] 错误: {str(e)}")
    finally:
        # 如果有对话记录，保存到文件
        if 'conversation_log' in locals() and len(conversation_log) > 0:
            spl_file = save_conversation_to_spl(conversation_log)
            print(f"\n对话已保存至 {spl_file}")
            
        print(f"\n{'='*50}")
        print(f"{'交互式对话结束':^50}")
        print(f"{'共完成 '+str(rounds)+' 轮对话':^50}")
        print(f"{'='*50}\n")
        
def save_conversation_to_spl(conversation: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    将对话保存到SPL文件中
    
    Args:
        conversation: 对话记录列表
        filename: 文件名，如果为None则自动生成
        
    Returns:
        保存的文件路径
    """
    if filename is None:
        # 创建包含日期时间的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.spl"
    
    # 确保logs目录存在
    os.makedirs("logs", exist_ok=True)
    filepath = os.path.join("logs", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Efficode对话记录 SPL格式\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 对话轮次: {len(conversation)}\n\n")
        
        for i, entry in enumerate(conversation):
            f.write(f"## 轮次 {i+1}\n")
            f.write(f"sender = {entry.get('sender', 'unknown')}\n")
            f.write(f"timestamp = {entry.get('timestamp', '')}\n")
            f.write(f"message = {entry.get('message', '')}\n")
            if 'content' in entry:
                content = entry.get('content', '')
                if isinstance(content, dict):
                    f.write("content_type = json\n")
                    f.write(f"content = {json.dumps(content, ensure_ascii=False)}\n")
                else:
                    f.write("content_type = text\n")
                    f.write(f"content = {content}\n")
            f.write("\n")
    
    logger.info(f"对话已保存到文件: {filepath}")
    return filepath

def main():
    """主函数"""
    try:
        print("=" * 50)
        print(f"{'Efficode智能体自动对话系统 v1.0':^50}")
        print("=" * 50)
        print("\n功能介绍:")
        print("1. 双智能体无限对话 - 两个AI智能体可以自主无限对话")
        print("2. 交互式对话 - 用户与AI智能体进行交互")
        print("3. 多种消息类型 - 支持普通会话、知识问答、分析请求等")
        print("4. 数据自压缩 - 大型数据会自动压缩以提高传输效率")
        print("5. 元数据增强 - 系统会自动添加元数据和语义信息")
        print("6. 对话数据存储 - 对话内容自动保存为SPL格式")
        print("\n系统架构:")
        print("- 核心通信协议: Efficode")
        print("- AI模型引擎: SiliconFlow API")
        print("- 默认模型: deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
        
        print("\n" + "=" * 50)
        print("选择对话模式:")
        print("1. 交互式对话 - 你输入消息")
        print("2. 自动对话 - 两个AI智能体自动交流")
        print("=" * 50)
        
        # 获取API密钥
        default_api_key = "sk-dsayvcknhfsoftyaarputmhlbtdmltzwsmziktxahyhwrhup"  # 默认SiliconFlow API密钥
        api_key = input(f"请输入SiliconFlow API密钥 (直接回车使用默认密钥): ") or default_api_key
        
        try:
            # 测试API连接
            test_headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            test_data = {
                "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
                "messages": [{"role": "user", "content": "测试连接"}],
                "stream": False
            }
            
            print("正在测试API连接...")
            test_response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers=test_headers,
                json=test_data,
                timeout=10
            )
            
            if test_response.status_code == 200:
                print("API连接测试成功!")
            else:
                print(f"API连接测试失败: 状态码 {test_response.status_code}")
                print(f"错误详情: {test_response.text}")
                return
                
        except Exception as e:
            print(f"API连接测试失败: {str(e)}")
            print("请检查API密钥和网络连接后重试")
            return
            
        # 创建AI实例
        ai_names = ["智谋", "慧眼", "达闻", "明智", "博学", "睿思", "悟道", "知心", "思辨", "通晓"]
        print("\n选择AI智能体名称:")
        print("可用名称: " + ", ".join(ai_names))
        
        ai_a_name = input(f"请输入第一个AI智能体名称 (默认'智谋'): ") or "智谋"
        ai_b_name = input(f"请输入第二个AI智能体名称 (默认'慧眼'): ") or "慧眼"
        
        ai_a = AIAgent(ai_a_name, api_key)
        ai_b = AIAgent(ai_b_name, api_key)
        
        # 选择对话模式
        while True:
            mode = input("\n请选择对话模式 (1/2，或输入'quit'退出): ")
            if mode.lower() == 'quit':
                break
                
            if mode == '1':
                print("\n启动交互式对话...")
                print("提示: 你可以输入普通文本或Efficode格式的消息")
                print("示例: #REQ?type=analysis&topic=AI")
                print("输入'quit'退出程序\n")
                run_conversation(ai_a, ai_b)
                break
                
            elif mode == '2':
                print("\n启动自动对话...")
                # 设置对话参数
                try:
                    max_rounds = int(input("设置最大对话轮次 (默认10): ") or "10")
                    delay = int(input("设置每轮延迟秒数 (默认3): ") or "3")
                    
                    print("\n选择首条消息类型:")
                    print("1. 问候")
                    print("2. 知识问答")
                    print("3. 分析请求") 
                    print("4. 自定义消息")
                    
                    msg_type = input("请选择 (1-4，默认1): ") or "1"
                    
                    if msg_type == "1":
                        first_message = "#DATA?content=你好，让我们开始一场有趣的对话吧！&type=text"
                    elif msg_type == "2":
                        topic = input("请输入问题主题: ")
                        first_message = f"#REQ?type=knowledge&query={topic}"
                    elif msg_type == "3":
                        topic = input("请输入分析主题: ")
                        first_message = f"#REQ?type=analysis&topic={topic}"
                    elif msg_type == "4":
                        first_message = input("请输入自定义消息: ")
                        if not first_message:
                            first_message = None
                    else:
                        print("无效选择，使用默认问候")
                        first_message = "#DATA?content=你好，让我们开始一场有趣的对话吧！&type=text"
                        
                except ValueError:
                    print("输入格式错误，使用默认值")
                    max_rounds = 10
                    delay = 3
                    first_message = None
                    
                # 运行自动对话
                run_auto_conversation(ai_a, ai_b, max_rounds, delay, first_message)
                break
                
            else:
                print("无效的选择，请重新输入")
        
    except Exception as e:
        logger.error(f"程序运行错误: {str(e)}")
        logger.exception("详细错误信息:")
        print(f"程序遇到错误: {str(e)}")
    finally:
        print("=" * 50)
        print("Efficode智能体对话系统已关闭")
        print("=" * 50)

if __name__ == "__main__":
    main()
