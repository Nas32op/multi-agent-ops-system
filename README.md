# Multi-Agent Ops Automation System

## 特性

- Planner / Executor / Reviewer 三角色协作
- 支持 YAML 任务输入
- 支持 OpenAI API，也支持无 Key 的本地 Mock 模式
- 输出结构化 JSON 结果
- 自带测试与 Docker 配置

## 项目结构

```text
multi-agent-ops-system/
├── src/multi_agent_ops/
│   ├── agents.py
│   ├── cli.py
│   ├── config.py
│   ├── llm.py
│   ├── tools.py
│   └── workflow.py
├── examples/example_task.yaml
├── tests/test_workflow.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 安装

```bash
pip install -r requirements.txt
cp .env.example .env
```

## 运行

### 1) 使用示例任务

```bash
python -m multi_agent_ops.cli --task-file examples/example_task.yaml
```

### 2) 直接输入任务

```bash
python -m multi_agent_ops.cli --task "为一款 AI 学习产品制定 7 天内容运营方案"
```

### 3) 不配置 API Key 也能跑

系统会自动切换到 Mock 模式，方便本地调试、展示和写 GitHub 项目说明。

## 输出示例

会生成包含以下字段的 JSON：

- `plan`
- `execution`
- `review`
- `final_output`
- `metadata`

## Docker

```bash
docker compose up --build
```

## 可扩展方向

- 增加工具调用：搜索、表格分析、邮件发送、CRM 写入
- 增加持久化记忆：SQLite / Redis / Postgres
- 增加任务队列：Celery / RQ / Dramatiq
- 增加 Web UI：FastAPI + React / Next.js
