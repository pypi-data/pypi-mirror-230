from typing import Awaitable
from urllib.parse import quote_plus

from sensenova.api_resources.abstract.api_resource import APIResource


class DeletableAPIResource(APIResource):
    @classmethod
    def __prepare_delete(cls, sid):
        if isinstance(cls, APIResource):
            raise ValueError(".delete may only be called as a class method now.")

        base = cls.class_url()
        extn = quote_plus(sid)

        url = "%s/%s" % (base, extn)
        return url

    @classmethod
    def delete(cls, sid, **params):
        url = cls.__prepare_delete(sid)

        return cls._static_request(
            "delete", url, **params
        )

    @classmethod
    def adelete(cls, sid, **params) -> Awaitable:
        url = cls.__prepare_delete(sid)

        return cls._astatic_request(
            "delete", url, **params
        )
