import io
import json
import time
from tempfile import NamedTemporaryFile

import sensenova


def test_dataset_add_file(id, description="1Test client??"):
    result = sensenova.Dataset.add_file(id=id, description=description)
    print(result)
    return result["url"]


def test_dataset_list():
    result = sensenova.Dataset.list()
    # for i in range(12):
    #     sensenova.Dataset.delete(sid=result['datasets'][i]['id'])
        # sleep 2s
        # time.sleep(2)
    print(result)


def test_dataset_retrieve(id="mrkd"):
    result = sensenova.Dataset.retrieve(id=id)
    print(result)


def test_dataset_delete(id):
    result = sensenova.Dataset.delete(sid=id)
    print(result)


def test_dataset_upload(url):
    # payload = [
    #     {
    #         "instruction": "我们如何在日常生活中减少用水？",
    #         "input": "",
    #         "output": "1. 使用节水装置，如节水淋浴喷头和水龙头。 \n2. 使用水箱或水桶收集家庭废水，例如洗碗和洗浴。 \n3. 在社区中提高节水意识。 \n4. 检查水管和灌溉系统的漏水情况，并及时修复它们。 \n5. 洗澡时间缩短，使用低流量淋浴头节约用水。 \n6. 收集雨水，用于园艺或其他非饮用目的。 \n7. 刷牙或擦手时关掉水龙头。 \n8. 减少浇水草坪的时间。 \n9. 尽可能多地重复使用灰水（来自洗衣机、浴室水槽和淋浴的水）。 \n10. 只购买能源效率高的洗碗机和洗衣机。"
    #     },
    #     {
    #         "instruction": "编辑文章，使其更吸引读者。",
    #         "input": "自主机器人是计算机控制的机器，被编程执行特定任务而不需要任何人类输入。自主机器人在各个行业中被越来越广泛地应用，从制造业到医疗保健再到安全。",
    #         "output": "自主机器人是计算机控制的机器，被编程执行特定任务而不需要任何人类输入，从而实现了新的效率、精确度和可靠性水平。自主机器人在各个行业中被越来越广泛地应用，从制造业，它们可以使用精度和一致的质量组装复杂的组件，到医疗保健，可以协助进行医疗测试和处理，再到安全，可以监控大面积地区，保障人们和财产的安全。自主机器人还可以减少在危险或有害环境中的错误和增加安全，在工业流程的检查或维修期间等。由于其多样性，自主机器人将彻底改变我们工作方式的方式，使任务变得更加简单、快速，最终更加愉悦。"
    #     }
    # ]

    with open("../../test.json") as file:
        result = sensenova.Dataset.upload_file(aoss_url=url, file=file)
    print(result)


def test_dataset_download(id="mrkd", file_id="1"):
    result = sensenova.Dataset.download(id=id, file_id=file_id)
    print(result.decode('utf-8'))


def test_dataset_create(description="Test client"):
    result = sensenova.Dataset.create(description=description)
    print(result)
    return result["dataset"]["id"]


