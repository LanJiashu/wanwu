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

## 13. 代码更新与重新部署指南

### 13.1 是否需要重新构建 Docker 镜像？

**取决于代码更新的范围和部署方式**：

| 场景 | 是否需要重建镜像 | 操作方式 |
|------|----------------|----------|
| **生产部署** (使用 `docker-compose.yaml` 拉取远程镜像) | **是** | 重新构建镜像并推送，或拉取新镜像 |
| **开发部署** (使用 `docker-compose-develop.yaml` 挂载本地二进制) | **否** | 重新编译二进制文件，重启容器即可 |
| **前端代码更新** | 视情况 | 开发模式直接刷新；生产模式需重新构建 |
| **Python RAG/Callback 代码更新** | **否** (开发模式) | 直接修改代码，重启容器 |
| **Protobuf 定义更新** | **是** | 重新生成代码，重新编译/构建 |

### 13.2 开发模式快速更新 (推荐开发时使用)

项目提供了 `docker-compose-develop.yaml`，**通过 Volume 挂载本地编译的二进制文件和源码**，实现代码更新后快速生效：

#### Go 后端服务更新

```bash
# 1. 停止目标服务 (以 bff-service 为例)
make -f Makefile.develop stop-bff

# 2. 重新编译二进制文件
make build-bff-amd64
# 输出: ./bin/amd64/bff-service

# 3. 重新启动服务 (docker-compose-develop.yaml 会自动挂载新的二进制)
make -f Makefile.develop run-bff
```

**关键机制**：`docker-compose-develop.yaml` 中使用 Volume 挂载本地二进制：

```yaml
bff-service:
  volumes:
    - ./bin/${WANWU_ARCH}/bff-service:/app/bin/bff-service  # 挂载本地编译的二进制
    - ./configs/microservice/bff-service/configs:/app/configs/microservice/bff-service/configs  # 挂载配置
```

#### Python RAG 服务更新

```bash
# 1. 停止 RAG 服务
make -f Makefile.develop stop-rag-wanwu

# 2. 直接修改 rag/ 目录下的 Python 代码

# 3. 重新启动服务 (代码通过 Volume 实时挂载)
make -f Makefile.develop run-rag-wanwu
```

**关键机制**：`docker-compose-develop.yaml` 中挂载整个源码目录：

```yaml
rag:
  volumes:
    - ./rag/rag_open_source:/model_extend  # 挂载整个 RAG 源码目录
```

#### Python Callback 服务更新

```bash
# 1. 停止 Callback 服务
make -f Makefile.develop stop-callback

# 2. 直接修改 callback/ 目录下的 Python 代码

# 3. 重新启动服务
make -f Makefile.develop run-callback
```

**关键机制**：`docker-compose-develop.yaml` 中挂载整个 callback 目录：

```yaml
callback:
  volumes:
    - ./callback:/callback  # 挂载整个 callback 源码目录
```

#### 前端更新

```bash
cd web

# 开发模式：热更新，保存即刷新
pnpm serve

# 生产模式：重新构建
pnpm build
# 然后将 dist/ 目录内容复制到 nginx 服务目录
```

### 13.3 生产模式更新 (使用预构建镜像)

如果使用 `docker-compose.yaml` (生产部署，拉取远程镜像)：

```bash
# 1. 停止所有服务
docker compose --env-file .env --env-file .env.image.amd64 down

# 2. 更新代码
git pull

# 3. 重新构建镜像
make docker-image-backend   # 构建后端镜像
make docker-image-frontend  # 构建前端镜像
make docker-image-rag       # 构建 RAG 镜像
make docker-image-callback  # 构建 Callback 镜像

# 4. 推送镜像到仓库 (如果需要)
docker push wanwulite/wanwu-backend:${WANWU_VERSION}
docker push wanwulite/wanwu-frontend:${WANWU_VERSION}
# ...

# 5. 重新启动
docker compose --env-file .env --env-file .env.image.amd64 up -d
```

### 13.4 数据库数据会丢失吗？

**不会丢失**。数据通过 Docker Volume 持久化存储，与容器生命周期分离：

#### 数据持久化机制

