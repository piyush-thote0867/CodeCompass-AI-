import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

def visualize_graph(graph, output_path="dependency_graph.png"):
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(graph, k=0.5, seed=42)
    nx.draw(
        graph, pos,
        with_labels=True,
        node_color="lightblue",
        node_size=800,
        font_size=7,
        arrows=True,
        edge_color="gray"
    )
    plt.title("Codebase dependency graph")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Graph saved to {output_path}")