package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

// SiliconFlowClient 是SiliconFlow API客户端
type SiliconFlowClient struct {
	APIKey     string
	BaseURL    string
	HTTPClient *http.Client
}

// Message 表示聊天消息
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ChatRequest 表示聊天请求
type ChatRequest struct {
	Messages []Message `json:"messages"`
	Model    string    `json:"model"`
}

// ChatResponse 表示聊天响应
type ChatResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
}

// NewSiliconFlowClient 创建新的SiliconFlow客户端
func NewSiliconFlowClient() *SiliconFlowClient {
	apiKey := os.Getenv("SILICONFLOW_API_KEY")
	if apiKey == "" {
		apiKey = "默认API密钥" // 实际使用时应该从配置中获取
	}

	baseURL := os.Getenv("SILICONFLOW_API_URL")
	if baseURL == "" {
		baseURL = "https://api.siliconflow.com/v1"
	}

	return &SiliconFlowClient{
		APIKey:  apiKey,
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// SendChatRequest 发送聊天请求
func (c *SiliconFlowClient) SendChatRequest(messages []Message) (string, error) {
	model := os.Getenv("SILICONFLOW_MODEL")
	if model == "" {
		model = "gpt-3.5-turbo" // 默认模型
	}

	reqBody := ChatRequest{
		Messages: messages,
		Model:    model,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("请求序列化失败: %v", err)
	}

	req, err := http.NewRequest("POST", c.BaseURL+"/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("发送请求失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API请求失败: HTTP状态码 %d", resp.StatusCode)
	}

	var result ChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("解析响应失败: %v", err)
	}

	if len(result.Choices) == 0 {
		return "", fmt.Errorf("API响应为空")
	}

	return result.Choices[0].Message.Content, nil
}

// GenerateResponse 生成智能体响应
func (c *SiliconFlowClient) GenerateResponse(prompt string) (string, error) {
	messages := []Message{
		{
			Role:    "user",
			Content: prompt,
		},
	}
	return c.SendChatRequest(messages)
}

// GenerateDialogue 生成对话响应
func (c *SiliconFlowClient) GenerateDialogue(history []Message, newMessage string) (string, error) {
	messages := make([]Message, len(history)+1)
	copy(messages, history)
	messages[len(history)] = Message{
		Role:    "user",
		Content: newMessage,
	}
	return c.SendChatRequest(messages)
}