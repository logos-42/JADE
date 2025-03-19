import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import * as api from '../services/api'

// Efficode工具类
import { compressContent, decompressContent } from '../services/efficode'

export const useAgentStore = defineStore('agents', () => {
  // 状态
  const agents = ref([])
  const conversations = ref([])
  const currentConversationId = ref(null)
  const loading = ref(false)
  
  // Getter
  const getAgentById = computed(() => {
    return (id) => agents.value.find(agent => agent.id === parseInt(id))
  })
  
  const getCurrentConversation = computed(() => {
    if (!currentConversationId.value) return null
    return conversations.value.find(conv => conv.id === currentConversationId.value) || null
  })
  
  // 动作
  
  // 加载智能体列表
  async function loadAgents() {
    try {
      loading.value = true;
      console.log("开始加载智能体列表...");
      
      // 尝试最多3次
      let attempts = 0;
      let maxAttempts = 3;
      let response;
      
      while (attempts < maxAttempts) {
        try {
          response = await api.getAgents();
          break; // 成功则跳出循环
        } catch (err) {
          attempts++;
          console.warn(`加载智能体尝试 ${attempts}/${maxAttempts} 失败:`, err);
          
          if (attempts >= maxAttempts) {
            throw err; // 达到最大尝试次数，抛出错误
          }
          
          // 等待一秒后重试
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
      
      console.log("智能体API响应:", response);
      
      // 获取本地存储的头像和价格
      const localAgents = JSON.parse(localStorage.getItem('agent_avatars') || '{}');
      
      // 合并API返回的数据和本地数据
      agents.value = response.map(agent => {
        // 检查本地是否有该智能体的数据
        const localData = localAgents[agent.id] || {};
        const price = localData.price || 0.01;
        
        return {
          ...agent,
          avatar: localData.avatar || null,
          price: price,
          marketValue: price, // 使用价格作为市场价值
          createdAt: agent.created_at,
          updatedAt: agent.updated_at
        };
      });
      
      console.log("成功加载智能体，数量:", agents.value.length);
      return { success: true };
    } catch (error) {
      console.error('加载智能体失败:', error);
      // 显示更友好的错误信息
      const errorMsg = error.message && error.message.includes('网络连接') 
        ? '无法连接到后端服务器，请确保服务已启动'
        : error.message || '加载智能体列表失败';
      return { success: false, message: errorMsg };
    } finally {
      loading.value = false;
    }
  }
  
  // 创建新智能体
  async function createAgent(agentData) {
    try {
      loading.value = true;
      
      // 准备带角色描述的JSON结构
      const roleDescription = agentData.description || "";
      
      // 发送API请求
      console.log("发送创建智能体请求:", {
        name: agentData.name,
        role: agentData.role || "智能体",
        description: roleDescription,
        price: agentData.price || 0.01
      });
      
      const response = await api.createAgent(
        agentData.name, 
        agentData.role || "智能体", 
        roleDescription
      );
      
      if (response) {
        // 存储前端上传的头像和价格
        let localAgents = JSON.parse(localStorage.getItem('agent_avatars') || '{}');
        localAgents[response.id] = {
          avatar: agentData.avatar,
          price: agentData.price || 0.01
        };
        localStorage.setItem('agent_avatars', JSON.stringify(localAgents));
        
        // 添加到本地状态，包含前端自定义字段
        const newAgent = {
          id: response.id,
          name: response.name,
          description: roleDescription,
          role: response.role,
          did: response.did,
          avatar: agentData.avatar || null,
          price: agentData.price || 0.01,
          marketValue: agentData.price || 0.01, // 使用价格作为市场价值
          createdAt: response.created_at,
          updatedAt: response.updated_at
        };
        
        agents.value.push(newAgent);
        return { success: true, agent: newAgent };
      }
      return { success: false, message: "创建智能体失败" };
    } catch (error) {
      console.error('创建智能体失败:', error);
      return { success: false, message: error.message };
    } finally {
      loading.value = false;
    }
  }
  
  // 更新智能体
  function updateAgent(id, data) {
    const index = agents.value.findIndex(agent => agent.id === id)
    if (index !== -1) {
      agents.value[index] = { ...agents.value[index], ...data }
      return true
    }
    return false
  }
  
  // 铸造智能体NFT
  async function mintAgentNFT(agentId, walletAddress) {
    // 这里预留NFT铸造功能，后续集成区块链功能
    const agent = getAgentById.value(agentId)
    if (!agent) return { success: false, message: '智能体不存在' }
    
    try {
      // 模拟NFT铸造过程
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 模拟成功
      updateAgent(agentId, {
        nftMinted: true,
        nftAddress: `0x${Math.random().toString(16).substr(2, 40)}`,
        mintedAt: new Date().toISOString(),
        ownerAddress: walletAddress
      })
      
      return { 
        success: true, 
        message: '智能体NFT铸造成功',
        nftAddress: agent.nftAddress
      }
    } catch (error) {
      console.error('铸造NFT失败:', error)
      return { 
        success: false, 
        message: `铸造失败: ${error.message || '未知错误'}` 
      }
    }
  }
  
  // 创建对话
  async function createConversation(agentId1, agentId2 = 0) {
    try {
      console.log(`开始创建对话，智能体ID: ${agentId1}, 伙伴ID: ${agentId2}`);
      
      // 调用API创建对话
      const response = await api.createConversation(agentId1, agentId2);
      
      if (response && response.conversation_id) {
        const agent1 = getAgentById.value(agentId1);
        
        // 如果agentId2为0，表示用户与智能体对话
        // 如果不为0，表示两个智能体之间的对话
        let participant2Name = '用户';
        if (agentId2 !== 0) {
          const agent2 = getAgentById.value(agentId2);
          if (!agent2) {
            return { success: false, message: '对话智能体不存在' };
          }
          participant2Name = agent2.name;
        }
        
        const newConversation = {
          id: response.conversation_id,
          createdAt: new Date().toISOString(),
          participants: [
            { agentId: agentId1, name: agent1 ? agent1.name : `智能体${agentId1}` },
            { agentId: agentId2, name: participant2Name }
          ],
          messages: []
        };
        
        conversations.value.push(newConversation);
        currentConversationId.value = response.conversation_id;
        
        // 加载初始消息
        await loadConversationMessages(response.conversation_id);
        
        console.log(`对话创建成功，ID: ${response.conversation_id}`);
        return { success: true, conversationId: response.conversation_id };
      }
      
      console.error('创建对话失败:', response);
      return { 
        success: false, 
        message: response.message || '创建对话失败' 
      };
    } catch (error) {
      console.error('创建对话失败:', error);
      
      // 使用真实后端，不再使用本地模拟
      return { 
        success: false, 
        message: `创建对话失败: ${error.message}。请确保后端服务正常运行。` 
      };
    }
  }
  
  // 加载对话消息
  async function loadConversationMessages(conversationId) {
    try {
      const conversation = conversations.value.find(conv => conv.id === conversationId);
      if (!conversation) {
        return { success: false, message: '对话不存在' };
      }
      
      const messages = await api.getConversationMessages(conversationId);
      
      if (messages && Array.isArray(messages)) {
        // 清空现有消息并添加新消息
        conversation.messages = messages.map(msg => ({
          id: msg.id,
          timestamp: msg.created_at,
          type: msg.sender === 'SYSTEM' ? 'system' : 'message',
          senderId: msg.sender,
          receiverId: msg.receiver,
          content: msg.content,
          originalContent: msg.originalContent,
          contentType: msg.content_type
        }));
        
        return { success: true, count: messages.length };
      }
      
      return { success: true, count: 0 };
    } catch (error) {
      console.error(`加载对话${conversationId}消息失败:`, error);
      return { 
        success: false, 
        message: error.message || '加载消息时出错' 
      };
    }
  }
  
  // 发送消息
  async function sendMessage(conversationId, senderAgentId, content, type = 'message') {
    try {
      const conversation = conversations.value.find(conv => conv.id === conversationId);
    if (!conversation) {
        return { success: false, message: '对话不存在' };
      }
      
      // 确定发送者和接收者
      let senderId = senderAgentId.toString();
      let receiverId = "0"; // 默认接收者是用户
      
      // 如果发送者是用户，接收者是智能体
      if (senderId === "0") {
        receiverId = conversation.participants[0].agentId.toString();
      }
      
      // 如果有两个智能体，确保接收者是另一个智能体
      if (conversation.participants.length > 1 && 
          conversation.participants[1].agentId !== 0 &&
          senderId === conversation.participants[0].agentId.toString()) {
        receiverId = conversation.participants[1].agentId.toString();
      }
      
      // 添加"发送中"状态的消息到本地状态
      const tempMessageId = uuidv4();
      const tempMessage = {
        id: tempMessageId,
        timestamp: new Date().toISOString(),
        type: 'pending',
        senderId: senderId,
        receiverId: receiverId,
        content: content,
        contentType: 'text'
      };
      
      conversation.messages.push(tempMessage);
      
      // 调用API发送消息
      const response = await api.sendMessage(
        conversationId,
        senderId,
        receiverId,
        content,
        'text'
      );
      
      if (response && response.success) {
        // 更新临时消息状态为已发送
        const tempIndex = conversation.messages.findIndex(m => m.id === tempMessageId);
        if (tempIndex !== -1) {
          conversation.messages[tempIndex].type = type;
          conversation.messages[tempIndex].id = response.message_id;
        }
        
        return { success: true, messageId: response.message_id };
      }
      
      // 发送失败，更新消息状态
      const tempIndex = conversation.messages.findIndex(m => m.id === tempMessageId);
      if (tempIndex !== -1) {
        conversation.messages[tempIndex].type = 'error';
        conversation.messages[tempIndex].error = response.message || '发送失败';
      }
      
      return { 
        success: false, 
        message: response.message || '发送消息失败' 
      };
    } catch (error) {
      console.error('发送消息失败:', error);
      
      // 查找临时消息并标记为错误
      const conversation = conversations.value.find(conv => conv.id === conversationId);
      if (conversation) {
        const tempIndex = conversation.messages.findIndex(
          m => m.type === 'pending' && m.senderId === senderAgentId.toString()
        );
        
        if (tempIndex !== -1) {
          conversation.messages[tempIndex].type = 'error';
          conversation.messages[tempIndex].error = error.message || '发送失败';
        }
      }
      
      return { 
        success: false, 
        message: error.message || '发送消息时出错' 
      };
    }
  }
  
  // 建立WebSocket连接，接收实时消息
  function connectWebSocket(agentId) {
    return api.connectWebSocket(agentId, (message) => {
      // 处理接收到的WebSocket消息
      console.log('收到WebSocket消息:', message);
      
      // 如果消息是对象并且包含type和message字段，可能是来自mock服务器的消息
      if (message && typeof message === 'object') {
        if (message.type === 'new_message' && message.message) {
          const msg = message.message;
          
          // 查找对应的对话
          const conversation = conversations.value.find(
            conv => conv.id === msg.conversation_id
          );
          
          if (conversation) {
            // 添加消息到对话
            conversation.messages.push({
              id: msg.id,
              timestamp: msg.created_at,
              type: 'message',
              senderId: msg.sender,
              receiverId: msg.receiver,
              content: msg.content,
              contentType: msg.content_type
            });
          }
        }
      }
      // 如果是Efficode格式的消息
      else if (message && message.opCode && message.params) {
        // 这里处理解析后的Efficode消息
        if (message.opCode === 'DATA' && message.params.content) {
          // 查找发送者正在进行的对话
          const senderId = message.params.senderId || '';
          
          // 尝试查找当前对话
          if (currentConversationId.value) {
            const conversation = conversations.value.find(
              conv => conv.id === currentConversationId.value
            );
            
            if (conversation) {
              // 添加消息到对话
              conversation.messages.push({
                id: uuidv4(), // 临时ID，实际应使用服务器返回的ID
                timestamp: new Date().toISOString(),
                type: 'message',
                senderId: senderId,
                content: message.params.content,
                contentType: message.params.type || 'text'
              });
            }
          }
        }
      }
    });
  }
  
  // 导出状态和方法
  return {
    agents,
    conversations,
    currentConversationId,
    loading,
    getAgentById,
    getCurrentConversation,
    loadAgents,
    createAgent,
    updateAgent,
    mintAgentNFT,
    createConversation,
    loadConversationMessages,
    sendMessage,
    connectWebSocket
  }
}) 