import axios from 'axios';
import { createEfficodeMessage, compressContent, decompressContent, parseEfficodeMessage } from './efficode';

// 模拟数据存储
const mockDB = {
  agents: JSON.parse(localStorage.getItem('mock_agents') || '[]'),
  conversations: JSON.parse(localStorage.getItem('mock_conversations') || '[]'),
  messages: JSON.parse(localStorage.getItem('mock_messages') || '[]'),
  agentIdCounter: parseInt(localStorage.getItem('mock_agent_counter') || '1'),
  conversationIdCounter: parseInt(localStorage.getItem('mock_conversation_counter') || '1'),
  messageIdCounter: parseInt(localStorage.getItem('mock_message_counter') || '1')
};

// 保存模拟数据到localStorage
function saveMockData() {
  localStorage.setItem('mock_agents', JSON.stringify(mockDB.agents));
  localStorage.setItem('mock_conversations', JSON.stringify(mockDB.conversations));
  localStorage.setItem('mock_messages', JSON.stringify(mockDB.messages));
  localStorage.setItem('mock_agent_counter', mockDB.agentIdCounter.toString());
  localStorage.setItem('mock_conversation_counter', mockDB.conversationIdCounter.toString());
  localStorage.setItem('mock_message_counter', mockDB.messageIdCounter.toString());
}

