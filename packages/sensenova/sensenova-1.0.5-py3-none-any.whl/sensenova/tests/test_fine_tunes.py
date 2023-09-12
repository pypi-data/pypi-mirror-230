import json
from tempfile import NamedTemporaryFile

import sensenova


def test_finetune_create():
    result = sensenova.FineTune.create(
        hyperparams= {
            "max_steps": 10,
            "method": "lora",
            "lr_scheduler_type": "cosine",
            "learning_rate": 0.0001,
            "warmup_ratio": 0.03,
            "weight_decay": 0,
            "save_steps": 10,
            "modules_to_save": "word_embeddings",
            "lora_rank": 8,
            "lora_dropout": 0.05,
            "lora_alpha": 32
        },
        model="nova-ptc-xs-v1",
        suffix="wand",
        training_file="e2f9075e-ed8d-4b79-87cd-072e974963fd"
    )
    print(result)


def test_finetune_list():
    resp = sensenova.FineTune.list()
    print(resp)

def test_finetune_cancel(id):
    resp = sensenova.FineTune.cancel(id)
    print(resp)


if __name__ == "__main__":
    id = 'ft-62e72ad8e1624bdc812cbfc71940505d'
    # test_finetune_list()
    # test_finetune_create()
    # test_finetune_list()
    print(sensenova.FineTune.retrieve(id=id))
    # test_finetune_cancel(id=id)
    # print(sensenova.FineTune.delete(sid=id))
    # test_finetune_list()
