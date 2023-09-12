import logging
import os
import re
import sys
import time
import jwt
import sensenova.sensenova_object
from sensenova import sensenova_response
import sensenova

SENSENOVA_LOG = os.environ.get("SENSENOVA_LOG")

logger = logging.getLogger("sensenova")


def ak_sk_to_header(access_key_id, secret_access_key):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": access_key_id,
        "exp": int(time.time()) + 1800,  # 有效时间
        "nbf": int(time.time()) - 5  # 签发时间
    }
    token = jwt.encode(payload, secret_access_key, headers=headers)
    return {
        "Authorization": f"Bearer {token}"
    }


def finetune_completions_option_params():
    return [
        ["temperature", "Temperature sampling parameter, the value is (0,2]. Values greater than 1 tend to generate "
                        "more diverse replies, and values less than 1 tend to generate more stable replies. Default "
                        "0.8", True],
        ["top_p", "Kernel sampling parameter, the value is (0,1]."
                  " When decoding and generating tokens, sampling is performed in the minimum token set whose probability"
                  " sum is greater than or equal to top_p. "
                  "Default 0.7", True],
        ["max_new_tokens", "The maximum number of tokens generated. Note: input_tokens + max_new_tokens <= 1512", True],
        ["repetition_penalty", "Repeat penalty factor, 1 means no penalty, "
                               "greater than 1 tends to generate non-repeat token, "
                               "less than 1 tends to generate repeat token."
                               " Default 1", True],
    ]


def fine_tunes_hyperparams():
    # name, help, if eval
    return [
        ["max_steps", "The maximum number of training iterations.", True],
        ["method", "The finetune method.", False],
        ["lr_scheduler_type", "Learning Rate Adjustment Strategy.", False],
        ["learning_rate", "Learning rate.", True],
        ["warmup_ratio", "Warmup iteration ratio.", True],
        ["weight_decay", "Regularized weight decay.", True],
        ["save_steps", "Weight saving iteration interval.", True],
        ["modules_to_save", "Modules that need to be trained and saved.", False],
    ] + fine_tune_lora_params()


def fine_tune_lora_params():
    return [
        ["lora_rank", "The rank of the lora layer.", True],
        ["lora_dropout", "The dropout probability of the lora layer.", True],
        ["lora_alpha", "The regularization strength of the lora layer.", True]
    ]


def logfmt(props):
    def fmt(key, val):
        if hasattr(val, 'decode'):
            val = val.decode("utf-8")

        if not isinstance(val, str):
            val = str(val)

        if re.search(r"\s", val):
            val = repr(val)

        if re.search(r"\s", key):
            key = repr(key)
        return "{key}={val}.".format(key=key, val=val)

    return " ".join([fmt(key, val) for key, val in sorted(props.items())])


def _console_log_level():
    if sensenova.log in ["debug", "info"]:
        return sensenova.log
    elif SENSENOVA_LOG in ["debug", "info"]:
        return SENSENOVA_LOG
    else:
        return None


def log_debug(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)
    logger.debug(msg)


def default_access_key_id() -> str:
    if sensenova.access_key_id is not None:
        return sensenova.access_key_id
    else:
        raise sensenova.error.AuthenticationError(
            "No access key id provided. You can set your access key id in code using 'sensenova.access_key_id = <ACCESS-KEY-ID>', or you can set the environment variable "
            "SENSENOVA_ACCESS_KEY_ID=<ACCESS-KEY-ID>)."
        )


def default_secret_access_key() -> str:
    if sensenova.secret_access_key is not None:
        return sensenova.secret_access_key
    else:
        raise sensenova.error.AuthenticationError(
            "No secret access key id provided. You can set your secret access key in code using 'sensenova.secret_access_key = <SECRET-ACCESS-KEY>', or you can set the environment variable "
            "SENSENOVA_SECRET_ACCESS_KEY=<SECRET-ACCESS-KEY>)."
        )


def get_object_classes():
    from sensenova.object_classes import OBJECT_CLASSES

    return OBJECT_CLASSES


def convert_to_sensenova_object(resp, access_key_id=None, secret_access_key=None, plain_old_data=False):
    if isinstance(resp, sensenova_response.SensenovaResponse):
        resp = resp.data

    if plain_old_data:
        return resp
    elif isinstance(resp, list):
        return [
            convert_to_sensenova_object(
                i, access_key_id, secret_access_key
            )
            for i in resp
        ]
    elif isinstance(resp, dict) and not isinstance(
        resp, sensenova.sensenova_object.SensenovaObject
    ):
        resp = resp.copy()
        klass_name = resp.get("object")
        if isinstance(klass_name, str):
            klass = get_object_classes().get(
                klass_name, sensenova.sensenova_object.SensenovaObject
            )
        else:
            klass = sensenova.sensenova_object.SensenovaObject

        return klass.construct_from(
            resp,
            access_key_id=access_key_id, secret_access_key=secret_access_key
        )
    else:
        return resp


def log_debug(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() == "debug":
        print(msg, file=sys.stderr)
    logger.debug(msg)


def log_info(message, **params):
    msg = logfmt(dict(message=message, **params))
    if _console_log_level() in ["debug", "info"]:
        print(msg, file=sys.stderr)
    logger.info(msg)


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z
