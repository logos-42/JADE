package models

import (
	"time"
)

// Agent 表示一个智能体
type Agent struct {
	ID        int64     `json:"id" gorm:"primaryKey"`
	Name      string    `json:"name"`
	DID       string    `json:"did" gorm:"column:d_id"`
	Role      string    `json:"role" gorm:"type:jsonb"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Conversation 表示一个对话
type Conversation struct {
	ID        int64     `json:"id" gorm:"primaryKey"`
	Title     string    `json:"title"`
	Mode      string    `json:"mode"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Message 表示一条消息
type Message struct {
	ID             int64     `json:"id" gorm:"primaryKey"`
	ConversationID int64     `json:"conversation_id"`
	Sender         string    `json:"sender"`
	Receiver       string    `json:"receiver"`
	Content        string    `json:"content"`
	ContentType    string    `json:"content_type"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
}

// Participant 表示对话参与者
type Participant struct {
	ID             int64     `json:"id" gorm:"primaryKey"`
	ConversationID int64     `json:"conversation_id"`
	AgentID        int64     `json:"agent_id"`
	Role           string    `json:"role"`
	CreatedAt      time.Time `json:"created_at"`
}
