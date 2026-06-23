import os
import shutil
import subprocess
import stat
from parser_engine import scan_repo
from graph_engine import build_dependency_graph
from vector_engine import chunck_and_store_repo
from query_engine import search_codebase, generate_answer, generate_summary
from graph_visualize import visualize_graph
#change int he pdf or books format 
from collections import Counter
from pypdf import PdfReader

def get_repo_name(github_url):
    return github_url.rstrip("/").split("/")[-1].replace(".git", "")

def _remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(github_url, dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, onerror=_remove_readonly)
    print(f"Cloning {github_url} ...")
    subprocess.run(["git", "clone", "--depth", "1", github_url, dest_dir], check=True)
    print("Clone done.")
    return dest_dir


CODE_EXTENSIONS = {
    ".py": "Python", ".cpp": "C++", ".cc": "C++", ".h": "C/C++ header",
    ".hpp": "C++ header", ".c": "C", ".js": "JavaScript", ".ts": "TypeScript",
    ".java": "Java", ".go": "Go", ".rs": "Rust",
}

DOCUMENT_EXTENSIONS = {
    ".pdf": "PDF documents", ".epub": "ebook files",
    ".docx": "Word documents", ".md": "Markdown notes", ".txt": "text files",
}

def detect_repo_content(repo_path):
    counts = Counter()
    for root, _, files in os.walk(repo_path):
        if "venv" in root or ".git" in root:
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            counts[ext] += 1

    if not counts:
        return "empty", None

    top_ext, _ = counts.most_common(1)[0]

    if top_ext in CODE_EXTENSIONS:
        return "code", CODE_EXTENSIONS[top_ext]
    elif top_ext in DOCUMENT_EXTENSIONS:
        return "documents", DOCUMENT_EXTENSIONS[top_ext]
    else:
        return "unknown", top_ext


def extract_document_text(repo_path, max_chars=15000):
    text_chunks = []
    for root, _, files in os.walk(repo_path):
        if ".git" in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            try:
                if ext == ".pdf":
                    reader = PdfReader(path)
                    for page in reader.pages[:5]:
                        text_chunks.append(page.extract_text() or "")
                elif ext in (".txt", ".md"):
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text_chunks.append(f.read())
            except Exception:
                continue
            total_len = sum(len(t) for t in text_chunks)
            if total_len > max_chars:
                return "\n".join(text_chunks)[:max_chars]
    return "\n".join(text_chunks)[:max_chars]


def run_pipeline(repo_path, query):
    report = scan_repo(repo_path)
    graph = build_dependency_graph(report)
    chunck_and_store_repo(repo_path)
    results = search_codebase(query, repo_path=repo_path)
    answer = generate_answer(query, results)
    return answer, graph


if __name__ == "__main__":
    github_url = "https://github.com/pallets/flask" # for the terminal work 
    query = "how does flask handle routing"

    repo_name = get_repo_name(github_url)
    repo_path = clone_repo(github_url, dest_dir=f"cloned_repos/{repo_name}")

    report = scan_repo(repo_path)
    graph = build_dependency_graph(report)
    chunck_and_store_repo(repo_path)

    print("\n=== REPO OVERVIEW ===")
    print(generate_summary(report, graph))

    visualize_graph(graph, f"{repo_name}_dependency_graph.png")

    print(f"\n=== QUESTION: {query} ===")
    results = search_codebase(query, repo_path=repo_path)
    print(generate_answer(query, results))