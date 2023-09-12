from urllib.parse import quote_plus
import json
from typing import cast
from urllib.parse import quote_plus

import sensenova

from sensenova import api_requestor, util
from sensenova.api_resources.abstract.api_resource import APIResource


class DownloadableAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def __prepare_file_download(
        cls,
        id,
        file_id,
        access_key_id=None,
        secret_access_key=None,
        api_base=None
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base or sensenova.api_base,
        )
        url = f"{cls.class_url()}/{quote_plus(id)}/files/{file_id}"

        return requestor, url

    @classmethod
    def download(
        cls,
        id,
        file_id,
        access_key_id=None, secret_access_key=None,
        api_base=None
    ):
        requestor, url = cls.__prepare_file_download(
            id, file_id, access_key_id, secret_access_key, api_base
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

    # @classmethod
    # async def adownload(
    #     cls,
    #     id,
    #     file_id,
    #     access_key_id=None, secret_access_key=None,
    #     api_base=None
    # ):
    #     requestor, url = cls.__prepare_file_download(
    #         id, file_id, access_key_id, secret_access_key, api_base
    #     )
    #     async with api_requestor.aiohttp_session() as session:
    #         result = await requestor.arequest_raw("get", url, session)
    #         if not 200 <= result.status < 300:
    #             raise requestor.handle_error_response(
    #                 result.content,
    #                 result.status,
    #                 json.loads(cast(bytes, result.content)),
    #                 result.headers,
    #                 stream_error=False,
    #             )
    #         return result.content
