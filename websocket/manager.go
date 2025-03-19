package websocket

import (
	"log"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

// Client 表示一个WebSocket客户端
type Client struct {
	ID     string
	Agent  string
	Conn   *websocket.Conn
	Send   chan []byte
	Manager *Manager
}

// Manager WebSocket连接管理器
type Manager struct {
	clients    map[string]*Client
	broadcast  chan []byte
	register   chan *Client
	unregister chan *Client
	mutex      sync.Mutex
}

// 定义WebSocket升级器
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // 允许所有来源
	},
}

// NewManager 创建一个新的WebSocket管理器
func NewManager() *Manager {
	return &Manager{
		clients:    make(map[string]*Client),
		broadcast:  make(chan []byte),
		register:   make(chan *Client),
		unregister: make(chan *Client),
	}
}

// Run 启动WebSocket管理器
func (m *Manager) Run() {
	for {
		select {
		case client := <-m.register:
			m.mutex.Lock()
			m.clients[client.ID] = client
			m.mutex.Unlock()
			log.Printf("客户端 %s 已连接", client.ID)

		case client := <-m.unregister:
			if _, ok := m.clients[client.ID]; ok {
				m.mutex.Lock()
				delete(m.clients, client.ID)
				m.mutex.Unlock()
				close(client.Send)
				log.Printf("客户端 %s 已断开", client.ID)
			}

		case message := <-m.broadcast:
			m.mutex.Lock()
			for _, client := range m.clients {
				select {
				case client.Send <- message:
				default:
					close(client.Send)
					delete(m.clients, client.ID)
				}
			}
			m.mutex.Unlock()
		}
	}
}

// HandleConnection 处理新的WebSocket连接
func (m *Manager) HandleConnection(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket升级失败: %v", err)
		return
	}

	agentID := r.URL.Query().Get("agent_id")
	if agentID == "" {
		log.Printf("缺少agent_id参数")
		conn.Close()
		return
	}

	client := &Client{
		ID:     agentID,
		Agent:  agentID,
		Conn:   conn,
		Send:   make(chan []byte, 256),
		Manager: m,
	}

	m.register <- client

	// 启动读写协程
	go client.readPump()
	go client.writePump()
}

// 读取客户端消息
func (c *Client) readPump() {
	defer func() {
		c.Manager.unregister <- c
		c.Conn.Close()
	}()

	for {
		_, message, err := c.Conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("读取消息错误: %v", err)
			}
			break
		}
		log.Printf("收到消息: %s", message)
		// 处理接收到的消息，可以在这里添加自定义处理逻辑
	}
}

// 发送消息到客户端
func (c *Client) writePump() {
	defer func() {
		c.Conn.Close()
	}()

	for {
		message, ok := <-c.Send
		if !ok {
			// 通道已关闭
			c.Conn.WriteMessage(websocket.CloseMessage, []byte{})
			return
		}

		err := c.Conn.WriteMessage(websocket.TextMessage, message)
		if err != nil {
			log.Printf("发送消息错误: %v", err)
			return
		}
	}
}

// SendToAgent 发送消息给指定智能体
func (m *Manager) SendToAgent(agentID string, message []byte) {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	client, ok := m.clients[agentID]
	if ok {
		select {
		case client.Send <- message:
			log.Printf("消息已发送给智能体 %s", agentID)
		default:
			log.Printf("发送失败，智能体 %s 缓冲区已满", agentID)
			close(client.Send)
			delete(m.clients, agentID)
		}
	} else {
		log.Printf("智能体 %s 未连接", agentID)
	}
}

// BroadcastMessage 广播消息给所有客户端
func (m *Manager) BroadcastMessage(message []byte) {
	m.broadcast <- message
}