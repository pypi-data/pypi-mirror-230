import argparse
import os

from .compute_metrics import ComputeMetrics
from .network_graph import GraphViz
from .process_file import ProcessFile
from .read_file import ReadFile


def cli():
    parser = argparse.ArgumentParser(description="A Python interface for histcite.")

    # Positional arguments
    parser.add_argument(
        "folder_path",
        type=str,
        help="Folder path of downloaded data.",
    )
    parser.add_argument(
        "source",
        type=str,
        choices=["wos", "cssci", "scopus"],
        help="Data source.",
    )

    # Exclusive arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--top", type=int, help="Top N nodes with the highest LCS.")
    group.add_argument(
        "--threshold",
        type=int,
        help="Nodes with LCS greater than threshold.",
    )

    parser.add_argument(
        "--disable_timeline",
        action="store_false",
        help="Whether to disable timeline.",
    )

    args = parser.parse_args()
    output_path = os.path.join(args.folder_path, "result")
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    docs_df = ReadFile(args.folder_path, args.source).read_all()
    process = ProcessFile(docs_df, args.source)
    refs_df = process.extract_reference()
    citation_relationship = process.process_citation(refs_df)

    cm = ComputeMetrics(docs_df, citation_relationship, args.source)
    cm.write2excel(os.path.join(output_path, "descriptive_statistics.xlsx"))

    graph = GraphViz(docs_df, citation_relationship, args.source)

    if args.top is not None:
        doc_indices = (
            citation_relationship[citation_relationship["LCS"] > 0]
            .sort_values("LCS", ascending=False)
            .index[: args.top]
            .tolist()
        )

    elif args.threshold is not None:
        doc_indices = citation_relationship[
            citation_relationship["LCS"] >= args.threshold
        ].index.tolist()

    else:
        raise ValueError("One of -top, -threshold must be specified.")

    graph_dot_file = graph.generate_dot_file(
        doc_indices, show_timeline=args.disable_timeline
    )
    graph_dot_path = os.path.join(output_path, "graph.dot")
    with open(graph_dot_path, "w") as f:
        f.write(graph_dot_file)
    graph._export_graph_node_info(os.path.join(output_path, "graph_node_info.xlsx"))
