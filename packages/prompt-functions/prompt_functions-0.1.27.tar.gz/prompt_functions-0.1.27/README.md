# Prompt Functions ⚙️
`prompt-functions` aims to make it easy to build functions with LLMs that have structured I/O, and to move prompts out of the code into serialized and versioned formats.


## Getting Started
### 1. Installation
Install the package using pip:
```bash
pip install prompt-functions
```
### 2. Setting Up Your First Function
Let's create a sentiment classification function:

**Step 1**: Create a directory named sentiment. Inside this directory, you need two files:
```bash
└─ sentiment
   ├── function_args.json
   ├── model_args.json
   └── template.txt
```
**Step 2:** Define your prompt template in template.txt:
```bash
Aalyze and determine whether the sentiment of the following sentence is positive, negative, or neutral.
Sentence:
{sentence}
```
**Step 3:** Set model paramters in model_args.json:
```json
{
    "temperature": 0.0,
    "model": "gpt-3.5-turbo"
}
```

**Step 4:** Specify the function's output format in function_args.json:
```json
{
    "function_name": "sentiment_classifier",
    "description": "Classify the sentiment of a sentence",
    "properties": {
        "thoughts": {
            "type": "string",
            "description": "Your thoughts when classifying sentiment of the given sentence."
        },
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
            "description": "The sentiment of the given sentence."
        }
    }
}
```
### 3. Using Your Prompt Function in Python

Here's how you can load and use your prompt function:

```python
from prompt_functions import PromptFunction

# Load your function
sentiment = PromptFunction.from_dir("./sentiment/")

# Make a prediction
pred = sentiment(sentence="I am super happy!")

# Expected Output:
# {
#   "thoughts": "The sentiment in the sentence is positive",
#   "sentiment": "positive"
# }
```
## Prompt Versioning
*Coming up..*
