import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
print("Loading embedding model (this might take a second )...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def chunck_and_store_repo(repo_path):
    """
    reads all python files, breaks them into small chunks ,
    and saves them int0 a faiss datbase """

    documents =[]
    metadata=[] #are the adiitonal info 

    for  root,_,files in os.walk(repo_path):
        if "venv" in root or ".git" in root :
            continue 
        for file in files :
            if not file.endswith(".py"):
                continue
            file_path= os.path.join(root,file)
            with  open(file_path , "r", encoding="utf-8" ) as f :
                content = f.read()
                documents.append(content)
                metadata.append(os.path.relpath(file_path,repo_path).replace('\\', '/'))


    if not documents :
        print("No python files found to inde!!")
        return None,[],[]
    

    #split code in chuncks 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size= 600,
        chunk_overlap = 100,
        length_function = len
    )
    chunks =[]
    chunk_meta=[]

    for doc , file_name in zip(documents, metadata):
        split_texts = text_splitter.split_text(doc)
        for text in split_texts:
            chunks.append(text)
            chunk_meta.append(file_name)
# text >>> numbers
    print(f"converting {len(chunks)} code chunks into vector embeddings...")
    embeddings = model.encode(chunks)

   # Faiss idx to store and serach these vector 
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    print("Successfully built store")
 

    # Save  FAISS index ->> disk
    faiss.write_index(index, "faiss_index.bin")

    # Save chunks + metadata separately (FAISS only stores vectors, not text)
    with open("vector_store_data.pkl", "wb") as f:
        pickle.dump({"chunks": chunks, "metadata": chunk_meta}, f)

    print("Saved index + metadata to disk.")
    return index , chunks , chunk_meta


if __name__ == "__main__":

    current_dir = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__))else "."
    index , chunks , meta = chunck_and_store_repo(current_dir)

    if index :
        print(f"Total vectors stored in database :{index.ntotal}")
        print(f"\n--- Sample Chunk from Database ---")
        print(f"File: {meta[0]}")
        print(f"Code:\n{chunks[0]}")
        print(f"----------------------------------")
