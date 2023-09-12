from sensenova import api_requestor, util
from sensenova.api_resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):
    @classmethod
    def auto_paging_iter(cls, *args, **params):
        return cls.list(*args, **params).auto_paging_iter()

    @classmethod
    def __prepare_list_requestor(cls, access_key_id=None, secret_access_key=None, api_base=None):
        requestor = api_requestor.APIRequestor(
            access_key_id,secret_access_key,
            api_base=api_base or cls.api_base()
        )

        url = cls.class_url()
        return requestor, url

    @classmethod
    def list(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor, url = cls.__prepare_list_requestor(
            access_key_id, secret_access_key,
            api_base
        )

        response, _, access_key_id, secret_access_key = requestor.request(
            "get", url, params
        )

        sensenova_object = util.convert_to_sensenova_object(
            response, access_key_id, secret_access_key
        )

        # sensenova_object._retrieve_params = params
        return sensenova_object


    @classmethod
    async def alist(
        cls,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor, url = cls.__prepare_list_requestor(
            access_key_id, secret_access_key,
            api_base
        )

        response, _, access_key_id, secret_access_key = await requestor.arequest(
            "get", url, params
        )

        sensenova_object = util.convert_to_sensenova_object(
            response, access_key_id, secret_access_key
        )

        # sensenova_object._retrieve_params = params
        return sensenova_object