class Client:
    def __init__(self, api_key):
        self.api_key = api_key

    def exec(self, flow_name, input):
        raise NotImplementedError("This method should be implemented.")

    async def exec_async(self, flow_name, input):
        raise NotImplementedError("This method should be implemented asynchronously.")
