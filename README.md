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

```
Q: what does the 'aspect' term in Aspect-based Sentiment Analysis task refer to? Explain in one sentence.
A: In Aspect-based Sentiment Analysis task, the term 'aspect' refers to a specific feature, attribute, or aspect of a product or service that a user may express an opinion about.

Q: what does the 'opinion' term in Aspect-based Sentiment Analysis task refer to? Explain in one sentence.
A: In Aspect-based Sentiment Analysis task, the term 'opinion' refers to the sentiment or attitude expressed by a user towards a particular aspect or feature of a product or service.

Q: what does the 'sentiment polarity' term in Aspect-based Sentiment Analysis task refer to? Explain in one sentence.
A: In Aspect-based Sentiment Analysis task, the term 'sentiment polarity' refers to the degree of positivity, negativity or neutrality expressed in the opinion towards a particular aspect or feature of a product or service.

prompts:
According to the following definition: 
The term 'aspect' refers to a specific feature, attribute, or aspect of a product or service that a user may express an opinion about. 
The term 'opinion' refers to the sentiment or attitude expressed by a user towards a particular aspect or feature of a product or service.
The term 'sentiment polarity' refers to the degree of positivity, negativity or neutrality expressed in the opinion towards a particular aspect or feature of a product or service. 
Recognize all aspects terms with their corresponding opinion terms and sentiment polarity in the following reviews in the format of <aspect, sentiment_polarity, opinion>: 
Boot time is super fast , around anywhere from 35 seconds to 1 minute .
```

#### Datasets
* D17:  14lap, 14res, 15res  (wang)
* D19:  14lap, 14res, 15res, 16res  (fan)
* D20a: 14lap, 14res, 15res, 16res  (penga)
* D20b: 14lap, 14res, 15res, 16res  (pengb)

#### 4.1 Aspect Term Extraction(AE): Extracting all the aspect terms from a sentence.
```
Recognize all aspect terms in the following review with the format ['aspect_1', 'aspect_2', ...]: 
"Great food but the service was dreadful !"

output: ['food', 'service']
```

#### 4.2 Opinion Term Extraction (OE): Extracting all the opinion terms from a sentence.
```
Recognize all opinion terms in the following review with the format ['opinion_1', 'opinion_2', ...]: 
"Great food but the service was dreadful !"

output: ['Great', 'dreadful']
```

#### 4.3 Aspect-level Sentiment Classification (ALSC): Predicting the sentiment polarities for every given aspect terms in a sentence.
```
Recognize the sentiment polarity for aspect term 'food' in the following review with the format ['aspect', 'sentiment']: 
"Great food but the service was dreadful !"

output: ['food', 'positive']
```

#### 4.4 Aspect-oriented Opinion Extraction (AOE): Extracting the paired opinion terms for every given aspect terms in a sentence.
```
Recognize the opinion term for aspect term 'food' in the following review with the format ['opinion_1', 'opinion_2', ...]: 
"Great food but the service was dreadful !"

output: ['Great']
```


#### 4.5 Aspect Term Extraction and Sentiment Classification (AESC): Extracting the aspect terms as well as the corresponding sentiment polarities simultaneously.
```
Recognize all aspect terms with their corresponding sentiment polarity in the following review with the format ['aspect', 'sentiment_polarity']: 
"Great food but the service was dreadful !"

output: ['food', 'positive'] 
        ['service', 'negative']
```

#### 4.6 Pair Extraction (Pair): Extracting the aspect terms as well as the corresponding opinion terms simultaneously.
```
Recognize all aspect terms with their corresponding opinion terms in the following review with the format ['aspect', 'opinion']: 
"Great food but the service was dreadful !"

output: ['food', 'great']
        ['service', 'dreadful']
```

#### 4.7 Triplet Extraction (Triplet): Extracting all aspects terms with their corresponding opinion terms and sentiment polarity simultaneously.
```
Recognize all aspect terms with their corresponding opinion terms and sentiment polarity in the following review with the format ['aspect', 'sentiment', 'opinion']: 
"Great food but the service was dreadful !"

output: ['food', 'positive', 'great']
        ['service', 'negative', 'dreadful']
```


<!-- ```
I'm going to give you a sentence and ask you to identify the entities and label the entity category. There will only be 4 types of entities: ['LOC', 'MISC', 'ORG', 'PER']. Please present your results in list form. "Japan then laid siege to the Syrian penalty area and had a goal disallowed for offside in the 16th minute." Make the list like: ['entity name1', 'entity type1'],['entity name2', 'entity type2']......
``` -->
