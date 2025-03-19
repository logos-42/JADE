package routes

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"nftagent/handlers"
)

// RegisterRoutes 注册API路由
func RegisterRoutes(r *gin.Engine, db *gorm.DB) {
	// 初始化处理器
	handlers.Init()

	// API路由组
	api := r.Group("/api")
	{
		// 智能体相关
		api.POST("/agents", handlers.CreateAgent)
		api.GET("/agents", handlers.GetAgents)
		api.GET("/agents/:id", handlers.GetAgentByID)
		
		// 对话相关
		api.POST("/conversations", handlers.CreateConversation)
		api.GET("/conversations/:id/messages", handlers.GetMessages)
		
		// 消息相关
		api.POST("/messages", handlers.SendMessage)
	}
	
	// 静态文件服务
	r.Static("/static", "./public")
	r.StaticFile("/", "./public/index.html")
	
	// WebSocket
	r.GET("/ws", handlers.HandleWebSocket)
}