import os
from typing import Optional
import semantic_version

from .console import Console
from .async_console import AsyncConsole
from ..utils import split_name



class FlowConfig:
    def __init__(self, data: dict):
        self.flow = data.get('flow')
        self.name = data.get('name')
        self.resources = data.get('resources')
        self.components = data.get('components')
        self.description = data.get('description')

    def dict(self):
        return {
            'flow': self.flow,
            'name': self.name,
            'resources': self.resources,
            'components': self.components,
            'description': self.description
        }


class Flow:
    def __init__(self, flow_name: str, config: FlowConfig, private: bool, version: Optional[str] = None):
        if version:
            # Throws Value error if version string is not a valid sematic version
            semantic_version.Version(version)

        self.org, self.name = split_name(flow_name)
        self.config: FlowConfig = config
        self.version = version
        self.private = private

    def __str__(self):
        if self.version:
            return f"{self.org}/{self.name}/{self.version}"
        return f"{self.org}/{self.name}"


class Prompt:
    def __init__(self, prompt_name: str, content: str, version: Optional[str] = None, variables: Optional[dict] = None):
        if version:
            # Throws Value error if version string is not a valid sematic version
            semantic_version.Version(version)

        self.org, self.name = split_name(prompt_name)
        self.version = version
        self.content = content
        self.variables = variables or {}
        self.prompt_id = None  # This will be set when retrieved from or created in the console

    def __str__(self):
        if self.version:
            return f"{self.org}/{self.name}/{self.version}"
        return f"{self.org}/{self.name}"




class PromptOperations:
    def __init__(self, console):
        self.console = console

    async def get(self, prompt_name: str) -> Prompt:
        version = None
        if len(prompt_name.split("/")) > 2:
            version = prompt_name.split("/")[-1]
        org, name = split_name(prompt_name)
        prompt_dict =await self.console.get_prompt_version(org, name, version)
        prompt = Prompt(f"{prompt_dict['author_name']}/{prompt_dict['prompt_name']}", prompt_dict["content"], prompt_dict["version"], prompt_dict["variables"])
        prompt.prompt_id = prompt_dict['prompt_id']
        return prompt

    async def create(self, prompt: Prompt) -> Prompt:
        result = await self.console.create_prompt(prompt.org, prompt.name, prompt.version, prompt.content, prompt.variables)
        prompt.prompt_id = result['data']['prompt_id']
        return prompt

    async def update(self, prompt: Prompt) -> Prompt:
        current_prompt = await self.console.get_prompt_version(prompt.org, prompt.name, None)
        result = await self.console.add_prompt_version(current_prompt['prompt_id'], prompt.version, prompt.content, prompt.variables)
        prompt.prompt_id = result['data']['prompt_id']
        return prompt

    async def get_by_author(self, author_name: str) -> list[Prompt]:
        if len(author_name) > 1 and author_name[0] == "@":
            author_name = author_name[1:]
        prompts_list = await self.console.get_prompts_by_author(author_name)
        # return [Prompt(p['author_name'], p['prompt_name'], None , p['content'], p.get('variables')) for p in prompts_list]
        return prompts_list

    async def get_all_versions(self, prompt: Prompt) -> list[Prompt]:
        versions = await self.console.get_all_versions_by_prompt(prompt.prompt_id)
        return [Prompt(f"{prompt.org}/{prompt.name}", v['content'], v['version'], v.get('variables')) for v in versions]
        # return versions

class FlowOperations:
    def __init__(self, console):
        self.console = console

    async def execute(self, flow: Flow, input_dict: dict):
        response = await self.console.execute_flow(flow.org, flow.name, input_dict, flow.version)
        return response

    async def run(self, flow_config: FlowConfig, input_dict: dict):
        response = await self.console.run_flow(flow_config.dict(), input_dict)
        return response

    async def get(self, flow_name: str) -> Flow:
        version = None
        if len(flow_name.split("/")) > 2:
            version = flow_name.split("/")[-1]
        org, name = split_name(flow_name)
        flow_dict = await self.console.get_flow(org, name, version)
        return Flow(flow_name, FlowConfig(flow_dict.get('config')), flow_dict.get('private'), flow_dict.get('version'))

    async def get_by_author(self, author_name: str) -> list[Flow]:
        if len(author_name) > 1 and author_name[0] == "@":
            author_name = author_name[1:]
        flows_list = await self.console.get_flows_by_author(author_name)
        return flows_list
        # return [Flow(f"{flow['org']}/{flow[' name']}", FlowConfig(flow.get('config', {}))) for flow in flows_list]

    async def deploy(self, flow: Flow):
        if len(flow.org) > 1 and flow.org[0] == "@":
            flow.org = flow.org[1:]
        response = await self.console.deploy_flow(flow.org, flow.name, flow.config.dict(), flow.private, flow.version)
        return response

class KnowledgeOperations:
    def __init__(self, console):
        self.console = console

    async def add(self, knowledge_name: str, absolute_file_path: str):
        org, knowledge_name = split_name(knowledge_name)

        if not os.path.exists(absolute_file_path):
            raise FileNotFoundError(f"The file {absolute_file_path} does not exist.")

        if not os.access(absolute_file_path, os.R_OK):
            raise PermissionError(f"The file {absolute_file_path} is not readable.")

        max_size = 200 * 1024 * 1024  # 200MB in bytes
        if os.path.getsize(absolute_file_path) > max_size:
            raise ValueError(f"The file {absolute_file_path} exceeds the maximum allowed size of 200MB.")

        allowed_types = ['.csv', '.txt', '.pdf', '.md']
        file_extension = os.path.splitext(absolute_file_path)[1].lower()
        if file_extension not in allowed_types:
            raise ValueError(f"Unsupported file type. Allowed types are: {', '.join(allowed_types)}")

        return await self.console.add_knowledge(absolute_file_path, org, knowledge_name)

    async def get_context_for_prompt(self, knowledge_name: str, prompt_text: str):
        org, knowledge_name = split_name(knowledge_name)
        response = await self.console.get_knowledge_context_for_prompt(org, knowledge_name, prompt_text)
        return response

class AsyncMiraClient:
    def __init__(self, config=None):
        self.config = config or {}
        self.console = AsyncConsole(self.config.get("API_KEY"))
        self.prompt = PromptOperations(self.console)
        self.flow = FlowOperations(self.console)
        self.knowledge = KnowledgeOperations(self.console)
