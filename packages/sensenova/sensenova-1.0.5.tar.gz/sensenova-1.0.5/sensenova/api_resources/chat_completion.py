from sensenova import error
from sensenova.api_resources.abstract import EngineAPIResource


class ChatCompletion(EngineAPIResource):
    OBJECT_NAME = "llm.chat-completions"

    @classmethod
    def create(cls, *args, **kwargs):
        messages = kwargs.get("messages", None)

        if not messages:
            raise error.InvalidRequestError(
                "The parameter messages is required"
            )
        return super().create(*args, **kwargs)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        messages = kwargs.get("messages", None)

        if not messages:
            raise error.InvalidRequestError(
                "The parameter messages is required"
            )

        return await super().acreate(*args, **kwargs)
