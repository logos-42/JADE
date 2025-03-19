"""
对话管理模块

这个模块提供了对话管理功能，包括自动对话、交互对话以及对话记录的保存。
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, cast
from datetime import datetime

from efficode_core import (
    EfficodePacket, 
    create_request_packet,
    create_data_packet,
    create_error_packet,
    create_ack_packet
)
from ai_agent import AIAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Dialogue_Manager')

class DialogueManager:
    """对话管理类，负责处理和记录AI智能体之间的对话"""
    
    def __init__(self, agent1: AIAgent, agent2: AIAgent):
        """
        初始化对话管理器
        
        Args:
            agent1: 第一个AI智能体
            agent2: 第二个AI智能体
        """
        self.agent1 = agent1
        self.agent2 = agent2
        self.conversation_history: List[Dict[str, str]] = []
        self.logs_dir = "logs"
        
        # 确保日志目录存在
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            logger.info(f"创建日志目录: {self.logs_dir}")
    
    def run_auto_conversation(self, topic: str, rounds: int = 5, user_input: Optional[str] = None) -> List[Dict[str, str]]:
        """
        运行自动对话模式 - 一问一答式高认知探索
        
        Args:
            topic: 对话主题
            rounds: 对话轮数
            user_input: 用户输入（可选）
            
        Returns:
            对话历史记录
        """
        logger.info(f"开始自动对话, 主题: {topic}, 轮数: {rounds}")
        self.conversation_history = []
        
        try:
            # 身份验证
            if not self._authenticate_agents():
                logger.error("身份验证失败，无法开始对话")
                print("身份验证失败，无法开始对话。可能是API调用问题，请检查API密钥。")
                return self.conversation_history
            
            # 确定问答角色
            # 假设agent1为提问者，agent2为回答者
            questioner = self.agent1
            answerer = self.agent2
            
            # 如果角色不匹配，交换位置确保提问者是"智谋"，回答者是"慧眼"
            if "回答" in questioner.role.get("description", "") or "提问" in answerer.role.get("description", ""):
                questioner, answerer = answerer, questioner
                logger.info(f"交换智能体角色: {questioner.name}作为提问者, {answerer.name}作为回答者")
            
            # 开始对话
            print(f"\n=== 开始高认知探索对话 ===")
            print(f"提问者: {questioner.name} - {questioner.role.get('description', '')}")
            print(f"回答者: {answerer.name} - {answerer.role.get('description', '')}")
            print(f"主题: {topic}")
            print(f"轮数: {rounds}")
            print("=" * 50)
            
            # 如果有用户输入，作为初始话题描述
            initial_message = user_input if user_input is not None else f"关于'{topic}'的探索和思考"
            
            # 创建初始主题请求 - 普通文本，不加密
            initial_packet = create_request_packet(
                content=initial_message,
                req_type="exploration",
                sender="用户"
            )
            
            # 记录初始消息
            print(f"\n[用户]: {initial_message}")
            self._record_message("用户", initial_message)
            
            # 发送到提问者，让其生成第一个问题
            print(f"\n[系统] {questioner.name} 正在思考第一个问题...")
            # API会返回加密的Efficode格式消息
            encrypted_response = questioner.process_message(initial_packet)
            
            if not encrypted_response:
                print(f"{questioner.name} 无法生成问题，对话终止")
                return self.conversation_history
                
            # 将字符串响应解析为EfficodePacket对象
            first_question_packet = EfficodePacket.from_string(encrypted_response, questioner.name)
            
            # 解压并显示第一个问题
            first_question_packet = first_question_packet.decompress_content()
            if first_question_packet.op_code == "REQ" and "content" in first_question_packet.params:
                question = first_question_packet.params.get("content", "")
                print(f"\n[{questioner.name}]: {question}")
                self._record_message(questioner.name, question)
            else:
                question = first_question_packet.to_string()
                print(f"\n[{questioner.name}]: {question}")
                self._record_message(questioner.name, question)
            
            # 当前处理中的消息
            current_packet = first_question_packet
            
            # 进行对话轮次
            for i in range(rounds):
                # 间隔一段时间再继续，避免频繁API调用
                time.sleep(2)
                
                # 答案阶段: 回答者处理问题并给出回答
                print(f"\n[系统] {answerer.name} 正在思考回答...")
                # API会返回加密的Efficode格式消息
                encrypted_answer = answerer.process_message(current_packet)
                
                if not encrypted_answer:
                    print(f"{answerer.name} 无法生成回答，对话终止")
                    break
                
                # 解析响应
                answer_packet = EfficodePacket.from_string(encrypted_answer, answerer.name)
                
                # 解压并显示回答
                answer_packet = answer_packet.decompress_content()
                if answer_packet.op_code == "DATA" and "content" in answer_packet.params:
                    answer = answer_packet.params.get("content", "")
                    print(f"\n[{answerer.name}]: {answer}")
                    self._record_message(answerer.name, answer)
                else:
                    answer = answer_packet.to_string()
                    print(f"\n[{answerer.name}]: {answer}")
                    self._record_message(answerer.name, answer)
                
                # 如果已经是最后一轮，则结束对话
                if i == rounds - 1:
                    break
                
                # 间隔一段时间再继续
                time.sleep(2)
                
                # 提问阶段: 提问者基于回答生成新的问题
                print(f"\n[系统] {questioner.name} 正在思考下一个问题...")
                # API会返回加密的Efficode格式消息
                encrypted_question = questioner.process_message(answer_packet)
                
                if not encrypted_question:
                    print(f"{questioner.name} 无法生成问题，对话终止")
                    break
                
                # 解析响应
                question_packet = EfficodePacket.from_string(encrypted_question, questioner.name)
                
                # 解压并显示新问题
                question_packet = question_packet.decompress_content()
                if question_packet.op_code == "REQ" and "content" in question_packet.params:
                    question = question_packet.params.get("content", "")
                    print(f"\n[{questioner.name}]: {question}")
                    self._record_message(questioner.name, question)
                else:
                    question = question_packet.to_string()
                    print(f"\n[{questioner.name}]: {question}")
                    self._record_message(questioner.name, question)
                
                # 更新当前处理的消息
                current_packet = question_packet
            
            print("\n==== 高认知探索对话结束 ====")
            
            # 保存对话历史
            self._save_conversation("exploration")
            
        except Exception as e:
            logger.error(f"自动对话过程中出错: {str(e)}")
            logger.exception("详细错误信息")
            print(f"\n对话过程中发生错误: {str(e)}")
        
        return self.conversation_history
    
    def run_interactive_conversation(self) -> List[Dict[str, str]]:
        """
        运行交互式对话模式
        
        Returns:
            对话历史记录
        """
        logger.info("开始交互式对话")
        self.conversation_history = []
        
        try:
            # 身份验证
            if not self._authenticate_agents():
                logger.error("身份验证失败，无法开始对话")
                print("身份验证失败，无法开始对话。可能是API调用问题，请检查API密钥。")
                return self.conversation_history
            
            print(f"\n=== 交互式对话开始 ===")
            print(f"您将与 {self.agent1.name} 和 {self.agent2.name} 交流")
            print("输入 'exit' 或 'quit' 结束对话\n")
            
            while True:
                # 获取用户输入
                user_input = input("您: ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                # 记录用户消息
                self._record_message("用户", user_input)
                
                # 创建请求包 - 普通文本，不加密
                user_packet = create_request_packet(
                    content=user_input,
                    req_type="dialogue",
                    sender="用户"
                )
                
                # 发送给第一个智能体
                print(f"\n[系统] {self.agent1.name} 正在思考...")
                # API会返回加密的Efficode格式消息
                encrypted_response1 = self.agent1.process_message(user_packet)
                
                if encrypted_response1:
                    # 解析响应
                    agent1_response = EfficodePacket.from_string(encrypted_response1, self.agent1.name)
                    
                    # 解压并显示回答
                    agent1_response = agent1_response.decompress_content()
                    if agent1_response.op_code == "DATA" and "content" in agent1_response.params:
                        agent1_message = agent1_response.params.get("content", "")
                        print(f"\n[{self.agent1.name}]: {agent1_message}")
                        self._record_message(self.agent1.name, agent1_message)
                        
                        # 发送给第二个智能体
                        print(f"\n[系统] {self.agent2.name} 正在思考...")
                        # API会返回加密的Efficode格式消息
                        encrypted_response2 = self.agent2.process_message(agent1_response)
                        if encrypted_response2:
                            # 解析响应
                            agent2_response = EfficodePacket.from_string(encrypted_response2, self.agent2.name)
                            
                            # 解压并显示回答
                            agent2_response = agent2_response.decompress_content()
                            if agent2_response.op_code == "DATA" and "content" in agent2_response.params:
                                agent2_message = agent2_response.params.get("content", "")
                                print(f"\n[{self.agent2.name}]: {agent2_message}")
                                self._record_message(self.agent2.name, agent2_message)
                            else:
                                message = agent2_response.to_string()
                                print(f"\n[{self.agent2.name}]: {message}")
                                self._record_message(self.agent2.name, message)
                        else:
                            print(f"\n{self.agent2.name} 无法处理消息")
                    else:
                        message = agent1_response.to_string()
                        print(f"\n[{self.agent1.name}]: {message}")
                        self._record_message(self.agent1.name, message)
                else:
                    print(f"\n{self.agent1.name} 无法处理您的请求。请重试。")
            
            print("\n=== 对话结束 ===\n")
            
            # 保存对话历史
            self._save_conversation("interactive")
            
        except Exception as e:
            logger.error(f"交互式对话过程中出错: {str(e)}")
            logger.exception("详细错误信息")
            print(f"\n对话过程中发生错误: {str(e)}")
        
        return self.conversation_history
    
    def _authenticate_agents(self) -> bool:
        """身份验证过程"""
        try:
            logger.info("开始身份验证...")
            
            # Agent1 向 Agent2 发送身份验证
            auth_packet1 = EfficodePacket(
                op_code="DID",
                params={"value": self.agent1.did},
                sender=self.agent1.name
            )
            response1_str = self.agent2.process_message(auth_packet1)
            if response1_str:
                # 将字符串响应解析为EfficodePacket
                response1 = EfficodePacket.from_string(response1_str, self.agent2.name)
                if response1.op_code == "ACK":
                    logger.info(f"{self.agent1.name} 向 {self.agent2.name} 的身份验证成功")
                else:
                    logger.error(f"{self.agent1.name} 向 {self.agent2.name} 的身份验证失败")
                    return False
            else:
                logger.error(f"{self.agent1.name} 向 {self.agent2.name} 的身份验证失败")
                return False
            
            # Agent2 向 Agent1 发送身份验证
            auth_packet2 = EfficodePacket(
                op_code="DID",
                params={"value": self.agent2.did},
                sender=self.agent2.name
            )
            response2_str = self.agent1.process_message(auth_packet2)
            if response2_str:
                # 将字符串响应解析为EfficodePacket
                response2 = EfficodePacket.from_string(response2_str, self.agent1.name)
                if response2.op_code == "ACK":
                    logger.info(f"{self.agent2.name} 向 {self.agent1.name} 的身份验证成功")
                else:
                    logger.error(f"{self.agent2.name} 向 {self.agent1.name} 的身份验证失败")
                    return False
            else:
                logger.error(f"{self.agent2.name} 向 {self.agent1.name} 的身份验证失败")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"身份验证过程中出错: {str(e)}")
            logger.exception("详细错误信息")
            return False
    
    def _record_message(self, sender: str, content: str) -> None:
        """记录消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {
            "sender": sender,
            "content": content,
            "timestamp": timestamp
        }
        self.conversation_history.append(message)
        logger.debug(f"记录消息: {sender} -> {content[:50]}...")
    
    def _save_conversation(self, mode: str) -> None:
        """保存对话历史到文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.logs_dir}/dialogue_{mode}_{timestamp}.json"
            
            conversation_data = {
                "mode": mode,
                "agent1": {
                    "name": self.agent1.name,
                    "role": self.agent1.role["description"]
                },
                "agent2": {
                    "name": self.agent2.name,
                    "role": self.agent2.role["description"]
                },
                "timestamp": datetime.now().isoformat(),
                "messages": self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"对话历史已保存至: {filename}")
            
            # 保存SPL格式
            self._save_conversation_to_spl(mode, timestamp)
            
        except Exception as e:
            logger.error(f"保存对话历史时出错: {str(e)}")
    
    def _save_conversation_to_spl(self, mode: str, timestamp: str) -> None:
        """保存对话历史到SPL格式文件"""
        try:
            filename = f"{self.logs_dir}/dialogue_{mode}_{timestamp}.spl"
            
            with open(filename, 'w', encoding='utf-8') as f:
                for message in self.conversation_history:
                    sender = message["sender"]
                    content = message["content"]
                    
                    # SPL格式: <sender>: <content>
                    f.write(f"{sender}: {content}\n\n")
            
            logger.info(f"对话历史已保存为SPL格式: {filename}")
            
        except Exception as e:
            logger.error(f"保存SPL格式对话历史时出错: {str(e)}") 