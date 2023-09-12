from sensenova import api_requestor, util, error
from sensenova.api_resources.abstract.api_resource import APIResource


class UpdateableAPIResource(APIResource):
    plain_old_data = False

    @classmethod
    def __prepare_update_requestor(
            cls,
            sid,
            access_key_id=None, secret_access_key=None,
            api_base=None
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base,
        )

        base = cls.class_url()
        url = "%s/%s" % (base, sid)
        return requestor, url

    @classmethod
    def update(
            cls,
            sid,
            access_key_id=None, secret_access_key=None,
            api_base=None,
            **params
    ):
        requestor, url = cls.__prepare_update_requestor(
            sid,
            access_key_id, secret_access_key,
            api_base
        )

        response, _, access_key_id, secret_access_key = requestor.request(
            "put", url, params
        )

        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )

    @classmethod
    async def aupdate(
            cls,
            sid,
            access_key_id=None, secret_access_key=None,
            api_base=None,
            **params
    ):
        requestor, url = cls.__prepare_update_requestor(
            sid,
            access_key_id, secret_access_key,
            api_base
        )

        response, _, access_key_id, secret_access_key = await requestor.arequest(
            "put", url, params
        )

        return util.convert_to_sensenova_object(
            response,
            access_key_id, secret_access_key,
            plain_old_data=cls.plain_old_data
        )
