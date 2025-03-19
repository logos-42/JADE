package protocol

import (
	"bytes"
	"compress/gzip"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"strings"
)

// EfficodePacket 表示一个Efficode协议包
type EfficodePacket struct {
	OpCode string                 `json:"op_code"`
	Params map[string]interface{} `json:"params"`
}

// NewEfficodePacket 创建一个新的Efficode协议包
func NewEfficodePacket(opCode string, params map[string]interface{}) *EfficodePacket {
	if params == nil {
		params = make(map[string]interface{})
	}
	return &EfficodePacket{
		OpCode: opCode,
		Params: params,
	}
}

// FromString 从字符串解析Efficode包
func FromString(message string) (*EfficodePacket, error) {
	if len(message) == 0 {
		return nil, fmt.Errorf("空消息")
	}

	prefix := message[0]
	var opCode string
	var params map[string]interface{}

	switch prefix {
	case '@':
		// DID消息
		parts := strings.SplitN(message[1:], ":", 2)
		opCode = parts[0]
		params = make(map[string]interface{})
		
		if len(parts) > 1 {
			if err := json.Unmarshal([]byte(parts[1]), &params); err != nil {
				// 如果不是有效JSON，则作为单个值处理
				params["value"] = parts[1]
			}
		}
	case '#':
		// REQ或DATA消息
		parts := strings.SplitN(message[1:], "?", 2)
		opCode = parts[0]
		params = make(map[string]interface{})
		
		if len(parts) > 1 {
			queryParams := strings.Split(parts[1], "&")
			for _, param := range queryParams {
				keyVal := strings.SplitN(param, "=", 2)
				if len(keyVal) == 2 {
					params[keyVal[0]] = keyVal[1]
				}
			}
		}
	case '!':
		// ACK或ERROR消息
		parts := strings.SplitN(message[1:], ":", 2)
		opCode = parts[0]
		params = make(map[string]interface{})
		
		if len(parts) > 1 {
			if err := json.Unmarshal([]byte(parts[1]), &params); err != nil {
				// 如果不是有效JSON，则作为消息处理
				params["message"] = parts[1]
			}
		}
	default:
		return nil, fmt.Errorf("无效的消息前缀: %c", prefix)
	}

	return &EfficodePacket{
		OpCode: opCode,
		Params: params,
	}, nil
}

// ToString 将Efficode包转换为字符串
func (p *EfficodePacket) ToString() string {
	var prefix string
	switch p.OpCode {
	case "DID":
		prefix = "@"
	case "ACK", "ERROR":
		prefix = "!"
	default:
		prefix = "#"
	}

	var paramStr string
	if len(p.Params) > 0 {
		if p.OpCode == "DID" || p.OpCode == "ACK" || p.OpCode == "ERROR" {
			jsonBytes, _ := json.Marshal(p.Params)
			paramStr = ":" + string(jsonBytes)
		} else {
			var parts []string
			for k, v := range p.Params {
				parts = append(parts, fmt.Sprintf("%s=%v", k, v))
			}
			paramStr = "?" + strings.Join(parts, "&")
		}
	}

	return prefix + p.OpCode + paramStr
}

// CompressContent 压缩内容
func CompressContent(content string) (string, error) {
	var buf bytes.Buffer
	gz := gzip.NewWriter(&buf)
	if _, err := gz.Write([]byte(content)); err != nil {
		return "", err
	}
	if err := gz.Close(); err != nil {
		return "", err
	}
	return base64.StdEncoding.EncodeToString(buf.Bytes()), nil
}

// DecompressContent 解压缩内容
func DecompressContent(compressed string) (string, error) {
	data, err := base64.StdEncoding.DecodeString(compressed)
	if err != nil {
		return "", err
	}
	reader, err := gzip.NewReader(bytes.NewReader(data))
	if err != nil {
		return "", err
	}
	defer reader.Close()
	result, err := io.ReadAll(reader)
	if err != nil {
		return "", err
	}
	return string(result), nil
}

// NeedCompression 判断内容是否需要压缩
func NeedCompression(content string) bool {
	return len(content) > 500 // 超过500字节的内容需要压缩
}

// ProcessMessage 处理消息，根据需要自动压缩/解压缩
func ProcessMessage(packet *EfficodePacket) (*EfficodePacket, error) {
	// 如果是DATA消息，检查是否需要压缩
	if packet.OpCode == "DATA" {
		content, ok := packet.Params["content"].(string)
		if ok && NeedCompression(content) {
			compressed, err := CompressContent(content)
			if err != nil {
				return nil, err
			}
			packet.Params["content"] = compressed
			packet.Params["compressed"] = "true"
		}
	}
	return packet, nil
}

// ProcessReceivedMessage 处理接收到的消息，根据需要自动解压缩
func ProcessReceivedMessage(packet *EfficodePacket) (*EfficodePacket, error) {
	// 如果是DATA消息，检查是否需要解压缩
	if packet.OpCode == "DATA" {
		compressed, ok := packet.Params["compressed"].(string)
		if ok && compressed == "true" {
			content, ok := packet.Params["content"].(string)
			if ok {
				decompressed, err := DecompressContent(content)
				if err != nil {
					return nil, err
				}
				packet.Params["content"] = decompressed
				delete(packet.Params, "compressed")
			}
		}
	}
	return packet, nil
}