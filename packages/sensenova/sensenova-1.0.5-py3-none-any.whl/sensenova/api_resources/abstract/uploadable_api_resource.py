from sensenova import api_requestor, util
from sensenova.api_resources.abstract.api_resource import APIResource


class UploadableAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def __prepare_upload_file(
        cls,
        aoss_url,
        file,
        access_key_id=None,
        secret_access_key=None,
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=aoss_url[:12],
        )
        json_data = file.read()
        if hasattr(json_data, 'encode'):
            json_data = json_data.encode()
        return requestor, aoss_url[12:], json_data

    @classmethod
    def upload_file(
        cls,
        aoss_url,
        file,
        access_key_id=None,
        secret_access_key=None,
        **params
    ):
        requestor, url, content = cls.__prepare_upload_file(
            aoss_url, file, access_key_id, secret_access_key
        )

        response, _, access_key_id, secret_access_key = requestor.request(
            "put", url, params=content
        )
        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )

    @classmethod
    async def aupload_file(
        cls,
        aoss_url,
        file,
        access_key_id=None,
        secret_access_key=None,
        **params
    ):
        requestor, url, content = cls.__prepare_upload_file(
            aoss_url, file, access_key_id, secret_access_key
        )

        response, _, access_key_id, secret_access_key = await requestor.arequest(
            "put", url, params=content
        )
        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )
