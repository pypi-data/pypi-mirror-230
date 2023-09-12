from sensenova.api_resources.abstract import ListableAPIResource, DeletableAPIResource


class Model(ListableAPIResource, DeletableAPIResource):
    OBJECT_NAME = "llm.models"