| 服务 | Volume 名称 | 挂载路径 | 数据内容 |
|------|------------|----------|----------|
| MySQL | `wanwu_mysql_data` | `/var/lib/mysql` | 所有业务数据 |
| Redis | `wanwu_redis_data` | `/data` | 缓存、会话 |
| MinIO | `wanwu_minio_data` | `/data` | 上传的文件、文档 |
| Kafka | `wanwu_kafka_data` | `/bitnami/kafka/data` | 消息队列数据 |
| Elasticsearch | `wanwu_es_data` | `/usr/share/elasticsearch/data` | 向量索引、全文索引 |
| ES 证书 | `wanwu_es_certs` | `/usr/share/elasticsearch/config/certs` | TLS 证书 |

#### 关键要点

1. **`docker compose down` 不会删除 Volume 数据**
   - 数据存储在 Docker 管理的 Volume 中，与容器分离
   - 只有执行 `docker compose down -v` 或 `docker volume rm` 才会删除

2. **代码更新只影响应用容器，不影响数据 Volume**
   ```bash
   # 安全：只停止容器，保留 Volume
   docker compose down
   
   # 危险：会删除 Volume 和数据！
   docker compose down -v
   ```

3. **开发模式下的日志和临时文件**
   ```yaml
   # docker-compose-develop.yaml 中的挂载
   volumes:
     - ${WANWU_PROJECT_DIR}/bff-service/log:/app/log  # 日志持久化到宿主机
     - ${WANWU_PROJECT_DIR}/bff-service/tmp:/app/tmp  # 临时文件
   ```

### 13.5 不同更新场景的操作清单

#### 场景 1：只修改 Go 业务代码

```bash
# 1. 编译更新的服务
make build-bff-amd64
make build-agent-amd64
# ...

# 2. 重启对应服务
make -f Makefile.develop stop-bff
make -f Makefile.develop run-bff
```

#### 场景 2：修改 Protobuf 定义

```bash
# 1. 更新 .proto 文件

# 2. 重新生成 Go 代码
make grpc-protoc

# 3. 重新编译所有依赖该 proto 的服务
make build-bff-amd64
make build-agent-amd64
make build-assistant-amd64
# ...

# 4. 重启服务
```

#### 场景 3：修改数据库模型 (GORM)

```bash
# 1. 更新 Go struct 定义

# 2. 编译服务
make build-iam-amd64
make build-knowledge-amd64
# ...

# 3. 执行数据库迁移 (如果有迁移脚本)
# 注意：项目使用 GORM AutoMigrate，启动时自动同步表结构

# 4. 重启服务
```

#### 场景 4：修改前端代码

```bash
cd web

# 开发模式：自动热更新
pnpm serve

# 生产模式：构建并部署
pnpm build
# 复制 dist/ 到 nginx 目录
```

#### 场景 5：修改 Python RAG 代码

```bash
# 1. 直接修改 rag/ 目录代码

# 2. 重启 RAG 服务
make -f Makefile.develop stop-rag-wanwu
make -f Makefile.develop run-rag-wanwu
```

### 13.6 数据备份建议 (重要)

虽然代码更新不会丢失数据，但建议定期备份：

```bash
# MySQL 备份
docker exec mysql-wanwu mysqldump -u root -p'Wanwu123456' --all-databases > backup_$(date +%Y%m%d).sql

# MinIO 备份
docker run --rm -v wanwu_minio_data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/minio_$(date +%Y%m%d).tar.gz -C /data .

# Elasticsearch 快照
# 使用 ES Snapshot API 创建索引快照
```

### 13.7 常见问题

**Q: 更新后服务启动失败怎么办？**

A: 检查以下几点：
1. 是否重新编译了二进制文件？
2. 配置文件是否有更新？对比 `.env.bak` 和 `.env`
3. 数据库连接是否正常？
4. 查看服务日志：`docker logs bff-service`

**Q: 更新后需要清理缓存吗？**

A: 视情况而定：
- 修改业务逻辑：无需清理缓存
- 修改权限/角色：可能需要清理 Redis 缓存
- 修改静态资源：清理浏览器缓存或 CDN 缓存

**Q: 可以只更新单个服务吗？**

A: 可以。微服务架构支持独立更新：
```bash
# 只更新 agent-service
make build-agent-amd64
make -f Makefile.develop stop-agent
make -f Makefile.develop run-agent
```

