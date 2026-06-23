import os
import pickle 
from sentence_transformers import SentenceTransformer
import faiss
from groq import Groq
from parser_engine import scan_repo
from graph_engine import build_dependency_graph, get_related_files
from dotenv import load_dotenv 
load_dotenv()


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("Loading search Embedding Model ")
model = SentenceTransformer("all-MiniLM-L6-v2")


def build_file_index_map(metadata):
    file_map = {}
    for i, file in enumerate(metadata):
        file_map.setdefault(file, []).append(i)
    return file_map 



def search_codebase(query ,repo_path=".",index_path="faiss_index.bin",data_path="vector_store_data.pkl",top_k=3):
    """
    Human Language = query ; we embed it and faiss return the index m=with most predicatbke matching 
    """
    if not os.path.exists(index_path) or not os.path.exists(data_path):
        print("error : index not found , vector_engine.py first")
        return []

    index = faiss.read_index(index_path)

    with open(data_path , "rb") as f :
        data = pickle.load(f)
    chunks = data["chunks"]
    metadata = data["metadata"]

    query_vector = model.encode([query]).astype("float32")

    distances , indices =  index.search(query_vector , top_k)
#map the osition here , real code 
    results = []
    for dist , idx in zip(distances[0] , indices[0]):
        results.append({
                "file":metadata[idx],
                "code" : chunks[idx],
                "distance" : float(dist)
        })

    matched_files = set(r["file"] for r in results)
    report = scan_repo(repo_path)
    graph = build_dependency_graph(report)
    related_files = get_related_files(graph , matched_files)
    file_map=build_file_index_map(metadata)


    for f in related_files:
        if f in file_map:
            idx = file_map[f][0]
            results.append({
                "file": f,
                "code": chunks[idx],
                "distance": None,
                "reason": "structurally related (import link)"
            })

    print(f"\n--- search result for : '{query}'--")
    for r in results:
        if r["distance"] is not None:
            print(f"\nFile : {r['file']} (distance : { r['distance']:.4f})")
        else :
           print(f"\nFile : {r['file']} ({r.get('reason' , 'related')})")
        print(r['code'][:300])
        print("-"*40)
    

    return results 

def generate_answer(query , results):
    context = "\n\n".join(
        [f"File: {r['file']}\nCode:\n{r['code']}" for r in results]
    
    )

    
    prompt = f"""You are a code assistant explaining a codebase to a developer.
    Answer using ONLY the code snippets provided below.
      If the answer isn't fully supported by these snippets, 
      say "I don't have enough context to answer this confidently" 
      instead of guessing.

    Code Context:
    {context}

    Question: {query}

    Answer:"""

    response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
    
    return response.choices[0].message.content



def generate_summary(report, graph):
    file_list = "\n".join(
        [f"- {r['file']} (classes: {', '.join(r['classes']) or 'none'})" for r in report[:30]]
    )

    degrees = sorted(graph.degree, key=lambda x: x[1], reverse=True)[:5]
    key_files = "\n".join([f"- {f} ({d} connections)" for f, d in degrees])

    prompt = f"""You are a code assistant. Below is a scan of a codebase.

Files found:
{file_list}

Most structurally central files (highest number of import connections):
{key_files}

Write a short, plain-language summary (3-5 sentences) of what this codebase is and what its core modules likely do. Briefly define any framework-specific terms you use.

Summary:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    test_query = "How is the dependency graph built "
    results =search_codebase(test_query)
    if results :
        answer = generate_answer(test_query, results)
        print("\n ===here we go ==")
        print(answer)

