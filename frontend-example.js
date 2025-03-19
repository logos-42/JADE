 // API接口封装
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api';
const WS_URL = 'ws://localhost:8080/ws';

// WebSocket连接
export function connectWebSocket(agentId, onMessage) {
  const socket = new WebSocket(`${WS_URL}?agent_id=${agentId}`);
  
  socket.onopen = () => {
    console.log('WebSocket连接已建立');
  };
  
  socket.onmessage = (event) => {
    const message = event.data;
    // 解析Efficode消息
    const parsedMessage = parseEfficodeMessage(message);
    if (onMessage && typeof onMessage === 'function') {
      onMessage(parsedMessage);
    }
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket错误:', error);
  };
  
  socket.onclose = () => {
    console.log('WebSocket连接已关闭');
  };
  
  return socket;
}

// 解析Efficode消息
export function parseEfficodeMessage(message) {
  if (!message || typeof message !== 'string' || message.length === 0) {
    return { error: '空消息' };
  }

  const prefix = message.charAt(0);
  let opCode = '';
  let params = {};
  
  try {
    if (prefix === '@') {
      // DID消息
      const parts = message.substring(1).split(':', 2);
      opCode = parts[0];
      if (parts.length > 1) {
        try {
          params = JSON.parse(parts[1]);
        } catch (e) {
          params = { value: parts[1] };
        }
      }
    } else if (prefix === '#') {
      // REQ或DATA消息
      const parts = message.substring(1).split('?', 2);
      opCode = parts[0];
      
      if (parts.length > 1) {
        const paramPairs = parts[1].split('&');
        for (const pair of paramPairs) {
          const [key, value] = pair.split('=', 2);
          if (key && value !== undefined) {
            params[key] = value;
          }
        }
      }
    } else if (prefix === '!') {
      // ACK或ERROR消息
      const parts = message.substring(1).split(':', 2);
      opCode = parts[0];
      if (parts.length > 1) {
        try {
          params = JSON.parse(parts[1]);
        } catch (e) {
          params = { message: parts[1] };
        }
      }
    }
  } catch (error) {
    return { error: '解析失败: ' + error.message };
  }
  
  return { opCode, params };
}

// 创建Efficode消息
export function createEfficodeMessage(opCode, params) {
  let prefix = '#';
  if (opCode === 'DID') {
    prefix = '@';
  } else if (opCode === 'ACK' || opCode === 'ERROR') {
    prefix = '!';
  }

  let paramStr = '';
  if (params) {
    if (opCode === 'DID' || opCode === 'ACK' || opCode === 'ERROR') {
      paramStr = ':' + JSON.stringify(params);
    } else {
      const parts = [];
      for (const [key, value] of Object.entries(params)) {
        parts.push(`${key}=${value}`);
      }
      paramStr = '?' + parts.join('&');
    }
  }

  return prefix + opCode + paramStr;
}

// 智能体管理API
export const AgentAPI = {
  // 获取智能体列表
  async getAll() {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents`);
      return response.data;
    } catch (error) {
      console.error('获取智能体失败:', error);
      return [];
    }
  },
  
  // 创建智能体
  async create(name, role) {
    try {
      const response = await axios.post(`${API_BASE_URL}/agents`, { 
        name, 
        role 
      });
      return response.data;
    } catch (error) {
      console.error('创建智能体失败:', error);
      throw error;
    }
  }
};

// 对话管理API
export const ConversationAPI = {
  // 创建对话
  async create(title, mode) {
    try {
      const response = await axios.post(`${API_BASE_URL}/conversations`, {
        title,
        mode
      });
      return response.data;
    } catch (error) {
      console.error('创建对话失败:', error);
      throw error;
    }
  },
  
  // 获取对话消息
  async getMessages(conversationId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversations/${conversationId}/messages`);
      return response.data;
    } catch (error) {
      console.error('获取消息失败:', error);
      return [];
    }
  }
};

// 消息管理API
export const MessageAPI = {
  // 发送消息
  async send(conversationId, sender, receiver, content, contentType = 'text') {
    try {
      const response = await axios.post(`${API_BASE_URL}/messages`, {
        conversation_id: conversationId,
        sender,
        receiver,
        content,
        content_type: contentType
      });
      return response.data;
    } catch (error) {
      console.error('发送消息失败:', error);
      throw error;
    }
  }
};

// 示例使用
async function example() {
  // 1. 创建智能体
  const agent1 = await AgentAPI.create('用户智能体', '用户');
  const agent2 = await AgentAPI.create('AI助手', 'ai_assistant');
  
  // 2. 创建对话
  const conversation = await ConversationAPI.create('新对话', 'interactive');
  
  // 3. 建立WebSocket连接
  const socket = connectWebSocket(agent1.name, (message) => {
    console.log('收到消息:', message);
    // 处理接收到的消息
  });
  
  // 4. 发送消息
  await MessageAPI.send(
    conversation.id,
    agent1.name,
    agent2.name,
    '你好，AI助手！',
    'text'
  );
  
  // 5. 获取对话消息
  const messages = await ConversationAPI.getMessages(conversation.id);
  console.log('对话历史:', messages);
}