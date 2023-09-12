import sensenova
import sys


def test_chat_session():
    result = sensenova.ChatSession.create()
    print(result)
    result = sensenova.ChatSession.create(system_prompt=[
        {
            "role": "system",
            "content": "You are a translation expert."
        }
    ])
    print(result)


def test_chat_conversation():
    result = sensenova.ChatConversation.create(
        action="next",
        content="地球的直径是多少米?",
        model="nova-ptc-xl-v1",
        session_id="55b1f0815c76000",
        stream=False,
        know_ids=[]
    )
    print(result)


def test_chat_conversation_stream():
    resp = sensenova.ChatConversation.create(
        action="next",
        content="地球的直径是多少米?",
        model="nova-ptc-xl-v1",
        session_id="55b1f0815c76000",
        stream=True,
        know_ids=[]
    )
    for part in resp:
        print(part["data"]["delta"])