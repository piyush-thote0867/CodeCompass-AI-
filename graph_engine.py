import  networkx as nx 
def build_dependency_graph(repo_report):
    """
    it makes the graph <<- ingestion
      """
    G = nx.DiGraph() # directed graph 

    all_files = [data["file"] for data in repo_report]
    for file in all_files :
        G.add_node(file,type="file")


    for data in repo_report: #edges 
        current_file = data["file"]
        
        imports = data["imports"]
# if imported fiel equal t owithin files 
        for imp in imports:
            for target_file in all_files:
                target_base = target_file.split(".")[0]

                if imp == target_base  or imp.endswith(target_base):
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