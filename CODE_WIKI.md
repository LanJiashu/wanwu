# Wanwu AI Agent Platform - Code Wiki

> 本文档为 **万悟 AI 智能体平台** 的完整结构化 Code Wiki，涵盖项目整体架构、主要模块职责、关键类与函数说明、依赖关系及项目运行方式。

---

## 目录

1. [项目概述](#1-项目概述)
2. [整体架构](#2-整体架构)
3. [技术栈](#3-技术栈)
4. [目录结构](#4-目录结构)
5. [核心模块详解](#5-核心模块详解)
   - 5.1 [Go 后端微服务](#51-go-后端微服务)
   - 5.2 [Python RAG 服务](#52-python-rag-服务)
   - 5.3 [Python Callback 服务](#53-python-callback-服务)
   - 5.4 [前端 Web 应用](#54-前端-web-应用)
6. [关键类与函数](#6-关键类与函数)
   - 6.1 [Go 后端](#61-go-后端)
   - 6.2 [Python RAG](#62-python-rag)
   - 6.3 [Python Callback](#63-python-callback)
   - 6.4 [前端 Vue](#64-前端-vue)
7. [服务间通信](#7-服务间通信)
8. [数据流](#8-数据流)
9. [依赖关系](#9-依赖关系)
10. [项目运行方式](#10-项目运行方式)
11. [配置说明](#11-配置说明)
12. [Docker 部署](#12-docker-部署)

---

## 1. 项目概述

**万悟 (Wanwu)** 是一个企业级、一站式、商业友好的 AI 智能体开发平台。平台采用模块化架构设计，支持灵活的功能扩展和二次开发，核心功能覆盖：

- **模型全生命周期管理** (Model Hub)
- **MCP (Model Context Protocol)** 工具生态
- **Web 搜索增强**
- **可视化工作流编排** (Workflow Studio)
- **高精度 RAG** (检索增强生成)
- **AI 智能体开发框架** (Agent Framework)
- **BaaS (Backend as a Service)** API 服务

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户层 (Browser)                                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTP
┌─────────────────────────────────▼───────────────────────────────────────────┐
│  Nginx (反向代理 / 静态资源)                                                  │
│  - 前端静态资源服务                                                            │
│  - API 路由转发                                                                │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│  BFF Service (Backend for Frontend)                                         │
│  - HTTP Gateway / 统一入口                                                   │
│  - JWT 认证 / 权限校验                                                        │
│  - 请求路由聚合 / 服务编排                                                    │
│  - 文件上传 / MinIO 代理                                                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ gRPC / HTTP
┌─────────────────────────────────┼───────────────────────────────────────────┐
│                                 ▼                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ IAM Service  │  │Agent Service │  │Model Service │  │MCP Service       │ │
│  │ 身份认证     │  │ 智能体对话   │  │ 模型管理     │  │ MCP 工具管理    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │Knowledge     │  │RAG Service   │  │Assistant     │  │App Service       │ │
│  │Service       │  │ 检索服务     │  │Service       │  │ 应用管理        │ │
│  │ 知识库管理   │  │              │  │ 助手服务     │  │                 │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │Operate       │  │Workflow      │  │Callback      │                       │
│  │Service       │  │Service       │  │Service       │                       │
│  │ 运营管理     │  │ 工作流引擎   │  │ 回调处理     │                       │
│  └──────────────┘  └──────────────┘  └──────────────┘                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Python RAG 服务 (rag-wanwu)                                          │   │
│  │ - 文档解析 / 向量化 / 检索 / 知识图谱 / QA 库                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│  基础设施层                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ MySQL/   │ │ Redis    │ │ MinIO    │ │Kafka     │ │Elasticsearch     │  │
│  │ TiDB/    │ │ (缓存/   │ │ (对象    │ │(消息     │ │(向量+全文        │  │
│  │OceanBase │ │  会话)   │ │  存储)   │ │ 队列)    │ │ 索引)            │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 技术栈

### 后端 (Go)
| 技术 | 版本 | 用途 |
|------|------|------|
| Go | 1.24.0 | 编程语言 |
| Gin | v1.10.1 | HTTP Web 框架 |
| gRPC | v1.67.3 | 微服务间通信 |
| GORM | v1.25.11 | ORM 框架 |
| Eino | v0.7.32 | 字节跳动 AI 应用开发框架 |
| Viper | v1.20.1 | 配置管理 |
| Zap | v1.27.0 | 日志库 |
| JWT-Go | v3.2.0 | JWT 认证 |
| Casbin | v2.89.0 | 权限管理 |
| MinIO Go SDK | v7.0.88 | 对象存储 |
| go-redis | v9.8.0 | Redis 客户端 |

### RAG / Callback (Python)
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12 | 编程语言 |
| Flask | 3.0.2 / 3.1.2 | Web 框架 |
| Gunicorn | 21.2.0 / 23.0.0 | WSGI 服务器 |
| Elasticsearch | 8.15.0 | 向量+全文检索 |
| LangChain | 0.1.12 | LLM 应用框架 |
| PyMongo | 4.10.1 | MongoDB 客户端 |
| kafka-python | 2.0.2 | Kafka 客户端 |
| MinIO | 7.2.7 / 7.2.8 | 对象存储 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 2.6.11 | 前端框架 |
| Vue Router | 3.2.0 | 路由管理 |
| Vuex | 3.4.0 | 状态管理 |
| Element UI | 2.15.14 | UI 组件库 |
| AntV X6 | 2.18.1 | 工作流画布 |
| AntV G6 | 4.8.0 | 知识图谱可视化 |
| ECharts | 5.4.3 | 数据可视化 |
| Axios | 1.4.0 | HTTP 客户端 |
| Monaco Editor | 0.24.0 | 代码编辑器 |

### 基础设施
| 技术 | 用途 |
|------|------|
| MySQL / TiDB / OceanBase | 关系型数据库 |
| Redis | 缓存、会话、消息队列 |
| MinIO | 对象存储 (文档、图片) |
| Kafka | 消息队列 (异步任务、数据飞轮) |
| Elasticsearch | 向量检索、全文检索 |
| MongoDB | 日志存储、用户反馈 |

---

## 4. 目录结构

```
wanwu/
├── api/                          # 生成的 gRPC/Protobuf Go 代码
│   └── proto/                    # 各服务的 protobuf 生成的 Go 文件
├── cmd/                          # Go 服务入口 (main.go)
│   ├── agent-service/            # Agent 服务入口
│   ├── app-service/              # 应用服务入口
│   ├── assistant-service/        # 助手服务入口
│   ├── bff-service/              # BFF 网关服务入口
│   ├── iam-service/              # 身份认证服务入口
│   ├── knowledge-service/        # 知识库服务入口
│   ├── mcp-service/              # MCP 服务入口
│   ├── model-service/            # 模型服务入口
│   ├── operate-service/          # 运营服务入口
│   └── rag-service/              # RAG 服务入口
├── internal/                     # 内部实现 (不可被外部导入)
│   ├── agent-service/            # Agent 服务实现
│   ├── app-service/              # 应用服务实现
│   ├── assistant-service/        # 助手服务实现
│   ├── bff-service/              # BFF 服务实现
│   ├── iam-service/              # IAM 服务实现
│   ├── knowledge-service/        # 知识库服务实现
│   ├── mcp-service/              # MCP 服务实现
│   ├── model-service/            # 模型服务实现
│   ├── operate-service/          # 运营服务实现
│   └── rag-service/              # RAG 服务实现
├── pkg/                          # 公共包 (可被外部导入)
│   ├── constant/                 # 常量定义
│   ├── db/                       # 数据库连接封装
│   ├── es/                       # Elasticsearch 封装
│   ├── gin-util/                 # Gin 工具
│   ├── grpc-util/                # gRPC 工具
│   ├── http-client/              # HTTP 客户端
│   ├── i18n/                     # 国际化
│   ├── jwt-util/                 # JWT 工具
│   ├── minio/                    # MinIO 封装
│   ├── model-provider/           # 模型提供商统一接口
│   ├── openapi3-util/            # OpenAPI3 工具
│   ├── redis/                    # Redis 封装
│   ├── safe-go-util/             # 安全并发工具
│   ├── sse-util/                 # SSE 工具
│   └── util/                     # 通用工具
├── proto/                        # Protobuf 定义文件
├── web/                          # 前端 Vue.js 应用
│   ├── src/
│   │   ├── api/                  # API 接口定义
│   │   ├── assets/               # 静态资源
│   │   ├── components/           # Vue 组件
│   │   ├── lang/                 # 国际化语言包
│   │   ├── mixins/               # Vue Mixins
│   │   ├── router/               # 路由配置
│   │   ├── store/                # Vuex 状态管理
│   │   ├── style/                # SCSS 样式
│   │   ├── utils/                # 工具函数
│   │   └── views/                # 页面视图
│   └── package.json
├── rag/                          # Python RAG 服务
│   └── rag_open_source/
│       ├── rag_core/             # RAG 核心服务
│       └── rag_es_server_unify/  # ES 检索服务
├── callback/                     # Python Callback 服务
│   ├── callback/                 # 应用代码
│   ├── configs/                  # 配置
│   ├── extensions/               # 扩展 (MinIO, Redis)
│   └── utils/                    # 工具函数
├── docs/                         # API 文档 (Swagger)
├── configs/                      # 配置文件
│   └── middleware/               # 中间件配置
├── docker-compose.yaml           # Docker Compose 配置
├── Makefile                      # 构建脚本
├── go.mod                        # Go 模块定义
└── README.md                     # 项目说明
```

---

## 5. 核心模块详解

### 5.1 Go 后端微服务

#### 5.1.1 BFF Service (Backend for Frontend)

**职责**: 前端统一网关，聚合所有下游微服务，对外暴露 HTTP API。

**入口**: [cmd/bff-service/main.go](file:///workspace/cmd/bff-service/main.go)

**初始化流程**:
1. 加载配置 (`config.LoadConfig()`)
2. 初始化日志 (`log.InitLog()`)
3. 设置时区 (`util.InitTimeLocal()`)
4. 初始化国际化 (`i18n.Init()`)
5. 初始化敏感词过滤 (`ahocorasick.Init()`)
6. 初始化 JWT (`jwt_util.InitUserJWT()`)
7. 初始化 MinIO (`minio.InitCustom()` / `InitFileUpload()`)
8. 初始化 Redis (`redis.InitOP()`)
9. 初始化 OAuth2 (`oauth2_util.Init()`)
10. 初始化模型提供商 (`mp.Init()`)
11. 初始化 MCP Server (`mcp_util.Init()`)
12. 启动 HTTP 服务 (`handler.Start()`)

**关键文件**:
| 文件 | 职责 |
|------|------|
| [internal/bff-service/service/service.go](file:///workspace/internal/bff-service/service/service.go) | gRPC 客户端聚合，连接所有下游服务 |
| [internal/bff-service/service/login.go](file:///workspace/internal/bff-service/service/login.go) | 登录业务逻辑，JWT Token 生成 |
| [internal/bff-service/service/knowledge.go](file:///workspace/internal/bff-service/service/knowledge.go) | 知识库管理接口 |
| [internal/bff-service/service/assistant.go](file:///workspace/internal/bff-service/service/assistant.go) | 助手服务接口 |
| [internal/bff-service/service/workflow.go](file:///workspace/internal/bff-service/service/workflow.go) | 工作流服务接口 |
| [internal/bff-service/service/agent-skills.go](file:///workspace/internal/bff-service/service/agent-skills.go) | 智能体技能管理 |
| [internal/bff-service/service/model.go](file:///workspace/internal/bff-service/service/model.go) | 模型管理接口 |
| [internal/bff-service/service/mcp.go](file:///workspace/internal/bff-service/service/mcp.go) | MCP 服务接口 |
| [internal/bff-service/service/rag.go](file:///workspace/internal/bff-service/service/rag.go) | RAG 服务接口 |

#### 5.1.2 IAM Service (Identity and Access Management)

**职责**: 用户身份认证、权限管理、组织管理。

**入口**: [cmd/iam-service/main.go](file:///workspace/cmd/iam-service/main.go)

**初始化流程**:
1. 加载配置
2. 初始化日志
3. 初始化 SMTP (`smtp_util.Init()`)
4. 初始化 Redis (`redis.InitIAM()`)
5. 初始化数据库 (`db.New()`)
6. 启动 gRPC 服务器

**关键文件**:
| 文件 | 职责 |
|------|------|
| [internal/iam-service/client/client.go](file:///workspace/internal/iam-service/client/client.go) | gRPC 客户端 |
| [internal/iam-service/config/config.go](file:///workspace/internal/iam-service/config/config.go) | 配置定义 |

#### 5.1.3 Agent Service

**职责**: AI 智能体核心服务，支持单智能体和多智能体对话。

**入口**: [cmd/agent-service/main.go](file:///workspace/cmd/agent-service/main.go)

**关键文件**:
| 文件 | 职责 |
|------|------|
| [internal/agent-service/service/single_agent.go](file:///workspace/internal/agent-service/service/single_agent.go) | 单智能体实现 (基于 Eino ADK) |
| [internal/agent-service/service/multi_agent.go](file:///workspace/internal/agent-service/service/multi_agent.go) | 多智能体实现 (Supervisor 模式) |
| [internal/agent-service/service/mcp_service.go](file:///workspace/internal/agent-service/service/mcp_service.go) | MCP 工具集成 |
| [internal/agent-service/service/model_service.go](file:///workspace/internal/agent-service/service/model_service.go) | 模型调用服务 |
| [internal/agent-service/service/plugin_service.go](file:///workspace/internal/agent-service/service/plugin_service.go) | 插件服务 |
| [internal/agent-service/service/agent_tool_service.go](file:///workspace/internal/agent-service/service/agent_tool_service.go) | 智能体工具服务 |
| [internal/agent-service/service/agent_params_service.go](file:///workspace/internal/agent-service/service/agent_params_service.go) | 智能体参数服务 |

**单智能体架构**:
```
User Request
    ↓
SingleAgentChat()
    ↓
CreateSingleAgent()
    ├── buildAgentChatInfo()      # 构建聊天信息
    ├── createAgent()             # 创建 ChatModelAgent (Eino ADK)
    └── Chat()                    # 执行流式对话
```

**多智能体架构** (Supervisor 模式):
```
User Request
    ↓
MultiAgentChat()
    ↓
CreateSupervisorMultiAgent()
    ├── 创建 Supervisor (SingleAgent)
    ├── buildMultiSubAgent()      # 创建子智能体列表
    └── 组装 Supervisor 模式
    ↓
Supervisor 调度 Sub-Agent 1, Sub-Agent 2, ... Sub-Agent N
```

#### 5.1.4 Knowledge Service

**职责**: 知识库管理、文档处理、任务调度。

**入口**: [cmd/knowledge-service/main.go](file:///workspace/cmd/knowledge-service/main.go)

**关键文件**:
| 文件 | 职责 |
|------|------|
| [internal/knowledge-service/service/rag_knowledge_service.go](file:///workspace/internal/knowledge-service/service/rag_knowledge_service.go) | 知识库核心服务 |
| [internal/knowledge-service/service/rag_doc_service.go](file:///workspace/internal/knowledge-service/service/rag_doc_service.go) | 文档处理服务 |
| [internal/knowledge-service/service/rag_keyword_service.go](file:///workspace/internal/knowledge-service/service/rag_keyword_service.go) | 关键词服务 |
| [internal/knowledge-service/service/rag_qa_service.go](file:///workspace/internal/knowledge-service/service/rag_qa_service.go) | QA 问答对服务 |
| [internal/knowledge-service/service/rag_report_service.go](file:///workspace/internal/knowledge-service/service/rag_report_service.go) | 报告服务 |
| [internal/knowledge-service/service/dify_knowledge_service.go](file:///workspace/internal/knowledge-service/service/dify_knowledge_service.go) | Dify 知识库集成 |
| [internal/knowledge-service/service/minio_service.go](file:///workspace/internal/knowledge-service/service/minio_service.go) | MinIO 存储服务 |
| [internal/knowledge-service/task/](file:///workspace/internal/knowledge-service/task/) | 异步任务处理 |

#### 5.1.5 Model Service

**职责**: 模型管理、模型调用、多模型提供商适配。

**入口**: [cmd/model-service/main.go](file:///workspace/cmd/model-service/main.go)

**关键文件**:
| 文件 | 职责 |
|------|------|
| [pkg/model-provider/common.go](file:///workspace/pkg/model-provider/common.go) | 模型提供商通用接口 |
| [pkg/model-provider/mp-yuanjing/](file:///workspace/pkg/model-provider/mp-yuanjing/) | 联通元景模型适配 |
| [pkg/model-provider/mp-openai-compatible/](file:///workspace/pkg/model-provider/mp-openai-compatible/) | OpenAI 兼容模型适配 |
| [pkg/model-provider/mp-deepseek/](file:///workspace/pkg/model-provider/mp-deepseek/) | DeepSeek 模型适配 |
| [pkg/model-provider/mp-qwen/](file:///workspace/pkg/model-provider/mp-qwen/) | 通义千问模型适配 |
| [pkg/model-provider/mp-ollama/](file:///workspace/pkg/model-provider/mp-ollama/) | Ollama 本地模型适配 |
| [pkg/model-provider/mp-huoshan/](file:///workspace/pkg/model-provider/mp-huoshan/) | 火山引擎模型适配 |
| [pkg/model-provider/mp-qianfan/](file:///workspace/pkg/model-provider/mp-qianfan/) | 百度千帆模型适配 |
| [pkg/model-provider/mp-jina/](file:///workspace/pkg/model-provider/mp-jina/) | Jina AI 模型适配 |
| [pkg/model-provider/mp-infini/](file:///workspace/pkg/model-provider/mp-infini/) | 无问芯穹模型适配 |

**支持的模型类型**:
- LLM (大语言模型)
- Text Embedding (文本嵌入)
- Text Rerank (文本重排序)
- Multi-modal Embedding (多模态嵌入)
- Multi-modal Rerank (多模态重排序)
- OCR (光学字符识别)
- GUI (图形界面模型)
- PDF Parser (PDF 解析)
- ASR (语音识别)
- Text2Image (文生图)

#### 5.1.6 其他微服务

| 服务 | 职责 | 入口 |
|------|------|------|
| Assistant Service | 助手会话管理 | [cmd/assistant-service/main.go](file:///workspace/cmd/assistant-service/main.go) |
| App Service | 应用管理 | [cmd/app-service/main.go](file:///workspace/cmd/app-service/main.go) |
| MCP Service | MCP 工具管理 | [cmd/mcp-service/main.go](file:///workspace/cmd/mcp-service/main.go) |
| RAG Service | RAG 检索服务 | [cmd/rag-service/main.go](file:///workspace/cmd/rag-service/main.go) |
| Operate Service | 运营管理 | [cmd/operate-service/main.go](file:///workspace/cmd/operate-service/main.go) |

### 5.2 Python RAG 服务

**职责**: 文档解析、向量化、检索、知识图谱、QA 库管理。

#### 5.2.1 RAG 核心服务 (rag_core)

**入口**: [rag/rag_open_source/rag_core/run.py](file:///workspace/rag/rag_open_source/rag_core/run.py)

**核心功能路由**:

| 路由 | 功能 |
|------|------|
| `/rag/init-knowledge-base` | 初始化知识库 |
| `/rag/add-knowledge-temp` | 上传文件并解析 |
| `/rag/del-knowledge-base` | 删除知识库 |
| `/rag/search-knowledge-base` | 核心检索接口 (支持多知识库、rerank、metadata 过滤) |
| `/rag/list-knowledge-base` | 列出知识库 |
| `/rag/get-content-list` | 获取文件内容分块列表 |
| `/rag/batch-add-chunks` | 批量添加分块 |
| `/rag/doc_parser` | 外部文档解析并切分 |
| `/rag/user_feedback` | 用户反馈 (支持 Kafka 数据飞轮) |
| `/rag/knowledgeBase-graph` | 获取知识图谱 |
| `/rag/init-QA-base` ~ `/rag/search-QA-base` | 问答库 CRUD 与检索 |

**配置**: [rag/rag_open_source/rag_core/settings.py](file:///workspace/rag/rag_open_source/rag_core/settings.py)

| 配置类别 | 说明 |
|----------|------|
| KAFKA | 消息队列连接、Topic、Group ID |
| OSS/MINIO | 对象存储配置 |
| REDIS | 缓存配置 |
| MONGO | 日志存储配置 |
| LLM | 模型生成参数 (temperature, context length) |
| 向量/检索 | Milvus、ES 连接配置 |
| MODEL_PROVIDER | 模型提供方 URL 和 Token |
| GRAPH | 知识图谱服务 URL |

#### 5.2.2 ES 检索服务 (rag_es_server_unify)

**入口**: [rag/rag_open_source/rag_es_server_unify/es_rag_server.py](file:///workspace/rag/rag_open_source/rag_es_server_unify/es_rag_server.py)

**核心功能**:

| 路由 | 功能 |
|------|------|
| `/rag/kn/init_kb` | 初始化知识库 ES 索引 |
| `/rag/kn/add` | 批量添加向量数据 |
| `/rag/kn/search` | 多知识库 KNN 向量检索 |
| `/rag/kn/del_kb` | 删除知识库 |
| `/api/v1/rag/es/search` | Snippet 文本检索 |
| `/api/v1/rag/es/rescore` | 混合检索重排序 (BM25 + 向量 cosine 加权融合) |

**依赖**:
- Elasticsearch (向量+全文索引)
- Embedding 服务 (生成向量)
- 内部工具模块 (kb_info, meta_util, qa_util, mapping_util)

### 5.3 Python Callback 服务

**职责**: 文档处理回调、文件格式转换、Prompt 生成。

**入口**: [callback/run.py](file:///workspace/callback/run.py)

**核心路由**:

| 路由 | 方法 | 功能 |
|------|------|------|
| `/doc_pra` | POST | 文档解析生成 Prompt |
| `/generate_file` | POST | Markdown 转 PDF/DOCX/TXT 并上传 MinIO |

**业务逻辑**: [callback/callback/services/doc.py](file:///workspace/callback/callback/services/doc.py)

| 函数 | 功能 |
|------|------|
| `process_documents()` | 并发解析多个文档 URL，生成 RAG Prompt |
| `parse_doc()` | 调用外部 RAG `doc_parser` 接口解析单个文档 |
| `generate_file_to_minio()` | Markdown 格式转换并上传 MinIO |

**依赖**:
- requests (调用外部 RAG 服务)
- python-docx (生成 Word)
- reportlab (生成 PDF，支持中文)
- concurrent.futures (并发处理)

### 5.4 前端 Web 应用

**技术栈**: Vue 2 + Element UI + Vue Router + Vuex

**入口**: [web/src/main.js](file:///workspace/web/src/main.js)

**目录结构**:

```
web/src/
├── api/                    # API 接口
│   ├── permission/         # 权限相关 API
│   ├── agent.js            # 智能体 API
│   ├── chat.js             # 聊天 API
│   ├── knowledge.js        # 知识库 API
│   ├── workflow.js         # 工作流 API
│   └── ...
├── components/             # Vue 组件
│   ├── app/                # 应用组件
│   ├── createApp/          # 创建应用组件
│   ├── filePreview/        # 文件预览组件
│   ├── publishConfig/      # 发布配置组件
│   └── stream/             # 流式消息组件
├── views/                  # 页面视图
│   ├── agent/              # 智能体页面
│   ├── aiAssistant/        # AI 助手页面
│   ├── knowledge/          # 知识库页面
│   ├── workflowNew/        # 工作流页面
│   ├── rag/                # RAG 页面
│   └── ...
├── router/                 # 路由配置
│   └── index.js            # 路由定义
├── store/                  # Vuex 状态管理
│   ├── module/
│   │   ├── app.js          # 应用状态
│   │   ├── login.js        # 登录状态
│   │   ├── user.js         # 用户状态
│   │   └── workflow.js     # 工作流状态
│   └── index.js
├── utils/                  # 工具函数
│   ├── request.js          # Axios 封装
│   ├── streamProcessor.js  # 流式数据处理
│   └── crypto.js           # 加密工具
└── lang/                   # 国际化
    ├── zh.js               # 中文
    ├── en.js               # 英文
    └── index.js
```

**关键视图页面**:

| 视图 | 路径 | 功能 |
|------|------|------|
| 智能体 | `views/agent/index.vue` | 智能体管理 |
| 知识库 | `views/knowledge/index.vue` | 知识库管理 |
| 工作流 | `views/workflowNew/index.vue` | 可视化工作流编排 |
| RAG | `views/rag/index.vue` | RAG 配置 |
| 模型体验 | `views/modelExprience/index.vue` | 模型体验 |
| 应用广场 | `views/exploreSquare/index.vue` | 应用广场 |
| MCP 管理 | `views/mcpManagementPublic/square.vue` | MCP 广场 |

---

## 6. 关键类与函数

### 6.1 Go 后端

#### BFF Service

**Service 聚合层** ([internal/bff-service/service/service.go](file:///workspace/internal/bff-service/service/service.go))

```go
// 全局 gRPC 客户端变量
var (
    iam               api_iam.IAMServiceClient
    perm              api_perm.PermServiceClient
    model             api_model.ModelServiceClient
    mcp               api_mcp.MCPServiceClient
    knowledgeBase     api_kb.KnowledgeBaseServiceClient
    knowledgeBaseDoc  api_kb_doc.KnowledgeBaseDocServiceClient
    // ... 更多客户端
)

// Init 建立所有下游服务的 gRPC 连接
func Init()

// newConn 创建 gRPC 连接，使用 round_robin 负载均衡
func newConn(host string) (*grpc.ClientConn, error)
```

**登录服务** ([internal/bff-service/service/login.go](file:///workspace/internal/bff-service/service/login.go))

```go
// Login 标准用户名密码登录
func Login(ctx context.Context, req *LoginReq) (*LoginResp, error)

// LoginByEmail 邮箱登录
func LoginByEmail(ctx context.Context, req *LoginByEmailReq) (*LoginResp, error)

// getLoginResp 统一封装登录响应
func getLoginResp(ctx context.Context, user *User) (*LoginResp, error)
```

#### Agent Service

**单智能体** ([internal/agent-service/service/single_agent.go](file:///workspace/internal/agent-service/service/single_agent.go))

```go
type SingleAgent struct {
    ChatContext     *request.AgentChatContext
    ChatModelAgent  *adk.ChatModelAgent
    Req             *request.AgentChatParams
    AgentPreprocess *agent_preprocessor.AgentPreprocess
}

// SingleAgentChat 对外入口
func SingleAgentChat(ctx context.Context, req *request.AgentChatParams) (stream *AgentChatStream, err error)

// CreateSingleAgent 创建单智能体实例
func CreateSingleAgent(ctx context.Context, req *request.AgentChatParams) (*SingleAgent, error)

// Chat 执行流式 Agent 问答
func (s *SingleAgent) Chat(ctx context.Context) (stream *AgentChatStream, err error)

// Run 实现 adk.Agent 接口
func (s *SingleAgent) Run(ctx context.Context, input *schema.Message, opts ...adk.AgentOption) (*schema.StreamReader[*schema.Message], error)
```

**多智能体** ([internal/agent-service/service/multi_agent.go](file:///workspace/internal/agent-service/service/multi_agent.go))

```go
type MultiAgent struct {
    MultiAgent       adk.Agent
    AgentChatContext *request.AgentChatContext
}

// MultiAgentChat 对外入口
func MultiAgentChat(ctx context.Context, req *request.MultiAgentChatParams) (stream *AgentChatStream, err error)

// CreateSupervisorMultiAgent 创建 Supervisor 多智能体
func CreateSupervisorMultiAgent(ctx context.Context, req *request.MultiAgentChatParams) (*MultiAgent, error)

// buildMultiSubAgent 批量创建子智能体
func buildMultiSubAgent(ctx context.Context, subAgents []*SubAgentConfig) (map[string]adk.Agent, error)
```

#### 模型提供商

**通用接口** ([pkg/model-provider/common.go](file:///workspace/pkg/model-provider/common.go))

```go
// 模型类型常量
const (
    ModelTypeLLM              = "llm"
    ModelTypeTextEmbedding    = "text-embedding"
    ModelTypeTextRerank       = "text-rerank"
    ModelTypeMultiEmbedding   = "multi-modal-embedding"
    ModelTypeMultiRerank      = "multi-modal-rerank"
    ModelTypeOcr              = "ocr"
    ModelTypeGui              = "gui"
    ModelTypePdfParser        = "pdf-parser"
    ModelTypeSyncAsr          = "sync-asr"
    ModelTypeText2Image       = "text2image"
)

// 模型提供商常量
const (
    ProviderOpenAICompatible = "openai-compatible"
    ProviderYuanJing         = "yuanjing"
    ProviderHuoshan          = "huoshan"
    ProviderOllama           = "ollama"
    ProviderQwen             = "qwen"
    ProviderInfini           = "infini"
    ProviderQianfan          = "qianfan"
    ProviderDeepSeek         = "deepseek"
    ProviderJina             = "jina"
)

// Init 初始化模型回调 URL
func Init(callbackUrl string)
```

#### 数据库封装

**DB 客户端** ([pkg/db/client.go](file:///workspace/pkg/db/client.go))

```go
type Config struct {
    DBName     string     // 数据库类型: mysql/tidb/oceanbase/postgres
    MySQL      ConnConfig
    PostgreSQL ConnConfig
    TiDB       ConnConfig
    OceanBase  ConnConfig
}

type ConnConfig struct {
    Address      string
    User         string
    Password     string
    Database     string
    MaxOpenConns int
    MaxIdleConns int
    LogMode      bool
}

// New 根据配置创建数据库连接
func New(cfg *Config) (*gorm.DB, error)
```

#### Redis 封装

**Redis 客户端** ([pkg/redis/client.go](file:///workspace/pkg/redis/client.go))

```go
type Config struct {
    Host       string
    Port       string
    Username   string
    Password   string
    Standalone bool     // 是否为单机模式
    MasterName string   // 哨兵主节点名称
}

// 通用操作
func (c *client) Cli() *redis.Client
func (c *client) Del(keys ...string) error
func (c *client) Expire(key string, expiration time.Duration) error

// Hash 操作
func (c *client) HSet(key string, items ...HashItem) error
func (c *client) HGet(key, field string) (string, error)
func (c *client) HGetAll(key string) (map[string]string, error)

// 发布订阅
func (c *client) Publish(channel string, message interface{}) error
func (c *client) RegisterSubscribe(channel string, handler SubscribeHandler) error
```

### 6.2 Python RAG

**RAG 核心服务** ([rag/rag_open_source/rag_core/run.py](file:///workspace/rag/rag_open_source/rag_core/run.py))

```python
# Flask 应用实例
app = Flask(__name__)

# 核心路由函数
@app.route('/rag/search-knowledge-base', methods=['POST'])
def search_knowledge_base():
    """知识库检索 (支持多知识库、rerank、query 改写、metadata 过滤)"""

@app.route('/rag/doc_parser', methods=['POST'])
def doc_parser():
    """外部文档解析并切分"""

@app.route('/rag/user_feedback', methods=['POST'])
def user_feedback():
    """用户反馈 (支持数据飞轮推送 Kafka)"""
```

**ES 检索服务** ([rag/rag_open_source/rag_es_server_unify/es_rag_server.py](file:///workspace/rag/rag_open_source/rag_es_server_unify/es_rag_server.py))

```python
# 混合检索重排序
@app.route('/api/v1/rag/es/rescore', methods=['POST'])
def rescore():
    """BM25 + 向量 cosine 加权融合重排序"""

# 多知识库 KNN 向量检索
@app.route('/rag/kn/search', methods=['POST'])
def kn_search():
    """支持多模态、metadata 过滤、附件检索"""
```

### 6.3 Python Callback

**文档处理服务** ([callback/callback/services/doc.py](file:///workspace/callback/callback/services/doc.py))

```python
def process_documents(query, file_urls, sentence_size, overlap_size):
    """并发解析多个文档 URL，生成 RAG Prompt"""

def parse_doc(file_url, sentence_size, overlap_size):
    """调用外部 RAG doc_parser 接口解析单个文档"""

def generate_file_to_minio(formatted_markdown, filename, to_format):
    """将 Markdown 转为 PDF/DOCX/TXT 并上传 MinIO"""
```

### 6.4 前端 Vue

**API 封装** ([web/src/utils/request.js](file:///workspace/web/src/utils/request.js))

```javascript
// Axios 实例配置
const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API,
  timeout: 30000
});

// 请求拦截器 (添加 Token)
service.interceptors.request.use(config => { ... });

// 响应拦截器 (错误处理)
service.interceptors.response.use(response => { ... }, error => { ... });
```

**流式数据处理** ([web/src/utils/streamProcessor.js](file:///workspace/web/src/utils/streamProcessor.js))

```javascript
// SSE 流式数据解析处理
function processStream(response, callback) { ... }
```

---

## 7. 服务间通信

### 7.1 通信方式

| 通信方式 | 使用场景 | 协议 |
|----------|----------|------|
| HTTP RESTful | 前端 <-> BFF, 外部 API | HTTP/1.1, JSON |
| gRPC | 微服务间内部通信 | HTTP/2, Protobuf |
| SSE | 流式对话 (Agent 聊天) | HTTP/1.1, 文本流 |
| Kafka | 异步任务、数据飞轮 | 自定义协议 |
| Redis Pub/Sub | 实时消息推送 | Redis 协议 |

### 7.2 gRPC 服务定义

所有 gRPC 服务定义位于 [proto/](file:///workspace/proto/) 目录：

| 服务 | Proto 文件 | 生成代码 |
|------|-----------|----------|
| IAM Service | [proto/iam-service/iam-service.proto](file:///workspace/proto/iam-service/iam-service.proto) | [api/proto/iam-service/](file:///workspace/api/proto/iam-service/) |
| Model Service | [proto/model-service/model-service.proto](file:///workspace/proto/model-service/model-service.proto) | [api/proto/model-service/](file:///workspace/api/proto/model-service/) |
| Knowledge Service | [proto/knowledgebase-service/knowledgebase-service.proto](file:///workspace/proto/knowledgebase-service/knowledgebase-service.proto) | [api/proto/knowledgebase-service/](file:///workspace/api/proto/knowledgebase-service/) |
| RAG Service | [proto/rag-service/rag-service.proto](file:///workspace/proto/rag-service/rag-service.proto) | [api/proto/rag-service/](file:///workspace/api/proto/rag-service/) |
| Assistant Service | [proto/assistant-service/assistant-service.proto](file:///workspace/proto/assistant-service/assistant-service.proto) | [api/proto/assistant-service/](file:///workspace/api/proto/assistant-service/) |
| App Service | [proto/app-service/app-service.proto](file:///workspace/proto/app-service/app-service.proto) | [api/proto/app-service/](file:///workspace/api/proto/app-service/) |
| MCP Service | [proto/mcp-service/mcp-service.proto](file:///workspace/proto/mcp-service/mcp-service.proto) | [api/proto/mcp-service/](file:///workspace/api/proto/mcp-service/) |
| Operate Service | [proto/operate-service/operate-service.proto](file:///workspace/proto/operate-service/operate-service.proto) | [api/proto/operate-service/](file:///workspace/api/proto/operate-service/) |

**生成命令**:
```bash
make grpc-protoc
# 或
make pb
```

---

## 8. 数据流

### 8.1 智能体对话流

```
用户输入
    ↓
前端 Web → BFF Service (HTTP)
    ↓
BFF Service → Agent Service (gRPC)
    ↓
Agent Service:
    ├── 查询 Assistant 配置 (Assistant Service gRPC)
    ├── 加载 MCP 工具 (MCP Service gRPC)
    ├── 调用模型 (Model Service gRPC)
    ├── RAG 检索 (RAG Service gRPC)
    └── 执行工具调用
    ↓
SSE 流式响应返回前端
```

### 8.2 知识库文档处理流

```
用户上传文档
    ↓
前端 Web → BFF Service (HTTP)
    ↓
BFF Service → Knowledge Service (gRPC)
    ↓
Knowledge Service:
    ├── 保存文档元数据到 MySQL
    ├── 上传文件到 MinIO
    └── 发送 Kafka 消息 (异步处理)
    ↓
RAG 服务消费 Kafka 消息:
    ├── 从 MinIO 下载文档
    ├── 文档解析 (OCR/PDF/文本提取)
    ├── 文本切分 (通用切分/父子切分)
    ├── 向量化 (调用 Embedding 模型)
    └── 写入 Elasticsearch
    ↓
BFF 轮询文档状态 → 前端展示
```

### 8.3 RAG 检索流

```
用户提问
    ↓
前端 Web → BFF Service
    ↓
BFF Service → RAG Service (gRPC)
    ↓
RAG Service → Python RAG Core (HTTP)
    ↓
RAG Core:
    ├── Query 改写 (可选)
    ├── 向量检索 (ES KNN)
    ├── 全文检索 (ES BM25)
    ├── 混合检索重排序
    ├── 获取上下文片段
    └── 调用 LLM 生成回答
    ↓
流式响应返回
```

---

## 9. 依赖关系

### 9.1 服务依赖图

```
                    ┌─────────────┐
                    │   Nginx     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ BFF Service │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
   │  IAM    │      │  Agent    │      │  Model  │
   │ Service │      │ Service   │      │ Service │
   └────┬────┘      └─────┬─────┘      └────┬────┘
        │                 │                 │
        │           ┌─────▼─────┐           │
        │           │ Assistant │           │
        │           │ Service   │           │
        │           └───────────┘           │
        │                                   │
   ┌────▼───────────────────────────────────▼────┐
   │                                             │
   │  MySQL / TiDB / OceanBase    Redis         │
   │                                             │
   └─────────────────────────────────────────────┘

        ┌─────────────┐      ┌─────────────┐
        │ Knowledge   │      │    RAG      │
        │ Service     │◄────►│  Service    │
        └──────┬──────┘      └──────┬──────┘
               │                    │
               │            ┌───────▼───────┐
               │            │  Python RAG   │
               │            │  Core / ES    │
               │            └───────┬───────┘
               │                    │
        ┌──────▼──────┐      ┌─────▼──────┐
        │   MinIO     │      │Elasticsearch│
        │   Kafka     │      │  MongoDB    │
        └─────────────┘      └─────────────┘
```

### 9.2 外部依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0+ | 主数据库 |
| Redis | 6.0+ | 缓存、会话 |
| MinIO | Latest | 对象存储 |
| Kafka | 3.0+ | 消息队列 |
| Elasticsearch | 8.x | 向量+全文检索 |
| MongoDB | 5.0+ | 日志、反馈 |

---

## 10. 项目运行方式

### 10.1 环境要求

- **Go**: 1.24.0+
- **Node.js**: 14.20.0 (前端)
- **Python**: 3.12 (RAG/Callback)
- **Docker**: 20.10+ (推荐部署方式)
- **Docker Compose**: 2.0+

### 10.2 Docker 部署 (推荐)

#### 10.2.1 首次部署

```bash
# 1. 复制环境变量文件
cp .env.bak .env

# 2. 编辑 .env 文件，修改以下变量:
#    - WANWU_ARCH (amd64 / arm64)
#    - WANWU_EXTERNAL_IP (外部访问 IP)
#    - WANWU_BFF_JWT_SIGNING_KEY (JWT 签名密钥)

# 3. 创建 Docker 网络
docker network create wanwu-net

# 4. 启动服务 (amd64)
docker compose --env-file .env --env-file .env.image.amd64 up -d

# 4. 启动服务 (arm64)
docker compose --env-file .env --env-file .env.image.arm64 up -d
```

#### 10.2.2 访问系统

- **Web 界面**: http://localhost:8081
- **默认账号**: admin
- **默认密码**: Wanwu123456

#### 10.2.3 停止服务

```bash
# amd64
docker compose --env-file .env --env-file .env.image.amd64 down

# arm64
docker compose --env-file .env --env-file .env.image.arm64 down
```

### 10.3 源码开发模式

#### 10.3.1 启动基础设施

```bash
# 先按 Docker 部署方式启动所有基础设施 (MySQL, Redis, MinIO, Kafka, ES)
docker compose --env-file .env --env-file .env.image.amd64 up -d mysql redis minio kafka es
```

#### 10.3.2 编译并运行后端服务

```bash
# 以 BFF 服务为例

# 1. 停止 Docker 中的 BFF 服务
make -f Makefile.develop stop-bff

# 2. 编译可执行文件 (amd64)
make build-bff-amd64

# 3. 运行 BFF 服务
make -f Makefile.develop run-bff
```

#### 10.3.3 运行前端开发服务器

```bash
cd web

# 安装依赖
pnpm install

# 启动开发服务器
pnpm serve
```

### 10.4 数据库适配 (信创)

#### TiDB

```bash
# 1. 修改 .env: WANWU_DB_NAME=tidb

# 2. 启动 TiDB
docker compose --env-file .env --env-file .env.image.amd64 -f docker-compose.tidb.yaml up -d

# 3. 启动应用服务
docker compose --env-file .env --env-file .env.image.amd64 up -d
```

#### OceanBase

```bash
# 1. 修改 .env: WANWU_DB_NAME=oceanbase

# 2. 启动 OceanBase
docker compose --env-file .env --env-file .env.image.amd64 -f docker-compose.oceanbase.yaml up -d

# 3. 启动应用服务
docker compose --env-file .env --env-file .env.image.amd64 up -d
```

---

## 11. 配置说明

### 11.1 环境变量 (.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WANWU_VERSION` | 版本号 | v0.4.0 |
| `WANWU_ARCH` | 系统架构 | amd64 |
| `WANWU_EXTERNAL_IP` | 外部访问 IP | localhost |
| `WANWU_EXTERNAL_PORT` | 外部访问端口 | 8081 |
| `WANWU_DB_NAME` | 数据库类型 | mysql |
| `WANWU_MYSQL_PASSWORD` | MySQL 密码 | Wanwu123456 |
| `WANWU_REDIS_PASSWORD` | Redis 密码 | Wanwu123456 |
| `WANWU_MINIO_PASSWORD` | MinIO 密码 | Wanwu123456 |
| `WANWU_KAFKA_PASSWORD` | Kafka 密码 | Wanwu123456 |
| `WANWU_ELASTIC_PASSWORD` | ES 密码 | Wanwu123456 |
| `WANWU_BFF_JWT_SIGNING_KEY` | JWT 签名密钥 | (必填) |

### 11.2 服务端口

| 服务 | 端口 | 协议 |
|------|------|------|
| Nginx | 8081 | HTTP |
| BFF Service | 6668 | HTTP/gRPC |
| IAM Service | 8888 | gRPC |
| Model Service | 8989 | gRPC |
| MCP Service | 9898 | gRPC |
| Knowledge Service | 8889 | gRPC |
| RAG Service | 9640 | gRPC |
| Assistant Service | 8890 | gRPC |
| Agent Service | 8990 | gRPC |
| App Service | 9988 | gRPC |
| Operate Service | 9797 | gRPC |
| Callback Service | 8669 | HTTP |
| Workflow Service | 8998/8999 | HTTP |
| RAG Core | 5000 | HTTP |
| RAG ES Server | 15000 | HTTP |

---

## 12. Docker 部署

### 12.1 Docker 镜像构建

```bash
# 构建后端镜像
make docker-image-backend

# 构建前端镜像
make docker-image-frontend

# 构建 RAG 镜像
make docker-image-rag

# 构建 Callback 镜像
make docker-image-callback
```

### 12.2 Dockerfile 说明

| Dockerfile | 用途 |
|-----------|------|
| [Dockerfile.backend](file:///workspace/Dockerfile.backend) | Go 后端服务编译 |
| [Dockerfile.frontend](file:///workspace/Dockerfile.frontend) | Vue 前端构建 |
| [Dockerfile.rag](file:///workspace/Dockerfile.rag) | Python RAG 服务 |
| [Dockerfile.callback](file:///workspace/Dockerfile.callback) | Python Callback 服务 |
| [Dockerfile.callback-base](file:///workspace/Dockerfile.callback-base) | Callback 基础镜像 |

### 12.3 Docker Compose 服务清单

| 服务 | 镜像 | 说明 |
|------|------|------|
| mysql | MySQL 8.0 | 关系型数据库 |
| mysql-setup | MySQL 8.0 | 数据库初始化 (执行后退出) |
| redis | Redis 6.0 | 缓存服务 |
| minio | MinIO | 对象存储 |
| kafka | Kafka 3.0 | 消息队列 |
| es-setup | Elasticsearch 8.x | ES 证书初始化 (执行后退出) |
| es | Elasticsearch 8.x | 搜索引擎 |
| bff-service | wanwulite/wanwu-backend | BFF 网关 |
| iam-service | wanwulite/wanwu-backend | 身份认证 |
| model-service | wanwulite/wanwu-backend | 模型管理 |
| mcp-service | wanwulite/wanwu-backend | MCP 工具 |
| knowledge-service | wanwulite/wanwu-backend | 知识库 |
| rag-service | wanwulite/wanwu-backend | RAG 检索 |
| assistant-service | wanwulite/wanwu-backend | 助手服务 |
| agent-service | wanwulite/wanwu-backend | 智能体 |
| app-service | wanwulite/wanwu-backend | 应用管理 |
| operate-service | wanwulite/wanwu-backend | 运营管理 |
| callback | wanwulite/callback | 回调处理 |
| workflow | wanwulite/workflow | 工作流引擎 |
| rag | wanwulite/rag | Python RAG |
| nginx | wanwulite/wanwu-frontend | 前端 + 反向代理 |

---

## 附录

### A. 常用 Make 命令

```bash
# 构建服务 (以 bff 为例)
make build-bff-amd64
make build-bff-arm64

# 代码检查
make check

# 生成 gRPC 代码
make grpc-protoc

# 生成 Swagger 文档
make doc

# 初始化依赖
make init

# 国际化转换
make i18n-jsonl
```

### B. 前端开发命令

```bash
cd web

# 安装依赖
pnpm install

# 开发服务器
pnpm serve

# 生产构建
pnpm build

# 代码格式化
pnpm lint:fix
```

### C. 版本升级步骤

```bash
# 1. 停止服务
docker compose --env-file .env --env-file .env.image.amd64 down

# 2. 更新代码
git checkout main
git pull

# 3. 备份并更新环境变量
cp .env .env.old
cp .env.bak .env
# (根据需要修改 .env)

# 4. 重新启动
docker compose --env-file .env --env-file .env.image.amd64 up -d
```

---

> **文档版本**: v1.0  
> **适用项目版本**: Wanwu v0.4.0+  
> **最后更新**: 2026-05-14
