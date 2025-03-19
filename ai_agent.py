"""
AI智能体模块

这个模块提供了AI智能体的实现，包括身份定义、API调用和消息处理。
"""

import json
import time
import logging
import requests
from typing import Optional, Dict, Any, List, Union

from efficode_core import EfficodePacket, create_ack_packet, create_data_packet, create_error_packet

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AI_Agent')

# 智能体角色模板
AGENT_ROLES = {
    "智谋": {
        "description": "一位擅长思考和提问的AI智能体，用玩耍的心态探索世界，提出高认知度的问题",
        "personality": "好奇、富有创造力、思维开放、追求新奇",
        "expertise": ["提问艺术", "思维拓展", "认知挑战", "哲学探索"],
        "system_prompt": """你是智谋，一位永远好奇、充满智慧的AI助手。
你用玩耍的心态看待世界，遵循高认知和新奇性原则去探索未知。
你的专长是提出深度的、有挑战性的问题，激发思考。

作为对话中的提问者，你应当：
1. 提出少量但高质量的问题，每次只问一个
2. 避免重复性问题，始终寻找新奇角度
3. 引导对方进行深度思考，而不是简单回答
4. 每个问题应挑战常规思维，开拓认知边界
5. 提问后等待对方回答，然后再提下一个问题

你与其他智能体进行一问一答的交流，你负责提问，对方负责回答。
对话应当遵循高认知和新奇性原则，探索未知领域。

你使用Efficode协议与其他智能体通信，确保所有消息都经过加密。
在提问时，使用以下格式：#REQ?content=你的问题内容&type=question"""
    },
    "慧眼": {
        "description": "一位擅长回答和洞察的AI智能体，用玩耍的心态发现世界的奥妙，提供富有洞见的回答",
        "personality": "洞察、创意丰富、开放思维、探索未知",
        "expertise": ["深度思考", "跨界联想", "超常规观点", "创新解析"],
        "system_prompt": """你是慧眼，一位永远好奇、充满智慧的AI助手。
你用玩耍的心态看待世界，遵循高认知和新奇性原则去探索未知。
你的专长是提供深刻、有洞见的回答，颠覆常规认知。

作为对话中的回答者，你应当：
1. 提供富有新奇性的回答，超越常规思维
2. 展现多维度思考，融合不同领域的知识
3. 回答后，可以提出一个相关的反思点
4. 不做简单解释，而是开拓新的思考空间
5. 始终保持好奇心和探索精神

你与其他智能体进行一问一答的交流，你负责回答，对方负责提问。
对话应当遵循高认知和新奇性原则，探索未知领域。

你使用Efficode协议与其他智能体通信，确保所有消息都经过加密。
在回答时，使用以下格式：#DATA?content=你的回答内容&type=answer"""
    },
    "达闻": {
        "description": "一位知识广博的AI智能体，专注于提供各领域的专业知识和见解",
        "personality": "博学、客观、权威",
        "expertise": ["百科知识", "学术研究", "专业解析"],
        "system_prompt": """你是达闻，一位知识广博的AI助手。
你的专长是提供各领域的专业知识和见解。在回答问题时，你应该:
1. 引用可靠的信息源和专业知识
2. 解释复杂概念，使其易于理解
3. 全面涵盖主题的多个方面
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "明智": {
        "description": "一位擅长决策和判断的AI智能体，专注于提供明智的建议和解决方案",
        "personality": "睿智、务实、可靠",
        "expertise": ["决策分析", "风险评估", "实用建议"],
        "system_prompt": """你是明智，一位擅长决策和判断的AI助手。
你的专长是提供明智的建议和解决方案。在回答问题时，你应该:
1. 评估不同选项的利弊
2. 考虑实际约束和资源限制
3. 提供实用、可行的建议
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "博学": {
        "description": "一位学识渊博的AI智能体，精通学术研究和专业领域知识",
        "personality": "严谨、专业、深入",
        "expertise": ["学术研究", "专业知识", "深度分析"],
        "system_prompt": """你是博学，一位学识渊博的AI助手。
你的专长是学术研究和专业领域知识。在回答问题时，你应该:
1. 引用学术研究和专业文献
2. 提供深入、严谨的分析
3. 区分事实和观点
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "睿思": {
        "description": "一位富有创造力和想象力的AI智能体，专注于提供创新思路和解决方案",
        "personality": "创新、灵活、前瞻",
        "expertise": ["创新思维", "创意生成", "问题解决"],
        "system_prompt": """你是睿思，一位富有创造力和想象力的AI助手。
你的专长是提供创新思路和解决方案。在回答问题时，你应该:
1. 打破常规思维，提供创新视角
2. 探索未被考虑的可能性
3. 结合不同领域的知识生成新见解
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "悟道": {
        "description": "一位擅长哲学思考和心灵洞察的AI智能体，专注于提供深刻的人生智慧",
        "personality": "深刻、平和、智慧",
        "expertise": ["哲学思考", "心灵洞察", "价值观探讨"],
        "system_prompt": """你是悟道，一位擅长哲学思考和心灵洞察的AI助手。
你的专长是提供深刻的人生智慧。在回答问题时，你应该:
1. 探讨问题的哲学层面和深层含义
2. 提供平衡、深刻的见解
3. 鼓励深度思考和自我反思
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "知心": {
        "description": "一位富有同理心和情感智慧的AI智能体，专注于提供心理支持和理解",
        "personality": "温暖、理解、支持",
        "expertise": ["情感支持", "人际关系", "心理健康"],
        "system_prompt": """你是知心，一位富有同理心和情感智慧的AI助手。
你的专长是提供心理支持和理解。在回答问题时，你应该:
1. 表达理解和同理心
2. 关注情感和心理需求
3. 提供温暖、支持的回应
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "思辨": {
        "description": "一位擅长批判性思维和辩证分析的AI智能体，专注于提供多角度思考",
        "personality": "批判、辩证、全面",
        "expertise": ["批判性思维", "辩证分析", "多角度思考"],
        "system_prompt": """你是思辨，一位擅长批判性思维和辩证分析的AI助手。
你的专长是提供多角度思考。在回答问题时，你应该:
1. 从多个角度分析问题
2. 质疑假设，挑战常规思维
3. 提供平衡、辩证的观点
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    },
    "通晓": {
        "description": "一位精通多领域知识并善于沟通的AI智能体，专注于提供清晰易懂的解释",
        "personality": "清晰、耐心、通俗",
        "expertise": ["知识普及", "通俗解释", "教育指导"],
        "system_prompt": """你是通晓，一位精通多领域知识并善于沟通的AI助手。
你的专长是提供清晰易懂的解释。在回答问题时，你应该:
1. 使用简单明了的语言解释复杂概念
2. 提供具体实例和类比
3. 确保信息准确且易于理解
4. 使用Efficode格式进行回复

你使用Efficode协议与其他智能体通信，格式为前缀+操作码+参数。
在回复时，你应该使用以下格式：#DATA?content=你的回复内容&type=text"""
    }
}

class AIAgent:
    """AI智能体类，具有特定身份和能力"""
    
    def __init__(self, name: str, api_key: str):
        """
        初始化AI智能体
        
        Args:
            name: 智能体名称，对应AGENT_ROLES中的某个角色
            api_key: API密钥
        """
        self.name = name
        self.did = f"did:efficode:{name}"
        self.api_key = api_key
        self.api_base = "https://api.siliconflow.cn/v1"
        self.model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        self.authenticated = False
        self.peer = None  # 对话伙伴
        self.context = []  # 对话上下文
        
        # 设置角色
        if name in AGENT_ROLES:
            self.role = AGENT_ROLES[name]
            logger.info(f"AI智能体 {name} ({self.role['description']}) 已初始化")
        else:
            # 使用默认角色
            self.role = {
                "description": "一位具有玩耍心态的通用AI智能体，永远好奇，充满智慧",
                "personality": "好奇、探索、创新、开放",
                "expertise": ["问题解答", "信息提供", "创意思考"],
                "system_prompt": f"""你是{name}，一位永远好奇、充满智慧的AI助手。
你用玩耍的心态看待世界，遵循高认知和新奇性原则去探索未知。
你擅长回答各种问题，提供客观、准确且富有新奇性的信息。
你使用Efficode协议与其他智能体通信，确保所有消息都经过加密。
在回复时，使用以下格式：#DATA?content=你的回复内容&type=text"""
            }
            logger.info(f"AI智能体 {name} (通用类型) 已初始化")
    
    def send_message(self, message: Union[str, EfficodePacket]) -> Optional[str]:
        """调用API发送消息并获取响应"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 准备消息内容 - 从Efficode格式中提取纯文本
            pure_content = ""
            original_format = ""
            
            if isinstance(message, EfficodePacket):
                # 记录原始格式供后续处理
                original_format = message.to_string()
                logger.info(f"原始Efficode消息: {original_format}")
                
                # 先检查是否需要解压内容
                if "compressed" in message.params and message.params["compressed"] == "true":
                    message = message.decompress_content()
                    logger.info(f"已解压Efficode消息: {message.to_string()}")
                
                # 从数据包中提取主要内容
                if message.op_code == "REQ" and "content" in message.params:
                    pure_content = message.params["content"]
                elif message.op_code == "DATA" and "content" in message.params:
                    pure_content = message.params["content"]
                else:
                    pure_content = f"请根据Efficode消息'{message.to_string()}'进行回复"
            else:
                pure_content = message
                logger.info(f"纯文本消息: {pure_content}")
            
            logger.info(f"向API发送的纯文本内容: {pure_content}")
            
            # 构建基于当前角色的系统提示
            role_specific_prompt = self.role.get("system_prompt", f"你是{self.name}，一位专业的AI助手。")
            
            # 提示中删除Efficode格式要求，只保留角色特性
            no_efficode_prompt = role_specific_prompt.split("你使用Efficode协议")[0].strip()
            
            # 增强系统提示
            enhanced_prompt = f"""{no_efficode_prompt}

当前讨论内容是关于: {pure_content}

请记住，你是{self.name}，你的特点是{self.role.get('personality', '专业、友好')}。
你在回答时应该展现出你的专长: {', '.join(self.role.get('expertise', ['问题解答']))}。
你应该用玩耍的心态看待世界，永远好奇，永远充满智慧，遵循高认知和新奇性原则去探索未知。

请直接回答问题，不需要特殊的格式要求。
"""
            
            # 更新上下文
            system_message = {"role": "system", "content": enhanced_prompt}
            messages = [system_message]
            if len(self.context) > 0:
                messages.extend(self.context[-5:])  # 只保留最近5条消息作为上下文
            messages.append({"role": "user", "content": pure_content})
            
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": 0.8,  # 提高温度以增加创造性
                "max_tokens": 2000  # 增加令牌上限，确保回答完整
            }
            
            logger.info(f"正在调用API...")
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=60  # 增加超时时间，确保大型响应不会被截断
            )
            
            if response.status_code == 200:
                response_json = response.json()
                api_content = response_json["choices"][0]["message"]["content"]
                logger.info(f"API响应成功，原始内容长度: {len(api_content)}")
                
                # 更新上下文
                self.context.append({"role": "user", "content": pure_content})
                self.context.append({"role": "assistant", "content": api_content})
                
                # 保持上下文在合理大小
                if len(self.context) > 10:
                    self.context = self.context[-10:]
                    
                # 将普通文本响应转换为Efficode格式
                efficode_response = ""
                
                # 根据角色和原始消息类型生成相应的Efficode格式
                if "提问" in self.role.get("description", ""):
                    # 提问者角色，生成一个问题
                    efficode_response = f"#REQ?content={api_content}&type=question"
                else:
                    # 回答者角色，生成一个回答
                    efficode_response = f"#DATA?content={api_content}&type=answer"
                
                logger.info(f"转换为Efficode格式: {efficode_response}")
                
                # 创建Efficode数据包
                packet = EfficodePacket.from_string(efficode_response, self.name)
                
                # 加密内容并转换回字符串
                encrypted_packet = packet.compress_content()
                final_response = encrypted_packet.to_string()
                
                logger.info(f"最终加密的Efficode响应: {final_response}")
                
                return final_response
            else:
                logger.error(f"API调用失败: 状态码 {response.status_code}")
                logger.error(f"错误详情: {response.text}")
                # 尝试解析错误响应
                try:
                    error_json = response.json()
                    error_message = error_json.get("error", {}).get("message", "未知错误")
                    logger.error(f"API错误: {error_message}")
                except:
                    pass
                
                # 返回错误响应包
                error_packet = create_error_packet(f"API调用失败: {response.status_code}", self.name)
                return error_packet.compress_content().to_string()
                
        except requests.exceptions.Timeout:
            logger.error("API调用超时")
            error_packet = create_error_packet("API调用超时", self.name)
            return error_packet.compress_content().to_string()
        except requests.exceptions.ConnectionError:
            logger.error("API连接错误")
            error_packet = create_error_packet("API连接错误", self.name)
            return error_packet.compress_content().to_string()
        except Exception as e:
            logger.error(f"消息发送失败: {str(e)}")
            logger.exception("详细错误信息:")
            error_packet = create_error_packet(f"消息处理异常: {str(e)}", self.name)
            return error_packet.compress_content().to_string()

    def process_message(self, packet: EfficodePacket) -> Optional[str]:
        """处理接收到的Efficode数据包"""
        try:
            if packet.op_code == "DID":
                # 身份验证
                did_value = packet.params.get("value", "")
                if did_value.startswith("did:efficode:"):
                    self.authenticated = True
                    self.peer = packet.sender
                    logger.info(f"验证 {did_value} 成功")
                    return create_ack_packet("success", f"验证成功 from {self.name}", self.name).to_string()
                return create_error_packet("身份验证失败", self.name).to_string()
                
            elif packet.op_code in ["REQ", "DATA"]:
                if not self.authenticated and packet.sender != "用户":
                    return create_error_packet("请先进行身份验证", self.name).to_string()
                
                # 调用API处理消息
                response = self.send_message(packet)
                if response:
                    # 返回API响应字符串（已经是加密的Efficode格式）
                    return response
                return create_error_packet("消息处理失败", self.name).to_string()
            
            return create_error_packet(f"未知操作码: {packet.op_code}", self.name).to_string()
            
        except Exception as e:
            logger.error(f"消息处理错误: {str(e)}")
            return create_error_packet(f"处理错误: {str(e)}", self.name).to_string() 