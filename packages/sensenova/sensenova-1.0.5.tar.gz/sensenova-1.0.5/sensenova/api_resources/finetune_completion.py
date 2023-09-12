from sensenova import error
from sensenova.api_resources.abstract import EngineAPIResource

class FinetuneCompletion(EngineAPIResource):
    OBJECT_NAME = "nlp.finetune.completions"

    @classmethod
    def create(cls, *args, **kwargs):
        text = kwargs.get("text", None)
        model_id = kwargs.get("model_id", None)

        if not text:
            raise error.InvalidRequestError(
                "The parameter text is required"
            )

        if not model_id:
            raise error.InvalidRequestError(
                "The parameter model_id is required"
            )

        return super().create(*args, **kwargs)


    @classmethod
    async def acreate(cls, *args, **kwargs):
        text = kwargs.get("text", None)
        model_id = kwargs.get("model_id", None)

        if not text:
            raise error.InvalidRequestError(
                "The parameter text is required"
            )

        if not model_id:
            raise error.InvalidRequestError(
                "The parameter model_id is required"
            )

        return await super().acreate(*args, **kwargs)