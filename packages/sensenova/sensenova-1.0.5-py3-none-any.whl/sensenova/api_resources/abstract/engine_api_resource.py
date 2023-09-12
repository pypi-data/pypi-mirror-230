from typing import Optional
from urllib.parse import quote_plus

from sensenova import api_requestor, util
from sensenova.api_resources.abstract import APIResource
from sensenova.sensenova_response import SensenovaResponse


class EngineAPIResource(APIResource):
    plain_old_data = False

    def __init__(self, engine: Optional[str] = None, **kwargs):
        super().__init__(engine=engine, **kwargs)

    @classmethod
    def class_url(
        cls,
        engine: Optional[str] = None
    ):
        base = cls.OBJECT_NAME.replace(".", "/")
        if engine is None:
            return "/%s" % base
        extn = quote_plus(engine)
        return "/engines/%s/%s" % (extn, base)

    @classmethod
    def __prepare_create_request(
        cls,
        access_key_id=None,
        secret_access_key=None,
        api_base=None,
        **params,
    ):
        stream = params.get("stream", False)
        headers = params.pop("headers", None)
        requestor = api_requestor.APIRequestor(
            access_key_id,
            secret_access_key,
            api_base=api_base
        )
        url = cls.class_url()
        return (
            stream,
            headers,
            requestor,
            url,
            params,
        )

    @classmethod
    def create(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        (
            stream,
            headers,
            requestor,
            url,
            params,
        ) = cls.__prepare_create_request(
            access_key_id, secret_access_key, api_base, **params
        )

        response, _, access_key_id, secret_access_key = requestor.request(
            "post",
            url,
            params=params,
            headers=headers,
            stream=stream,
        )

        if stream:
            assert not isinstance(response, SensenovaResponse)
            return (
                util.convert_to_sensenova_object(
                    line,
                    access_key_id, secret_access_key,
                    plain_old_data=cls.plain_old_data
                )
                for line in response
            )
        else:
            obj = util.convert_to_sensenova_object(
                response,
                access_key_id, secret_access_key,
                plain_old_data=cls.plain_old_data
            )

        return obj

    @classmethod
    async def acreate(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        (
            stream,
            headers,
            requestor,
            url,
            params,
        ) = cls.__prepare_create_request(
            access_key_id, secret_access_key, api_base, **params
        )

        response, _, access_key_id, secret_access_key = await requestor.arequest(
            "post",
            url,
            params=params,
            headers=headers,
            stream=stream,
        )

        if stream:
            assert not isinstance(response, SensenovaResponse)
            return (
                util.convert_to_sensenova_object(
                    line,
                    access_key_id, secret_access_key,
                    plain_old_data=cls.plain_old_data
                )
                async for line in response
            )
        else:
            obj = util.convert_to_sensenova_object(
                response,
                access_key_id, secret_access_key,
                plain_old_data=cls.plain_old_data
            )

        return obj
