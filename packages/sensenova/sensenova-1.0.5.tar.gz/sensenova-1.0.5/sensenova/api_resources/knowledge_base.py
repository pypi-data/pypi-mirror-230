import json
from urllib.parse import quote_plus
from typing import cast
import sensenova
from sensenova import api_requestor, util

from sensenova.api_resources.abstract import DeletableAPIResource, ListableAPIResource, CreatableAPIResource, FileableAPIResource, DownloadableAPIResource, UploadableAPIResource, FileDeletableAPIResource, \
    UpdateableAPIResource


class KnowledgeBase(ListableAPIResource, DeletableAPIResource, CreatableAPIResource, DownloadableAPIResource, UploadableAPIResource, FileableAPIResource, FileDeletableAPIResource,
                    UpdateableAPIResource):
    OBJECT_NAME = "llm.knowledge-bases"
