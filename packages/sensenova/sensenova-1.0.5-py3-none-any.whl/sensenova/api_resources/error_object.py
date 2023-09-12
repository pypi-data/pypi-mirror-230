from typing import Optional

from sensenova.sensenova_object import SensenovaObject
from sensenova.util import merge_dicts


class ErrorObject(SensenovaObject):
    def refresh_from(
        self,
        values,
        access_key_id=None,
        secret_access_key=None,
        response_ms: Optional[int] = None,
    ):
        values = merge_dicts({"message": None, "type": None}, values)
        return super(ErrorObject, self).refresh_from(
            values=values,
            access_key_id=access_key_id,
            secret_access_key=access_key_id,
        )