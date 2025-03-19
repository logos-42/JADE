# 分布式智能体协作网络
# 分布式智能体协作网络
# AI智能体对话系统

这是一个基于Vue.js的前端应用程序，结合Node.js的Mock服务器，用于演示AI智能体之间的对话功能。

## 项目结构

```
项目根目录/
│
├── src/                  # 前端源代码
│   ├── components/       # Vue组件
│   ├── services/         # API服务和工具
│   ├── store/            # Pinia状态管理
│   ├── views/            # 页面视图
│   ├── App.vue           # 主应用组件
│   └── main.js           # 入口文件
│
├── mock-server/          # Mock后端服务器
│   ├── server.js         # 服务器代码
│   └── package.json      # 依赖配置
│
├── package.json          # 前端项目依赖
└── README.md             # 本文档
```

## 功能特性

- 智能体管理：创建、查看和更新AI智能体
- 对话系统：与智能体进行实时对话
- 消息压缩：自动压缩和解压大型消息
- WebSocket通信：实时接收智能体响应

## 开始使用

### 前提条件

- Node.js (v14+)
- npm 或 yarn

### 启动Mock服务器

1. 进入mock-server目录：
```bash
cd mock-server
```

2. 安装依赖：
```bash
npm install
```

3. 启动服务器：
```bash
npm start
```

服务器将在 http://localhost:8080 上运行，提供API和WebSocket服务。

### 启动前端应用

1. 在项目根目录安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

应用将在 http://localhost:5173 (或另一个可用端口) 上运行。

## 使用方法

1. 在浏览器中打开前端应用
2. 浏览现有智能体或创建新智能体
3. 点击智能体卡片开始对话
4. 在对话界面中输入消息并发送

## API参考

Mock服务器提供以下API端点：

### 智能体API

- `GET /api/agents` - 获取所有智能体
- `GET /api/agents/:id` - 获取特定智能体
- `POST /api/agents` - 创建新智能体

### 对话API

- `POST /api/conversations` - 创建新对话
- `GET /api/conversations/:id/messages` - 获取对话消息
- `POST /api/messages` - 发送消息

### WebSocket

- `ws://localhost:8080/ws?agent_id=<ID>` - 建立WebSocket连接接收实时消息

## 项目特色

### Efficode协议

本项目使用自定义的Efficode协议进行消息传输，具有以下特点：

- 消息压缩：自动压缩大于500字节的消息
- 结构化数据：支持不同类型的消息格式
- 实时通信：通过WebSocket推送消息更新

### 前端架构

- 使用Vue 3和Composition API
- Pinia状态管理
- 响应式设计
- 模块化组件结构

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。
这是一个基于Go语言实现的分布式智能体协作网络后端，支持Efficode协议进行智能体之间的通信。

## 功能特点

- 智能体管理（创建、查询）
- 对话管理（创建、管理对话）
- 消息处理（发送、接收消息）
- Efficode协议支持（消息压缩/解压缩、协议解析）
- WebSocket实时通信
- PostgreSQL数据存储
- Vue.js前端集成示例

## 技术栈

- **后端**：Go + Gin + GORM
- **数据库**：PostgreSQL
- **通信**：WebSocket + Efficode协议
- **AI服务**：SiliconFlow API
- **前端集成**：Vue.js

## 项目结构

```
├── api/                    # API客户端
│   └── siliconflow.go      # SiliconFlow API客户端
├── database/               # 数据库操作
│   └── db.go               # 数据库连接和操作
├── handlers/               # API处理器
│   └── api.go              # API请求处理
├── models/                 # 数据模型
│   └── agent.go            # 模型定义
├── protocol/               # 协议实现
│   └── efficode.go         # Efficode协议
├── routes/                 # 路由定义
│   └── routes.go           # API路由
├── websocket/              # WebSocket实现
│   └── manager.go          # WebSocket管理器
├── .env                    # 环境变量配置
├── db_init.go              # 数据库初始化
├── db_init.sql             # 数据库脚本
├── frontend-example.js     # 前端API封装
├── go.mod                  # Go模块定义
├── main.go                 # 主程序入口
└── README.md               # 项目说明
```

## 快速开始

### 准备工作

1. 安装Go 1.19+
2. 安装PostgreSQL 14+
3. 创建PostgreSQL数据库

### 安装与运行

1. 克隆仓库

```bash
git clone https://github.com/yourusername/nftagent.git
cd nftagent
```

2. 配置环境变量

复制`.env.example`为`.env`并修改配置：

```bash
cp .env.example .env
# 编辑.env文件，填写数据库信息和API密钥
```

3. 初始化数据库

```bash
psql -U postgres -f db_init.sql
```

4. 安装依赖

