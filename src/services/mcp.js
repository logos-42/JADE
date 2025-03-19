/**
 * MCP (Master Control Protocol) 服务
 * 用于AI代理访问外部资源和执行决策的协议
 */

import { decompressContent } from './efficode';

// 模拟资源端点
const RESOURCE_ENDPOINTS = {
  KNOWLEDGE: '/api/knowledge',
  TOOLS: '/api/tools',
  SENSORS: '/api/sensors',
  EXECUTE: '/api/execute',
  FETCH: '/api/fetch'
};

// 请求状态
const REQUEST_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  DENIED: 'denied',
  ERROR: 'error',
  TIMEOUT: 'timeout'
};

// 资源访问记录
const accessLog = [];

/**
 * 创建一个MCP请求
 * @param {string} agentId - 发起请求的代理ID
 * @param {string} resourceType - 资源类型
 * @param {object} params - 请求参数
 * @returns {object} 请求对象
 */
export function createRequest(agentId, resourceType, params = {}) {
  if (!agentId) {
    throw new Error('代理ID是必需的');
  }
  
  if (!Object.values(RESOURCE_ENDPOINTS).includes(resourceType)) {
    throw new Error(`不支持的资源类型: ${resourceType}`);
  }
  
  const request = {
    id: `mcp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    agentId,
    resourceType,
    params,
    timestamp: Date.now(),
    status: REQUEST_STATUS.PENDING,
    attempts: 0,
    result: null
  };
  
  // 记录访问
  accessLog.push({
    time: new Date().toISOString(),
    agentId,
    resource: resourceType,
    requestId: request.id
  });
  
  return request;
}

/**
 * 提交MCP请求并等待响应
 * @param {object} request - MCP请求对象
 * @returns {Promise<object>} 响应结果
 */
export async function submitRequest(request) {
  if (!request || !request.id) {
    throw new Error('无效的MCP请求');
  }
  
  request.attempts += 1;
  
  // 模拟请求处理
  await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));
  
  // 模拟请求验证
  const isApproved = Math.random() > 0.2; // 80%概率批准
  
  if (!isApproved) {
    request.status = REQUEST_STATUS.DENIED;
    request.result = {
      success: false,
      message: '访问被拒绝：权限不足或资源不可用'
    };
    return request;
  }
  
  try {
    // 根据资源类型模拟不同的响应
    let responseData = null;
    
    switch (request.resourceType) {
      case RESOURCE_ENDPOINTS.KNOWLEDGE:
        responseData = simulateKnowledgeResponse(request.params);
        break;
      case RESOURCE_ENDPOINTS.TOOLS:
        responseData = simulateToolsResponse(request.params);
        break;
      case RESOURCE_ENDPOINTS.SENSORS:
        responseData = simulateSensorsResponse(request.params);
        break;
      case RESOURCE_ENDPOINTS.EXECUTE:
        responseData = simulateExecuteResponse(request.params);
        break;
      case RESOURCE_ENDPOINTS.FETCH:
        responseData = simulateFetchResponse(request.params);
        break;
      default:
        throw new Error(`未实现的资源类型: ${request.resourceType}`);
    }
    
    request.status = REQUEST_STATUS.APPROVED;
    request.result = {
      success: true,
      data: responseData
    };
  } catch (error) {
    request.status = REQUEST_STATUS.ERROR;
    request.result = {
      success: false,
      message: error.message,
      error: String(error)
    };
  }
  
  return request;
}

/**
 * 获取MCP访问日志
 * @param {string} agentId - 可选的代理ID过滤器
 * @returns {array} 访问日志
 */
export function getAccessLog(agentId = null) {
  if (agentId) {
    return accessLog.filter(entry => entry.agentId === agentId);
  }
  return [...accessLog];
}

/**
 * 清除MCP访问日志
 * @param {string} agentId - 可选的代理ID过滤器
 */
export function clearAccessLog(agentId = null) {
  if (agentId) {
    const index = accessLog.findIndex(entry => entry.agentId === agentId);
    if (index !== -1) {
      accessLog.splice(index);
    }
  } else {
    accessLog.length = 0;
  }
}

// 模拟知识库响应
function simulateKnowledgeResponse(params) {
  const { query, format = 'text' } = params;
  
  if (!query) {
    throw new Error('查询参数是必需的');
  }
  
  const knowledge = {
    answer: `关于"${query}"的知识库结果`,
    confidence: 0.7 + Math.random() * 0.3,
    sources: [
      { name: '内部知识库', reliability: 0.9 },
      { name: '公共数据集', reliability: 0.6 }
    ]
  };
  
  if (format === 'compressed') {
    // TODO: 使用efficode压缩响应
    return `COMPRESSED:${JSON.stringify(knowledge)}`;
  }
  
  return knowledge;
}

// 模拟工具响应
function simulateToolsResponse(params) {
  const { toolName, args = {} } = params;
  
  if (!toolName) {
    throw new Error('工具名称是必需的');
  }
  
  return {
    toolName,
    result: `执行工具"${toolName}"的模拟结果，参数: ${JSON.stringify(args)}`,
    executionTime: Math.random() * 500
  };
}

// 模拟传感器响应
function simulateSensorsResponse(params) {
  const { sensorType } = params;
  
  if (!sensorType) {
    throw new Error('传感器类型是必需的');
  }
  
  return {
    sensorType,
    reading: Math.random() * 100,
    timestamp: Date.now(),
    status: 'active'
  };
}

// 模拟执行响应
function simulateExecuteResponse(params) {
  const { command, context = {} } = params;
  
  if (!command) {
    throw new Error('命令是必需的');
  }
  
  return {
    executed: true,
    command,
    context,
    output: `执行命令"${command}"的模拟输出`,
    exitCode: 0
  };
}

// 模拟获取响应
function simulateFetchResponse(params) {
  const { url, method = 'GET' } = params;
  
  if (!url) {
    throw new Error('URL是必需的');
  }
  
  return {
    url,
    method,
    status: 200,
    headers: {
      'content-type': 'application/json'
    },
    data: {
      success: true,
      message: `从${url}获取的模拟数据`
    }
  };
}

export default {
  RESOURCE_ENDPOINTS,
  REQUEST_STATUS,
  createRequest,
  submitRequest,
  getAccessLog,
  clearAccessLog
}; 