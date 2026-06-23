import streamlit as st
from pipeline import get_repo_name, clone_repo
from parser_engine import scan_repo
from graph_engine import build_dependency_graph
from vector_engine import chunck_and_store_repo
from query_engine import search_codebase, generate_answer, generate_summary
from graph_visualize import visualize_graph

st.set_page_config(page_title="CodeCompass AI", layout="wide")
st.title("CodeCompass AI — Codebase Q&A")

#actual
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

github_url = st.text_input("GitHub repo URL", placeholder="https://github.com/pallets/flask") # input 

if st.button("Analyze repo"):
    if not github_url.strip():
        st.error("Paste a GitHub URL first.")
    else:
        repo_name = get_repo_name(github_url)
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Cloning repo...")
        repo_path = clone_repo(github_url, dest_dir=f"cloned_repos/{repo_name}")
        progress_bar.progress(15)

       #scanning of files, as only python works here
        status_text.text("Scanning files...")
        report = scan_repo(repo_path)

        if len(report) == 0:
            from pipeline import detect_repo_content, extract_document_text
            from query_engine import generate_document_summary
            kind, detail = detect_repo_content(repo_path)
            if kind == "code":
                st.warning(f"This repo is primarily **{detail}**, not Python. CodeCompass currently only analyzes Python codebases.")
            elif kind == "documents":
                with st.spinner("Reading documents..."):
                    text = extract_document_text(repo_path)
                if text.strip():
                    summary = generate_document_summary(text)
                    st.info(f"This repo mainly contains **{detail}**, not source code.")
                    st.subheader("Document summary")
                    st.write(summary)
                else:
                    st.warning("Found document files but couldn't extract any readable text.")
            elif kind == "empty":
                st.warning("This repo appears to be empty, or all its files were skipped.")
            else:
                st.warning(f"Couldn't recognize this repo's content (mostly `{detail}` files). CodeCompass currently only analyzes Python source code.")
            st.stop()
        #graph of the all linked files 
        status_text.text("Building dependency graph...")
        graph = build_dependency_graph(report)
        progress_bar.progress(35)

        status_text.text("Building vector index...")
        chunck_and_store_repo(repo_path)
        progress_bar.progress(65)

        status_text.text("Generating overview...")
        overview = generate_summary(report, graph)
        progress_bar.progress(80)

        status_text.text("Drawing dependency graph...")
        graph_path = f"{repo_name}_dependency_graph.png"
        visualize_graph(graph, graph_path)
        progress_bar.progress(100)
        status_text.text("Done!")

        st.session_state.analyzed = True
        st.session_state.repo_path = repo_path
        st.session_state.report = report
        st.session_state.graph = graph
        st.session_state.overview = overview
        st.session_state.graph_path = graph_path

       

if st.session_state.analyzed:
    st.success(
        f"Parsed {len(st.session_state.report)} files — "
        f"{st.session_state.graph.number_of_nodes()} nodes, "
        f"{st.session_state.graph.number_of_edges()} edges."
    )
    st.subheader("Repo overview")
    st.write(st.session_state.overview)
    st.subheader("Dependency graph")
    st.image(st.session_state.graph_path)

    st.markdown("---")
    question = st.text_input("Ask a question about this repo")
    if st.button("Ask"):
        if question.strip():
            with st.spinner("Searching and generating answer..."):
                results = search_codebase(question, repo_path=st.session_state.repo_path)
                answer = generate_answer(question, results)
            st.subheader(f"Answer: {question}")
            st.write(answer)
        else:
            st.warning("Type a question first.")

st.markdown("---")
st.caption("Version 1 — made by Piyush")