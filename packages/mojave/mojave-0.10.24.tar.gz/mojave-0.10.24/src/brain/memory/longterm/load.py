# define a function to get pdf files from a folder and store them in a python list with their file paths.
import os
from PyPDF2 import PdfReader
from uuid import uuid4
from tqdm.auto import tqdm
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Get the path of the current file
current_file_path = os.path.abspath(__file__)

# Get the directory containing the current file
current_dir_path = os.path.dirname(current_file_path)

# Construct the path to the instructions folder relative to the current file
folder_path = os.path.join(current_dir_path, "instructions")


def extract(folder_path):
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_files.append(os.path.join(folder_path, file))
    return pdf_files


pdf_files = extract(folder_path)


def load(pdf_files):
    instructions = {}  # Dictionary to store file name -> extracted text pairs

    for file in pdf_files:
        try:
            # Open the PDF file using PdfReader
            pdf_reader = PdfReader(file)

            # Extract text from each page
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            # print(text)

            # Store extracted text in the dictionary
            file_name = os.path.basename(file)
            instructions[file_name] = text

        except Exception as e:
            print(f"Error processing {file}: {e}")

    data = []
    for file_name, text in instructions.items():
        data.append({"file_name": file_name, "text": text})

    return data


# Call the function and get the text dictionary
pdf_text_dict = load(pdf_files)
# print(pdf_text_dict)

# Print the dictionary
# for file_name, text in pdf_text_dict.items():
#     print(f"File: {file_name}\nText: {text}\n")
text = pdf_text_dict[0]["text"]
# print(text)
# chunking the paragraph output into sizable pieces
tokenizer = tiktoken.get_encoding("p50k_base")


# create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=[" ", "\n", "\n\n", ""],
)

# print(text_splitter.split_text(text))

# # even more processing

chunks = []
for record in tqdm(pdf_text_dict):
    pdf_chunks = text_splitter.split_text(record["text"])
    chunks.extend(
        [
            {"id": str(uuid4()), "text": chunk, "chunk": i, "file": record["file_name"]}
            for i, chunk in enumerate(pdf_chunks)
        ]
    )

# print(len(chunks))
# print(chunks[0])
# let's see how this adds up to everything else.
