from sensenova import api_requestor, util, error
from sensenova.api_resources.abstract.api_resource import APIResource


class CreatableAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def __prepare_create_requestor(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base,
        )

        url = cls.class_url()
        return requestor, url

    @classmethod
    def create(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor, url = cls.__prepare_create_requestor(
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
    async def acreate(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor, url = cls.__prepare_create_requestor(
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