def test_dataset_create_fileid():
    payload = [
        {
            "instruction": "我们如何在日常生活中减少用水？",
            "input": "",
            "output": "1. 使用节水装置，如节水淋浴喷头和水龙头。 \n2. 使用水箱或水桶收集家庭废水，例如洗碗和洗浴。 \n3. 在社区中提高节水意识。 \n4. 检查水管和灌溉系统的漏水情况，并及时修复它们。 \n5. 洗澡时间缩短，使用低流量淋浴头节约用水。 \n6. 收集雨水，用于园艺或其他非饮用目的。 \n7. 刷牙或擦手时关掉水龙头。 \n8. 减少浇水草坪的时间。 \n9. 尽可能多地重复使用灰水（来自洗衣机、浴室水槽和淋浴的水）。 \n10. 只购买能源效率高的洗碗机和洗衣机。"
        },
        {
            "instruction": "编辑文章，使其更吸引读者。",
            "input": "自主机器人是计算机控制的机器，被编程执行特定任务而不需要任何人类输入。自主机器人在各个行业中被越来越广泛地应用，从制造业到医疗保健再到安全。",
            "output": "自主机器人是计算机控制的机器，被编程执行特定任务而不需要任何人类输入，从而实现了新的效率、精确度和可靠性水平。自主机器人在各个行业中被越来越广泛地应用，从制造业，它们可以使用精度和一致的质量组装复杂的组件，到医疗保健，可以协助进行医疗测试和处理，再到安全，可以监控大面积地区，保障人们和财产的安全。自主机器人还可以减少在危险或有害环境中的错误和增加安全，在工业流程的检查或维修期间等。由于其多样性，自主机器人将彻底改变我们工作方式的方式，使任务变得更加简单、快速，最终更加愉悦。"
        }
    ]
    file_result = sensenova.File.create(file=io.StringIO(json.dumps(payload, ensure_ascii=False)),
                                        description="python test finetune create", scheme="FINE_TUNE_1",
                                        user_provided_filename="python_test_file.json")

    result = sensenova.Dataset.create(description="python test datasets create", files=[file_result["id"]])
    print(result)
    return result["dataset"]["id"]


def test_dataset_update_fileid():
    payload = [
        {
            "instruction": "我们如何在日常生活中减少用水？",
            "input": "",
            "output": "1. 使用节水装置，如节水淋浴喷头和水龙头。 \n2. 使用水箱或水桶收集家庭废水，例如洗碗和洗浴。 \n3. 在社区中提高节水意识。 \n4. 检查水管和灌溉系统的漏水情况，并及时修复它们。 \n5. 洗澡时间缩短，使用低流量淋浴头节约用水。 \n6. 收集雨水，用于园艺或其他非饮用目的。 \n7. 刷牙或擦手时关掉水龙头。 \n8. 减少浇水草坪的时间。 \n9. 尽可能多地重复使用灰水（来自洗衣机、浴室水槽和淋浴的水）。 \n10. 只购买能源效率高的洗碗机和洗衣机。"
        }
    ]
    file_result = sensenova.File.create(file=io.StringIO(json.dumps(payload, ensure_ascii=False)),
                                        description="python test fintune update", scheme="FINE_TUNE_1",
                                        user_provided_filename="python_test_file.json")

    result = sensenova.Dataset.update(description="python test datasets update", files=[file_result["id"]],
                                      sid="a35b04f1-0efd-4721-8e29-7e4f4435a738")
    print(result)
    return result["dataset"]["id"]


# test_dataset_list()
if __name__ == "__main__":
    id = "e2f9075e-ed8d-4b79-87cd-072e974963fd"
    file_id = "f22c2cd5-248d-4700-af46-a556210de46d"
    test_dataset_list()
    # test_dataset_delete(id="1502c678-1341-4f5a-a073-f78b5018e0b3")
    # test_dataset_delete(id="12d1ba23-427c-42ad-af1a-d0b927b8e3b7")
    # test_dataset_download(id=id)
    # id = test_dataset_create()
    # url = test_dataset_add_file(id=id, description="How are YOU!")
    # print(url)
    # test_dataset_upload(url)
    # url = 'https://aoss.cn-sh-01.sensecoreapi-oss.cn/nova-test-training-data/ca249841-727f-4917-a747-a58ca3000cfc?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=35C99457BF6D484C812AE6C7FCC2C459%2F20230629%2Fcn-north-1%2Fs3%2Faws4_request&X-Amz-Date=20230629T060440Z&X-Amz-Expires=600&X-Amz-SignedHeaders=host&X-Amz-Signature=ab953d05b7dfacf81ebaad59004c856a7a9d31aaabddf8e473596ae668359c0c'
    # test_dataset_list()
    test_dataset_retrieve(id=id)
    # test_dataset_download(id=id, file_id=file_id)
