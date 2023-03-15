import openai
import ast

def response_string_to_list(response):
    def get_list_by_string(list_str):
        try:
            res_list = ast.literal_eval(list_str) 
        except:
            res_list = []
        finally:
            return res_list
    
    response = response.lower()
    num_left = response.count("[")

    res_list = []

    if num_left == 0:
        return res_list
    
    if num_left == 1:
        start_idx = response.find('[')
        response = response[start_idx:]
        num_right = response.count("]")
        if num_right < 1:
            return res_list
        else:
            start_idx = response.find('[')
            end_idx = response.find(']')
            span = response[start_idx: end_idx+1]
            res_list = get_list_by_string(span)
            res_list = [res.strip() for res in res_list] 
            return res_list

    # "['a', 'b'], ['c', 'd']"
    start_idx = -1
    end_idx = -1

    for i, ch in enumerate(response):
        if ch == '[':
            start_idx = i
        if ch == ']':
            end_idx = i
        # print(start_idx, end_idx)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            span = response[start_idx: end_idx+1]
            tmp_list = get_list_by_string(span)
            tmp_list = [res.strip() for res in tmp_list] 
            res_list.append(tmp_list)
            start_idx = -1
            end_idx = -1
        

    return res_list

## openai api
openai.api_key_path = "./api-keys/api-key.txt"

bot = openai.ChatCompletion()

aspect = "food"
sentence = "Great food , great waitstaff , great atmosphere , and best of all GREAT beer"
"[aspect, start_word_index, end_word_index] [aspect_1, aspect_2, ...]"
"If one aspect term appears multiple times, then output this term in the format [aspect, start_word_index, end_word_index]"
aspect = "food"
sentence = "food , waitstaff"
# sentence = "Did not enjoy the new Windows 8 and touchscreen functions ."

# prompt = 'Recognize all aspect terms in the review "{}". Answer in the format [\'aspect_1\', \'aspect_2\', ...] without any explanation. If no opinion term exists, then only answer "[]".'.format(sentence)

# prompt = 'Recognize all opinion terms in the review "{}". Answer in the format [\'opinion_1\', \'opinion_2\', ...] without any explanation. If no aspecct term exists, then only answer "[]".'.format(sentence)

prompt = 'Recognize the sentiment polarity for the aspect term "{}" in the review "{}". Answer from the options ["positive", "negative", "neutral", "none"] without any explanation. If it cannot be judged, just answer "none"'.format(aspect, sentence)

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

# a = "[\"abs\"]"
# print(response_string_to_list(a))
