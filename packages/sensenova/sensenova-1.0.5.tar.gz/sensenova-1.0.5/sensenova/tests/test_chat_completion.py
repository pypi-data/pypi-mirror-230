import sys

import sensenova

# result = sensenova.ChatCompletion.create(
#     messages=[{"role": "user", "content": "Say this is a test!"}]
# )
stream = True
resp = sensenova.ChatCompletion.create(
    messages=[{"role": "user", "content": "Say this is a test!"}],
    model="nova-ptc-xs-v1",
    stream=stream,
)

if not stream:
    resp = [resp]
for part in resp:
    choices = part['data']["choices"]
    for c_idx, c in enumerate(choices):
        if len(choices) > 1:
            sys.stdout.write("===== Chat Completion {} =====\n".format(c_idx))
        if stream:
            delta = c.get("delta")
            if delta:
                sys.stdout.write(delta)
        else:
            sys.stdout.write(c["message"])
            if len(choices) > 1:  # not in streams
                sys.stdout.write("\n")
        sys.stdout.flush()
