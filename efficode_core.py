"""
Efficode核心模块

这个模块提供了Efficode协议的核心功能，包括数据包的创建、解析和处理。
"""

import json
import time
import logging
import zlib
import base64
import re
import gzip
import io
from typing import Optional, Dict, Any, List, Union, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Efficode_Core')

# 常量定义
COMPRESSION_THRESHOLD = 500  # 大于此字节大小的内容才进行压缩
COMPRESSION_METHODS = ['zlib', 'gzip']  # 支持的压缩方法

class EfficodePacket:
    """Efficode数据包类"""
    
    def __init__(self, op_code: str, params: Dict[str, Any], sender: str):
        """
        初始化Efficode数据包
        
        Args:
            op_code: 操作码
            params: 参数字典
            sender: 发送者
        """
        self.op_code = op_code
        self.params = params
        self.sender = sender
        self.timestamp = time.time()  # 时间戳
    
    def to_string(self) -> str:
        """将数据包转换为字符串格式"""
        # 为不同操作码选择不同的前缀
        prefix = {
            "DID": "@",
            "REQ": "#",
            "DATA": "#",
            "ACK": "!",
            "ERROR": "!"
        }.get(self.op_code, "#")
        
        # 处理参数字符串
        if not self.params:
            return f"{prefix}{self.op_code}"
            
        # 特殊处理JSON格式参数
        params_list = []
        for k, v in self.params.items():
            if isinstance(v, (dict, list)):
                # 将复杂类型转换为JSON字符串
                params_list.append(f"{k}={json.dumps(v, ensure_ascii=False)}")
            else:
                params_list.append(f"{k}={v}")
        
        params_str = "&".join(params_list)
        return f"{prefix}{self.op_code}?{params_str}"
    
    @classmethod
    def from_string(cls, packet_str: str, sender: str) -> 'EfficodePacket':
        """从字符串解析数据包"""
        try:
            if not packet_str:
                logger.error("解析数据包失败: 空字符串")
                return cls("ERROR", {"message": "空数据包"}, sender)
                
            prefix = packet_str[0] if packet_str else '#'
            
            # 基于前缀判断可能的操作码
            possible_ops = {
                '@': ['DID'],
                '#': ['REQ', 'DATA'],
                '!': ['ACK', 'ERROR']
            }.get(prefix, ['DATA'])
            
            # 尝试解压缩数据包
            if 'compressed=' in packet_str:
                logger.info("检测到压缩数据包，尝试解压...")
                packet_str = cls._decompress_packet_string(packet_str)
            
            # 分离操作码和参数
            if '?' in packet_str:
                main_part, params_str = packet_str[1:].split('?', 1)
            else:
                main_part, params_str = packet_str[1:], ""
            
            # 确定操作码
            op_code = None
            for op in possible_ops:
                if main_part.startswith(op):
                    op_code = op
                    break
                    
            if not op_code:
                op_code = "DATA"  # 默认为DATA
            
            # 解析参数
            params = {}
            if params_str:
                param_pairs = params_str.split('&')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        # 尝试解析JSON
                        try:
                            if (value.startswith('{') and value.endswith('}')) or \
                               (value.startswith('[') and value.endswith(']')):
                                params[key] = json.loads(value)
                            else:
                                params[key] = value
                        except json.JSONDecodeError:
                            params[key] = value
            
            # 创建实例
            packet = cls(op_code, params, sender)
            
            # 如果还有压缩内容，尝试解压
            if 'compressed' in packet.params and packet.params['compressed'] != 'false':
                packet = packet.decompress_content()
            
            return packet
            
        except Exception as e:
            logger.error(f"解析数据包时出错: {str(e)}")
            return cls("ERROR", {"message": f"解析错误: {str(e)}"}, sender)
    
    @staticmethod
    def _decompress_packet_string(packet_str: str) -> str:
        """从字符串中解压数据包"""
        try:
            # 提取编码和压缩算法
            pattern = r'content=([^&]+)&compressed=([^&]+)'
            match = re.search(pattern, packet_str)
            if match:
                encoded = match.group(1)
                compression_method = match.group(2)
                
                # 解码Base64
                compressed_data = base64.b64decode(encoded)
                
                # 根据压缩方法解压
                if compression_method == 'zlib':
                    content = zlib.decompress(compressed_data).decode('utf-8')
                elif compression_method == 'gzip':
                    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                        content = f.read().decode('utf-8')
                else:
                    # 默认尝试zlib解压
                    content = zlib.decompress(compressed_data).decode('utf-8')
                
                # 替换回原始内容
                packet_str = re.sub(r'content=[^&]+&compressed=[^&]+', f'content={content}', packet_str)
            
            return packet_str
        except Exception as e:
            logger.error(f"从字符串解压数据包失败: {str(e)}")
            return packet_str
    
    def compress_content(self) -> 'EfficodePacket':
        """智能压缩数据包中的content参数，返回压缩后的数据包"""
        if 'content' in self.params and isinstance(self.params['content'], str):
            content = self.params['content']
            
            # 小于阈值的内容不压缩
            if len(content) < COMPRESSION_THRESHOLD:
                logger.info(f"内容大小 ({len(content)} 字节) 小于阈值 ({COMPRESSION_THRESHOLD} 字节)，跳过压缩")
                return self
            
            # 尝试多种压缩方法，选择最佳效果
            best_result = self._find_best_compression(content)
            
            if best_result:
                method, encoded = best_result
                # 保存原始内容类型和压缩方法信息
                self.params['content'] = encoded
                self.params['compressed'] = method
                self.params['original_type'] = self.params.get('type', 'text')
                logger.info(f"内容已使用 {method} 压缩，原始大小: {len(content)} 字节，压缩后: {len(encoded)} 字节，压缩率: {len(encoded)/len(content):.2f}")
            else:
                logger.info(f"所有压缩方法都无效，保持原始大小: {len(content)} 字节")
        
        return self
    
    def _find_best_compression(self, content: str) -> Optional[Tuple[str, str]]:
        """尝试多种压缩方法，返回最佳结果(方法, 编码后内容)"""
        content_bytes = content.encode('utf-8')
        results = []
        
        # zlib压缩 (最高压缩级别)
        try:
            zlib_compressed = zlib.compress(content_bytes, level=9)
            zlib_encoded = base64.b64encode(zlib_compressed).decode('utf-8')
            results.append(('zlib', zlib_encoded, len(zlib_encoded)))
        except Exception as e:
            logger.warning(f"zlib压缩失败: {str(e)}")
        
        # gzip压缩
        try:
            gzip_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=gzip_buffer, mode='wb', compresslevel=9) as f:
                f.write(content_bytes)
            gzip_compressed = gzip_buffer.getvalue()
            gzip_encoded = base64.b64encode(gzip_compressed).decode('utf-8')
            results.append(('gzip', gzip_encoded, len(gzip_encoded)))
        except Exception as e:
            logger.warning(f"gzip压缩失败: {str(e)}")
        
        # 尝试导入zstandard (如果已安装)
        try:
            import zstandard as zstd
            compressor = zstd.ZstdCompressor(level=22)  # 最高压缩率
            zstd_compressed = compressor.compress(content_bytes)
            zstd_encoded = base64.b64encode(zstd_compressed).decode('utf-8')
            results.append(('zstd', zstd_encoded, len(zstd_encoded)))
        except ImportError:
            logger.debug("zstandard库未安装，跳过zstd压缩")
        except Exception as e:
            logger.warning(f"zstd压缩失败: {str(e)}")
        
        # 尝试导入brotli (如果已安装)
        try:
            import brotli # type: ignore
            brotli_compressed = brotli.compress(content_bytes, quality=11)
            brotli_encoded = base64.b64encode(brotli_compressed).decode('utf-8')
            results.append(('brotli', brotli_encoded, len(brotli_encoded)))
        except ImportError:
            logger.debug("brotli库未安装，跳过brotli压缩")
        except Exception as e:
            logger.warning(f"brotli压缩失败: {str(e)}")
            
        # 选择最佳压缩结果 (压缩率最高的)
        if results:
            results.sort(key=lambda x: x[2])  # 按压缩后大小排序
            best_method, best_encoded, best_size = results[0]
            
            # 只有当压缩确实减小了大小时才返回结果
            if best_size < len(content):
                return best_method, best_encoded
        
        return None
    
    def decompress_content(self) -> 'EfficodePacket':
        """解压数据包中的content参数，返回解压后的数据包"""
        if 'compressed' in self.params and self.params['compressed'] != 'false':
            try:
                encoded = self.params['content']
                compression_method = self.params['compressed']
                compressed_data = base64.b64decode(encoded)
                
                # 根据不同的压缩方法解压
                if compression_method == 'zlib':
                    content = zlib.decompress(compressed_data).decode('utf-8')
                elif compression_method == 'gzip':
                    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                        content = f.read().decode('utf-8')
                elif compression_method == 'zstd':
                    try:
                        import zstandard as zstd
                        decompressor = zstd.ZstdDecompressor()
                        content = decompressor.decompress(compressed_data).decode('utf-8')
                    except ImportError:
                        raise Exception("zstandard库未安装，无法解压zstd压缩的内容")
                elif compression_method == 'brotli':
                    try:
                        import brotli # type: ignore
                        content = brotli.decompress(compressed_data).decode('utf-8')
                    except ImportError:
                        raise Exception("brotli库未安装，无法解压brotli压缩的内容")
                else:
                    # 尝试zlib解压（默认）
                    content = zlib.decompress(compressed_data).decode('utf-8')
                
                # 恢复内容
                self.params['content'] = content
                # 恢复类型
                if 'original_type' in self.params:
                    self.params['type'] = self.params.pop('original_type')
                # 移除压缩标记
                self.params.pop('compressed', None)
                logger.info(f"内容已解压，解压后大小: {len(content)} 字节")
            except Exception as e:
                logger.error(f"解压内容失败: {str(e)}")
                logger.exception("详细错误信息")
        return self

    def get_content(self) -> str:
        """获取数据包的内容部分（如果有）"""
        # 如果是压缩的，先解压
        if 'compressed' in self.params and self.params['compressed'] != 'false':
            packet = self.decompress_content()
            return packet.get_content()
        
        if self.op_code in ["REQ", "DATA"] and "content" in self.params:
            content = self.params["content"]
            if isinstance(content, str):
                return content
            elif isinstance(content, (dict, list)):
                return json.dumps(content, ensure_ascii=False)
        return ""
        
    def is_error(self) -> bool:
        """检查是否为错误数据包"""
        return self.op_code == "ERROR"
        
    def is_ack(self) -> bool:
        """检查是否为确认数据包"""
        return self.op_code == "ACK"

    def add_metadata(self) -> 'EfficodePacket':
        """添加元数据到数据包"""
        if self.op_code in ["REQ", "DATA"]:
            self.params["metadata"] = {
                "timestamp": self.timestamp,
                "sender": self.sender,
                "id": f"{int(self.timestamp)}_{self.sender}"
            }
        return self
    
    def optimize(self) -> 'EfficodePacket':
        """优化数据包，压缩内容并添加元数据"""
        return self.add_metadata().compress_content()
    
    def create_self_extracting_packet(self) -> Dict[str, Any]:
        """创建自解压数据包，可直接在浏览器或其他环境中解压"""
        if self.op_code not in ["REQ", "DATA"] or "content" not in self.params:
            return {"error": "只有REQ和DATA类型的数据包支持自解压"}
            
        content = self.params["content"]
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
            
        # 压缩内容 (使用zlib，兼容性最好)
        compressed = zlib.compress(content.encode('utf-8'), level=9)
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        # 创建简化版解压器 (JavaScript)
        decompressor_js = """
        function efficodeDecompress(base64Data) {
            // 1. 将Base64转为字节数组
            const binaryString = atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            // 2. 使用pako.js解压 (需要引入pako库)
            // <script src="https://cdn.jsdelivr.net/npm/pako@2.0.4/dist/pako.min.js"></script>
            const decompressed = pako.inflate(bytes, { to: 'string' });
            return decompressed;
        }
        
        // 使用方法: efficodeDecompress('${encodedData}');
        """
        
        # Efficode语法结构说明
        syntax_guide = """
        Efficode协议格式说明：
        1. 基本格式: <前缀><操作码>[?<参数>]
           - 前缀: @ (身份验证), # (请求/数据), ! (确认/错误)
           - 操作码: DID (身份), REQ (请求), DATA (数据), ACK (确认), ERROR (错误)
           - 参数: 以key=value形式提供，多个参数用&连接
        
        2. 压缩数据: 当content参数长度超过500字节时，将自动压缩
           - 压缩格式: content=<BASE64编码的压缩数据>&compressed=<压缩方法>
           - 支持的压缩方法: zlib, gzip, zstd, brotli (自动选择最优)
        
        3. 示例:
           - 请求: #REQ?content=请求内容&type=question
           - 数据: #DATA?content=数据内容&type=answer
           - 压缩: #DATA?content=<压缩数据>&compressed=zlib&type=answer
        """
        
        # 创建自解压包
        self_extracting_packet = {
            "op_code": self.op_code,
            "params": {
                "compressed_data": encoded,
                "type": self.params.get("type", "text"),
                "decompressor": decompressor_js.replace('${encodedData}', encoded),
                "syntax_guide": syntax_guide,
                "original_size": len(content),
                "compressed_size": len(encoded),
                "compression_ratio": len(encoded) / len(content) if len(content) > 0 else 0
            },
            "sender": self.sender,
            "timestamp": self.timestamp,
            "self_extracting": True
        }
        
        return self_extracting_packet

