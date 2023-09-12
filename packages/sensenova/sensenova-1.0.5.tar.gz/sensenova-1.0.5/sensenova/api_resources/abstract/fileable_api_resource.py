from urllib.parse import quote_plus

from sensenova import api_requestor, util
from sensenova.api_resources.abstract.api_resource import APIResource


class FileableAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def __prepare_file_requestor(
        cls,
        id: str,
        access_key_id=None, secret_access_key=None,
        api_base=None
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id,
            secret_access_key,
            api_base=api_base,
        )

        url = f"{cls.class_url()}/{quote_plus(id)}/files"
        return requestor, url

    @classmethod
    def add_file(
        cls,
        id: str,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor, url = cls.__prepare_file_requestor(
            id,
            access_key_id, secret_access_key,
            api_base
        )

        response, _, access_key_id, secret_access_key = requestor.request(
            "post", url, params
        )

        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )

    @classmethod
    async def aadd_file(
        cls,
        id,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor, url = cls.__prepare_file_requestor(
            id,
            access_key_id, secret_access_key,
            api_base
        )

        response, _, access_key_id, secret_access_key = await requestor.arequest(
            "post", url, params
        )

        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )
