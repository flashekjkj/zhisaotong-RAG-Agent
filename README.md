# 智扫通机器人智能客服系统 🤖

---
## 📖 项目简介

**智扫通**是面向扫地机器人、扫拖一体机器人用户的轻量化AI智能体客服系统。项目基于Streamlit搭建可视化前端，依托LangChain+LangGraph构建自主决策ReAct智能体，包含以下功能：

- **混合检索RAG问答**：融合BM25关键词检索、Chroma向量检索、BGE-Rerank语义重排，解决传统单向量召回精准度低、关键词漏匹配问题，依托专属知识库，支持机器人故障排查、使用教程、日常保养、常见问题全场景咨询。
- **多模态故障识别**：具有图片识别能力，支持上传机器人故障实拍图，智能分析硬件异常、故障原因，输出对应解决方案。
- **高德服务**：调用高德地图官方API，实时获取用户IP定位、本地天气信息。
- **报告生成**：内置意图识别机制，自动切换专属报告提示词，读取用户使用数据，一键生成Markdown格式的机器人使用分析、保养建议报告。
- **自主多轮工具调用**：Agent可自主规划并多轮调用所配备的工具，直至满足用户需求。
- **前后端分离架构**：使用FastAPI封装核心能力为标准RESTful接口，前端Streamlit独立负责交互，实现服务解耦、跨端复用，同时解决进程隔离、上下文传递等工程问题。
- **完整会话管理体系**：历史会话持久化，支持对话记录保存、加载、删除，实现多轮连贯对话，上下文记忆不丢失。
- **完善的日志与历史**：配备结构化日志（文件 + 控制台）与对话历史记录。支持加载选择和删除历史对话。

---

## 📂 目录结构

```
zhisaotong-RAG-Agent/
├── app.py                        # Streamlit 前端启动入口
├── app_copy.py                   # 项目初始化备份文件
├── test.py                       # 功能测试脚本（含图片识别测试）
├── chat_sessions.json            # 历史对话持久化存储文件
├── md5.text                      # 知识库文档MD5去重记录
├── requirements.txt              # 项目依赖清单
├── agent/                        # Agent智能体核心模块
│   ├── react_agent.py            # ReAct智能体主逻辑
│   └── tools/
│       ├── agent_tools.py        # 全部工具函数定义
│       └── middleware.py         # 智能体中间件（日志、提示词切换）
├── rag/                          # RAG检索核心模块
│   ├── rag_service.py            # 检索、摘要生成服务
│   └── vector_store.py           # Chroma向量库初始化与管理
├── model/                        # 模型调度模块
│   └── factory.py                # LLM、Embedding模型工厂
├── utils/                        # 通用工具模块
│   ├── config_handler.py         # YAML配置文件加载器
│   ├── logger_handler.py         # 结构化日志工具
│   ├── prompt_loader.py          # 提示词文件加载工具
│   ├── file_handler.py           # PDF/TXT文档解析工具
│   └── path_tool.py              # 项目路径统一管理工具
├── config/                       # 全局配置文件
│   ├── agent.yml                 # 高德API、外部数据路径配置
│   ├── rag.yml                   # 大模型、向量模型配置
│   ├── chroma.yml                # 向量库、检索参数配置
│   └── prompts.yml               # 提示词文件路径配置
├── prompts/                      # 系统提示词模板
│   ├── main_prompt.txt           # 通用对话ReAct提示词
│   ├── rag_summarize.txt         # RAG检索摘要提示词
│   └── report_prompt.txt         # 专属报告生成提示词
├── data/                         # 行业知识库+用户数据
│   ├── 扫地机器人100问.pdf
│   ├── 扫地机器人100问2.txt
│   ├── 扫拖一体机器人100问.txt
│   ├── 故障排除.txt
│   ├── 维护保养.txt
│   ├── 选购指南.txt
│   └── external/
│       └── records.csv           # 用户设备使用记录数据
├── chroma_db/                    # 向量库持久化存储目录（自动生成）
├── logs/                         # 项目日志存储目录（自动生成）
└── uploads/                      # 用户上传图片、文件存储目录（自动生成）
```

---

## 📦 环境依赖

### Python 版本

建议使用 **Python 3.10+**。

### 主要依赖包

| 包名                  | 用途                                    
| --------------------- | --------------------------------------- 
| `streamlit`           | 前端 Web 框架                           
| `langchain`           | Agent / Chain / Tool 框架               
| `langchain-core`      | LangChain 核心抽象                      
| `langchain-community` | 通义千问、DashScope Embedding 等集成    
| `langgraph`           | 基于图的 Agent 执行引擎（含 `Runtime`） 
| `langchain-chroma`    | LangChain 与 Chroma 向量库集成          
| `chromadb`            | Chroma 向量数据库                       
| `dashscope`           | 阿里云 DashScope SDK（Embedding / LLM） 
| `pypdf` / `pypdf2`    | PDF 文档加载                            
| `pyyaml`              | YAML 配置文件解析                       

### 一键安装依赖

```bash
python -m pip install -r requirements.txt
```

---

## ⚙️ 配置说明

### 1. 阿里云 API Key

本项目使用阿里云通义千问大模型和 DashScope Embedding，需要配置系统环境变量：

```bash
OPENAI_API_KEY="your_open_api_key"
```

