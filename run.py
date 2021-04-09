import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join("sbol_enhancer")))
from builder.builder import GraphBuilder
from visual.cytoscape.visual import CytoscapeVisualiser
from dashboard.run import dash_runner
from sbol_enhancer.enhancer import SBOLEnhancer


def process_input(filename):
    graph_builder = GraphBuilder(filename,prune=True)
    enhancer = SBOLEnhancer(filename,staged=True)
    graph_visualiser = CytoscapeVisualiser(graph_builder)
    graph_title = filename.split(os.path.sep)[-1].split(".")[0]
    dash_runner(graph_visualiser,enhancer,graph_title)

def language_processor_args():
    parser = argparse.ArgumentParser(description="Network Visualisation Tool")
    parser.add_argument('filename', default=None, nargs='?',help="File to parse as Input")
    return  parser.parse_args()

if __name__ == "__main__":
    args = language_processor_args()
    process_input(args.filename)