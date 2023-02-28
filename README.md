# Evaluation-of-ChatGPT-on-Information-Extraction

An Evaluation of ChatGPT on Information Extraction task, including Named Entity Recognition (NER), Relation Extraction (RE), Event Extraction (EE) and Aspect-based Sentiment Analysis (ABSA).

*In progress* 
* Language: English
* Domain: General & Biomedical
* Setup: zero-shot & few-shot

## 1. Named Entity Recognition (NER)

### DataSets
```
[
    {
        "seq": "SOCCER - JAPAN GET LUCKY WIN , CHINA IN SURPRISE DEFEAT .",
        "entities": [
            {
                "e_name": "JAPAN",
                "e_type": "LOC",
                "start": 2,
                "end": 3,
            },
            {
                "e_name": "CHINA",
                "e_type": "PER",
                "start": 7,
                "end": 8,
            }
        ]

    },
    ...
]
```


## 2. Relation Extraction (RE)


## 3. Event Extraction (EE)


## 4. Aspect-based Sentiment Analysis (ABSA)


```python
def ner_data_process(dataset, input_file, output_file, separator=" "):

    total_num_entity = 0
    total_length_sentence = 0.0
    max_num_entity_per_sentence = 0

    output_path = os.path.join(output_dir, dataset) 
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    in_file_name = os.path.join(raw_data_dir, os.path.join(dataset, input_file))
    print("begin processing: ", in_file_name)
    with open(in_file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # print("#sentence of origin data   : ", len(data))
    
    new_data = []
    for example in data:
        seq_tokens = example['tokens']
        total_length_sentence += len(seq_tokens)
        sent = separator.join(seq_tokens)

        entities = example['entities']
        if len(entities) > max_num_entity_per_sentence:
            max_num_entity_per_sentence = len(entities)

        entity_list = []
        for entity in entities:
            total_num_entity += 1

            e_seq = separator.join(seq_tokens[entity['start']: entity['end']])
            e_type = entity['type']
            entity_list.append(
                {
                "e_name": e_seq,
                "e_type": e_type,
                "start": entity['start'],
                "end": entity["end"]
                }
            )

        entity_list = sorted(entity_list, key=lambda e: e['start'])

        new_example = dict()
        new_example['seq'] = sent
        new_example['entities'] = entity_list
        # print(new_example)
        new_data.append(new_example)

    print("#sentences: ", len(new_data))
    print("#entities : ", total_num_entity)
    print("avg. sentence length       : ", total_length_sentence/len(new_data))
    print("max. #entities per sentence: ", max_num_entity_per_sentence)
    print("avg. #entities per sentence: ", total_num_entity*1.0/len(new_data))
    # json.dump(new_data, open(os.path.join(output_path, output_file), 'w'))
    with open(os.path.join(output_path, output_file), 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(new_data, ensure_ascii=False))

```

```
I'm going to give you a sentence and ask you to identify the entities and label the entity category. There will only be 4 types of entities: ['LOC', 'MISC', 'ORG', 'PER']. Please present your results in list form. "Japan then laid siege to the Syrian penalty area and had a goal disallowed for offside in the 16th minute." Make the list like: ['entity name1', 'entity type1'],['entity name2', 'entity type2']......
```

[  {"entity_type": "LOC", "entity_name": "Singapore"},  {"entity_type": "MISC", "entity_name": "American teenager"},  {"entity_type": "PER", "entity_name": "Mickey Kantor"},  {"entity_type": "ORG", "entity_name": "WTO"}]



#### ABSA
```
Q: what does the 'aspect' term in Aspect-based Sentiment Analysis task refer to? Explain in one sentence.
A: In Aspect-based Sentiment Analysis task, the term 'aspect' refers to a specific feature, attribute, or aspect of a product or service that a user may express an opinion about.

Q: what does the 'opinion' term in Aspect-based Sentiment Analysis task refer to? Explain in one sentence.
A: In Aspect-based Sentiment Analysis task, the term 'opinion' refers to the sentiment or attitude expressed by a user towards a particular aspect or feature of a product or service.

Q: what does the 'sentiment polarity' term in Aspect-based Sentiment Analysis task refer to? Explain in one sentence.
A: In Aspect-based Sentiment Analysis task, the term 'sentiment polarity' refers to the degree of positivity, negativity or neutrality expressed in the opinion towards a particular aspect or feature of a product or service.
```


According to the following definition: 
The term 'aspect' refers to a specific feature, attribute, or aspect of a product or service that a user may express an opinion about. 
The term 'opinion' refers to the sentiment or attitude expressed by a user towards a particular aspect or feature of a product or service.
The term 'sentiment polarity' refers to the degree of positivity, negativity or neutrality expressed in the opinion towards a particular aspect or feature of a product or service. 
Recognize all aspects terms with their corresponding opinion terms and sentiment polarity in the following reviews in the format of <aspect, sentiment_polarity, opinion>: 
Boot time is super fast , around anywhere from 35 seconds to 1 minute .

* Aspect Term Extraction(AE): Extracting all the aspect terms from a sentence.
* Opinion Term Extraction (OE): Extracting all the opinion terms from a sentence.
* Aspect-level Sentiment Classification (ALSC): Predicting the sentiment polarities for every given aspect terms in a sentence.
* Aspect-oriented Opinion Extraction (AOE): Extracting the paired opinion terms for every given aspect terms in a sentence.
* Aspect Term Extraction and Sentiment Classification (AESC): Extracting the aspect terms as well as the corresponding sentiment polarities simultaneously.
* Pair Extraction (Pair): Extracting the aspect terms as well as the corresponding opinion terms simultaneously.
* Triplet Extraction (Triplet): Extracting all aspects terms with their corresponding opinion terms and sentiment polarity simultaneously.