```bash
go mod tidy
```

5. 运行服务器

```bash
go run .
```

服务器默认在8080端口启动。

## API接口

### 智能体管理

- `POST /api/agents` - 创建新智能体
  ```json
  {
    "name": "智能体名称",
    "role": "智能体角色"
  }
  ```

- `GET /api/agents` - 获取所有智能体

### 对话管理

- `POST /api/conversations` - 创建新对话
  ```json
  {
    "title": "对话标题",
    "mode": "interactive"
  }
  ```

- `GET /api/conversations/:id/messages` - 获取对话消息

### 消息管理

- `POST /api/messages` - 发送消息
  ```json
  {
    "conversation_id": 1,
    "sender": "发送者名称",
    "receiver": "接收者名称",
    "content": "消息内容",
    "content_type": "text"
  }
  ```

### WebSocket

- `GET /ws?agent_id=<agent_id>` - 建立WebSocket连接

## Efficode协议

Efficode协议是一种用于智能体之间通信的轻量级协议，支持以下操作码：

- `DID` - 身份验证，格式: `@DID:{...}`
- `REQ` - 请求，格式: `#REQ?param1=value1&param2=value2`
- `DATA` - 数据传输，格式: `#DATA?content=xxx&type=text`
- `ACK` - 确认，格式: `!ACK:{...}`
- `ERROR` - 错误，格式: `!ERROR:{...}`

协议支持消息压缩功能，超过500字节的消息会自动压缩。

## 前端集成

项目提供了Vue.js前端集成示例，展示了如何：

1. 连接WebSocket
2. 发送/接收Efficode消息
3. 使用API创建智能体和对话
4. 处理消息历史

## 性能优化

- 数据库连接池
- WebSocket连接管理
- 消息压缩/解压缩
- 索引优化
- 消息历史自动清理（保留3天）

## 贡献指南

欢迎贡献代码或提出问题！请遵循以下步骤：

1. Fork仓库
2. 创建分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

## 许可证

MIT License
这是一个基于Vue.js 3的分布式智能体协作网络应用，允许创建、管理智能体并进行交互。项目具有赛博朋克风格的用户界面，支持智能体之间的通信和对话，并实现了亮色/暗色主题切换。

![应用截图](./screenshot.png)

## 功能特点

### 1. 智能体通信系统
- 使用Efficode协议进行智能体通信
- 消息大小超过500字节自动压缩
- 支持多种压缩算法

### 2. 前端设计
- 赛博朋克风格UI组件库
- **全新双主题支持：深色模式和浅色模式**
- 自适应设计，适配多种设备尺寸
- 定制化组件：CyberInput、CyberEditor、CyberCard、CyberTerminal

### 3. 核心功能
- 智能体创建和注册页面
- 实时通信系统，支持消息压缩
- **MetaMask钱包集成**：支持钱包连接和智能体绑定
- 区块链集成，支持NFT铸造（前端模拟）
- MCP协议接口，用于外部资源访问

### 4. 技术实现
- Vue.js 3 + Composition API
- Pinia状态管理
- Vue Router路由管理
- 前端模拟区块链功能
- **MetaMask API集成**

## 最近更新

### 2024年6月30日 - 用户界面优化与钱包集成

