# pip install zhipuai 请先在终端进行安装

import os
import zhipuai

_apikey = os.getenv("ZHIPU_API_KEY")  or ""
zhipuai.api_key = _apikey


def get_chat_completion(
    messages,
    model="chatglm_std",  # use "gpt-4" for better results
    stream = False,
    temperature= 0.9,
    top_p= 0.7,
):
    response = zhipuai.model_api.sse_invoke(
        model= model,
        prompt= messages,
        temperature= temperature,
        top_p= top_p,
        incremental=stream
    )

    res = []
    for event in response.events():
        if event.event == "add":
            res.append(event.data, end="")
        elif event.event == "error" or event.event == "interrupted":
            res.append(event.data, end="")
        elif event.event == "finish":
            res.append(event.data)
            res.append(event.meta, end="")
        else:
            res.append(event.data, end="")

    return "".join(res)