
config = "{  \"protocol\": \"http\",  \"method\": \"POST\",  \"url\": \"https://api.openai.com/v1/chat/completions\",  \"header\": {    \"ContentType\": \"application/json\",   \"Authorization\": \"Bearer ${OPENAI_API_KEY}\"  },  \"requestBody\":  {\"model\": \"${model}\",  \"messages\": ${message},  \"temperature\": ${temperature},  \"stream\": ${stream}},  \"responseBody\":{   \"id\": \"chatcmpl-7lZq4UwSCrkvyOTUcyReAMXpAydSQ\",  \"object\": \"chat.completion\",  \"created\": \"1691573536\",  \"model\": \"gpt-3.5-turbo-0613\",  \"choices\": ${result},  \"usage\": {    \"prompt_tokens\": 36,  \"completion_tokens\": 104,  \"total_tokens\": 140}   }  }"


requestBody = config[str(config).index('requestBody') - 1: str(config).index('responseBody') - 1]
responseBody = config[str(config).index('responseBody') - 1: len(config)]
config = config.replace(requestBody, '').replace(responseBody, '')
requestBody_content = requestBody[str(requestBody).index('{'): str(requestBody).rindex('}') + 1]
requestBody_content = requestBody_content.replace('\"', '\\"')
config = config + "\"requestBody\":\"" + requestBody_content + '\"}'
print(requestBody)