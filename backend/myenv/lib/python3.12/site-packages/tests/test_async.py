import pytest
from unittest.mock import AsyncMock, patch
from mira_sdk.mira.client.async_mira_client import AsyncMiraClient, Flow, FlowConfig, Prompt

@pytest.fixture
def mira_client():
    return AsyncMiraClient(config={"API_KEY": "test_api_key"})

@pytest.mark.asyncio
async def test_execute_flow(mira_client):
    flow = Flow("org/flow", FlowConfig({"name": "test_flow"}), private=False, version="1.0.0")
    input_dict = {"key": "value"}

    with patch.object(mira_client.console, 'execute_flow', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = {"result": "success"}
        result = await mira_client.flow.execute(flow, input_dict)

    mock_execute.assert_called_once_with("org", "flow", input_dict, "1.0.0")
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_run_flow(mira_client):
    flow_config = FlowConfig({"name": "test_flow"})
    input_dict = {"key": "value"}

    with patch.object(mira_client.console, 'run_flow', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = {"result": "success"}
        result = await mira_client.flow.run(flow_config, input_dict)

    mock_run.assert_called_once_with(flow_config.dict(), input_dict)
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_get_flow(mira_client):
    with patch.object(mira_client.console, 'get_flow', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "config": {"name": "test_flow"},
            "private": True,
            "version": "1.0.0"
        }
        flow = await mira_client.flow.get("org/flow/1.0.0")

    mock_get.assert_called_once_with("org", "flow", "1.0.0")
    assert isinstance(flow, Flow)
    assert flow.org == "org"
    assert flow.name == "flow"
    assert flow.version == "1.0.0"
    assert flow.private == True

@pytest.mark.asyncio
async def test_get_flows_by_author(mira_client):
    with patch.object(mira_client.console, 'get_flows_by_author', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [{"org": "org", "name": "flow1"}, {"org": "org", "name": "flow2"}]
        flows = await mira_client.flow.get_by_author("@author")

    mock_get.assert_called_once_with("author")
    assert len(flows) == 2
    assert flows[0]["name"] == "flow1"
    assert flows[1]["name"] == "flow2"

@pytest.mark.asyncio
async def test_deploy_flow(mira_client):
    flow = Flow("org/flow", FlowConfig({"name": "test_flow"}), private=True, version="1.0.0")

    with patch.object(mira_client.console, 'deploy_flow', new_callable=AsyncMock) as mock_deploy:
        mock_deploy.return_value = {"result": "success"}
        result = await mira_client.flow.deploy(flow)

    mock_deploy.assert_called_once_with("org", "flow", flow.config.dict(), True, "1.0.0")
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_get_prompt(mira_client):
    with patch.object(mira_client.console, 'get_prompt_version', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "author_name": "org",
            "prompt_name": "prompt",
            "content": "Test content",
            "version": "1.0.0",
            "variables": {},
            "prompt_id": "123"
        }
        prompt = await mira_client.prompt.get("org/prompt/1.0.0")

    mock_get.assert_called_once_with("org", "prompt", "1.0.0")
    assert isinstance(prompt, Prompt)
    assert prompt.org == "org"
    assert prompt.name == "prompt"
    assert prompt.version == "1.0.0"
    assert prompt.content == "Test content"
    assert prompt.prompt_id == "123"

@pytest.mark.asyncio
async def test_create_prompt(mira_client):
    prompt = Prompt("org/prompt", "Test content", "1.0.0", {"var": "value"})

    with patch.object(mira_client.console, 'create_prompt', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"data": {"prompt_id": "123"}}
        result = await mira_client.prompt.create(prompt)

    mock_create.assert_called_once_with("org", "prompt", "1.0.0", "Test content", {"var": "value"})
    assert result.prompt_id == "123"
    assert result == prompt

@pytest.mark.asyncio
async def test_update_prompt(mira_client):
    prompt = Prompt("org/prompt", "Updated content", "1.1.0", {"var": "new_value"})

    with patch.object(mira_client.console, 'get_prompt_version', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"prompt_id": "123"}
        with patch.object(mira_client.console, 'add_prompt_version', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {"data": {"prompt_id": "456"}}
            result = await mira_client.prompt.update(prompt)

    mock_get.assert_called_once_with("org", "prompt", None)
    mock_update.assert_called_once_with("123", "1.1.0", "Updated content", {"var": "new_value"})
    assert result.prompt_id == "456"
    assert result == prompt
