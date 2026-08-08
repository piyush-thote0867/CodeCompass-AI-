import os
import  networkx as nx 
def build_dependency_graph(repo_report):
    """
    it makes the graph <<- ingestion
      """
    G = nx.DiGraph() # directed graph 

    all_files = [data["file"] for data in repo_report]
    for file in all_files :
        G.add_node(file,type="file")

    # map a file's basename (no extension) -> list of files that share it
    # e.g. "src/flask/app.py" -> key "app"
    # __init__.py also gets mapped under its parent folder name, since
    # "from . import x" / "import mypkg" usually refers to the package
    basename_map = {}
    for f in all_files:
        base = os.path.splitext(os.path.basename(f))[0]
        basename_map.setdefault(base, []).append(f)
        if base == "__init__":
            pkg_name = os.path.basename(os.path.dirname(f))
            if pkg_name:
                basename_map.setdefault(pkg_name, []).append(f)

    for data in repo_report: #edges 
        current_file = data["file"]
        imports = data["imports"]

        for imp in imports:
            # dotted import like "flask.app" -> check each segment,
            # since local imports can be absolute ("flask.app"),
            # relative ("app"), or partial ("app" from "flask.app.something")
            parts = imp.split(".")
            for part in parts:
                for target_file in basename_map.get(part, []):
                    if target_file != current_file:
                        G.add_edge(current_file, target_file)
    return G

def get_related_files(graph, matched_files):
    """
    GIven a built dependency rpah ,fiels direclty connected 
    """
    related = set()
    for file in matched_files:
        if file in graph:
            related.update(graph.successors(file))
            related.update(graph.predecessors(file))
    return related - set(matched_files)


if __name__ == "__main__":
    from parser_engine import scan_repo as scan_repository 
    import os 

    current_dir = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__))else "."
    report = scan_repository(current_dir)
    graph = build_dependency_graph(report)

    print("--- Dependency Graph Stats ---")
    print(f"Total Files (Nodes): {graph.number_of_nodes()}")
    print(f"Total Connections (Edges): {graph.number_of_edges()}")
    print("Nodes list:", list(graph.nodes))
    print("Connections list:", list(graph.edges))