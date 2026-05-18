# 工具系统开发指南

## 概述

本项目基于 OpenAPI 3.0 规范实现工具系统，支持两种工具集成方式：
- **自定义工具**：将已有的 API 服务快速集成到系统中
- **自建 API 服务**：参考 callback 服务开发新的工具服务

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        Agent Service                        │
│                     (智能体服务层)                           │
├─────────────────────────────────────────────────────────────┤
│    BuildAgentToolsConfig()                                  │
│    ├── GetToolsFromMCPServers()  → MCP 服务器工具           │
│    └── GetToolsFromOpenAPISchema() → OpenAPI 规范工具        │
├─────────────────────────────────────────────────────────────┤
│                        BFF Service                          │
│                    (前端接口服务层)                           │
├─────────────────────────────────────────────────────────────┤
│    tool.go        → 工具查询与选择                           │
│    tool_custom.go → 自定义工具管理（增删改查）                │
│    tool_builtin.go → 内置工具管理                            │
├─────────────────────────────────────────────────────────────┤
│                        MCP Service                          │
│                     (MCP 协议服务层)                          │
├─────────────────────────────────────────────────────────────┤
│                      Callback Service                       │
│              (Flask API 服务，用于工具实现)                   │
└─────────────────────────────────────────────────────────────┘
```

## 方式一：使用自定义工具（推荐）

如果你已有现成的 API 服务，推荐使用此方式。

### 步骤 1：准备 OpenAPI 3.0 规范文档

确保你的 API 服务提供完整的 OpenAPI 3.0 规范，示例：

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "我的工具 API",
    "version": "1.0.0"
  },
  "paths": {
    "/search": {
      "get": {
        "operationId": "searchContent",
        "summary": "搜索内容",
        "description": "根据关键词搜索相关内容",
        "parameters": [
          {
            "name": "keyword",
            "in": "query",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "搜索关键词"
          },
          {
            "name": "limit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "integer",
              "default": 10
            },
            "description": "返回结果数量限制"
          }
        ],
        "responses": {
          "200": {
            "description": "搜索成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "results": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "title": {"type": "string"},
                          "url": {"type": "string"},
                          "snippet": {"type": "string"}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 步骤 2：配置 API 认证（可选）

如果你的 API 需要认证，支持以下方式：

```go
type ApiAuthWebRequest struct {
    AuthType           string // 认证类型：header、query、none
    ApiKeyHeaderPrefix string // Header 前缀（如 "Bearer "）
    ApiKeyHeader       string // Header 名称（如 "Authorization"）
    ApiKeyQueryParam   string // Query 参数名（如 "api_key"）
    ApiKeyValue        string // API Key 值
}
```

### 步骤 3：通过系统界面添加自定义工具

1. 在系统中进入「工具管理」页面
2. 选择「自定义工具」
3. 填写以下信息：
   - 工具名称和描述
   - OpenAPI 3.0 Schema（JSON 格式）
   - API 认证配置（如需要）
   - 工具图标（可选）

## 方式二：开发新的 API 服务（参考 callback）

如果需要从零开发工具服务，参考 `callback` 目录的架构。

### 项目结构

```
callback/
├── callback/
│   ├── models/                      # 数据模型层（ORM）
│   ├── routes/                      # 路由层（定义 API 接口）
│   │   ├── hello.py                # 示例：GET/POST/PUT 请求
│   │   ├── doc.py                  # 文档处理相关
│   │   ├── minio.py                # 文件存储相关
│   │   └── tavily_news.py          # 新闻搜索相关
│   ├── services/                   # 业务逻辑层
│   │   ├── hello.py                # 示例服务
│   │   ├── doc.py
│   │   ├── minio.py
│   │   └── tavily_news.py
│   ├── static/                     # 静态文件
│   └── utils/                      # 工具函数
│       ├── response.py             # 响应封装
│       ├── decorators.py          # 装饰器
│       └── log.py                  # 日志工具
├── configs/
│   ├── config.ini                  # 配置文件
│   └── config.py                   # 配置加载器
├── extensions/                     # 第三方服务初始化
│   ├── minio.py                    # MinIO 客户端
│   └── redis.py                    # Redis 客户端
└── run.py                          # 服务入口
```

### 开发示例：创建一个简单的工具

#### 1. 定义路由（routes/hello.py）

```python
from flask import request
from callback.services import hello as hello_service
from utils.response import BizError, response_ok
from . import callback_bp

