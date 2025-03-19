package handlers

import (
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"nftagent/api"
	"nftagent/database"
	"nftagent/models"
	"nftagent/protocol"
	"nftagent/websocket"
)

var wsManager *websocket.Manager
var sfClient *api.SiliconFlowClient

// 初始化
func Init() {
	wsManager = websocket.NewManager()
	go wsManager.Run()
	sfClient = api.NewSiliconFlowClient()
}

// CreateAgent 创建智能体
func CreateAgent(c *gin.Context) {
	var input struct {
		Name        string `json:"name" binding:"required"`
		Role        string `json:"role" binding:"required"`
		Description string `json:"description"`
		Avatar      string `json:"avatar"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误: " + err.Error()})
		return
	}

	// 生成DID
	// 使用多种方法确保DID不为空
	var did string

	// 方法1: 使用UUID
	uniqueID := uuid.New().String()

	// 方法2: 如果UUID为空，使用时间戳和随机数
	if uniqueID == "" || len(uniqueID) < 5 {
		uniqueID = time.Now().Format("20060102150405") + "-" + strconv.FormatInt(time.Now().UnixNano(), 10)
	}

	// 构建DID
	did = "did:efficode:" + uniqueID

	// 最终安全检查，确保DID不为空
	if did == "" || did == "did:efficode:" {
		// 最后的保障方案
		timestamp := time.Now().Unix()
		random := strconv.FormatInt(int64(time.Now().Nanosecond()), 10)
		did = "did:efficode:backup-" + strconv.FormatInt(timestamp, 10) + "-" + random
	}

	log.Printf("创建智能体，名称=%s, DID=%s", input.Name, did)

	// 创建role JSON
	roleJSON := `{"description":"` + input.Description + `"}`

	agent := &models.Agent{
		Name:      input.Name,
		DID:       did, // 确保DID字段有值
		Role:      roleJSON,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// 打印创建前的agent信息进行检查
	log.Printf("即将创建智能体: %+v", agent)

	// 安全检查：最后一次确认DID不为空
	if agent.DID == "" {
		agent.DID = "did:efficode:emergency-" + strconv.FormatInt(time.Now().UnixNano(), 10)
		log.Printf("警告：DID为空，已使用紧急备用DID: %s", agent.DID)
	}

	if err := database.CreateAgent(agent); err != nil {
		log.Printf("创建智能体失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建失败: " + err.Error()})
		return
	}

	log.Printf("创建智能体成功: ID=%d, 名称=%s, DID=%s", agent.ID, agent.Name, agent.DID)
	c.JSON(http.StatusOK, agent)
}

// GetAgents 获取所有智能体
func GetAgents(c *gin.Context) {
	agents, err := database.GetAllAgents()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取失败: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, agents)
}

// GetAgentByID 根据ID获取智能体
func GetAgentByID(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的智能体ID"})
		return
	}

	agent, err := database.GetAgentByID(id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "智能体不存在"})
		return
	}

	c.JSON(http.StatusOK, agent)
}

// CreateConversation 创建对话
func CreateConversation(c *gin.Context) {
	var input struct {
		Title     string `json:"title" binding:"required"`
		Mode      string `json:"mode" binding:"required"`
		AgentID   int64  `json:"agent_id" binding:"required"`
		PartnerID int64  `json:"partner_id"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误: " + err.Error()})
		return
	}

	conv := &models.Conversation{
		Title:     input.Title,
		Mode:      input.Mode,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := database.CreateConversation(conv); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建失败: " + err.Error()})
		return
	}

	// 添加参与者
	if err := database.AddParticipantToConversation(conv.ID, input.AgentID, "participant"); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "添加参与者失败: " + err.Error()})
		return
	}

	// 如果提供了伙伴ID，添加伙伴
	if input.PartnerID > 0 {
		if err := database.AddParticipantToConversation(conv.ID, input.PartnerID, "participant"); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "添加参与者失败: " + err.Error()})
			return
		}
	}
	// 不再添加用户(ID为0)作为参与者，而是在前端处理

	c.JSON(http.StatusOK, gin.H{
		"conversation_id": conv.ID,
		"success":         true,
		"message":         "对话创建成功",
	})
}

// SendMessage 发送消息
func SendMessage(c *gin.Context) {
	var input struct {
		ConversationID int64  `json:"conversation_id" binding:"required"`
		Sender         string `json:"sender" binding:"required"`
		Receiver       string `json:"receiver" binding:"required"`
		Content        string `json:"content" binding:"required"`
		ContentType    string `json:"content_type"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "参数错误: " + err.Error()})
		return
	}

	if input.ContentType == "" {
		input.ContentType = "text"
	}

	// 保存消息
	msg := &models.Message{
		ConversationID: input.ConversationID,
		Sender:         input.Sender,
		Receiver:       input.Receiver,
		Content:        input.Content,
		ContentType:    input.ContentType,
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
	}

	if err := database.SaveMessage(msg); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "保存失败: " + err.Error()})
		return
	}

	// 创建Efficode消息
	params := map[string]interface{}{
		"content": input.Content,
		"type":    input.ContentType,
	}
	packet := protocol.NewEfficodePacket("DATA", params)
	processed, err := protocol.ProcessMessage(packet)
	if err != nil {
		log.Printf("消息处理失败: %v", err)
	}

	// 通过WebSocket发送
	wsManager.SendToAgent(input.Receiver, []byte(processed.ToString()))

	// 如果接收者是智能体（非用户），使用API生成响应
	if input.Receiver != "0" && input.Receiver != "user" {
		go func() {
			// 使用API调用生成回复
			response, err := sfClient.GenerateResponse(input.Content)
			if err != nil {
				log.Printf("API请求失败: %v", err)
				return
			}

			// 保存AI回复
			replyMsg := &models.Message{
				ConversationID: input.ConversationID,
				Sender:         input.Receiver,
				Receiver:       input.Sender,
				Content:        response,
				ContentType:    "text",
				CreatedAt:      time.Now(),
				UpdatedAt:      time.Now(),
			}

			if err := database.SaveMessage(replyMsg); err != nil {
				log.Printf("保存回复失败: %v", err)
				return
			}

			// 创建Efficode回复消息
			replyParams := map[string]interface{}{
				"content": response,
				"type":    "text",
			}
			replyPacket := protocol.NewEfficodePacket("DATA", replyParams)
			processed, _ := protocol.ProcessMessage(replyPacket)

			wsManager.SendToAgent(input.Sender, []byte(processed.ToString()))
		}()
	}

	c.JSON(http.StatusOK, gin.H{
		"message_id": msg.ID,
		"success":    true,
	})
}

// GetMessages 获取对话消息
func GetMessages(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的对话ID"})
		return
	}

	messages, err := database.GetMessagesByConversationID(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取失败: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, messages)
}

// HandleWebSocket 处理WebSocket连接
func HandleWebSocket(c *gin.Context) {
	wsManager.HandleConnection(c.Writer, c.Request)
}
