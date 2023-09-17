import openai
import os
from IPython.display import Markdown, display
import read
from read import augmented_query

augmented_query = read.augmented_query

# Set the OpenAI API key
openai.api_key = os.environ["OPENAI"]

# System message to prime the model
primer = f"""You are a Q&A bot. A highly intelligent system that answers human questions based on the information provided by the human above each question.
If the information cannot be found in the information provided by the user, you truthfully say "I don't know". 
"""

# Get augmented query
user_input = augmented_query  # Assuming the function returns user input

# Create chat completion
res = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": primer},
        {"role": "user", "content": user_input},
    ],
)

# Get the response content
response_content = res["choices"][0]["message"]["content"]

# Display the Markdown content (for Jupyter Notebook)
# markdown_response = Markdown(response_content)
# display(markdown_response)

# Print the response content (for standard Python script)
# print(response_content)

# we need more tests for the job of mental model function. it seems like something we'll have to do with the model itself
