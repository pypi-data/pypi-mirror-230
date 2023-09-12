import sensenova
from sensenova.api_resources.abstract import ListableAPIResource, DeletableAPIResource, FileDownloadAPIResource, \
    FileCreateAPIResource


class File(ListableAPIResource, DeletableAPIResource, FileDownloadAPIResource, FileCreateAPIResource):
    OBJECT_NAME = "files"

    @classmethod
    def list(cls, **params):
        return super().list(api_base=sensenova.api_base_file, **params)

    @classmethod
    async def alist(cls, **params):
        return await super().alist(api_base=sensenova.api_base_file, **params)

    @classmethod
    def delete(cls, id: str, **params):
        return super().delete(api_base=sensenova.api_base_file, sid=id, **params)

    @classmethod
    async def adelete(cls, id: str, **params):
        return await super().adelete(api_base=sensenova.api_base_file, sid=id, **params)

    @classmethod
    def retrieve(cls, id: str, **params):
        return super().retrieve(api_base=sensenova.api_base_file, id=id, **params)

    @classmethod
    async def aretrieve(cls, id: str, **params):
        return await super().aretrieve(api_base=sensenova.api_base_file, id=id, **params)

    @classmethod
    def download(cls, id: str, **params):
        return super().download(api_base=sensenova.api_base_file, id=id, **params)

    @classmethod
    async def adownload(cls, id: str, **params):
        return await super().adownload(api_base=sensenova.api_base_file, id=id, **params)

    @classmethod
    def create(cls, file, **params):
        return super().create(file, **params)

    @classmethod
    async def acreate(cls, file, **params):
        return await super().acreate(file, **params)
