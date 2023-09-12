from typing import Awaitable
from urllib.parse import quote_plus

from sensenova.api_resources.abstract.api_resource import APIResource


class FileDeletableAPIResource(APIResource):
    @classmethod
    def __prepare_file_delete(cls, sid, file_id):
        if isinstance(cls, APIResource):
            raise ValueError(".delete may only be called as a class method now.")

        base = cls.class_url()
        ext_sid = quote_plus(sid)
        ext_file_id = quote_plus(file_id)

        url = f"{base}/{ext_sid}/files/{ext_file_id}"
        return url
        #　extn: file_id


    @classmethod
    def delete_file(cls, sid, file_id, **params):
        url = cls.__prepare_file_delete(sid, file_id)

        return cls._static_request("delete", url, **params)

    @classmethod
    def adelete_file(cls, sid, file_id, **params):
        url = cls.__prepare_file_delete(sid, file_id)

        return cls._static_request("delete", url, **params)