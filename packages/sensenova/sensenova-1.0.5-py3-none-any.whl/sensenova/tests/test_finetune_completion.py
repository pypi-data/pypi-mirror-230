import sys

from sensenova.util import finetune_completions_option_params

import sensenova

stream = True
resp = sensenova.FinetuneCompletion.create(
    model_id="SC-PTC-S-V1-20230601-test_unlimit-lhk1-2023-06-13-06-37-09",
    text="想一个寓言故事",
    stream=stream
)

if not stream:
    resp = [resp]

for part in resp:
    content = part['answer']
    if content:
        sys.stdout.write(content)
    sys.stdout.flush()