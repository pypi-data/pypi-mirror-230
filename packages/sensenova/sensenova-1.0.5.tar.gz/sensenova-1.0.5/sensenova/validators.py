import json
import os
import sys
from typing import Any, Callable, NamedTuple, Optional


class Remediation(NamedTuple):
    name: str
    immediate_msg: Optional[str] = None
    necessary_msg: Optional[str] = None
    necessary_fn: Optional[Callable[[Any], Any]] = None
    optional_msg: Optional[str] = None
    optional_fn: Optional[Callable[[Any], Any]] = None
    error_msg: Optional[str] = None


def clean_data(metas):
    input_set = set()
    new_metas = []
    error_msg = None
    immediate_msg = None
    for meta in metas:
        if ("instruction" not in meta) or ("input" not in meta):
            error_msg = '[ERROR] Training item must have keys of instruction and input!!!'
        if "output" not in meta:
            error_msg = '[ERROR] Training item must have an output!!!'
            break
        if (meta['instruction'] + '###' + meta['input']) not in input_set:
            new_metas.append(meta)
            input_set.add(meta['instruction'] + '###' + meta['input'])
    if not error_msg:
        immediate_msg = f"Data length before clean: {len(metas)}\nData length after clean length: {len(new_metas)}\n"
    return new_metas, Remediation(name="num_examples", immediate_msg=immediate_msg, error_msg=error_msg)


def read_any_format(fname):
    remediation = None
    necessary_msg = None
    immediate_msg = None
    error_msg = None
    metas = None

    if os.path.isfile(fname):
        try:
            metas = json.load(open(fname, 'r'))
        except Exception:
            error_msg = f"Your file {fname} cannot be loaded in json format"
    else:
        error_msg = f"File {fname} does not exist."

    remediation = Remediation(
        name="read_any_format",
        necessary_msg=necessary_msg,
        immediate_msg=immediate_msg,
        error_msg=error_msg,
    )
    return metas, remediation


def apply_necessary_remediation(metas, remediation):
    if remediation.error_msg is not None:
        sys.stderr.write(
            f"\n\nERROR in {remediation.name}: {remediation.error_msg}\n\nAborting..."
        )
        sys.exit(1)
    if remediation.immediate_msg is not None:
        sys.stdout.write(remediation.immediate_msg)
    if remediation.necessary_fn is not None:
        metas = remediation.necessary_fn(metas)
    return metas


def get_processors():
    return [
        clean_data
    ]


def write_out_file(metas, fname):
    new_fname = f'cleaned_{os.path.basename(fname)}'
    json.dump(metas, open(new_fname, 'w', encoding='utf-8'), ensure_ascii=False)
    sys.stdout.write(f"The processed data is saved as {new_fname}\n")


def apply_processors(metas, fname, processors, write_out_file_func):
    for process in processors:
        metas, remediation = process(metas)
        metas = apply_necessary_remediation(metas, remediation)

    write_out_file_func(metas, fname)
