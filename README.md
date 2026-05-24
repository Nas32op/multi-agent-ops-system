# Multi-Agent Ops Automation System

> 将单次 LLM 调用升级为 Planner → Executor → Reviewer 三 Agent 协作的运营自动化流水线。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.2.0-green)](https://github.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue)](https://github.com/features/actions)

## 架构

```
用户任务 ──→ PlannerAgent ──→ ExecutorAgent ──→ ReviewerAgent ──→ 结构化输出
               (规划拆解)        (内容生成)        (质量审核)

               MemoryStore 全链路追溯 · 指数退避重试 · Mock 自动降级
```

三个专业 Agent 串行协作：Planner 拆解目标制定执行计划 → Executor 基于计划产出具体文案与落地步骤 → Reviewer 检查完整性、KPI 与风险控制，最终输出包含 plan / execution / review / final_output / metadata 的结构化 JSON。

支持 **异步顺序执行** 与 **并行执行**（Planner 和 Executor 并发启动后 Reviewer 审核），缩短总耗时。

## 特性

- **三 Agent 协作** — Planner / Executor / Reviewer 分工明确，输出质量可控
- **Mock 自动降级** — 无 API Key 时自动切换 MockLLM，离线可跑、演示友好
- **结构化输出** — 标准 JSON 含 plan / execution / review / final_output / metadata + 全链路 Memory
- **YAML 任务输入** — 结构化任务描述，支持批量标准化处理
- **多入口** — CLI 命令行 / FastAPI Web API / Docker 容器化
- **异步并行** — `AsyncMultiAgentWorkflow.run_parallel()` Planner 与 Executor 并发
- **指数退避重试** — 同步 `@retry` + 异步 `@retry_async` 装饰器
- **10 种异常类型** — 精细化错误分类（含 RetryExhaustedError）
- **日志轮转** — 结构化日志 + 文件轮转
- **测试 + CI** — pytest + pytest-asyncio + pytest-cov，GitHub Actions 矩阵测试 + ruff + mypy

## 项目结构

```text
multi-agent-ops-system/
├── src/multi_agent_ops/
│   ├── agents.py           # Planner / Executor / Reviewer 三 Agent
│   ├── workflow.py          # 同步工作流编排
│   ├── async_workflow.py    # 异步工作流（顺序 + 并行）
│   ├── api.py               # FastAPI Web API
│   ├── cli.py               # 命令行入口
│   ├── config.py            # Pydantic 配置管理
│   ├── llm.py               # LLM 抽象层（OpenAI + Mock）
│   ├── tools.py             # MemoryStore / 工具函数
│   ├── exceptions.py        # 10 种自定义异常
│   ├── retry.py             # 同步/异步重试 + 指数退避
│   └── logger.py            # 结构化日志
├── examples/
│   └── example_task.yaml    # 示例任务文件
├── tests/                   # 测试套件（7 个文件）
├── .github/workflows/
│   └── ci.yml               # CI/CD 流水线
├── Dockerfile               # 多阶段构建
├── docker-compose.yml       # 开发环境
├── docker-compose.prod.yml  # 生产环境（3 副本 + Redis + 健康检查）
├── pyproject.toml
└── requirements.txt
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置（可选，不配置则自动 Mock 模式）
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 运行
python -m multi_agent_ops.cli --task "为一款 AI 学习产品制定 7 天内容运营方案"
```

## 使用方式

### 1) CLI — YAML 任务文件

```bash
python -m multi_agent_ops.cli --task-file examples/example_task.yaml
```

YAML 任务格式 (`examples/example_task.yaml`)：

```yaml
title: "AI 学习产品周运营"
objective: "提升新用户激活率与内容转化"
audience: "学生与初级开发者"
constraints:
  tone: "专业、简洁、可执行"
  output_length: "medium"
task: "为一款 AI 学习产品制定 7 天内容运营方案，包含选题、发布节奏、增长策略、复盘指标。"
```

### 2) CLI — 直接输入任务

```bash
python -m multi_agent_ops.cli --task "为新品发布制定社交媒体推广方案"
```

### 3) FastAPI Web API

```bash
# 启动 API 服务
python -c "from multi_agent_ops.api import start_api; start_api()"

# 或通过 uvicorn
uvicorn multi_agent_ops.api:app --host 0.0.0.0 --port 8000
```

API 端点：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查，返回版本与 Mock 状态 |
| `POST` | `/api/v1/tasks` | 同步执行任务 |
| `POST` | `/api/v1/tasks/async` | 异步提交任务（返回 task_id） |
| `GET` | `/api/v1/tasks/{task_id}` | 查询异步任务状态 |

请求示例：

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "制定本周内容运营计划", "max_rounds": 1}'
```

### 4) Docker

```bash
# 开发环境
docker compose up --build

# 生产环境（3 副本 + Redis + 健康检查）
docker compose -f docker-compose.prod.yml up --build
```

## 配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key，不设置则 Mock 模式 | — |
| `OPENAI_MODEL` | 使用的模型 | `gpt-4o-mini` |
| `MAX_RETRIES` | 最大重试次数 | `3` |
| `RETRY_DELAY` | 重试间隔（秒） | `1.0` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 输出格式

```json
{
  "plan": "PlannerAgent 输出的执行计划",
  "execution": "ExecutorAgent 输出的具体内容",
  "review": "ReviewerAgent 输出的审核意见",
  "final_output": "整合后的最终方案",
  "metadata": {
    "model": "gpt-4o-mini",
    "mock_mode": false,
    "rounds": 1,
    "timestamp": "2026-05-24T...",
    "memory": [
      {"role": "user", "content": "...", "timestamp": "..."},
      {"role": "planner", "content": "...", "timestamp": "..."},
      {"role": "executor", "content": "...", "timestamp": "..."},
      {"role": "reviewer", "content": "...", "timestamp": "..."}
    ]
  }
}
```

## 开发

```bash
# 安装开发依赖
pip install pytest pytest-asyncio pytest-cov ruff mypy

# 运行测试
pytest tests/ -v --cov=multi_agent_ops

# 代码检查
ruff check .
mypy src/multi_agent_ops --ignore-missing-imports
```

## CI/CD

GitHub Actions 流水线：Python 3.10 / 3.11 / 3.12 矩阵测试 → ruff lint + mypy 类型检查 → 构建打包 → Docker 镜像推送（仅 main 分支）。

## 路线图

- [ ] 工具调用：搜索、表格分析、邮件发送、CRM 写入
- [ ] 持久化记忆：SQLite / Redis / PostgreSQL
- [ ] 任务队列：Celery / RQ / Dramatiq
- [ ] Web UI：FastAPI + React / Next.js
