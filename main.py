"""
Efficode AI通信系统主程序

这个程序提供了AI智能体之间的通信功能，支持高认知探索式对话和交互式对话两种模式。
"""

import os
import sys
import logging
import argparse
from typing import Optional, Tuple

from ai_agent import AIAgent, AGENT_ROLES
from dialogue_manager import DialogueManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Main')

def get_api_key() -> str:
    """获取API密钥"""
    # 首先尝试从环境变量获取
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if api_key:
        return api_key
    
    # 如果环境变量中没有，则从用户输入获取
    print("\n请输入您的SiliconFlow API密钥（按回车使用默认密钥）：")
    user_input = input().strip()
    
    if user_input:
        return user_input
    else:
        # 使用默认密钥
        default_key = "sk-dsayvcknhfsoftyaarputmhlbtdmltzwsmziktxahyhwrhup"
        print(f"使用默认密钥: {default_key[:5]}...{default_key[-5:]}")
        return default_key

def test_api_connection(api_key: str) -> bool:
    """测试API连接是否正常"""
    print("\n正在测试API连接...")
    try:
        import requests
        
        test_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        test_data = {
            "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "messages": [{"role": "user", "content": "你好"}],
            "stream": False,
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers=test_headers,
            json=test_data,
            timeout=15  # 增加超时时间
        )
        
        if response.status_code == 200:
            print("✓ API连接测试成功！")
            return True
        else:
            print(f"✗ API连接测试失败: 状态码 {response.status_code}")
            error_message = response.json().get("error", {}).get("message", "未知错误")
            print(f"  错误信息: {error_message}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ API连接测试失败: 连接超时")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ API连接测试失败: 无法连接到服务器")
        return False
    except Exception as e:
        print(f"✗ API连接测试失败: {str(e)}")
        return False

def select_agents() -> Tuple[str, str]:
    """选择对话智能体"""
    print("\n=== 选择AI智能体角色 ===")
    print("对话将采用一问一答的高认知探索模式")
    print("• 一个智能体作为提问者，提出高认知度问题")
    print("• 一个智能体作为回答者，提供富有洞见的回答")
    print("• 双方都会用玩耍的心态看待世界，保持好奇和创新")
    print("• 我们推荐选择'智谋'作为提问者，'慧眼'作为回答者")
    
    roles = list(AGENT_ROLES.keys())
    print("\n可选角色:")
    for i, role in enumerate(roles, 1):
        description = AGENT_ROLES[role]["description"]
        print(f"{i}. {role}: {description}")
    
    while True:
        try:
            print("\n请选择提问者（输入编号）：")
            questioner_idx = int(input()) - 1
            if 0 <= questioner_idx < len(roles):
                questioner_name = roles[questioner_idx]
                
                print(f"\n已选择提问者: {questioner_name}")
                print("\n请选择回答者（输入编号）：")
                for i, role in enumerate(roles, 1):
                    if role != questioner_name:
                        description = AGENT_ROLES[role]["description"]
                        print(f"{i}. {role}: {description}")
                
                answerer_idx = int(input()) - 1
                if 0 <= answerer_idx < len(roles):
                    answerer_name = roles[answerer_idx]
                    if answerer_name == questioner_name:
                        # 选择了相同的角色，选择另一个
                        print(f"提问者和回答者不能是同一个角色，将为您选择另一个角色作为回答者。")
                        for role in roles:
                            if role != questioner_name:
                                answerer_name = role
                                break
                    
                    return questioner_name, answerer_name
            
            print("\n无效的选择，请重试。")
        except (ValueError, IndexError):
            print("\n请输入有效的编号。")

def select_dialogue_mode() -> Tuple[str, Optional[str], Optional[int]]:
    """选择对话模式"""
    print("\n=== 请选择对话模式 ===")
    print("1. 高认知探索对话（一问一答式自动交流）")
    print("2. 交互式对话（您参与对话）")
    
    while True:
        try:
            mode = input("\n请选择（输入编号）：").strip()
            if mode == "1":
                print("\n请输入探索主题：")
                topic = input().strip()
                print("\n请输入对话轮数（默认5轮）：")
                rounds_input = input().strip()
                rounds = int(rounds_input) if rounds_input else 5
                return "auto", topic, rounds
            elif mode == "2":
                return "interactive", None, None
            else:
                print("\n请输入有效的编号（1或2）。")
        except ValueError:
            print("\n请输入有效的数字。")

def main():
    """主程序入口"""
    try:
        print("\n" + "=" * 50)
        print("Efficode 高认知探索对话系统".center(50))
        print("=" * 50)
        
        print("\n系统特点：")
        print("1. 玩耍心态 - 智能体以好奇心和创造力看待世界")
        print("2. 高认知问答 - 一个智能体提问，一个智能体回答")
        print("3. 新奇性原则 - 探索未知领域，提出创新见解")
        print("4. 高效压缩 - 使用智能多算法压缩，超过500字节才压缩")
        print("5. 自解压协议 - 数据包支持自解压，首次通信时包含语法说明")
        print("6. 精炼对话 - 少而精的问题，避免重复，注重启发")
        
        print("\n技术说明：")
        print("- AI模型引擎: SiliconFlow API")
        print("- 默认模型: deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
        print("- 通信协议: Efficode (高效压缩与自解压)")
        print("- 压缩算法: 自动选择zlib/gzip/zstd/brotli最优算法")
        print("- 压缩阈值: 超过500字节的内容才会自动压缩")
        print("- 首次通信: 自动包含解压方法和完整协议语法说明")
        
        # 自动使用默认API密钥
        print("\n正在使用默认API密钥...")
        api_key = "sk-dsayvcknhfsoftyaarputmhlbtdmltzwsmziktxahyhwrhup"
        
        # 测试API连接
        connection_ok = test_api_connection(api_key)
        if not connection_ok:
            print("\n警告: API连接测试失败，但仍将继续执行程序。")
        
        # 自动选择智能体
        questioner_name = "智谋"
        answerer_name = "慧眼"
        print(f"\n已自动选择智能体：")
        print(f"- 提问者: {questioner_name}")
        print(f"- 回答者: {answerer_name}")
        
        # 创建智能体实例
        print(f"\n正在初始化智能体...")
        questioner = AIAgent(questioner_name, api_key)
        answerer = AIAgent(answerer_name, api_key)
        print(f"智能体初始化完成！")
        
        # 创建对话管理器
        dialogue_manager = DialogueManager(questioner, answerer)
        
        # 自动设置对话主题和轮数
        topic = "AI与人类的未来"
        rounds = 3
        
        # 运行对话
        print("\n" + "=" * 50)
        print(f"开始高认知探索对话 | 主题: {topic} | 轮数: {rounds}")
        print(f"提问者: {questioner_name} | 回答者: {answerer_name}")
        print("=" * 50 + "\n")
        dialogue_manager.run_auto_conversation(topic, rounds)
        
        print("\n对话已结束。对话历史已保存到logs目录。")
        
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断。")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        logger.exception("详细错误信息:")
        print(f"\n程序遇到错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 