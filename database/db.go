package database

import (
	"fmt"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"nftagent/models"
)

// DB 全局数据库连接
var DB *gorm.DB

// InitDB 初始化数据库连接
func InitDB() (*gorm.DB, error) {
	host := os.Getenv("DB_HOST")
	if host == "" {
		host = "localhost"
	}

	port := os.Getenv("DB_PORT")
	if port == "" {
		port = "5432"
	}

	user := os.Getenv("DB_USER")
	if user == "" {
		user = "postgres"
	}

	password := os.Getenv("DB_PASSWORD")
	if password == "" {
		password = "112358"
	}

	dbname := os.Getenv("DB_NAME")
	if dbname == "" {
		dbname = "postgres"
	}

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
		host, user, password, dbname, port)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, fmt.Errorf("数据库连接失败: %v", err)
	}

	// 自动迁移数据库表结构将在调用方完成

	DB = db
	return db, nil
}

// GetDB 获取数据库连接
func GetDB() *gorm.DB {
	return DB
}

// 以下是针对Agent的CRUD操作

// CreateAgent 创建新智能体
func CreateAgent(agent *models.Agent) error {
	return DB.Create(agent).Error
}

// GetAgentByID 根据ID获取智能体
func GetAgentByID(id int64) (*models.Agent, error) {
	var agent models.Agent
	if err := DB.First(&agent, id).Error; err != nil {
		return nil, err
	}
	return &agent, nil
}

// GetAllAgents 获取所有智能体
func GetAllAgents() ([]models.Agent, error) {
	var agents []models.Agent
	if err := DB.Find(&agents).Error; err != nil {
		return nil, err
	}
	return agents, nil
}

// UpdateAgent 更新智能体信息
func UpdateAgent(agent *models.Agent) error {
	return DB.Save(agent).Error
}

// DeleteAgent 删除智能体
func DeleteAgent(id int64) error {
	return DB.Delete(&models.Agent{}, id).Error
}

// 以下是针对对话的CRUD操作

// CreateConversation 创建新对话
func CreateConversation(conversation *models.Conversation) error {
	return DB.Create(conversation).Error
}

// GetConversationByID 根据ID获取对话
func GetConversationByID(id int64) (*models.Conversation, error) {
	var conversation models.Conversation
	if err := DB.First(&conversation, id).Error; err != nil {
		return nil, err
	}
	return &conversation, nil
}

// AddParticipantToConversation 添加参与者到对话
func AddParticipantToConversation(conversationID, agentID int64, role string) error {
	participant := &models.Participant{
		ConversationID: conversationID,
		AgentID:        agentID,
		Role:           role,
	}
	return DB.Create(participant).Error
}

// GetConversationParticipants 获取对话参与者
func GetConversationParticipants(conversationID int64) ([]models.Participant, error) {
	var participants []models.Participant
	if err := DB.Where("conversation_id = ?", conversationID).Find(&participants).Error; err != nil {
		return nil, err
	}
	return participants, nil
}

// 以下是针对消息的CRUD操作

// SaveMessage 保存消息
func SaveMessage(message *models.Message) error {
	return DB.Create(message).Error
}

// GetMessagesByConversationID 获取对话的所有消息
func GetMessagesByConversationID(conversationID int64) ([]models.Message, error) {
	var messages []models.Message
	if err := DB.Where("conversation_id = ?", conversationID).Order("created_at").Find(&messages).Error; err != nil {
		return nil, err
	}
	return messages, nil
}
