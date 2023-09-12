from sensenova import error
from sensenova.api_resources.abstract.createable_api_resource import CreatableAPIResource
from sensenova.api_resources.abstract import EngineAPIResource


class ChatSession(CreatableAPIResource):
    OBJECT_NAME = "llm.chat.sessions"

    @classmethod
    def create(cls, *args, **kwargs):
        if len(kwargs) == 0:
            kwargs = {
                "system_prompt": []
            }
        return super().create(*args, **kwargs)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        return await super().acreate(*args, **kwargs)


class ChatConversation(EngineAPIResource):
    OBJECT_NAME = "llm.chat-conversations"

    @classmethod
    def create(cls, *args, **kwargs):
        content = kwargs.get("content", None)

        if not content:
            raise error.InvalidRequestError(
                "The parameter content is required"
            )
        return super().create(*args, **kwargs)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        content = kwargs.get("content", None)

        if not content:
            raise error.InvalidRequestError(
                "The parameter content is required"
            )

        return await super().acreate(*args, **kwargs)


