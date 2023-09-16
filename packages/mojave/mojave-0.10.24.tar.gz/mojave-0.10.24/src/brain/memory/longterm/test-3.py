import os
from PyPDF2 import PdfReader

#  Get the path of the current file
currentPath = os.path.abspath(__file__)

# Get the directory containing the current file

currentDir = os.path.dirname(currentPath)

#  construct the path to the nba facts folder

folderPath = os.path.join(currentDir, "instructions")

print(folderPath)


def extract(folderPath):
    # create a list of all the files
    pdfFiles = []
    # create a loop to go through all the in the folder path
    for file in os.listdir(folderPath):
        # add a condition to read only files with .pdf extensions
        if file.endswith(".pdf"):
            pdfFiles.append(os.path.join(file))
    return pdfFiles


pdfFiles = extract(folderPath)

# print(pdfFiles)


def read(pdf_files):
    # create a dictionary that stores key value pairs of the title of the file and the content of the file
    datasets = {}

    for file in pdf_files:
        try:
            # open the PDF file using PdfReader
            pdf_reader = PdfReader(file)

            # Now we exatract the text from each page of the file
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

            # store extracted text in the dictionary
            file_name = os.path.basename(file)
            datasets[file_name] = text

        except Exception as e:
            print(f"Error processing {file}: {e}")

    data = []
    for file_name, text in datasets.items():
        data.append({"file_name": file_name, "text": text})

    return data


dataset = read(pdfFiles)
print(dataset)
