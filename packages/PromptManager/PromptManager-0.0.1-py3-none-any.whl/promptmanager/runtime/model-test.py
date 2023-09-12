from promptmanager.runtime.model import PMOpenAIPMLLM

api_key = "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"
pmOpenAIPMLLM = PMOpenAIPMLLM.load_from_openai_key(api_key)

message = [{"role": "user", "content": "我要写一本书"}, {"role": "user", "content": "名字叫做《我和你》"}]
params = [{'name': 'model'}, {'name': 'stream', 'value': False}]

result = pmOpenAIPMLLM.request_by_message(message, params)
print(result)