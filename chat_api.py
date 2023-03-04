import openai

openai.api_key_path = "./api-keys/api-key.txt"

bot = openai.ChatCompletion()

aspect = "price"
sentence = "Great food , great waitstaff , great atmosphere , and best of all GREAT beer"
"[aspect, start_word_index, end_word_index] [aspect_1, aspect_2, ...]"
"If one aspect term appears multiple times, then output this term in the format [aspect, start_word_index, end_word_index]"
# sentence = "Did not enjoy the new Windows 8 and touchscreen functions ."

# prompt = 'Recognize all aspect terms in the review "{}". Answer in the format [\'aspect_1\', \'aspect_2\', ...] without any explanation. If no opinion term exists, then only answer "[]".'.format(sentence)

prompt = 'Recognize all opinion terms in the review "{}". Answer in the format [\'opinion_1\', \'opinion_2\', ...] without any explanation. If no aspecct term exists, then only answer "[]".'.format(sentence)

# prompt = 'Recognize the sentiment polarity for the aspect term "{}" in the review "{}". Answer from the options [positive, negative, neutral] without any explanation.'.format(aspect, sentence)

# prompt = 'Recognize the opinion terms for the aspect term "{}" in the review "{}". Answer in the format [opinion_1, opinion_2, ...] without any explanation. If no opinion term exists, then only answer "[]".'.format(aspect, sentence)

# prompt = 'Recognize all aspect terms with their corresponding sentiment polarity in the review "{}". Answer in the format [aspect, sentiment] without any explanation. If no aspect term exists, then only answer "[]".'.format(sentence)

# prompt = 'Recognize all aspect terms with their corresponding opinion terms in the review "{}". Answer in the format [aspect, opinion] without any explanation. If no aspect term exists, then only answer "[]".'.format(sentence)

# prompt = 'Recognize all aspect terms with their corresponding opinion terms and sentiment polarity in the review "{}". Answer in the format [aspect, sentiment, opinion] without any explanation. If no aspect term exists, then only answer "[]".'.format(sentence)

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
