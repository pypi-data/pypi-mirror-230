import time

import sensenova
import io
import json


def test_file_list():
    result = sensenova.File.list()
    print(result)


def test_file_delete(id: str = "7007c025-d5a8-4b35-a4de-23ae4fe1c1fc"):
    result = sensenova.File.delete(id)
    print(result)


def test_file_retrieve(id: str = "7007c025-d5a8-4b35-a4de-23ae4fe1c1fc"):
    result = sensenova.File.retrieve(id)
    print(result)
    return result


def test_file_download(id: str = "7007c025-d5a8-4b35-a4de-23ae4fe1c1fc"):
    result = sensenova.File.download(id)
    print(result.decode("utf-8"))


def test_file_create():
    payload = {
        "text_lst": [
            "xxx",
            "xxx"
        ]
    }
    result = sensenova.File.create(file=io.StringIO(json.dumps(payload, ensure_ascii=False)),
                                   scheme="KNOWLEDGE_BASE_1",
                                   description="测试知识库文件")
    print(result)
    return result["id"]


def test_file_create_finetune():
    payload = [
        {
            "instruction": "测试指令",
            "input": "",
            "output": "测试输出"
        }
    ]
    result = sensenova.File.create(file=io.StringIO(json.dumps(payload, ensure_ascii=False)),
                                   scheme="FINE_TUNE_1",
                                   description="测试Finetune文件")
    print(result)
    return result["id"]


def test_file_all():
    file_id = test_file_create()
    time.sleep(1)  # rate limit
    test_file_list()
    time.sleep(1)  # rate limit
    count = 0
    while True:
        file_result = test_file_retrieve(file_id)
        if file_result["file"]["status"] == "VALID":
            break
        count += 1
        if count >= 30:
            break
        time.sleep(1)
        print("wait for valid")
    # only valid file can be downloaded
    time.sleep(1)  # rate limit
    test_file_download(file_id)
    time.sleep(1)  # rate limit
    test_file_delete(file_id)