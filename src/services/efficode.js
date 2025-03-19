/**
 * Efficode协议实现
 * 用于智能体之间通信的数据压缩和解压功能
 */

// 压缩阈值，超过此大小才进行压缩
const COMPRESSION_THRESHOLD = 500;

/**
 * 压缩内容
 * @param {string} content 需要压缩的内容
 * @returns {string} 压缩后的内容或原内容（如果不需要压缩）
 */
export async function compressContent(content) {
  if (typeof content !== 'string') {
    throw new Error('只能压缩字符串内容');
  }
  
  // 计算内容字节大小
  const contentSize = new Blob([content]).size;
  
  // 如果小于阈值，不进行压缩
  if (contentSize < COMPRESSION_THRESHOLD) {
    return content;
  }
  
  try {
    // 使用base64编码模拟压缩
    const compressedData = btoa(encodeURIComponent(content));
    
    // 在前端模拟中，我们使用与Go后端兼容的格式
    return `EFFICODE:${compressedData}`;
  } catch (error) {
    console.error('压缩失败:', error);
    return content; // 失败则返回原内容
  }
}

/**
 * 解压内容
 * @param {string} compressedContent 压缩的内容
 * @returns {string} 解压后的原始内容
 */
export async function decompressContent(compressedContent) {
  try {
    // 检查是否是EFFICODE格式的压缩数据
    if (typeof compressedContent === 'string' && compressedContent.startsWith('EFFICODE:')) {
      const compressedData = compressedContent.substring(9); // 移除 "EFFICODE:" 前缀
      return decodeURIComponent(atob(compressedData));
    }
    
    // 尝试解析JSON (兼容Go后端的JSON格式)
    try {
      const parsedData = JSON.parse(compressedContent);
      
      // 检查是否是有效的压缩数据
      if (parsedData && parsedData.method && parsedData.data) {
        return decodeURIComponent(atob(parsedData.data));
      }
    } catch (e) {
      // 不是JSON格式，继续处理
    }
    
    // 如果不是压缩数据，返回原内容
    return compressedContent;
  } catch (error) {
    console.error('解压失败:', error);
    // 解压失败，返回原内容
    return compressedContent;
  }
}

/**
 * 解析Efficode消息
 * @param {string} message - Efficode格式的消息
 * @returns {Object} - 解析后的消息对象
 */
export function parseEfficodeMessage(message) {
  if (!message || typeof message !== 'string') {
    return { error: '无效消息' };
  }
  
  try {
    const prefix = message.charAt(0);
    let opCode = '';
    let params = {};
    
    if (prefix === '@') {
      // DID消息格式: @DID:{...}
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
      // REQ/DATA消息格式: #REQ?param1=value1&param2=value2
      const parts = message.substring(1).split('?', 2);
      opCode = parts[0];
      if (parts.length > 1) {
        const paramPairs = parts[1].split('&');
        for (const pair of paramPairs) {
          const [key, value] = pair.split('=', 2);
          if (key && value !== undefined) {
            params[key] = decodeURIComponent(value);
          }
        }
      }
    } else if (prefix === '!') {
      // ACK/ERROR消息格式: !ACK:{...}
      const parts = message.substring(1).split(':', 2);
      opCode = parts[0];
      if (parts.length > 1) {
        try {
          params = JSON.parse(parts[1]);
        } catch (e) {
          params = { message: parts[1] };
        }
      }
    } else {
      return { error: '无效的消息前缀' };
    }
    
    // 检查内容是否需要解压
    if (opCode === 'DATA' && params.content && typeof params.content === 'string') {
      if (params.compressed === 'true' || params.content.startsWith('EFFICODE:')) {
        try {
          // 由于decompressContent是异步的，需要用Promise包装
          return new Promise(async (resolve) => {
            params.content = await decompressContent(params.content);
            delete params.compressed;
            resolve({ opCode, params });
          });
        } catch (e) {
          console.error('解压消息内容失败:', e);
        }
      }
    }
    
    return { opCode, params };
  } catch (error) {
    console.error('解析Efficode消息失败:', error);
    return { error: '解析失败: ' + error.message };
  }
}

/**
 * 创建Efficode消息
 * @param {string} opCode - 操作码
 * @param {Object} params - 参数对象
 * @returns {string} - Efficode格式的消息
 */
