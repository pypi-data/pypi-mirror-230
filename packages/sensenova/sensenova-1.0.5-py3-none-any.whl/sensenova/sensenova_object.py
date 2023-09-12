import json
from copy import deepcopy
from typing import Optional

from sensenova import util, api_requestor


class SensenovaObject(dict):
    api_base_override = None

    def __init__(
        self,
        id=None,
        access_key_id=None,
        secret_access_key=None,
        api_base=None,
        **params,
    ):
        super(SensenovaObject, self).__init__()

        self._retrieve_params = params

        object.__setattr__(self, "access_key_id", access_key_id)
        object.__setattr__(self, "secret_access_key", secret_access_key)
        object.__setattr__(self, "api_base_override", api_base)
        if id:
            self["id"] = id

    def __setattr__(self, k, v):
        if k[0] == "_" or k in self.__dict__:
            return super(SensenovaObject, self).__setattr__(k, v)

        self[k] = v
        return None

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)
        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __delattr__(self, k):
        if k[0] == "_" or k in self.__dict__:
            return super(SensenovaObject, self).__delattr__(k)
        else:
            del self[k]

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                "You cannot set %s to an empty string. "
                "We interpret empty strings as None in requests."
                "You may set %s.%s = None to delete the property" % (k, str(self), k)
            )
        super(SensenovaObject, self).__setitem__(k, v)

    def __delitem__(self, k):
        raise NotImplementedError("del is not supported")

    def __setstate__(self, state):
        self.update(state)

    def __reduce__(self):
        reduce_value = (
            type(self),
            (
                self.get("id", None),
                self.access_key_id, self.secret_access_key
            ),
            dict(self)
        )
        return reduce_value

    @classmethod
    def construct_from(
        cls,
        values,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ):
        instance = cls(
            values.get("id"),
            access_key_id=access_key_id, secret_access_key=secret_access_key
        )
        instance.refresh_from(
            values,
            access_key_id=access_key_id, secret_access_key=secret_access_key,
        )
        return instance

    def refresh_from(
        self,
        values,
        access_key_id=None,
        secret_access_key=None
    ):
        self.access_key_id = access_key_id or getattr(values, "access_key_id", None)
        self.secret_access_key = secret_access_key or getattr(values, "secret_access_key", None)

        self.clear()
        for k, v in values.items():
            super(SensenovaObject, self).__setitem__(
                k, util.convert_to_sensenova_object(v, access_key_id, secret_access_key)
            )

        self._previous = values

    @classmethod
    def api_base(cls):
        return None

    def request(
        self,
        method,
        url,
        params=None,
        headers=None,
        stream=False,
        plain_old_data=False
    ):
        if params is None:
            params = self._retrieve_params

        requestor = api_requestor.APIRequestor(
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            api_base=self.api_base_override or self.api_base(),
        )

        response, stream, access_key_id, secret_access_key = requestor.request(
            method,
            url,
            params=params,
            stream=stream,
            headers=headers
        )

        if stream:
            assert not isinstance(response, SensenovaObject)
            return (
                util.convert_to_sensenova_object(
                    line,
                    access_key_id,
                    secret_access_key,
                    plain_old_data=plain_old_data
                )
                for line in response
            )
        else:
            return util.convert_to_sensenova_object(
                response,
                access_key_id, secret_access_key,
                plain_old_data=plain_old_data
            )

    async def arequest(
        self,
        method,
        url,
        params=None,
        headers=None,
        stream=False,
        plain_old_data=False
    ):
        if params is None:
            params = self._retrieve_params

        requestor = api_requestor.APIRequestor(
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            api_base=self.api_base_override or self.api_base(),
        )

        response, stream, access_key_id, secret_access_key = await requestor.arequest(
            method,
            url,
            params=params,
            stream=stream,
            headers=headers
        )

        if stream:
            assert not isinstance(response, SensenovaObject)
            return (
                util.convert_to_sensenova_object(
                    line,
                    access_key_id, secret_access_key,
                    plain_old_data=plain_old_data
                )
                for line in response
            )
        else:
            return util.convert_to_sensenova_object(
                response,
                access_key_id, secret_access_key,
                plain_old_data=plain_old_data
            )

    def __copy__(self):
        copied = SensenovaObject(
            self.get("id"),
            self.access_key_id, self.secret_access_key
        )

        copied._retrieve_params = self._retrieve_params

        for k, v in self.items():
            super(SensenovaObject, copied).__setitem__(k, v)

        return copied

    def __deepcopy__(self, memo):
        copied = self.__copy__()
        memo[id(self)] = copied

        for k, v in self.items():
            super(SensenovaObject, copied).__setitem__(k, deepcopy(v, memo))

        return copied

    def __repr__(self):
        ident_parts = [type(self).__name__]

        obj = self.get("object")
        if isinstance(obj, str):
            ident_parts.append(obj)

        if isinstance(self.get("id"), str):
            ident_parts.append("id=%s" % (self.get("id"),))

        unicode_repr = "<%s at %s> JSON: %s" % (
            " ".join(ident_parts),
            hex(id(self)),
            str(self),
        )

        return unicode_repr

    def __str__(self):
        obj = self.to_dict_recursive()
        return json.dumps(obj, sort_keys=True, indent=2)

    def to_dict(self):
        return dict(self)

    def to_dict_recursive(self):
        d = dict(self)
        for k, v in d.items():
            if isinstance(v, SensenovaObject):
                d[k] = v.to_dict_recursive()
            elif isinstance(v, list):
                d[k] = [
                    e.to_dict_recursive() if isinstance(e, SensenovaObject) else e
                    for e in v
                ]
        return d