// 初始化模拟数据（如果为空）
function initMockData() {
  if (mockDB.agents.length === 0) {
    // 添加几个示例智能体
    mockDB.agents = [
      {
        id: 1,
        name: '助手智能体',
        role: '智能助手',
        description: '我是一个全能助手，可以回答各种问题并提供帮助。',
        did: `did:efficode:${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        name: '创意大师',
        role: '创意助手',
        description: '我擅长提供创意想法、设计建议和艺术灵感。',
        did: `did:efficode:${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        name: '技术专家',
        role: '技术顾问',
        description: '我可以提供编程、技术和工程方面的专业建议。',
        did: `did:efficode:${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ];
    
    mockDB.agentIdCounter = 4;
    saveMockData();
  }
}

// 使用模拟模式
const USE_MOCK = true; // 使用真实后端，后端数据库字段映射已修复

// 打印启动模式
console.log('=== 智能体系统启动 ===');
console.log(`模拟模式: ${USE_MOCK ? '开启' : '关闭'}`);
console.log(`后端模式: 使用真实后端API，DID字段映射已修复`);
console.log('=====================');

// 初始化模拟数据
initMockData();

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器 - 压缩大消息并处理模拟API
api.interceptors.request.use(
  async (config) => {
    // 模拟API模式
    if (USE_MOCK) {
      const mockResponse = await handleMockRequest(config);
      return Promise.reject({
        config,
        response: {
          data: mockResponse,
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config,
        },
        isAxiosError: true,
        toJSON: () => ({}),
      });
    }
    
    // 如果是发送消息，检查是否需要压缩
    if (config.url === '/messages' && config.method === 'post') {
      const content = config.data.content;
      if (content && content.length > 500) {
        config.data.content = await compressContent(content);
        config.data.compressed = true;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器 - 解压缩消息
api.interceptors.response.use(
  async (response) => {
    // 如果是消息列表，检查是否需要解压缩
    if (response.config.url.includes('/messages') && response.data) {
      if (Array.isArray(response.data)) {
        for (const msg of response.data) {
          if (msg.compressed && msg.content) {
            msg.content = await decompressContent(msg.content);
            delete msg.compressed;
          }
        }
      }
    }
    return response;
  },
  (error) => {
    // 如果是模拟响应，直接返回模拟数据
    if (error.response && error.response.data && USE_MOCK) {
      return Promise.resolve({ data: error.response.data });
    }
    
    // 处理API错误
    console.error('API请求错误:', error);
    
    // 检查网络连接
    if (!navigator.onLine) {
      return Promise.reject(new Error('网络连接已断开，请检查您的网络设置'));
    }
    
    // 从错误响应中提取信息
    if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status;
      const data = error.response.data;
      
      // 提取错误消息
      let errorMessage = `服务器错误 [${status}]`;
      if (data && data.error) {
        errorMessage += `: ${data.error}`;
      }
      
      return Promise.reject(new Error(errorMessage));
    } else if (error.request) {
      // 请求发送但没有收到响应，可能是服务器未启动
      return Promise.reject(new Error('无法连接到服务器，请确认后端服务是否启动'));
    }
    
    return Promise.reject(error);
  }
);

// 处理模拟请求
async function handleMockRequest(config) {
  // 等待一小段时间模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 300));
  
  const url = config.url;
  const method = config.method.toUpperCase();
  const data = config.data;
  
  console.log(`[模拟API] ${method} ${url}`, data);
  
  // 处理不同的API请求
  if (url === '/agents' && method === 'GET') {
    return mockDB.agents;
  }
  
  if (url === '/agents' && method === 'POST') {
    const newAgent = {
      id: mockDB.agentIdCounter++,
      name: data.name,
      role: data.role,
      description: data.description,
      did: `did:efficode:${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    mockDB.agents.push(newAgent);
    saveMockData();
    return newAgent;
  }
  
  if (url.match(/\/agents\/\d+/) && method === 'GET') {
    const id = parseInt(url.split('/').pop());
    const agent = mockDB.agents.find(a => a.id === id);
    return agent || { error: '智能体不存在' };
  }
  
  if (url === '/conversations' && method === 'POST') {
    const newConversation = {
      conversation_id: mockDB.conversationIdCounter++,
      title: data.title,
      mode: data.mode,
      agent_id: data.agent_id,
      partner_id: data.partner_id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    mockDB.conversations.push(newConversation);
    saveMockData();
    return {
      conversation_id: newConversation.conversation_id,
      success: true,
      message: '对话创建成功'
    };
  }
  
  if (url.match(/\/conversations\/\d+\/messages/) && method === 'GET') {
    const conversationId = parseInt(url.split('/')[2]);
    return mockDB.messages.filter(m => m.conversation_id === conversationId);
  }
  
  if (url === '/messages' && method === 'POST') {
    const newMessage = {
      id: mockDB.messageIdCounter++,
      conversation_id: data.conversation_id,
      sender: data.sender,
      receiver: data.receiver,
      content: data.content,
      content_type: data.content_type,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    mockDB.messages.push(newMessage);
    
    // 自动生成AI回复
    if (data.receiver !== '0' && data.receiver !== 'user') {
      setTimeout(() => {
        const aiReply = {
          id: mockDB.messageIdCounter++,
          conversation_id: data.conversation_id,
          sender: data.receiver,
          receiver: data.sender,
          content: generateAIResponse(data.content),
          content_type: 'text',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        mockDB.messages.push(aiReply);
        saveMockData();
        
        // 如果有WebSocket连接，通知新消息
        if (mockWSHandlers.has(data.sender)) {
          const handlers = mockWSHandlers.get(data.sender);
          handlers.forEach(handler => {
            handler({
              type: 'new_message',
              message: aiReply
            });
          });
        }
      }, 1000);
    }
    
    saveMockData();
    return {
      message_id: newMessage.id,
      success: true
    };
  }
  
  return { error: '未知的API端点' };
}

// 生成AI响应
function generateAIResponse(message) {
  const responses = [
    "我理解您的问题，让我来解答。",
    "这是一个有趣的观点，我的看法是...",
    "感谢您的信息，我已经记录下来了。",
    "我需要更多信息来帮助您解决这个问题。",
    "根据我的分析，您可能需要考虑以下几点...",
    "我已处理您的请求，结果如下。",
    "这是一个复杂的问题，让我分析一下。",
    "我已经查询了相关信息，以下是我的发现。"
  ];
  
  const response = responses[Math.floor(Math.random() * responses.length)];
  return `${response}\n\n您说: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`;
}

// 模拟WebSocket连接
const mockWSHandlers = new Map();

// 创建智能体
export async function createAgent(name, role, description = '') {
  try {
    console.log(`开始创建智能体: 名称=${name}, 角色=${role}, 描述长度=${description.length}`);
    
    // 确保所有字段都有值
    if (!name || !role) {
      throw new Error('名称和角色不能为空');
    }
    
    const response = await api.post('/agents', { name, role, description });
    console.log(`创建智能体成功, 返回数据:`, response.data);
    
    // 验证返回的数据包含必要字段
    if (!response.data || !response.data.id || !response.data.did) {
      console.warn('警告: 创建智能体返回的数据缺少必要字段:', response.data);
    }
    
    return response.data;
  } catch (error) {
    console.error('创建智能体失败:', error);
    
    // 增强错误信息
    let errorMessage = '创建智能体失败';
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage += `: ${error.response.data.error}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    
    // 抛出更有用的错误信息
    throw new Error(errorMessage);
  }
}

// 获取智能体列表
export async function getAgents() {
  try {
    const response = await api.get('/agents');
    return response.data;
  } catch (error) {
    console.error('获取智能体列表失败:', error);
    throw error;
  }
}

// 获取单个智能体
export async function getAgentById(id) {
  try {
    const response = await api.get(`/agents/${id}`);
    return response.data;
  } catch (error) {
    console.error(`获取智能体${id}失败:`, error);
    throw error;
  }
}

// 创建对话
export async function createConversation(agentId, partnerId = 0) {
  try {
    const response = await api.post('/conversations', {
      title: `与智能体${agentId}的对话`,
      mode: 'interactive',
      agent_id: agentId,
      partner_id: partnerId
    });
    return response.data;
  } catch (error) {
    console.error('创建对话失败:', error);
    throw error;
  }
}

// 获取对话消息
export async function getConversationMessages(conversationId) {
  try {
    const response = await api.get(`/conversations/${conversationId}/messages`);
    
    // 解析Efficode消息
    const messages = [];
    for (const msg of response.data) {
      let content = msg.content;
      
      // 尝试解析Efficode消息
      try {
        const parsed = parseEfficodeMessage(content);
        if (parsed && !parsed.error) {
          // 如果是Promise（解压缩过程），等待解析完成
          if (parsed instanceof Promise) {
            const resolvedParsed = await parsed;
            if (resolvedParsed.params && resolvedParsed.params.content) {
              content = resolvedParsed.params.content;
            }
          } else if (parsed.params && parsed.params.content) {
            content = parsed.params.content;
          }
        }
      } catch (e) {
        console.warn('解析消息失败，使用原始内容:', e);
      }
      
      messages.push({
        ...msg,
        originalContent: msg.content,
        content: content
      });
    }
    
    return messages;
  } catch (error) {
    console.error(`获取对话${conversationId}消息失败:`, error);
    throw error;
  }
}

// 发送消息
export async function sendMessage(conversationId, sender, receiver, content, contentType = 'text') {
  try {
    // 创建Efficode格式消息
    const efficodeContent = await createEfficodeMessage('DATA', {
      content,
      type: contentType
    });
    
    const response = await api.post('/messages', {
      conversation_id: conversationId,
      sender,
      receiver,
      content: efficodeContent,
      content_type: contentType
    });
    return response.data;
  } catch (error) {
    console.error('发送消息失败:', error);
    throw error;
  }
}

// WebSocket连接
export function connectWebSocket(agentId, onMessage) {
  if (USE_MOCK) {
    // 模拟WebSocket连接
    console.log(`[模拟WebSocket] 已连接，智能体ID: ${agentId}`);
    
    // 将消息处理器添加到映射中
    if (!mockWSHandlers.has(agentId.toString())) {
      mockWSHandlers.set(agentId.toString(), []);
    }
    
    mockWSHandlers.get(agentId.toString()).push(onMessage);
    
    // 返回模拟的WebSocket对象
    return {
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
      close: () => {
        console.log(`[模拟WebSocket] 连接关闭，智能体ID: ${agentId}`);
        mockWSHandlers.delete(agentId.toString());
      },
      send: (message) => {
        console.log(`[模拟WebSocket] 发送消息: ${message}`);
      }
    };
  } else {
    // 真实WebSocket连接
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8080/ws?agent_id=${agentId}`;
    
    console.log(`[WebSocket] 连接到 ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log(`[WebSocket] 连接已建立，智能体ID: ${agentId}`);
    };
    
    ws.onmessage = (event) => {
      console.log('[WebSocket] 收到消息:', event.data);
      
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('[WebSocket] 解析消息失败:', error);
        // 尝试作为Efficode消息解析
        try {
          const message = parseEfficodeMessage(event.data);
          onMessage(message);
        } catch (e) {
          console.error('[WebSocket] 解析Efficode消息失败:', e);
          // 作为原始消息传递
          onMessage({
            type: 'raw',
            content: event.data
          });
        }
      }
    };
    
    ws.onerror = (error) => {
      console.error('[WebSocket] 错误:', error);
    };
    
    ws.onclose = (event) => {
      console.log(`[WebSocket] 连接关闭，代码: ${event.code}, 原因: ${event.reason}`);
      
      // 如果连接异常关闭，可以尝试重连
      if (event.code !== 1000) {
        console.log('[WebSocket] 尝试在5秒后重新连接...');
        setTimeout(() => {
          connectWebSocket(agentId, onMessage);
        }, 5000);
      }
    };
    
    return ws;
  }
}

export default {
  createAgent,
  getAgents,
  getAgentById,
  createConversation,
  getConversationMessages,
  sendMessage,
  connectWebSocket
}; 
