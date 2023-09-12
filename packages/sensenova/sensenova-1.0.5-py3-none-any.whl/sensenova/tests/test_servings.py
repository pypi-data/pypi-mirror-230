import json
import sensenova


def test_serving_create(model_id):
    result = sensenova.Serving.create(
        model=model_id,
        config={
            "run_time": 60
        }
    )
    print(result)


def test_serving_list():
    resp = sensenova.Serving.list()
    print(resp)


def test_serving_cancel(id):
    resp = sensenova.Serving.cancel(id)
    print(resp)


def test_serving_retrieve(id):
    resp = sensenova.Serving.retrieve(id)
    print(resp)


def test_serving_relaunch(id):
    resp = sensenova.Serving.relaunch(id)
    print(resp)


if __name__ == "__main__":
    id = "26f8d926-0579-40e8-a934-5ec99a84ab7e"
    model_id = "llama-7b-test:wzh2"
    # test_finetune_list()
    # test_serving_list()
    # test_serving_list()

    # test_serving_create(model_id)
    # test_serving_cancel(id)
    # print(sensenova.Serving.delete(sid=id))
    # test_serving_relaunch(id)
    test_serving_retrieve(id)
    # test_serving_cancel()
    # test_serving_list()
