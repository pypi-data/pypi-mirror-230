# Janex
A free open-source framework which can be used to build Machine Learning tools, LLMs, and Natural Language Processing scripts with full simplicity. This edition of Janex is built reliant on the main Janex library, and utilises PyTorch and the Natural Language Toolkit to attempt a slightly different approach of Intent Classification.

<h3> How to use? </h3>

Firstly, you need to install the Janex: PyTorch Edition library.
```
pip install JanexPT
```

Secondly, you need to import JanexPT into your code.
```
from JanexPT import *
```

Next, create an instance of the JanexPT class and define the path to your intents, thesaurus, and the name you wish to give to your AI.
```
intents_file_path, thesaurus_file_path, UIName = "intents.json", "thesaurus.json", "May" # Use whichever name you like.

janexpt = JanexPT(intents_file_path, thesaurus_file_path, UIName)

```

Then, you will need to train your intents data into a pth file. If you do not have a training program, it will curl install the pre-built one from this repo.
```
janexpt.trainpt()
```

Next, you need to give the program some text you wish to send to your AI, and then send it.
```
YourInput = input("You: ")
YourName = "Bob" # Whatever you wish your AI to refer to you as

classification = JanexPT.pattern_compare(YourInput, YourName)
response = JanexPT.response_compare(input_string, classification)

print(response)
```

And there we have it, the code will use a triple-layer NeuralNet to predict which class your input belongs in, and then uses the Janex library to pick the best response from those available.

If you would like your responses to be regenerated using the NLTK wordnet function, then you can use the experimental Response Generator, which uses both Janex and NLTK to fine-tune the response and make it less pre-programmed in a sense. Although, the coherence of your responses relies on the accuracy of both vanilla Janex and the Natural Language Toolkit. Here is the code.

From 0.0.18 onwards, you must now declare the strength of how 'rough' you want the generator to be. The larger the strength, the more rigorous the word replacement is, and potentially the longer the waiting time for an end result.
```
strength = 5 # for example, will only inspect five tokens from the response, and will replace them if suitable
NewResponse = JanexPT.generate_response_with_synonyms(response, strength)
print(NewResponse)
```