1. **全面浅色模式支持**
   - 所有页面现在都支持浅色模式和深色模式切换
   - 将原有鲜绿色(#00ff00)元素在浅色模式下改为墨绿色(#006633)
   - 优化了文本颜色对比度和可读性

2. **对话功能优化**
   - 修复了智能体列表和智能体详情页的"开始对话"功能
   - 优化了对话创建逻辑，确保创建成功后再导航到对话页面
   - 简化了市场页面布局，移除了冗余的对话按钮

3. **MetaMask钱包集成**
   - 实现了钱包连接组件
   - 添加了智能体与钱包绑定功能
   - 支持显示钱包地址和余额
   - 优化了NFT铸造流程，依赖于钱包绑定

## 开发路线图

### 已完成
- ✅ 前端基础UI框架
- ✅ 智能体列表、详情和对话页面
- ✅ 智能体创建和管理
- ✅ 模拟对话功能
- ✅ 浅色/深色模式切换
- ✅ MetaMask钱包集成
- ✅ 前端NFT铸造模拟

### 进行中
- 🔄 UI组件优化
- 🔄 响应式布局完善

### 计划中
- 📅 **后端服务集成**
  - RESTful API设计和实现
  - 智能体数据持久化存储
  - 用户认证和授权系统
  - 真实对话历史记录

- 📅 **区块链功能增强**
  - 实际智能合约部署
  - 真实NFT铸造和交易
  - 多链支持(Ethereum, Polygon等)

- 📅 **AI功能增强**
  - 接入实际LLM模型API
  - 支持多种AI模型选择
  - 智能体个性化配置

## 后端集成计划

### 1. API设计 (计划时间：2周)
- 设计RESTful API接口文档
- 实现以下端点:
  - `/api/agents` - 智能体CRUD操作
  - `/api/conversations` - 对话管理
  - `/api/messages` - 消息发送和接收
  - `/api/users` - 用户管理
  - `/api/blockchain` - 区块链相关操作

### 2. 数据库设计 (计划时间：1周)
- 设计关系型数据库架构
- 表设计：用户、智能体、对话、消息等
- 优化查询和索引

### 3. 身份验证与授权 (计划时间：1周)
- 实现JWT认证
- 用户角色和权限管理
- OAuth2集成(可选)

### 4. AI服务集成 (计划时间：2周)
- 与OpenAI API集成
- 配置智能体个性和行为模式
- 消息历史管理和上下文处理

### 5. 区块链服务 (计划时间：2周)
- 智能合约开发和部署
- NFT铸造API实现
- 交易验证和确认

### 6. 前后端集成 (计划时间：2周)
- 修改前端代码，使用实际API替换模拟数据
- 实现加载状态和错误处理
- 优化性能和用户体验

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式启动

```bash
npm run dev
```

### 生产模式构建

```bash
npm run build
```

## 项目结构

```
src/
├── assets/         # 静态资源文件
├── components/     # 通用组件
│   ├── CyberCard.vue       # 赛博朋克风格卡片组件
│   ├── CyberEditor.vue     # 代码/大文本编辑器组件
│   ├── CyberTerminal.vue   # 终端对话组件
│   ├── WalletConnect.vue   # 钱包连接组件
│   └── ...
├── router/         # 路由配置
├── services/       # 服务
│   ├── blockchain.js       # 区块链集成服务
│   ├── efficode.js         # 数据压缩服务
│   └── mcp.js              # MCP协议服务
├── store/          # Pinia状态管理
│   └── agents.js           # 智能体状态管理
├── views/          # 页面视图
│   ├── AgentsList.vue      # 智能体列表页面
│   ├── AgentDetail.vue     # 智能体详情页面
│   ├── AgentDialog.vue     # 智能体对话页面
│   ├── MarketPlace.vue     # 智能体市场页面
│   └── AgentRegister.vue   # 智能体注册页面
├── App.vue         # 主应用组件
└── main.js         # 应用入口文件
```
身份层	ERC-721 + IPFS	无需开发
行动层	ERC-4337账户抽象 + agent	仅需接口对接
经济层	Seaport + Royalty Registry	直接调用
## 组件和功能详解

### 1. 智能体管理

系统支持创建和管理多个智能体，每个智能体有以下属性：
- 名称
- 描述
- 创建时间
- ID（自动生成）
- 钱包地址（可选，通过MetaMask绑定）
- NFT身份证明（可选）

### 2. 通信协议

#### Efficode压缩系统
- 自动检测内容大小，超过阈值自动压缩
- 支持对大型JSON数据的高效压缩
- 自动解压缩接收到的压缩数据

#### MCP（Master Control Protocol）
- 提供智能体访问外部资源的标准接口
- 包括知识库、工具、传感器等资源访问端点
- 请求验证和权限管理

### 3. 区块链集成

- 支持MetaMask钱包连接
- 智能体可绑定到钱包地址
- 智能体可铸造NFT作为身份证明
- 支持多种区块链网络切换（模拟）

## 使用指南

### 创建新智能体

1. 在主页点击"注册智能体"
2. 填写智能体名称和描述
3. 点击"创建"按钮
4. 新创建的智能体会出现在智能体列表中

### 与智能体对话

1. 在智能体列表中找到要对话的智能体
2. 点击"开始对话"按钮
3. 在对话框中输入消息并发送
4. 智能体会自动回复你的消息

### 绑定钱包和铸造NFT

1. 进入智能体详情页面
2. 在"区块链功能"区域，连接MetaMask钱包
3. 点击"绑定钱包"按钮，将智能体与钱包地址关联
4. 钱包绑定后，点击"铸造NFT"按钮创建智能体的数字身份证明

## 注意事项

- 所有数据都保存在浏览器内存中，刷新页面后数据会丢失
- 区块链功能目前仅为模拟，不会执行实际交易
- 智能体的回复是模拟的，不是真正的AI生成

## 许可证

本项目采用MIT许可证。

## 联系我们

- 项目维护者：[Your Name](mailto:your.email@example.com)
- 项目主页：[https://github.com/yourusername/efficodeagent](https://github.com/yourusername/efficodeagent)

---

EfficodeAgent - 智能体自由通信的未来 