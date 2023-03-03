import openai

openai.api_key_path = "./api-keys/api-key.txt"

bot = openai.ChatCompletion()

para = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": "Recognize all aspect terms from the following review in the format [aspect_1, aspect_2, ...] without any explanation: \"tech support would not fix the problem unless I bought your plan for $ 150 plus .\". If no term exists, then only answer '[]'.",
            }
        ]
    }

para_1 = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {   "role": "user", 
                "content": "What are aspect terms, opinion terms and sentiment polarities in Aspect-based Sentiment Analysis?", 
                "role": "assistant", 
                "content": "The term 'aspect' refers to a specific feature, attribute, or aspect of a product or service that a user may express an opinion about.\nThe term 'opinion' refers to the sentiment or attitude expressed by a user towards a particular aspect or feature of a product or service.\nThe term 'sentiment polarity' refers to the degree of positivity, negativity or neutrality expressed in the opinion towards a particular aspect or feature of a product or service.", 
                "role": "user",
                "content": "Recognize all aspect terms from the following review in the format [aspect_1, aspect_2, ...] without any explanation: \"tech support would not fix the problem unless I bought your plan for $ 150 plus .\". If no term exists, then only answer '[]'.",
            }
        ]
    }

para_2 = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": "From the options [positive, negative, neutral], recognize the sentiment polarity for the aspect term 'tech support' in the following review without any explanation: \"tech support would not fix the problem unless I bought your plan for $ 150 plus .\".",
            }
        ]
    }

para_3 = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": "Recognize the corresponding opinion term for the aspect term 'tech support' in the following review in the list format without any explanation: \"tech support would not fix the problem unless I bought your plan for $ 150 plus .\".",
            }
        ]
    }

# response = bot.create(**para).choices[0].message
# response = response["content"].strip()
# print(response)

# response = bot.create(**para_1).choices[0].message
# response = response["content"].strip()
# print(response)

# response = bot.create(**para_2).choices[0].message
# response = response["content"].strip()
# print(response)

response = bot.create(**para_3).choices[0].message
response = response["content"].strip()
print(response)