---

## 14. Docker Volume 详解

### 14.1 什么是 Docker Volume？

**Docker Volume** 是 Docker 提供的一种**数据持久化机制**，用于将容器内的数据存储到宿主机上，实现数据与容器生命周期的分离。

#### 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│  容器 (Container)              宿主机 (Host)                 │
│  ┌──────────────┐              ┌──────────────┐             │
│  │  应用代码     │              │              │             │
│  │  ├─ 二进制    │              │  Docker      │             │
│  │  ├─ 配置      │              │  Volume      │             │
│  │  └─ 运行时    │              │  存储区域     │             │
│  │              │              │              │             │
│  │  /var/lib/   │◄────────────►│ /var/lib/    │             │
│  │  mysql/data  │   Volume     │ docker/      │             │
│  │              │   映射       │ volumes/     │             │
│  └──────────────┘              └──────────────┘             │
│                                                              │
│  容器删除后：应用代码消失，但 Volume 数据保留在宿主机          │
└─────────────────────────────────────────────────────────────┘
```

#### Volume 的三种类型

| 类型 | 语法 | 用途 | 示例 |
|------|------|------|------|
| **命名 Volume** | `volume_name:/path` | Docker 管理，推荐用于数据持久化 | `wanwu_mysql_data:/var/lib/mysql` |
| **绑定挂载** | `/host/path:/container/path` | 宿主机路径直接挂载，开发常用 | `./bin/amd64/bff-service:/app/bin/bff-service` |
| **匿名 Volume** | `/path` (无名称) | 临时数据，容器删除后自动清理 | 较少使用 |

### 14.2 本项目中的 Volume 使用

#### 生产环境 (`docker-compose.yaml`)

```yaml
services:
  mysql:
    volumes:
      - wanwu_mysql_data:/var/lib/mysql  # 命名 Volume：MySQL 数据持久化

  redis:
    volumes:
      - wanwu_redis_data:/data           # 命名 Volume：Redis 数据持久化

  minio:
    volumes:
      - wanwu_minio_data:/data           # 命名 Volume：对象存储数据持久化

  es:
    volumes:
      - wanwu_es_data:/usr/share/elasticsearch/data   # ES 索引数据
      - wanwu_es_certs:/usr/share/elasticsearch/config/certs  # TLS 证书

# Volume 定义（在文件底部）
volumes:
  wanwu_mysql_data:    # Docker 自动创建和管理
  wanwu_redis_data:
  wanwu_minio_data:
  wanwu_es_data:
  wanwu_es_certs:
```

#### 开发环境 (`docker-compose-develop.yaml`)

```yaml
services:
  bff-service:
    volumes:
      # 绑定挂载：本地编译的二进制直接映射到容器
      - ./bin/${WANWU_ARCH}/bff-service:/app/bin/bff-service
      # 绑定挂载：本地配置文件映射到容器
      - ./configs/microservice/bff-service/configs:/app/configs/microservice/bff-service/configs

  rag:
    volumes:
      # 绑定挂载：整个 Python 源码目录映射到容器
      - ./rag/rag_open_source:/model_extend

  callback:
    volumes:
      # 绑定挂载：整个 callback 源码目录映射到容器
      - ./callback:/callback
```

### 14.3 Volume 数据存储位置

#### 命名 Volume 的宿主机路径

```bash
# Docker 管理的 Volume 默认存储在
/var/lib/docker/volumes/

# 例如 MySQL Volume 的实际路径
/var/lib/docker/volumes/wanwu_mysql_data/_data/

# 查看所有 Volume
docker volume ls

# 查看 Volume 详情
docker volume inspect wanwu_mysql_data
```

#### 绑定挂载的宿主机路径

```bash
# 绑定挂载直接使用宿主机路径
# 例如：./bin/amd64/bff-service 映射到容器内的 /app/bin/bff-service
# 宿主机的相对路径就是项目目录下的 bin/amd64/bff-service
```

### 14.4 Volume 生命周期管理

#### 查看 Volume

```bash
# 列出所有 Volume
docker volume ls