export async function createEfficodeMessage(opCode, params = {}) {
  let prefix = '';
  let paramStr = '';
  
  // 创建参数的副本，避免修改原始对象
  const paramsCopy = { ...params };
  
  // 确定消息前缀
  if (opCode === 'DID') {
    prefix = '@';
  } else if (['ACK', 'ERROR'].includes(opCode)) {
    prefix = '!';
  } else {
    prefix = '#';
  }
  
  // 如果是DATA类型且内容较大，尝试压缩
  if (opCode === 'DATA' && paramsCopy.content && 
      typeof paramsCopy.content === 'string' && 
      paramsCopy.content.length > COMPRESSION_THRESHOLD) {
    // 执行压缩
    paramsCopy.content = await compressContent(paramsCopy.content);
    paramsCopy.compressed = 'true';
  }
  
  // 根据消息类型，格式化参数字符串
  if (['DID', 'ACK', 'ERROR'].includes(opCode)) {
    paramStr = ':' + JSON.stringify(paramsCopy);
  } else {
    const parts = [];
    for (const [key, value] of Object.entries(paramsCopy)) {
      if (value !== undefined && value !== null) {
        parts.push(`${key}=${encodeURIComponent(String(value))}`);
      }
    }
    if (parts.length > 0) {
      paramStr = '?' + parts.join('&');
    }
  }
  
  return prefix + opCode + paramStr;
}

/**
 * 创建语法指南
 * @returns {string} Efficode语法说明
 */
export function createSyntaxGuide() {
  return `
# Efficode协议语法指南

Efficode是一种专为AI智能体间通信设计的高效压缩协议。

## 基本格式
- 消息前缀:
  * @ - 身份相关
  * # - 数据/请求
  * ! - 确认/错误

## 操作码:
  * DID: 身份验证，格式: @DID:{...}
  * REQ: 请求，格式: #REQ?param1=value1&param2=value2
  * DATA: 数据传输，格式: #DATA?content=xxx&type=text
  * ACK: 确认，格式: !ACK:{...}
  * ERROR: 错误，格式: !ERROR:{...}

## 压缩数据格式
当消息大小超过${COMPRESSION_THRESHOLD}字节时，将被自动压缩，格式为:
EFFICODE:<base64编码的压缩数据>
`;
}

/**
 * 创建自解压数据包
 * @param {string} content 需要打包的内容
 * @returns {string} HTML格式的自解压数据包
 */
export async function createSelfExtractingPacket(content) {
  // 压缩内容
  const compressedContent = await compressContent(content);
  
  // 创建语法指南
  const syntaxGuide = createSyntaxGuide();
  
  // 创建HTML自解压包
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Efficode自解压数据包</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .header { text-align: center; margin-bottom: 20px; }
    pre { background: #f5f5f5; padding: 15px; border-radius: 4px; overflow: auto; }
    button { padding: 10px 15px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
    button:hover { background: #45a049; }
    .result { margin-top: 20px; display: none; }
    .explanation { margin: 20px 0; line-height: 1.6; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Efficode自解压数据包</h1>
    </div>
    
    <div class="explanation">
      <p>这是一个Efficode自解压数据包，包含压缩的Efficode消息数据。点击下方按钮解压查看内容。</p>
    </div>
    
    <button id="extract">解压查看内容</button>
    
    <div id="result" class="result">
      <h3>解压后内容:</h3>
      <pre id="content"></pre>
    </div>
    
    <div class="explanation">
      <h3>Efficode协议说明</h3>
      <pre>${syntaxGuide}</pre>
    </div>
  </div>
  
  <script>
    // 存储压缩数据
    const compressedData = '${compressedContent}';
    
    // 解压函数
    function decompressContent(compressed) {
      if (compressed.startsWith('EFFICODE:')) {
        const base64Data = compressed.substring(9);
        return decodeURIComponent(atob(base64Data));
      }
      return compressed;
    }
    
    // 添加解压按钮事件
    document.getElementById('extract').addEventListener('click', function() {
      const resultElement = document.getElementById('result');
      const contentElement = document.getElementById('content');
      
      resultElement.style.display = 'block';
      contentElement.textContent = decompressContent(compressedData);
    });
  </script>
</body>
</html>
`;
}

export default {
  compressContent,
  decompressContent,
  parseEfficodeMessage,
  createEfficodeMessage,
  createSyntaxGuide,
  createSelfExtractingPacket
}; 