import openai
import os
import read
from read import augmented_query

augmented_query = read.augmented_query
# print(augmented_query)

# Set the OpenAI API key
openai.api_key = os.environ["OPENAI"]

# system message to prime the model
primer = f"""You are Q&A bot. A highly intelligent system that answers human questions based on the information provded by the user above each question.
If the information can not be found in the information provided by the user, come up with a plausible answer.
"""

res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k-0613",
    messages=[
        {"role": "system", "content": primer},
        {"role": "user", "content": augmented_query},
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
)

print(res["choices"][0]["message"]["content"])
# response = display(Markdown(res["choices"][0]["message"]["content"]))
# print(response)
