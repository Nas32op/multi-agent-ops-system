from multi_agent_ops.config import AppConfig
from multi_agent_ops.workflow import MultiAgentWorkflow


def test_workflow_runs_in_mock_mode():
    cfg = AppConfig(openai_api_key=None, openai_model="gpt-4o-mini", mock_mode=True)
    wf = MultiAgentWorkflow(cfg)
    result = wf.run("为 AI 学习产品制定 7 天游运营方案")

    assert result.plan
    assert result.execution
    assert result.review
    assert "PLAN" in result.final_output
    assert result.metadata["mock_mode"] is True
