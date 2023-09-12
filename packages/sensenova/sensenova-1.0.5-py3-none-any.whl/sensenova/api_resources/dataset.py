import json
from typing import cast
from urllib.parse import quote_plus

import sensenova
from sensenova import api_requestor, util
from sensenova.api_resources.abstract import DeletableAPIResource, ListableAPIResource, CreatableAPIResource, FileableAPIResource, DownloadableAPIResource, UploadableAPIResource, UpdateableAPIResource


class Dataset(ListableAPIResource, DeletableAPIResource, CreatableAPIResource, FileableAPIResource, DownloadableAPIResource, UploadableAPIResource,UpdateableAPIResource):
    OBJECT_NAME = "llm.fine-tune.datasets"
