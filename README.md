# 智能音箱客服系统 - 项目文档

## 项目概述

这是一个基于AI的智能音箱客服系统，采用ReAct（Reasoning + Acting）架构，能够为用户提供智能音箱相关的专业咨询、故障排除、使用指导、个性化报告生成等服务。系统集成了RAG（检索增强生成）技术、多工具调用能力和流式响应，提供高质量的客服体验。

## 系统架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vue3)   │◄──►│   API (FastAPI)  │◄──►│   AI Agent      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                      │
                              │              ┌─────────────────┐
                              │              │   RAG 服务       │
                              │              └─────────────────┘
                              │                      │
                              │              ┌─────────────────┐
                              └────────────►│   向量数据库     │
                                             └─────────────────┘
```

### 核心组件

1. **前端界面** (Vue3 + Vite)
   - 现代化的聊天界面
   - 支持对话历史管理
   - 主题切换（明暗模式）
   - 实时流式响应显示

2. **API服务** (FastAPI)
   - RESTful API接口
   - 流式响应支持
   - 静态文件服务
   - CORS跨域支持

3. **AI Agent** (LangChain)
   - ReAct推理架构
   - 多工具集成
   - 中间件监控
   - 提示词动态切换

4. **RAG服务**
   - 向量检索
   - 文档摘要
   - 知识库管理

## 目录结构

```
├── agent/                    # AI Agent核心模块
│   ├── react_agent.py       # ReAct Agent主类
│   └── tools/               # 工具集
│       ├── agent_tools.py   # 具体工具实现
│       └── middleware.py    # 中间件
├── api.py                   # FastAPI主服务
├── config/                  # 配置文件
│   ├── agent.yml           # Agent配置
│   ├── chroma.yml          # 向量数据库配置
│   ├── prompts.yml         # 提示词配置
│   └── rag.yml             # RAG配置
├── data/                   # 数据文件
│   ├── external/           # 外部数据
│   │   └── records.csv     # 用户使用记录
│   └── *.pdf/*.txt         # 知识库文档
├── frontend/               # 前端代码
│   ├── src/
│   │   └── App.vue         # 主组件
│   ├── index.html
│   └── package.json
├── model/                  # 模型工厂
│   └── factory.py          # 模型实例化
├── prompts/                # 提示词文件
│   ├── main_prompt.txt     # 主提示词
│   ├── rag_summarize.txt   # RAG摘要提示词
│   └── report_prompt.txt   # 报告提示词
├── rag/                    # RAG相关
│   ├── rag_service.py      # RAG服务
│   └── vector_store.py     # 向量存储
├── utils/                  # 工具函数
│   ├── chain_debug.py      # 链式调试
│   ├── config_handler.py   # 配置处理
│   ├── file_handler.py     # 文件处理
│   ├── logger_handler.py   # 日志处理
│   ├── path_tools.py       # 路径工具
│   └── prompt_loader.py    # 提示词加载
└── static/                 # 静态资源
```

## 核心功能

### 1. 智能对话
- **多轮对话管理**：支持上下文感知的对话
- **流式响应**：实时显示AI思考过程
- **工具调用**：自主决定何时调用工具获取信息

### 2. 工具系统
系统集成了7个核心工具：

| 工具名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `rag_summarize` | RAG检索摘要 | 获取专业知识 |
| `get_weather` | 天气查询 | 环境适配建议 |
| `get_user_location` | 用户位置 | 地理位置相关服务 |
| `get_user_id` | 用户ID获取 | 个性化服务 |
| `get_current_month` | 当前月份 | 时间相关查询 |
| `fetch_external_data` | 用户数据检索 | 个性化报告 |
| `fill_context_for_report` | 报告上下文注入 | 报告生成前置步骤 |

### 3. RAG增强生成
- **向量检索**：基于Chroma的相似度检索
- **文档处理**：支持PDF、TXT、CSV格式
- **智能摘要**：结合检索结果的生成式摘要

### 4. 个性化报告
- **用户行为分析**：基于历史使用数据
- **月度报告生成**：自动统计分析
- **改进建议**：个性化优化建议

## 配置说明

### 主要配置文件

**config/rag.yml**
```yaml
rag_summarize_prompt_path: prompts/rag_summarize.txt
main_prompt_path: prompts/main_prompt.txt
report_prompt_path: prompts/report_prompt.txt
chat_model_name: qwen3-max-preview
embedding_model_name: text-embedding-v4
```

**config/agent.yml**
```yaml
external_data_path: data/external/records.csv
```

**config/chroma.yml**
```yaml
collection_name: agent
persist_directory: chroma_db
k: 3
```

## 数据格式

### 用户记录数据 (records.csv)
包含用户智能音箱使用情况的详细记录：
- 用户基本信息（居住面积、家庭结构、地面材质）
- 语音识别性能数据
- 连接稳定性统计
- 使用偏好分析
- 设备维护信息

### 知识库文档
- `智能音箱.pdf` - 产品说明书
- `智能音箱故障排除.txt` - 故障处理指南
- `智能音箱维护保养.txt` - 维护指南
- `智能音箱选购指南.txt` - 选购建议

## API接口

### 聊天接口
**POST /chat**
```json
{
  "messages": [
    {"role": "user", "content": "我的音箱经常断连"},
    {"role": "assistant", "content": "让我帮您检查一下..."}
  ]
}
```

**响应**：流式文本响应

### 前端接口
- `GET /` - Vue应用主入口
- `GET /dist/{path}` - 静态资源服务
- `GET /static` - 静态文件服务

## 提示词工程

### 主提示词设计原则
1. **ReAct流程规范**：严格遵循思考→行动→观察→再思考
2. **工具使用约束**：明确工具调用条件和参数要求
3. **报告生成规范**：固定执行流程确保数据完整性
4. **输出格式控制**：结构化思考和自然语言输出

### 提示词动态切换
- 根据用户意图自动切换提示词模板
- 报告生成场景专用提示词
- 上下文感知的提示词调整

## 技术栈

### 后端技术
- **Python 3.8+**
- **FastAPI** - Web框架
- **LangChain** - AI应用框架
- **Chroma** - 向量数据库
- **DashScope** - 大模型和嵌入模型

### 前端技术
- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **TypeScript** - 类型系统

### 部署相关
- **Uvicorn** - ASGI服务器
- **CORS** - 跨域支持

## 运行指南

### 环境准备
```bash
# 安装依赖
pip install -r requirements.txt
cd frontend && npm install

# 启动后端
python api.py

# 启动前端
cd frontend && npm run dev
```

### 配置文件说明
1. 配置DashScope API密钥
2. 准备知识库文档
3. 配置向量数据库路径

## 扩展开发

### 添加新工具
1. 在`agent_tools.py`中定义工具函数
2. 使用`@tool`装饰器
3. 在`react_agent.py`中注册工具

### 扩展知识库
1. 在`data/`目录添加文档
2. 支持PDF、TXT、CSV格式
3. 系统会自动处理并建立向量索引

### 自定义提示词
1. 在`prompts/`目录创建提示词文件
2. 在配置文件中指定路径
3. 支持动态切换逻辑

## 监控和调试

### 中间件功能
- **工具监控**：记录工具调用情况
- **模型日志**：跟踪模型输入输出
- **提示词切换**：报告生成场景监控

### 日志系统
- 详细的操作日志
- 错误追踪
- 性能监控

## 性能优化

### 缓存策略
- 提示词文件缓存
- 向量检索结果缓存
- 用户会话本地存储

### 流式处理
- 实时响应分块传输
- 增量更新UI
- 内存使用优化

## 安全考虑

### 数据安全
- 用户数据本地处理
- 敏感信息保护
- API访问控制

### 输入验证
- 用户输入清理
- 工具参数验证
- 异常处理机制

## 未来规划

### 功能扩展
1. **多语言支持**：国际化界面
2. **语音交互**：语音输入输出
3. **设备集成**：直接控制智能设备
4. **数据分析**：更深入的使用行为分析

### 技术升级
1. **模型优化**：更高效的推理模型
2. **检索增强**：更精准的向量检索
3. **界面改进**：更丰富的交互体验
4. **部署优化**：容器化部署方案

---

*文档版本：1.0.0*
*最后更新：2025年4月*