# 输出示例：
# DRIVER    VOLUME NAME
# local     wanwu_mysql_data
# local     wanwu_redis_data
# local     wanwu_minio_data
# local     wanwu_es_data
```

#### 创建 Volume

```bash
# 手动创建命名 Volume
docker volume create my_volume
```

#### 删除 Volume

```bash
# 删除指定 Volume（谨慎操作！）
docker volume rm wanwu_mysql_data

# 删除所有未使用的 Volume
docker volume prune

# ⚠️ 危险：docker compose down -v 会删除所有关联 Volume
docker compose down -v
```

#### 备份 Volume

```bash
# 方法 1：使用临时容器打包备份
docker run --rm \
  -v wanwu_mysql_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/mysql_$(date +%Y%m%d).tar.gz -C /data .

# 方法 2：针对 MySQL 使用 mysqldump
docker exec mysql-wanwu \
  mysqldump -u root -p'Wanwu123456' --all-databases \
  > backup_$(date +%Y%m%d).sql
```

#### 恢复 Volume

```bash
# 从备份恢复
docker run --rm \
  -v wanwu_mysql_data:/data \
  -v $(pwd)/backup:/backup \
  alpine sh -c "cd /data && tar xzf /backup/mysql_20260115.tar.gz"
```

### 14.5 为什么代码更新不会丢失数据？

```
代码更新流程：

1. 停止容器
   docker compose down
   │
   ├── 容器 bff-service 停止并删除 ❌
   ├── 容器 mysql 停止并删除 ❌
   ├── Volume wanwu_mysql_data 保留 ✅
   └── Volume wanwu_redis_data 保留 ✅

2. 更新代码 / 重新编译
   git pull
   make build-bff-amd64
   │
   └── 只影响宿主机上的二进制文件

3. 启动新容器
   docker compose up -d
   │
   ├── 创建新的 bff-service 容器（包含新代码）✅
   ├── 创建新的 mysql 容器 ✅
   ├── 重新挂载 Volume wanwu_mysql_data ✅
   └── 数据完整保留！
```

### 14.6 Volume vs 容器文件系统

| 特性 | 容器内文件 | Volume 挂载的文件 |
|------|-----------|------------------|
| 生命周期 | 随容器删除而丢失 | 独立于容器，持久保留 |
| 性能 | 使用联合文件系统，有开销 | 直接访问宿主机文件系统，性能更好 |
| 共享 | 容器间隔离 | 可被多个容器共享挂载 |
| 备份 | 困难 | 可直接备份宿主机目录 |
| 适用场景 | 应用代码、临时文件 | 数据库数据、用户上传文件、日志 |

### 14.7 常见问题

**Q: Volume 数据会占用多少磁盘空间？**

A: 取决于实际数据量。可以通过以下命令查看：
```bash
# 查看 Volume 磁盘使用
docker system df -v

# 查看特定目录大小
du -sh /var/lib/docker/volumes/wanwu_mysql_data/_data
```

**Q: 如何迁移数据到另一台机器？**

A:
```bash
# 1. 在原机器备份 Volume
docker run --rm -v wanwu_mysql_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/mysql_data.tar.gz -C /data .

# 2. 传输备份文件到新机器
scp mysql_data.tar.gz new-server:/backup/

# 3. 在新机器恢复
docker volume create wanwu_mysql_data
docker run --rm -v wanwu_mysql_data:/data -v /backup:/backup alpine \
  tar xzf /backup/mysql_data.tar.gz -C /data
```

**Q: 开发模式下修改 Volume 挂载的源码需要重启容器吗？**

A:
- **Go 二进制**：需要重新编译并重启容器（因为二进制文件被替换后需要重新加载）
- **Python 源码**：通常不需要重启（解释型语言，下次请求会读取新代码）
- **前端代码**：开发模式热更新，生产模式需要重新构建

**Q: 容器崩溃会导致 Volume 数据损坏吗？**

A: 一般不会。Volume 数据存储在宿主机文件系统上，容器崩溃不会影响宿主机上的数据。但如果在崩溃瞬间有未完成的写操作，可能会导致数据不一致，建议使用数据库的事务机制来保证数据完整性。

---

> **文档版本**: v1.2  
> **适用项目版本**: Wanwu v0.4.0+  
> **最后更新**: 2026-05-14
