import requests
import aiohttp
import logging
from mira_sdk.mira.constants import CONSOLE_BFF_URL

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class AsyncConsole:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = CONSOLE_BFF_URL

    async def _request(self, method, path, query_params=None, json_data=None, files=None, data=None):
        url = f"{self.base_url}/{path}"
        headers = {
            "MiraAuthorization": f"{self.api_key}",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    url,
                    params=query_params,
                    json=json_data,
                    data=data,
                    headers=headers,
                    # Note: handling file uploads with aiohttp requires a different approach
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise Exception(f"Response status: {response.status}, detail: {text}")
                    return await response.json()
            except aiohttp.ClientError as e:
                logging.error(f"An error occurred: {e}")
                return None

    async def create_prompt(self, author_name, prompt_name, version, content, variables):
        path = f"v1/prompts/"
        json_data = {
            "name": prompt_name,
            "author_name": author_name,
            "content": content,
            "variables": variables,
            "version": version
        }
        response = await self._request(method="post", path=path, json_data=json_data)
        return response

    async def add_prompt_version(self, prompt_id, version, content, variables):
        path = f"v1/prompts/version"
        json_data = {
            "prompt_id": prompt_id,
            "content": content,
            "variables": variables,
            "version": version
        }
        response = await self._request(method="post", path=path, json_data=json_data)
        return response

    async def update_prompt(self, author_name, prompt_name):
        path = f"v1/prompts/"
        json_data = {
            "name": prompt_name,
            "author_name": author_name
        }
        response = await self._request(method="post", path=path, json_data=json_data)
        return response

    async def get_prompt_version(self, author_name: str, prompt_name: str, version=None):
        path = f"v1/prompts/{author_name}/{prompt_name}"
        params = {}
        if version:
            params["version"] = version
        response = await self._request(method="get", path=path, query_params=params)
        return response.get("data")

    async def execute_flow(self, author_name, flow_name, input_dict, version):
        path = f"v1/flows/flows/{author_name}/{flow_name}"
        params = {
            "version": version
        }
        response = await self._request(method="post", path=path, json_data=input_dict, query_params=params)
        return response

    async def run_flow(self, flow_config, input_dict):
        path = f"v1/flows/flows/run"
        json_data = {
            "flow_config": flow_config,
            "input": input_dict
        }
        response = await self._request(method="post", path=path, json_data=json_data)
        return response

    async def get_flow(self, author_name, flow_name, version):
        path = f"v1/flows/flows/{author_name}/{flow_name}"
        params = {}
        if version:

            params = {
                "version": version
            }
        response = await self._request(method="get", path=path, query_params=params)
        return response.get("data")

    async def get_flows_by_author(self, author_name):
        path = f"v1/flows/flows/{author_name}"
        response = await self._request(method="get", path=path)
        return response.get("data")

    async def deploy_flow(self, author_name, flow_name, flow_config, is_private, version):
        path = f"v1/flows/deploy/{author_name}/{flow_name}"
        json_data = {
            "flow": flow_config,
            "private": is_private
        }
        if version:
            params = {
                "version": version
            }
            response = await self._request(method="post", path=path, json_data=json_data, query_params=params)
            return response
        response = await self._request(method="post", path=path, json_data=json_data)
        return response

    async def get_prompts_by_author(self, author_name):
        path = f"v1/prompts/{author_name}"
        response = await self._request(method="get", path=path)
        return response.get("data")

    async def get_all_versions_by_prompt(self, prompt_id):
        if prompt_id is None:
            raise Exception("Prompt ID not found for this prompt")
        path = f"v1/prompts/{prompt_id}/versions"
        response = await self._request(method="get", path=path)
        return response.get("data")

    async def add_knowledge(self, file_path, author_name, knowledge_name):
        path = "v1/knowledge/upload"
        files = {'file': open(file_path, 'rb')}
        data = {
            'author_name': author_name,
            'knowledge_name': knowledge_name
        }
        response = await self._request(method="post", path=path, files=files, data=data)
        return response

    async def get_knowledge_context_for_prompt(self, author_name: str, knowledge_name: str, prompt_text: str):
        path = f"v1/knowledge/{author_name}/{knowledge_name}"
        params = {}
        if prompt_text:
            params["prompt"] = prompt_text
        response = await self._request(method="get", path=path, query_params=params)
        return response.get("data")