@callback_bp.route("/hello", methods=["GET"])
def get_hello():
    """
    API 示例 - GET 请求
    ---
    tags:
      - hello
    parameters:
      - name: username
        description: 用户名
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: 返回问候信息
        content:
          application/json:
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 0
                msg:
                  type: string
                  example: "success"
                data:
                  type: string
                  example: "Hello, {username}!"
    """
    username = request.args.get("username")
    if not username:
        raise BizError("username is required")
    return response_ok(hello_service.get_message(username))
```

#### 2. 实现服务逻辑（services/hello.py）

```python
def get_message(username):
    """生成问候消息"""
    return f"Hello, {username}!"
```

#### 3. 注册蓝图（callback/\_\_init\_\_.py）

```python
from flask import Flask
from callback.routes import hello, doc, minio, tavily_news
from configs.config import config

def create_app():
    app = Flask(__name__)
    app.config.update(config.callback_cfg)

    # 注册蓝图
    app.register_blueprint(hello.callback_bp, url_prefix='/api/v1/hello')

    return app
```

#### 4. 启动服务（run.py）

```python
from callback import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8669, debug=True)
```

### 响应格式规范

使用统一的响应格式，便于工具调用方处理：

```python
# utils/response.py
def response_ok(data):
    """成功响应"""
    return {
        "code": 0,
        "msg": "success",
        "data": data
    }

def response_err(code, msg):
    """错误响应"""
    return {
        "code": code,
        "msg": msg,
        "data": None
    }

class BizError(Exception):
    """业务逻辑错误"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
```

### 配置管理

配置文件使用 INI 格式（configs/config.ini）：

```ini
[REDIS]
HOST=localhost
PORT=6379
PASSWORD=

[MINIO]
ENDPOINT=localhost:9000
ACCESS_KEY=minioadmin
SECRET_KEY=minioadmin
BUCKET=callback

[DEFAULT]
PORT=8669
```

### Docker 部署

参考项目的 `Dockerfile.callback` 和 `docker-compose.yaml` 进行容器化部署。

## OpenAPI 到 MCP 协议转换

系统使用 `pkg/openapi3-util/openapi3_to_mcp_protocol.go` 将 OpenAPI 规范自动转换为 MCP 协议工具：

```go
// 核心转换逻辑
func Schema2MCPProtocolTools(ctx context.Context, schema []byte) ([]*protocol.Tool, error)
func Doc2MCPProtocolTools(doc *openapi3.T) ([]*protocol.Tool, error)
func Operation2MCPProtocolTool(operation *openapi3.Operation) *protocol.Tool
```

支持的类型映射：

| OpenAPI Type | MCP Type    |
|--------------|-------------|
| string       | String      |
| integer      | Integer     |
| number       | Number      |
| boolean      | Boolean     |
| array        | Array       |
| object       | Object      |

## 最佳实践

1. **完整的 API 文档**：为每个接口编写清晰的 Swagger 文档注释
2. **统一的响应格式**：始终使用 `response_ok()` 和 `response_err()` 封装响应
3. **错误处理**：使用 `BizError` 处理业务逻辑错误
4. **日志记录**：在关键步骤添加日志，便于问题排查
5. **认证安全**：敏感操作添加 API Key 认证，不要在代码中硬编码密钥
6. **参数校验**：在路由层验证必填参数

## 常见问题

### Q: 如何调试工具 API？

A: 启动 callback 服务后访问 `http://localhost:8669/apidocs` 查看 Swagger 文档。

### Q: 如何添加新的 API 认证方式？

A: 在 `common.ApiAuthWebRequest` 中扩展认证类型。

### Q: 工具调用失败如何排查？

A: 1. 检查 OpenAPI Schema 是否符合规范
   2. 检查 API 认证配置是否正确
   3. 查看 agent-service 和 callback 服务的日志

## 参考代码

- 工具管理服务：[internal/bff-service/service/tool.go](file:///workspace/internal/bff-service/service/tool.go)
- 自定义工具管理：[internal/bff-service/service/tool_custom.go](file:///workspace/internal/bff-service/service/tool_custom.go)
- OpenAPI 转换工具：[pkg/openapi3-util/openapi3_to_mcp_protocol.go](file:///workspace/pkg/openapi3-util/openapi3_to_mcp_protocol.go)
- 工具构建配置：[internal/agent-service/service/agent_tool_service.go](file:///workspace/internal/agent-service/service/agent_tool_service.go)
