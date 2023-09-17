import openai
import os
import pinecone
from tqdm.auto import tqdm
from time import sleep
import load
from load import chunks

# text = load.chunks
# print(input)
# Set the OpenAI API key
openai.api_key = os.environ["OPENAI"]

embed_model = "text-embedding-ada-002"

# res = openai.Embedding.create(input=text, engine=embed_model)

# print(res.keys())
# print(len(res["data"]))

# initilize pinecone

index_name = "mojave"
dimension = 1536

# initialize connection
pinecone.init(api_key=os.environ["PINECONE"], environment="us-west4-gcp-free")

# check if index exists
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=dimension, metric="dotproduct")

# connect to index
index = pinecone.Index(index_name)
# view index stat
# print(index.describe_index_stats())

# upsert embeddings
chunks = load.chunks
# print(chunks)
# print(len(chunks))

batch_size = 100

# ...
# your previous code

# initialize an empty list to accumulate embeddings and metadata
all_embeddings = []
all_meta_batch = []

for i in tqdm(range(0, len(chunks), batch_size)):
    # find the end of the batch
    i_end = min(len(chunks), i + batch_size)
    meta_batch = chunks[i:i_end]
    # print(meta_batch)
    # get ids
    ids_batch = [x["id"] for x in meta_batch]
    # print(len(ids_batch))
    # get texts to encode
    texts = [x["text"] for x in meta_batch]
    # print(len(texts))
    # create embeddings (try-except to avoid RateLimitError)

    try:
        res = openai.Embedding.create(input=texts, engine=embed_model)
        print(len(res["data"][0]["embedding"]))
    except:
        done = False
        while not done:
            sleep(5)
            try:
                res = openai.Embedding.create(input=texts, engine=embed_model)
                print(len(res["data"][0]["embedding"]))
                done = True
            except:
                pass

    # accumulate embeddings and metadata
    embeds = [record["embedding"] for record in res["data"]]
    all_embeddings.extend(embeds)
    all_meta_batch.extend(meta_batch)

# clean up metadata
to_upsert = [
    (
        record["id"],
        embedding,
        {"text": record["text"], "chunk": record["chunk"], "file_name": record["file"]},
    )
    for record, embedding in zip(all_meta_batch, all_embeddings)
]

# upsert embeddings
index.upsert(vectors=to_upsert)
