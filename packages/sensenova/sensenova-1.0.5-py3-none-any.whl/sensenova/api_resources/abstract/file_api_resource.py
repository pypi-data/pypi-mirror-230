import json
from typing import cast
from yarl import URL
import sensenova
from sensenova import api_requestor, util
from sensenova.api_resources.abstract.api_resource import APIResource


class FileDownloadAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def __prepare_file_download(
            cls,
            id,
            access_key_id=None,
            secret_access_key=None,
            api_base=None
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base or sensenova.api_base_file,
        )
        url = f"{cls.class_url()}/{id}/content"

        return requestor, url

    @classmethod
    def download(
            cls,
            id,
            access_key_id=None, secret_access_key=None,
            api_base=None
    ):
        requestor, url = cls.__prepare_file_download(
            id, access_key_id, secret_access_key, api_base
        )

        result = requestor.request_raw("get", url)
        if not 200 <= result.status_code < 300:
            raise requestor.handle_error_response(
                result.content,
                result.status_code,
                json.loads(cast(bytes, result.content)),
                result.headers,
                stream_error=False,
            )
        return result.content

    @classmethod
    async def adownload(
            cls,
            id,
            access_key_id=None, secret_access_key=None,
            api_base=None
    ):
        requestor, url = cls.__prepare_file_download(
            id, access_key_id, secret_access_key, api_base
        )

        async with api_requestor.aiohttp_session() as session:
            result = await requestor.arequest_raw("get", url, session, allow_redirects=False)
            if result.status == 302:
                # 获取Location头
                file_url = result.headers["Location"]
                request_kwargs = {
                    "method": "get",
                    "url": URL(file_url,encoded=True),
                    "allow_redirects": True,
                }
                result = await session.request(**request_kwargs)
            reader = result.content
            content = await reader.read(-1)
            if not 200 <= result.status < 300:
                raise requestor.handle_error_response(
                    content,
                    result.status,
                    json.loads(cast(bytes, content)),
                    result.headers,
                    stream_error=False,
                )
            return content


class FileCreateAPIResource(APIResource):
    @classmethod
    def __prepare_file_create(
            cls,
            access_key_id=None,
            secret_access_key=None,
            api_base=None
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base or sensenova.api_base_file,
        )
        url = cls.class_url()

        return requestor, url

    @classmethod
    def create(
            cls,
            file,
            access_key_id=None,
            secret_access_key=None,
            api_base=None,
            **params
    ):
        requestor, url = cls.__prepare_file_create(
            access_key_id, secret_access_key, api_base
        )
        files = [("file", ("file", file, "application/octet-stream"))]
        response, _, access_key_id, secret_access_key = requestor.request("post", url, files=files, params=params)

        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )

    @classmethod
    async def acreate(
            cls,
            file,
            access_key_id=None,
            secret_access_key=None,
            api_base=None,
            **params
    ):
        requestor, url = cls.__prepare_file_create(
            access_key_id, secret_access_key, api_base
        )
        files = [("file", ("file", file, "application/octet-stream"))]

        response, _, access_key_id, secret_access_key = \
            await requestor.arequest("post", url, files=files, params=params)

        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )
