from urllib.parse import quote_plus, urlencode

import sensenova
from sensenova import error, api_requestor, util
from sensenova.sensenova_object import SensenovaObject


class APIResource(SensenovaObject):
    api_prefix = ""

    @classmethod
    def retrieve(cls, id, access_key_id=None, secret_access_key=None, **params):
        instance = cls(id=id, access_key_id=access_key_id, secret_access_key=secret_access_key, **params)
        instance.refresh()
        return instance

    @classmethod
    def aretrieve(
        cls, id, access_key_id=None, secret_access_key=None, request_id=None, request_timeout=None, **params
    ):
        instance = cls(id=id, access_key_id=access_key_id, secret_access_key=secret_access_key, **params)
        return instance.arefresh()

    def refresh(self):
        self.refresh_from(
            self.request(
                "get",
                self.instance_url()
            )
        )
        return self

    async def arefresh(self):
        self.refresh_from(
            await self.arequest(
                "get",
                self.instance_url(),
            )
        )
        return self

    @classmethod
    def class_url(cls):
        if cls == APIResource:
            raise NotImplementedError(
                "APIResource is an abstract class. You should perform actions on its subclasses."
            )

        base = cls.OBJECT_NAME.replace(".", "/")
        if cls.api_prefix:
            return "/%s/%s" % (cls.api_prefix, base)
        return "/%s" % base

    def instance_url(self, operation=None):
        id = self.get("id")

        if not isinstance(id, str):
            raise error.InvalidRequestError(
                "Could not determine which URL to request: %s instance "
                "has invalid ID: %r, %s. ID should be of type `str` (or"
                " `unicode`)" % (type(self).__name__, id, type(id)),
                "id",
            )

        extn = quote_plus(id)
        base = self.class_url()
        return "%s/%s" % (base, extn)

    @classmethod
    def _static_request(
        cls,
        method_,
        url_,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base,
        )
        response, _, access_key_id, secret_access_key = requestor.request(
            method_, url_, params
        )
        return util.convert_to_sensenova_object(response, access_key_id, secret_access_key, )

    @classmethod
    async def _astatic_request(
        cls,
        method_,
        url_,
        access_key_id=None, secret_access_key=None,
        api_base=None,
        **params
    ):
        requestor = api_requestor.APIRequestor(
            access_key_id, secret_access_key,
            api_base=api_base,
        )
        response, _, access_key_id, secret_access_key = await requestor.arequest(
            method_, url_, params
        )
        return response
