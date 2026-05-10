# 元景万悟智能体平台 — Code Wiki

> 项目仓库：[github.com/UnicomAI/wanwu](https://github.com/UnicomAI/wanwu)
> License：Apache 2.0
> Go 版本：≥ 1.24.0 | Node 版本：14.20.0

---

## 一、项目概述

**元景万悟智能体平台（Wanwu AI Agent Platform）** 是一款面向企业级场景的一站式智能体开发平台，由联通 AI 团队开源。平台整合大语言模型、业务流程自动化、RAG 检索增强生成、知识图谱等前沿技术，提供覆盖模型全生命周期管理、MCP 协议、联网检索、智能体开发、企业知识库建设、复杂工作流编排的完整功能体系。

核心能力包括：

- **模型纳管**：统一接入数百种专有/开源大模型（GPT、Claude、Llama、DeepSeek、Qwen 等）
- **高精度 RAG**：文档解析→向量化→检索→精排全流程，支持 GraphRAG 知识图谱
- **智能体开发**：基于 Function Calling 的 Agent 框架，支持工具扩展与多轮对话
- **可视化工作流**：低代码拖拽画布，支持条件分支、API、大模型、知识库、代码、MCP 等节点
- **MCP 协议**：标准化接口连接外部工具，内置 100+ 行业 MCP 接口
- **安全护栏**：敏感词表、内容审核、权限控制
- **多租户架构**：组织/角色/用户三级权限体系，数据隔离

---

## 二、整体架构

### 2.1 架构全景图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                             │
│                   Vue2 + Element UI + AntV X6                │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP / SSE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Nginx (反向代理)                          │
│              端口: 8081 → 路由分发至 BFF/前端静态资源            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BFF-Service (聚合层)                        │
│            Go + Gin | 端口: 6668 | RESTful API               │
│    路由分发 · 业务聚合 · JWT认证 · 权限校验 · 文件上传           │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┘
       │      │      │      │      │      │      │
       │gRPC  │gRPC  │gRPC  │gRPC  │gRPC  │gRPC  │HTTP
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│IAM-Service││Model-Svc ││Knowledge ││RAG-Service││Assistant ││Agent-Svc ││MCP-Service│
│身份认证   ││模型管理   ││知识库管理 ││检索增强   ││助手服务   ││智能体    ││MCP协议   │
│:8888     ││:8989     ││:8889     ││:9640     ││:8890     ││:8990     ││:9898     │
└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
     │           │           │           │           │           │           │
     ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                               │
│  MySQL/TiDB/OceanBase │ Redis │ MinIO │ Kafka │ Elasticsearch│
└─────────────────────────────────────────────────────────────┘

额外独立服务：
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Callback     │  │ RAG (Python) │  │ Workflow     │
│ 文档解析回调  │  │ 向量化/检索   │  │ 工作流引擎    │
│ :8669       │  │ :8613/:8681  │  │ :8998/:8999  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 技术栈总览

| 层次 | 技术选型 |
|------|---------|
| **前端** | Vue 2.6 + Vue Router 3 + Vuex 3 + Element UI 2.15 + AntV X6/G6 + Monaco Editor + WangEditor |
| **BFF 层** | Go 1.24 + Gin + gRPC Client + JWT + Swagger |
| **微服务层** | Go 1.24 + gRPC Server + GORM + Viper(配置) + Zap(日志) |
| **RAG 引擎** | Python 3 + Flask + Gunicorn + LangChain + Elasticsearch + Milvus |
| **Callback 服务** | Python 3 + Flask + Gunicorn + MinIO SDK |
| **工作流引擎** | Go (独立项目 wanwu-workflow) |
| **数据库** | MySQL 8.0 / TiDB v8.5 / OceanBase 4.3 |
| **缓存** | Redis 7.0 |
| **对象存储** | MinIO |
| **消息队列** | Kafka 3.9 (KRaft 模式) |
| **搜索引擎** | Elasticsearch 8.12 (SSL + 安全认证) |
| **容器化** | Docker Compose |
| **前端构建** | Vue CLI 5 + Webpack + Sass |
| **代码规范** | Prettier + Husky + lint-staged |

---

## 三、微服务架构详解

### 3.1 服务清单

| 服务名 | 端口 | 语言 | 职责 | 关键依赖 |
|--------|------|------|------|---------|
| **bff-service** | 6668 | Go | BFF 聚合层，前端唯一入口，路由分发、业务逻辑聚合、JWT 认证、权限校验 | MinIO, Redis, 各 gRPC 服务 |
| **iam-service** | 8888 | Go | 身份认证与用户管理，登录/注册/密码重置/OAuth | MySQL, Redis, SMTP |
| **model-service** | 8989 | Go | 模型生命周期管理，模型注册/参数配置/体验对话 | MySQL, Redis |
| **knowledge-service** | 8889 | Go | 知识库核心管理，文档上传/解析/分段/导入任务调度 | MySQL, Redis, MinIO, Kafka |
| **rag-service** | 9640 | Go | RAG 检索增强生成，消息构建/向量搜索调度 | MySQL, Redis |
| **assistant-service** | 8890 | Go | 智能助手服务，助手创建/对话管理/会话存储 | MySQL, Redis, MinIO, ES |
| **agent-service** | 8990 | Go | 智能体执行引擎，单Agent/多Agent编排/工具调用/MCP | MinIO |
| **mcp-service** | 9898 | Go | MCP 协议管理，MCP Server 注册/工具管理 | MySQL, Redis |
| **operate-service** | 9797 | Go | 运营统计服务，平台使用数据统计 | MySQL |
| **app-service** | 9988 | Go | 应用管理服务，应用空间/版本管理/API Key | MySQL, Redis, MinIO |
| **callback** | 8669 | Python | 文档解析回调，Prompt 构造/LLM 工具调用/文件生成 | Redis, MinIO |
| **rag (Python)** | 8613/8681 | Python | RAG 核心引擎，文档向量化/分段/检索/ES 索引/知识图谱 | MinIO, Kafka, ES |
| **workflow** | 8998/8999 | Go | 工作流引擎，节点编排/执行/调试 | MySQL, Redis, MinIO |
| **nginx** | 8081 | Nginx | 反向代理 + 前端静态资源服务 | — |

### 3.2 服务间通信方式

| 通信方式 | 使用场景 | 协议 |
|---------|---------|------|
| **gRPC** | BFF → 各后端微服务（IAM/Model/Knowledge/RAG/Assistant/Agent/MCP/Operate/App） | Protobuf over HTTP/2 |
| **HTTP REST** | 前端 → BFF；BFF → Callback/RAG/Workflow；Workflow → BFF/Agent/Callback | JSON over HTTP |
| **SSE** | 流式对话输出（Agent/RAG/Workflow 的流式响应） | Server-Sent Events |
| **Kafka** | 文档导入任务异步处理（Knowledge-Service → RAG Python） | SASL_PLAINTEXT |
| **Redis** | 缓存、会话管理、分布式锁 | Redis Protocol |

### 3.3 Protobuf 接口定义

所有 gRPC 接口定义在 [proto/](file:///workspace/proto) 目录下：

| Proto 文件 | 服务 |
|-----------|------|
| [iam-service.proto](file:///workspace/proto/iam-service/iam-service.proto) | 用户/组织/角色管理 |
| [model-service.proto](file:///workspace/proto/model-service/model-service.proto) | 模型 CRUD/参数配置 |
| [knowledgebase-service.proto](file:///workspace/proto/knowledgebase-service/knowledgebase-service.proto) | 知识库管理 |
| [knowledgebase-doc-service.proto](file:///workspace/proto/knowledgebase-doc-service/knowledgebase-doc-service.proto) | 文档管理 |
| [knowledgebase-splitter-service.proto](file:///workspace/proto/knowledgebase-splitter-service/knowledgebase-splitter-service.proto) | 文档分段 |
| [knowledgebase-qa-service.proto](file:///workspace/proto/knowledgebase-qa-service/knowledgebase-qa-service.proto) | QA 问答对管理 |
| [knowledgebase-tag-service.proto](file:///workspace/proto/knowledgebase-tag-service/knowledgebase-tag-service.proto) | 标签管理 |
| [knowledgebase-keywords-service.proto](file:///workspace/proto/knowledgebase-keywords-service/knowledgebase-keywords-service.proto) | 关键词管理 |
| [knowledgebase-permission-service.proto](file:///workspace/proto/knowledgebase-permission-service/knowledgebase-permission-service.proto) | 知识库权限 |
| [knowledgebase-report-service.proto](file:///workspace/proto/knowledgebase-report-service/knowledgebase-report-service.proto) | 知识图谱社区报告 |
| [rag-service.proto](file:///workspace/proto/rag-service/rag-service.proto) | RAG 检索增强生成 |
| [assistant-service.proto](file:///workspace/proto/assistant-service/assistant-service.proto) | 助手管理 |
| [app-service.proto](file:///workspace/proto/app-service/app-service.proto) | 应用管理 |
| [mcp-service.proto](file:///workspace/proto/mcp-service/mcp-service.proto) | MCP 协议管理 |
| [safety-service.proto](file:///workspace/proto/safety-service/safety-service.proto) | 安全护栏 |
| [perm-service.proto](file:///workspace/proto/perm-service/perm-service.proto) | 权限控制 |
| [operate-service.proto](file:///workspace/proto/operate-service/operate-service.proto) | 运营统计 |
| [common.proto](file:///workspace/proto/common/common.proto) | 公共消息定义 |
| [err-code.proto](file:///workspace/proto/err-code/err-code.proto) | 错误码定义 |

生成的 Go 代码位于 [api/proto/](file:///workspace/api/proto) 目录。

---

## 四、核心模块详解

### 4.1 BFF-Service（聚合层）

**路径**：[internal/bff-service/](file:///workspace/internal/bff-service)

BFF 是前端唯一入口，承担路由分发、业务聚合、认证鉴权等职责。

#### 关键服务模块

| 模块文件 | 功能 |
|---------|------|
| [login.go](file:///workspace/internal/bff-service/service/login.go) | 登录认证、JWT Token 生成 |
| [oauth.go](file:///workspace/internal/bff-service/service/oauth.go) | OAuth 单点登录 |
| [perm.go](file:///workspace/internal/bff-service/service/perm.go) | 权限管理基础逻辑 |
| [permission_org.go](file:///workspace/internal/bff-service/service/permission_org.go) | 组织维度权限控制 |
| [permission_role.go](file:///workspace/internal/bff-service/service/permission_role.go) | 角色维度权限控制 |
| [permission_user.go](file:///workspace/internal/bff-service/service/permission_user.go) | 用户维度权限校验 |
| [model.go](file:///workspace/internal/bff-service/service/model.go) | 模型管理（注册/获取/参数配置） |
| [model_chat_completions.go](file:///workspace/internal/bff-service/service/model_chat_completions.go) | 模型对话补全 |
| [knowledge.go](file:///workspace/internal/bff-service/service/knowledge.go) | 知识库管理 |
| [knowledge_doc.go](file:///workspace/internal/bff-service/service/knowledge_doc.go) | 知识库文档管理 |
| [rag.go](file:///workspace/internal/bff-service/service/rag.go) | RAG 检索功能 |
| [rag_chat.go](file:///workspace/internal/bff-service/service/rag_chat.go) | RAG 对话功能 |
| [assistant.go](file:///workspace/internal/bff-service/service/assistant.go) | 智能助手管理 |
| [assistant_chat.go](file:///workspace/internal/bff-service/service/assistant_chat.go) | 助手对话 |
| [workflow.go](file:///workspace/internal/bff-service/service/workflow.go) | 工作流管理 |
| [chatflow.go](file:///workspace/internal/bff-service/service/chatflow.go) | 聊天流管理 |
| [mcp.go](file:///workspace/internal/bff-service/service/mcp.go) | MCP 协议管理 |
| [safety.go](file:///workspace/internal/bff-service/service/safety.go) | 安全护栏 |
| [sensitive_check.go](file:///workspace/internal/bff-service/service/sensitive_check.go) | 敏感词检查 |
| [agent-skills.go](file:///workspace/internal/bff-service/service/agent-skills.go) | Agent 技能管理 |
| [tool.go](file:///workspace/internal/bff-service/service/tool.go) | 工具管理 |
| [file_upload.go](file:///workspace/internal/bff-service/service/file_upload.go) | 文件上传 |

#### 配置

- [config.go](file:///workspace/internal/bff-service/config/config.go)：BFF 服务配置（端口、中间件连接、JWT 密钥等）
- [const.go](file:///workspace/internal/bff-service/config/const.go)：常量定义
- [workflow.go](file:///workspace/internal/bff-service/config/workflow.go)：工作流模板配置
- [skill.go](file:///workspace/internal/bff-service/config/skill.go)：技能模板配置

### 4.2 Agent-Service（智能体引擎）

**路径**：[internal/agent-service/](file:///workspace/internal/agent-service)

#### 核心组件

| 组件 | 路径 | 功能 |
|------|------|------|
| 单 Agent | [local-agent/chat_agent.go](file:///workspace/internal/agent-service/service/local-agent/chat_agent.go) | 单智能体对话执行 |
| 视觉 Agent | [local-agent/vision_chat_agent.go](file:///workspace/internal/agent-service/service/local-agent/vision_chat_agent.go) | 多模态视觉对话 |
| 多 Agent | [multi_agent.go](file:///workspace/internal/agent-service/service/multi_agent.go) | 多智能体协同编排 |
| 工具服务 | [agent_tool_service.go](file:///workspace/internal/agent-service/service/agent_tool_service.go) | Agent 工具注册与调用 |
| MCP 服务 | [mcp_service.go](file:///workspace/internal/agent-service/service/mcp_service.go) | MCP 协议调用 |
| 模型服务 | [model_service.go](file:///workspace/internal/agent-service/service/model_service.go) | 模型推理调用 |
| 插件服务 | [plugin_service.go](file:///workspace/internal/agent-service/service/plugin_service.go) | 插件动态加载 |
| 消息流 | [agent-message-flow/](file:///workspace/internal/agent-service/service/agent-message-flow) | 消息流处理工厂 |
| 消息处理 | [agent-message-processor/](file:///workspace/internal/agent-service/service/agent-message-processor) | Agent 消息处理与结果加工 |
| 预处理 | [agent-preprocessor/](file:///workspace/internal/agent-service/service/agent-preprocessor) | Agent 请求预处理 |

#### Agent 执行流程

```
用户请求 → BFF → Agent-Service
  → 预处理(agent_preprocessor)
  → 参数构建(agent_params_service)
  → 模型调用(model_service) + 工具调用(agent_tool_service/mcp_service)
  → 消息流处理(agent_message_flow)
  → 结果加工(agent_result_processor)
  → SSE 流式返回
```

### 4.3 Knowledge-Service（知识库管理）

**路径**：[internal/knowledge-service/](file:///workspace/internal/knowledge-service)

#### 核心服务

| 服务 | 功能 |
|------|------|
| [rag_knowledge_service.go](file:///workspace/internal/knowledge-service/service/rag_knowledge_service.go) | 知识库 CRUD、权限控制 |
| [rag_doc_service.go](file:///workspace/internal/knowledge-service/service/rag_doc_service.go) | 文档上传、存储管理 |
| [rag_doc_segment_service.go](file:///workspace/internal/knowledge-service/service/rag_doc_segment_service.go) | 文档段落切分、特征提取 |
| [rag_keyword_service.go](file:///workspace/internal/knowledge-service/service/rag_keyword_service.go) | 关键词管理 |
| [rag_qa_service.go](file:///workspace/internal/knowledge-service/service/rag_qa_service.go) | QA 问答对管理 |
| [rag_report_service.go](file:///workspace/internal/knowledge-service/service/rag_report_service.go) | 知识图谱社区报告 |
| [dify_knowledge_service.go](file:///workspace/internal/knowledge-service/service/dify_knowledge_service.go) | Dify 外部知识库兼容 |

#### 异步任务

| 任务 | 功能 |
|------|------|
| [doc_import_task_service.go](file:///workspace/internal/knowledge-service/task/doc_import_task_service.go) | 文档导入全流程调度 |
| [doc_re_import_task_service.go](file:///workspace/internal/knowledge-service/task/doc_re_import_task_service.go) | 文档重新导入 |
| [doc_segment_import_task_service.go](file:///workspace/internal/knowledge-service/task/doc_segment_import_task_service.go) | 分段导入 |
| [doc_delete_task_service.go](file:///workspace/internal/knowledge-service/task/doc_delete_task_service.go) | 文档删除 |
| [knowledge_qa_import_task_service.go](file:///workspace/internal/knowledge-service/task/knowledge_qa_import_task_service.go) | QA 导入 |
| [knowledge_report_task_service.go](file:///workspace/internal/knowledge-service/task/knowledge_report_task_service.go) | 知识图谱报告生成 |

#### 文档导入流程

```
用户上传文档 → BFF → Knowledge-Service
  → 文档存储到 MinIO
  → 创建导入任务(doc_import_task)
  → 发送 Kafka 消息
  → RAG Python 消费消息
    → 文档解析(PDF/Word/Excel/PPT等)
    → 文档分段(通用/父子/自适应切分)
    → 向量化(Embedding)
    → 存入 Elasticsearch
  → 回调 BFF 更新文档状态
```

### 4.4 RAG-Service（检索增强生成）

**路径**：[internal/rag-service/](file:///workspace/internal/rag-service)

| 组件 | 功能 |
|------|------|
| [rag_message_service.go](file:///workspace/internal/rag-service/service/message-builder/rag_message_service.go) | RAG 消息上下文构建（提问+历史+检索片段整合） |
| [knowledge_start_builder.go](file:///workspace/internal/rag-service/service/message-builder/knowledge_start_builder.go) | 知识库启动构建器 |

#### RAG Python 引擎

**路径**：[rag/rag_open_source/](file:///workspace/rag/rag_open_source)

| 模块 | 路径 | 功能 |
|------|------|------|
| 文档加载器 | [rag_core/chains/](file:///workspace/rag/rag_open_source/rag_core/chains) | PDF/Word/Excel/PPT/HTML/Markdown/图片等格式解析 |
| 文本切分 | [rag_core/textsplitter/](file:///workspace/rag/rag_open_source/rag_core/textsplitter) | 中文切分/阿里切分 |
| QA 检索 | [rag_core/qa/](file:///workspace/rag/rag_open_source/rag_core/qa) | 向量检索/语义搜索 |
| 知识图谱 | [rag_core/graph/](file:///workspace/rag/rag_open_source/rag_core/graph) | GraphRAG 图谱构建与检索 |
| ES 服务 | [rag_es_server_unify/](file:///workspace/rag/rag_open_source/rag_es_server_unify) | Elasticsearch 统一检索服务 |
| URL 解析 | [rag_core/url_parser/](file:///workspace/rag/rag_open_source/rag_core/url_parser) | 网页资源抓取与解析 |
| 工具集 | [rag_core/utils/](file:///workspace/rag/rag_open_source/rag_core/utils) | ES/Milvus/MinIO/Redis/Kafka/OCR/ASR 等工具 |

#### RAG 完整流程

```
1. 文档导入阶段：
   文档上传 → MinIO 存储 → Kafka 消息 → RAG Python 消费
   → 文档解析(OCR/MinerU) → 文本切分 → Embedding 向量化
   → 存入 Elasticsearch + Milvus → 回调更新状态

2. 检索问答阶段：
   用户提问 → RAG-Service(Go) → 消息构建
   → 调用 RAG Python 检索接口
     → 向量检索 + 全文检索 + 混合检索
     → Rerank 精排
   → 检索结果 + 历史消息 → LLM 生成回答
   → SSE 流式返回
```

### 4.5 Model-Service（模型管理）

**路径**：[internal/model-service/](file:///workspace/internal/model-service)

管理平台接入的所有 AI 模型，包括 LLM、Embedding、Rerank、ASR、OCR、PDF Parser 等。

#### 支持的模型提供商

| 提供商 | 路径 | 支持的模型类型 |
|--------|------|--------------|
| **OpenAI Compatible** | [mp-openai-compatible/](file:///workspace/pkg/model-provider/mp-openai-compatible) | LLM, Text Embedding, Text Rerank |
| **联通元景** | [mp-yuanjing/](file:///workspace/pkg/model-provider/mp-yuanjing) | LLM, Text Embedding, Text Rerank, Multimodal Rerank, ASR, OCR, PDF Parser, GUI, Text2Image |
| **DeepSeek** | [mp-deepseek/](file:///workspace/pkg/model-provider/mp-deepseek) | LLM |
| **通义千问** | [mp-qwen/](file:///workspace/pkg/model-provider/mp-qwen) | LLM, Text Embedding, Text Rerank, ASR |
| **百度千帆** | [mp-qianfan/](file:///workspace/pkg/model-provider/mp-qianfan) | LLM, Text Embedding, Text Rerank |
| **火山引擎** | [mp-huoshan/](file:///workspace/pkg/model-provider/mp-huoshan) | LLM, Text Embedding |
| **Ollama** | [mp-ollama/](file:///workspace/pkg/model-provider/mp-ollama) | LLM, Text Embedding |
| **Jina** | [mp-jina/](file:///workspace/pkg/model-provider/mp-jina) | Text Embedding, Text Rerank, Multimodal Embedding, Multimodal Rerank |
| **Infini** | [mp-infini/](file:///workspace/pkg/model-provider/mp-infini) | LLM, Text Embedding, Text Rerank |

#### 模型类型

| 类型 | 接口文件 |
|------|---------|
| LLM 对话 | [mp-common-llm.go](file:///workspace/pkg/model-provider/mp-common/mp-common-llm.go) |
| Text Embedding | [mp-common-text-embedding.go](file:///workspace/pkg/model-provider/mp-common/mp-common-text-embedding.go) |
| Text Rerank | [mp-common-text-rerank.go](file:///workspace/pkg/model-provider/mp-common/mp-common-text-rerank.go) |
| Multimodal Embedding | [mp-common-multimodal-embedding.go](file:///workspace/pkg/model-provider/mp-common/mp-common-multimodal-embedding.go) |
| Multimodal Rerank | [mp-common-multimodal-rerank.go](file:///workspace/pkg/model-provider/mp-common/mp-common-multimodal-rerank.go) |
| ASR 语音识别 | [mp-common-asr.go](file:///workspace/pkg/model-provider/mp-common/mp-common-asr.go) |
| OCR 文字识别 | [mp-common-ocr.go](file:///workspace/pkg/model-provider/mp-common/mp-common-ocr.go) |
| PDF Parser | [mp-common-pdf-parser.go](file:///workspace/pkg/model-provider/mp-common/mp-common-pdf-parser.go) |
| GUI | [mp-common-gui.go](file:///workspace/pkg/model-provider/mp-common/mp-common-gui.go) |
| Text2Image | [mp-common-text2image.go](file:///workspace/pkg/model-provider/mp-common/mp-common-text2image.go) |

### 4.6 IAM-Service（身份认证）

**路径**：[internal/iam-service/](file:///workspace/internal/iam-service)

- 用户注册/登录/密码重置
- 组织管理
- 角色管理
- OAuth 单点登录（BFF 层通过 RSA 密钥对处理）
- SMTP 邮件服务集成

### 4.7 MCP-Service（MCP 协议管理）

**路径**：[internal/mcp-service/](file:///workspace/internal/mcp-service)

- MCP Server 注册与管理
- MCP 工具定义与发现
- MCP 协议转译（OpenAPI → MCP Schema）
- 自定义 MCP Server 创建

### 4.8 Safety & Permission（安全与权限）

#### 安全护栏

- [safety-service.proto](file:///workspace/proto/safety-service/safety-service.proto)：安全检查 gRPC 接口
- [sensitive_check.go](file:///workspace/internal/bff-service/service/sensitive_check.go)：敏感词检测与过滤
- 安全护栏功能：用户创建敏感词表，控制模型输入输出安全性

#### 权限体系

- [perm-service.proto](file:///workspace/proto/perm-service/perm-service.proto)：权限控制 gRPC 接口
- 三级权限模型：**组织 → 角色 → 用户**
- 前端路由级权限控制（[router/index.js](file:///workspace/web/src/router/index.js) 中的 `meta.perm`）
- 基于角色的访问控制（RBAC），使用 Casbin 实现

### 4.9 Callback 服务

**路径**：[callback/](file:///workspace/callback)

Python Flask 服务，负责文档解析回调与辅助功能。

| 路由 | 功能 |
|------|------|
| [doc.py](file:///workspace/callback/callback/routes/doc.py) | 文档解析路由 |
| [minio.py](file:///workspace/callback/callback/routes/minio.py) | MinIO 文件操作 |
| [ali_multi_modal.py](file:///workspace/callback/callback/routes/ali_multi_modal.py) | 阿里多模态调用 |
| [bocha.py](file:///workspace/callback/callback/routes/bocha.py) | 博查搜索 |
| [tavily_news.py](file:///workspace/callback/callback/routes/tavily_news.py) | Tavily 新闻搜索 |
| [hello.py](file:///workspace/callback/callback/routes/hello.py) | 健康检查 |

工具层：
- [llm_tools.py](file:///workspace/callback/utils/llm_tools.py)：LLM 工具调用辅助
- [build_prompt.py](file:///workspace/callback/utils/build_prompt.py)：Prompt 构造
- [tokenizers.py](file:///workspace/callback/utils/tokenizers.py)：Token 计数

---

## 五、前端架构

### 5.1 技术栈

- **框架**：Vue 2.6 + Vue Router 3 (history mode) + Vuex 3
- **UI 库**：Element UI 2.15
- **图表**：ECharts 5.4 + AntV G6/X6
- **编辑器**：Monaco Editor（代码编辑）+ WangEditor（富文本）
- **Markdown**：markdown-it + marked + highlight.js + KaTeX
- **HTTP**：Axios
- **国际化**：vue-i18n（中文/英文）
- **微前端**：qiankun（可选）
- **SSE**：@microsoft/fetch-event-source

### 5.2 目录结构

```
web/src/
├── api/          # API 接口层（agent/knowledge/rag/model/safety/workflow/mcp 等）
├── components/   # 公共组件（知识库选择/模型选择/文件上传/分页/Markdown 渲染等）
├── lang/         # 国际化资源（zh/en）
├── mixins/       # 混入（通用方法/SSE/分块上传/Markdown 渲染）
├── router/       # 路由配置（权限过滤/动态路由）
├── sse/          # SSE 客户端封装
├── store/        # Vuex 状态管理
├── style/        # 全局样式
├── utils/        # 工具函数（HTTP 请求/加密/配置/流处理）
├── views/        # 页面视图
├── App.vue       # 根组件
└── main.js       # 入口文件
```

### 5.3 核心页面模块

| 路由 | 页面 | 权限 |
|------|------|------|
| `/modelAccess` | 模型管理 | MODEL_MANAGE |
| `/knowledge` | 知识库管理 | KNOWLEDGE |
| `/rag/test` | 文本问答 | RAG |
| `/agent/test` | 智能体 | AGENT |
| `/workflow` | 工作流编排 | WORKFLOW |
| `/safety` | 安全护栏 | SAFETY |
| `/mcp` | MCP 广场 | MCP |
| `/mcpService` | MCP 服务管理 | MCP_SERVICE |
| `/tool` | 工具管理 | TOOL |
| `/prompt` | 提示词管理 | PROMPT |
| `/explore` | 应用广场 | EXPLORE |
| `/permission` | 权限管理 | PERMISSION |
| `/openApiKey` | API Key 管理 | API_KEY_MANAGE |
| `/skill` | Skills | SKILL |
| `/statistics` | 统计 | STATISTIC |
| `/oauth` | OAuth 配置 | OAUTH |

### 5.4 前端请求流程

```
组件 → api/*.js → utils/request.js（Axios 封装，自动添加 JWT Header）
  → Nginx(:8081) → BFF-Service(:6668) → 各微服务
```

---

## 六、公共包（pkg/）

| 包 | 路径 | 功能 |
|---|------|------|
| **model-provider** | [pkg/model-provider/](file:///workspace/pkg/model-provider) | 模型提供商抽象层，统一 LLM/Embedding/Rerank 等调用接口 |
| **minio** | [pkg/minio/](file:///workspace/pkg/minio) | MinIO 对象存储客户端封装 |
| **redis** | [pkg/redis/](file:///workspace/pkg/redis) | Redis 客户端封装 |
| **db** | [pkg/db/](file:///workspace/pkg/db) | 数据库客户端封装（GORM，支持 MySQL/TiDB/OceanBase/Postgres/SQLServer） |
| **jwt-util** | [pkg/jwt-util/](file:///workspace/pkg/jwt-util) | JWT 工具（Token 生成与验证） |
| **i18n** | [pkg/i18n/](file:///workspace/pkg/i18n) | 后端国际化（JSONL/XLSX 加载） |
| **es** | [pkg/es/](file:///workspace/pkg/es) | Elasticsearch 客户端封装 |
| **sse-util** | [pkg/sse-util/](file:///workspace/pkg/sse-util) | SSE 服务端推送工具 |
| **http-client** | [pkg/http-client/](file:///workspace/pkg/http-client) | HTTP 客户端封装 |
| **openapi3-util** | [pkg/openapi3-util/](file:///workspace/pkg/openapi3-util) | OpenAPI 3.0 解析与 MCP/Schema 转换 |
| **gin-util** | [pkg/gin-util/](file:///workspace/pkg/gin-util) | Gin 框架工具（路由/中间件） |
| **grpc-util** | [pkg/grpc-util/](file:///workspace/pkg/grpc-util) | gRPC 工具（状态码转换） |
| **safe-go-util** | [pkg/safe-go-util/](file:///workspace/pkg/safe-go-util) | 安全并发工具（Goroutine/Channel） |
| **util** | [pkg/util/](file:///workspace/pkg/util) | 通用工具（认证/校验/转换/加密/文件/ID/UUID/版本/ZIP） |
| **constant** | [pkg/constant/](file:///workspace/pkg/constant) | 全局常量 |

---

## 七、依赖关系

### 7.1 中间件依赖

```
MySQL 8.0 ─── IAM / Model / Knowledge / RAG / Assistant / MCP / Operate / App / Workflow
Redis 7.0 ─── BFF / IAM / Model / Knowledge / RAG / Assistant / MCP / App / Callback / Workflow
MinIO ─────── BFF / Knowledge / Agent / Assistant / App / Callback / RAG(Python) / Workflow
Kafka 3.9 ─── Knowledge / RAG(Python)
ES 8.12 ──── Assistant / RAG(Python)
```

### 7.2 服务依赖图

```
nginx → bff-service → iam-service (gRPC)
                  → model-service (gRPC)
                  → knowledge-service (gRPC)
                  → rag-service (gRPC)
                  → assistant-service (gRPC)
                  → agent-service (gRPC)
                  → mcp-service (gRPC)
                  → operate-service (gRPC)
                  → app-service (gRPC)
                  → callback (HTTP)
                  → workflow (HTTP)

workflow → bff-service (HTTP callback)
        → agent-service (HTTP)
        → callback (HTTP)
        → rag-python (HTTP)

callback → rag-python (HTTP)

rag-python → bff-service (HTTP callback)
           → kafka (consume)
           → elasticsearch
           → minio
```

---

## 八、项目运行方式

### 8.1 Docker Compose 部署（推荐）

```bash
# 1. 拷贝环境变量
cp .env.bak .env

# 2. 修改 .env 文件
#    WANWU_ARCH=amd64          # 或 arm64
#    WANWU_EXTERNAL_IP=localhost # 或实际 IP
#    WANWU_BFF_JWT_SIGNING_KEY=  # 自定义 JWT 签名密钥

# 3. 创建 Docker 网络
docker network create wanwu-net

# 4. 启动服务
docker compose --env-file .env --env-file .env.image.amd64 up -d

# 5. 访问系统
# http://localhost:8081
# 默认账号: admin / Wanwu123456
```

### 8.2 源码开发模式

```bash
# 1. 先用 Docker Compose 启动完整服务
# 2. 停止需要开发的服务
make -f Makefile.develop stop-bff

# 3. 编译
make build-bff-amd64

# 4. 启动
make -f Makefile.develop run-bff
```

### 8.3 信创适配

```bash
# TiDB
WANWU_DB_NAME=tidb
docker compose --env-file .env --env-file .env.image.amd64 -f docker-compose.tidb.yaml up -d

# OceanBase
WANWU_DB_NAME=oceanbase
docker compose --env-file .env --env-file .env.image.amd64 -f docker-compose.oceanbase.yaml up -d
```

### 8.4 关键环境变量

| 变量 | 说明 |
|------|------|
| `WANWU_ARCH` | 系统架构：amd64 / arm64 |
| `WANWU_EXTERNAL_IP` | 对外访问 IP |
| `WANWU_BFF_JWT_SIGNING_KEY` | JWT 签名密钥（必填） |
| `WANWU_DB_NAME` | 数据库类型：mysql / tidb / oceanbase |
| `WANWU_BFF_OAUTH_SWITCH` | OAuth 开关 |
| `WANWU_BFF_REGISTER_BY_EMAIL` | 邮箱注册开关 |
| `WANWU_WORKFLOW_CODE_RUNNER_TYPE` | 工作流代码节点运行器类型 |

---

## 九、数据库设计

平台使用 GORM 作为 ORM，支持 MySQL / TiDB / OceanBase 三种数据库。

主要数据域：
- **用户域**：用户、组织、角色、权限
- **模型域**：模型配置、模型参数、模型体验对话
- **知识库域**：知识库、文档、文档分段、关键词、标签、QA 对、社区报告
- **应用域**：助手、智能体、工作流、RAG 应用、API Key
- **安全域**：敏感词表、安全策略
- **运营域**：使用统计

---

## 十、构建与发布

### Dockerfile 清单

| 文件 | 用途 |
|------|------|
| [Dockerfile.backend](file:///workspace/Dockerfile.backend) | Go 后端服务镜像 |
| [Dockerfile.frontend](file:///workspace/Dockerfile.frontend) | 前端 Nginx 镜像 |
| [Dockerfile.callback](file:///workspace/Dockerfile.callback) | Callback Python 服务镜像 |
| [Dockerfile.rag](file:///workspace/Dockerfile.rag) | RAG Python 引擎镜像 |

### Makefile 命令

| 命令 | 功能 |
|------|------|
| `make build-bff-amd64` | 编译 BFF 服务 (amd64) |
| `make build-bff-arm64` | 编译 BFF 服务 (arm64) |
| `make -f Makefile.develop stop-bff` | 停止 BFF 服务 |
| `make -f Makefile.develop run-bff` | 运行 BFF 服务 |

---

## 十一、API 文档

平台提供 Swagger 文档，位于 [docs/](file:///workspace/docs) 目录：

| 文档 | 路径 |
|------|------|
| BFF API | [docs/v1/](file:///workspace/docs/v1) |
| OpenAPI | [docs/openapi/](file:///workspace/docs/openapi) |
| OpenURL | [docs/openurl/](file:///workspace/docs/openurl) |
| Callback API | [docs/callback/](file:///docs/callback) |

---

## 十二、项目特色与亮点

1. **Apache 2.0 License**：商用友好，无限制
2. **信创适配**：华为鲲鹏 CPU / 欧拉 / 麒麟 / TiDB / OceanBase
3. **高精度 RAG**：MutiHop-RAG 评测 F1 值领先 Dify 14%
4. **GraphRAG**：知识图谱增强检索，F1 值领先 Dify 17.2%
5. **多租户架构**：组织/角色/用户三级隔离
6. **MCP 协议**：标准化工具连接，内置 100+ 行业 MCP
7. **全栈开源**：前端 + 后端 + RAG 引擎 + 工作流引擎
