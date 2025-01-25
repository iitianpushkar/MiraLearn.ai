from pydantic import BaseModel


class ComposioConfig(BaseModel):
    COMPOSIO_API_KEY: str
    ACTION:str
    TASK:str
    ENTITY_ID:str