def create_request_packet(content: str, req_type: str, sender: str) -> EfficodePacket:
    """
    创建请求数据包
    
    Args:
        content: 请求内容
        req_type: 请求类型
        sender: 发送者
        
    Returns:
        EfficodePacket对象
    """
    packet = EfficodePacket(
        op_code="REQ",
        params={
            "content": content,
            "type": req_type
        },
        sender=sender
    )
    # 智能压缩内容
    return packet.compress_content()

def create_data_packet(content: str, data_type: str, sender: str) -> EfficodePacket:
    """
    创建数据数据包
    
    Args:
        content: 数据内容
        data_type: 数据类型
        sender: 发送者
        
    Returns:
        EfficodePacket对象
    """
    packet = EfficodePacket(
        op_code="DATA",
        params={
            "content": content,
            "type": data_type
        },
        sender=sender
    )
    # 智能压缩内容
    return packet.compress_content()

def create_error_packet(error_message: str, sender: str) -> EfficodePacket:
    """
    创建错误数据包
    
    Args:
        error_message: 错误信息
        sender: 发送者
        
    Returns:
        EfficodePacket对象
    """
    packet = EfficodePacket(
        op_code="ERROR",
        params={
            "message": error_message
        },
        sender=sender
    )
    # 错误消息也进行压缩（但只在消息较长时）
    if len(error_message) > COMPRESSION_THRESHOLD:
        return packet.compress_content()
    return packet

def create_ack_packet(status: str, message: str, sender: str) -> EfficodePacket:
    """
    创建确认数据包
    
    Args:
        status: 状态
        message: 消息
        sender: 发送者
        
    Returns:
        EfficodePacket对象
    """
    packet = EfficodePacket(
        op_code="ACK",
        params={
            "status": status,
            "message": message
        },
        sender=sender
    )
    # 确认消息通常较短，只在消息较长时压缩
    if len(message) > COMPRESSION_THRESHOLD:
        return packet.compress_content()
    return packet

def create_self_extracting_packet(content: str, data_type: str, sender: str) -> Dict[str, Any]:
    """
    创建自解压数据包
    
    Args:
        content: 内容
        data_type: 数据类型
        sender: 发送者
        
    Returns:
        自解压数据包字典
    """
    packet = EfficodePacket(
        op_code="DATA",
        params={
            "content": content,
            "type": data_type
        },
        sender=sender
    )
    return packet.create_self_extracting_packet() 