import openai

openai.api_key_path = "./api-keys/api-key.txt"

bot = openai.ChatCompletion()

prompt = 'Recognize all opinion terms in the review "The bread is top notch as well .". Answer in the format [opinion_1, opinion_2, ...] without any explanation. If no aspecct term exists, then only answer "[]".'

prompt = 'Recognize all aspect terms in the review "The bread is top notch as well .". Answer in the format [aspect_1, aspect_2, ...] without any explanation. If no opinion term exists, then only answer "[]".'

prompt = 'Recognize the sentiment polarity for the aspect term "bread" in the review "The bread is top notch as well .". Answer from the options [positive, negative, neutral] without any explanation.'

prompt = 'Recognize the opinion terms for the aspect term "bread" in the review "The bread is top notch as well .". Answer in the format [opinion_1, opinion_2, ...] without any explanation. If no opinion term exists, then only answer "[]".'

prompt = 'Recognize all aspect terms with their corresponding sentiment polarity in the review "The bread is top notch as well .". Answer in the format [aspect, sentiment] without any explanation. If no aspect term exists, then only answer "[]".'

prompt = 'Recognize all aspect terms with their corresponding opinion terms in the review "The bread is top notch as well .". Answer in the format [aspect, opinion] without any explanation. If no aspect term exists, then only answer "[]".'

prompt = 'Recognize all aspect terms with their corresponding opinion terms and sentiment polarity in the review "The bread is top notch as well .". Answer in the format [aspect, sentiment, opinion] without any explanation. If no aspect term exists, then only answer "[]".'

para = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    }

response = bot.create(**para).choices[0].message
response = response["content"].strip()
print(response)
