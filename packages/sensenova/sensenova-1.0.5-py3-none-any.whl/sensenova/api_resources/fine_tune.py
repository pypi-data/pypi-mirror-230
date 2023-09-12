from sensenova.api_resources.abstract import DeletableAPIResource, ListableAPIResource, CreatableAPIResource
from urllib.parse import quote_plus


class FineTune(ListableAPIResource, DeletableAPIResource, CreatableAPIResource):
    OBJECT_NAME = "llm.fine-tunes"

    @classmethod
    def _prepare_cancel(
        cls,
        id,
        access_key_id=None,
        secret_access_key=None,
        **params
    ):
        base = cls.class_url()
        extn = quote_plus(id)

        url = "%s/%s/cancel" % (base, extn)

        instance = cls(id, access_key_id, secret_access_key, **params)
        return instance, url

    @classmethod
    def cancel(cls, id, access_key_id=None, secret_access_key=None, **params):
        instance, url = cls._prepare_cancel(
            id,
            access_key_id,
            secret_access_key,
            **params
        )
        return instance.request("post", url)

    @classmethod
    async def acancel(cls, id, access_key_id=None, secret_access_key=None, **params):
        instance, url = cls._prepare_cancel(
            id,
            access_key_id, secret_access_key,
            **params
        )
        return await instance.arequest("post", url)