可在 [阿里云百炼平台](https://bailian.console.aliyun.com/) 获取 API Key。

### 2. 高德地图 API Key

编辑 `config/agent.yml`，将 `gaodekey` 替换为你的高德地图 Web 服务 API Key：

```yaml
# config/agent.yml
external_data_path: data/external/records.csv
gaodekey: 你的高德key! # ← 替换这里
gaode_base_url: https://restapi.amap.com
gaode_timeout: 5
```

可在 [高德开放平台](https://console.amap.com/) 申请 Web 服务类型的 API Key。

### 3. 模型配置

编辑 `config/rag.yml` 可调整所使用的模型：

```yaml
# config/rag.yml
chat_model_name: qwen3-max # 对话大模型
embedding_model_name: text-embedding-v4 # 向量化模型
```

### 4. 向量库配置

编辑 `config/chroma.yml` 可调整 RAG 检索参数：

```yaml
# config/chroma.yml
collection_name: agent
persist_directory: chroma_db
k: 3 # 检索返回的最相关文档数量
data_path: data
md5_hex_store: md5.text
allow_knowledge_file_type: ["txt", "pdf"]
chunk_size: 200 # 文本分块大小
chunk_overlap: 20 # 分块重叠长度
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/bamboo-moon/zhisaotong-Agent.git
cd zhisaotong-Agent
```

### 2. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 设置阿里云 DashScope API Key
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# 在 config/agent.yml 中配置高德地图 API Key
```

### 4. 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`，即可开始与智扫通机器人智能客服对话。

---

## 💬 使用方式

启动后，用户可以在网页聊天界面进行以下操作：

### 产品咨询

直接提问关于扫地机器人的使用、维护、故障排除等问题，Agent 会优先从知识库中检索相关资料进行回答：

```
用户：扫地机器人的滤网多久需要更换一次？
用户：扫拖一体机器人和扫地机器人有什么区别？
用户：扫地机器人吸力变弱了怎么办？
```

### 天气与定位查询

Agent 可调用高德 API 获取实时信息：

```
用户：我现在所在城市今天的天气怎么样？
```

### 使用报告生成

Agent 会自动检测报告生成意图，切换到报告提示词，并调用外部数据生成 Markdown 格式的使用情况报告：

```
用户：帮我生成我的使用报告
用户：给我一份扫地机器人的使用分析和保养建议
```

---

## 🛠 工具列表

Agent 配备了以下工具：

| 工具名                    | 描述                                           |
| ------------------------- | ---------------------------------------------- |
| `rag_summarize`           | 从向量知识库中检索参考资料，回答产品相关问题   |
| `get_weather`             | 获取指定城市的实时天气（高德 API）             |
| `get_user_location`       | 通过 IP 获取用户所在城市（高德 API）           |
| `get_user_id`             | 获取当前用户 ID                                |
| `get_current_month`       | 获取当前月份                                   |
| `fetch_external_data`     | 从外部系统获取指定用户指定月份的使用记录       |
| `fill_context_for_report` | 触发报告模式，通知中间件切换为报告生成提示词   |
| `detect_robot_fault`      | 分析扫地机器人的故障图片，识别图片中的故障问题 |

---

## 🔄 中间件机制

Agent 的三个中间件负责监控、日志和动态提示词切换：

```
monitor_tool         工具调用监控
  ├─ 记录每次工具调用的名称和参数
  ├─ 记录工具调用成功/失败状态
  └─ 检测 fill_context_for_report 调用，将 context["report"] 置为 True

log_before_model     模型调用前日志
  └─ 记录当前消息数量及最新消息内容

report_prompt_switch 动态提示词切换
  ├─ context["report"] == True  → 使用报告生成提示词
  └─ context["report"] == False → 使用主 ReAct 提示词
```

---

## 📋 日志说明

日志文件存放在 `logs/` 目录下，按天自动创建：

```
logs/
└── agent_20250101.log    # 格式：{name}_{YYYYMMDD}.log
```

日志格式：

```
2025-01-01 12:00:00,123 - agent - INFO - middleware.py:19 - [tool monitor]执行工具：get_weather
```

- **控制台**：输出 INFO 及以上级别日志
- **文件**：输出 DEBUG 及以上级别日志（更详细）

---

## 📚 知识库

知识库文档存放在 `data/` 目录下，支持 `.txt` 和 `.pdf` 格式。首次启动时，系统会自动将文档向量化并存入 Chroma 数据库（`chroma_db/`）。已处理文档通过 MD5 哈希追踪，重启后不会重复入库。

**内置知识库文档：**

| 文件                      | 内容                          |
| ------------------------- | ----------------------------- |
| `扫地机器人100问.pdf`     | 扫地机器人常见问题解答（PDF） |
| `扫地机器人100问2.txt`    | 扫地机器人补充问答            |
| `扫拖一体机器人100问.txt` | 扫拖一体机器人常见问题解答    |
| `故障排除.txt`            | 故障排除指南                  |
| `维护保养.txt`            | 日常维护保养说明              |
| `选购指南.txt`            | 购买建议与选型指南            |

如需扩展知识库，只需将新的 `.txt` 或 `.pdf` 文件放入 `data/` 目录，重启服务后会自动加载。

---

## 🔮 后续优化方向

- 将向量数据库从 Chroma 替换为 Redis（更适合生产部署）
- 地点、天气等功能完整迁移至高德 MCP 协议
- 增加用户身份认证与多用户会话隔离
- 支持更多文档格式（Word、Excel 等）

---

## 📄 许可证

感谢黑马程序员开源免费项目、阿里云和高德地图等开放平台。项目仅供学习与参考使用。
