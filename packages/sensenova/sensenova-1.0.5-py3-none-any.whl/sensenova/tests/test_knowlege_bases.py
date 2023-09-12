import io
import json
from tempfile import NamedTemporaryFile
import sensenova


def test_knowledge_base_add_file(id, description="1Test client??"):
    result = sensenova.KnowledgeBase.add_file(id=id, description=description)
    print(result)
    return result["url"]


def test_knowledge_base_list():
    result = sensenova.KnowledgeBase.list()
    print(result)


def test_knowledge_base_retrieve(id="mrkd"):
    result = sensenova.KnowledgeBase.retrieve(id=id)
    print(result)


def test_knowledge_base_delete(id):
    result = sensenova.KnowledgeBase.delete(sid=id)
    print(result)


def test_knowledge_base_upload(url):
    payload = {
        "qa_lst": [
            {
                "std_q": "xxx",
                "simi_qs": ["xxx", "xxx"],
                "answer": "xxx",
            },
            {
                "std_q": "xxx",
                "simi_qs": ["xxx", "xxx"],
                "answer": "xxx",
            },
        ],
        "text_lst": [
            "xxx",
            "xxx"
        ]
    }

    result = sensenova.KnowledgeBase.upload_file(aoss_url=url, file=io.StringIO(json.dumps(payload, ensure_ascii=False)))
    print(result)


def test_knowledge_base_download(id="mrkd", file_id="1"):
    result = sensenova.KnowledgeBase.download(id=id, file_id=file_id)
    print(result.decode('utf-8'))


def test_knowledge_base_create(description="Test client"):
    result = sensenova.KnowledgeBase.create(description=description)
    print(result)


def test_knowledge_base_create_fileid():
    payload = {
        "text_lst": [
            "xxx",
            "xxx"
        ]
    }
    file_result = sensenova.File.create(file=io.StringIO(json.dumps(payload, ensure_ascii=False)),
                                        description="python test", scheme="KNOWLEDGE_BASE_1",
                                        user_provided_filename="python_test_file.json")
    result = sensenova.KnowledgeBase.create(description="Test Knowledge with file id", files=[file_result["id"]])
    print(result)


def test_knowledge_base_update_fileid():
    payload = {
        "text_lst": [
            "xxx",
            "xxx"
        ]
    }
    file_result = sensenova.File.create(file=io.StringIO(json.dumps(payload, ensure_ascii=False)),
                                        description="python test2", scheme="KNOWLEDGE_BASE_1",
                                        user_provided_filename="python_test_file.json")
    result = sensenova.KnowledgeBase.update(description="Test Knowledge with file id2", files=[file_result["id"]],
                                            sid="s15ee93900bbe4a6db9d38f1ed02e8775")
    print(result)


# test_knowledge_base_list()
if __name__ == "__main__":
    id = "s53df1f33ff8f4cad957dcf6d24365937"
    file_id = "4d97311f90ad4c68a49924979b0a34d8"
    # test_knowledge_base_list()
    # test_knowledge_base_delete(id=id)
    # test_knowledge_base_download(id=id)
    # test_knowledge_base_create()
    # url = test_knowledge_base_add_file(id=id, description="How are YOU!")
    # test_knowledge_base_upload(url)
    # test_knowledge_base_retrieve(id=id)
    # test_knowledge_base_delete(id=id)
    # test_knowledge_base_list()
    # test_knowledge_base_download(id=id, file_id=file_id)
    # print(sensenova.KnowledgeBase.delete(id))
    # print(sensenova.KnowledgeBase.delete_file(sid=id, file_id=file_id))