from typing import Optional
import requests
import logging
from mira_sdk.mira.constants import CONSOLE_BFF_URL

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class Console:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = CONSOLE_BFF_URL

    def _request(self, method, path, query_params=None, json_data=None, files=None, data=None):
        url = f"{self.base_url}/{path}"
        headers = {
            "MiraAuthorization": f"{self.api_key}",
        }

        try:
            response = requests.request(
                method,
                url,
                params=query_params,
                json=json_data,
                data=data,
                headers=headers,
                files=files
            )
            if response.status_code != 200:
                raise Exception(f"Response status: {response.status_code}, detail: {response.json() if response.headers.get('content-type') == 'application/json' else response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle any request-related errors
            logging.error(f"An error occurred: {e}")
            return None

    def create_prompt(self, author_name, prompt_name, version, content, variables):
        path = f"v1/prompts/"
        json_data = {
            "name": prompt_name,
            "author_name": author_name,
            "content": content,
            "variables": variables,
            "version": version
        }
        return self._request(method="post", path=path, json_data=json_data)

    def add_prompt_version(self, prompt_id, version, content, variables):
        path = f"v1/prompts/version"
        json_data = {
            "prompt_id": prompt_id,
            "content": content,
            "variables": variables,
            "version": version
        }
        return self._request(method="post", path=path, json_data=json_data)

    def update_prompt(self, author_name, prompt_name):
        path = f"v1/prompts/"
        json_data = {
            "name": prompt_name,
            "author_name": author_name
        }
        return self._request(method="post", path=path, json_data=json_data)

    def get_prompt_version(self, author_name: str, prompt_name: str, version=None):
        path = f"v1/prompts/{author_name}/{prompt_name}"
        params = {}
        if version:
            params["version"] = version
        return self._request(method="get", path=path, query_params=params).get("data")

    def execute_flow(self, author_name, flow_name, input_dict, version, flow_type, composio_config):
        path = f"v1/flows/flows/{author_name}/{flow_name}"

        json_data = {
            "input": input_dict,
        }
        if composio_config is not None:
            json_data["composio_config"] = composio_config.dict()
            
        params = {}
        if version:
            params = {
                "version": version,
                "type": flow_type
            }

        return self._request(method="post", path=path, json_data=json_data, query_params=params)

    def run_flow(self, flow_config, input_dict, composio_config):

        path = f"v1/flows/flows/run"
        json_data = {
            "flow_config": flow_config,
            "input": input_dict,
        }
        if composio_config is not None:
            json_data["composio_config"] = composio_config.dict()
        return self._request(method="post", path=path, json_data=json_data)

    def get_flow(self, author_name, flow_name, version):
        path = f"v1/flows/flows/{author_name}/{flow_name}"
        params = {}
        if version:
            params = {
                "version": version
        }
        return self._request(method="get", path=path, query_params=params).get("data")
    # TODO: Improve data return through request

    def get_yaml_flow(self, author_name, flow_name, version):
        path = f"v1/flows/yaml/{author_name}/{flow_name}"
        params = {}
        if version:
            params = {
                "version": version
        }
        return self._request(method="get", path=path, query_params=params).get("data")

    def get_flows_by_author(self, author_name):
        path = f"v1/flows/flows/{author_name}"
        return self._request(method="get", path=path).get("data")
    # TODO: Improve data return through request

    def get_flows_by_tag(self, tag: str, user_id: str = None):
        path = f"v1/flows/flows_tag/tag_search"
        params = {"tag": tag}
        if user_id:
            params["user_id"] = user_id
        return self._request(method="get", path=path, query_params=params)

    def search_flow(self, query: str):
        path = f"v1/flows/flows_keyword/flow_search"
        params = {"keyword": query}
        return self._request(method="get", path=path, query_params=params)

    def get_all_versions_by_flow(self, author_name, flow_name):
        path = f"v1/flows/flows/{author_name}/{flow_name}/versions"
        return self._request(method="get", path=path)

    def deploy_flow(self, author_name, flow_name, flow_config, version=None, flow_type="PRIMITIVE"):
        path = f"v1/flows/deploy/{author_name}/{flow_name}"
        json_data = {
            "flow": flow_config,
            "type": flow_type
        }
        if version:
            params = {
                "version": version
            }
            return self._request(method="post", path=path, json_data=json_data, query_params=params)
        return self._request(method="post", path=path, json_data=json_data)

    def get_prompts_by_author(self, author_name):
        path = f"v1/prompts/{author_name}"
        return self._request(method="get", path=path).get("data")

    def get_all_versions_by_prompt(self, prompt_id):
        if prompt_id is None:
            raise Exception("Prompt ID not found for this prompt")
        path = f"v1/prompts/{prompt_id}/versions"
        return self._request(method="get", path=path).get("data")

    def add_knowledge_from_file(self, file_path, author_name, knowledge_name):
        path = "v1/knowledge/upload/"
        files = {'file': open(file_path, 'rb')}
        data = {
            'author_name': author_name,
            'name': knowledge_name
        }
        return self._request(method="post", path=path, files=files, data=data)

    def add_knowledge_from_url(self, url, author_name, knowledge_name):
        path = "v1/knowledge/process_url/"
        data = {
            'author_name': author_name,
            'name': knowledge_name,
            'url': url
        }
        return self._request(method="post", path=path, json_data=data)

    def create_dataset(self, author_name: str, dataset_name: str, description: Optional[str] = None):
        path = "v1/knowledge/create/"
        json_data = {
            "name": dataset_name,
            "author_name": author_name,
            "description": description
        }
        return self._request(method="post", path=path, json_data=json_data)

    def get_knowledge_context_for_prompt(self, author_name: str, knowledge_name: str, prompt_text: str):
        path = f"v1/knowledge/{author_name}/{knowledge_name}"
        params = {}
        if prompt_text:
            params["prompt"] = prompt_text
        return self._request(method="get", path=path, query_params=params)
