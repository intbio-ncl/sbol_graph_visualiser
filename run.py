import argparse
import os
from graph_builder.networkx_wrapper import NetworkXGraphWrapper

from graph_visualisation.networkx.visual import NetworkXGraphBuilder
from graph_visualisation.plotly.visual import PlotlyVisualiser
from graph_visualisation.cytoscape.visual import CytoscapeVisualiser

from graph_dashboards.dash.visual import DashBoard

from graph_visualisation.networkx.run import nwx_runner
from graph_visualisation.plotly.run import plotly_runner
from graph_dashboards.dash.run import dash_runner

from sbol_enhancer.specified_enhancer.enhancer import SBOLEnhancer

visual_mapper = {
                "networkx" : {"builder" : NetworkXGraphWrapper,"visual" : {"networkx" : NetworkXGraphBuilder}, "run" : nwx_runner},
                "plotly"   : {"builder" : NetworkXGraphWrapper,"visual" : {"plotly" : PlotlyVisualiser}, "run" : plotly_runner},
                "dash"     : {"builder" : NetworkXGraphWrapper,"visual" : {"plotly" : PlotlyVisualiser, "cytoscape" : CytoscapeVisualiser}, "run" : dash_runner}
                }


def process_input(filename,visualiser,graph_type):
    graph_builder = visual_mapper[visualiser]["builder"](filename,prune=True)
    enhancer = SBOLEnhancer(filename)
    graph_visualiser = visual_mapper[visualiser]["visual"][graph_type](graph_builder)
    graph_title = filename.split(os.path.sep)[-1].split(".")[0]
    visual_mapper[visualiser]["run"](graph_visualiser,enhancer,graph_title)

def language_processor_args():
    parser = argparse.ArgumentParser(description="Network Visualisation Tool")
    parser.add_argument('filename', default=None, nargs='?',help="File to parse as Input")
    parser.add_argument('-v', '--visual', default="dash",
                        choices=list(visual_mapper.keys()),
                        help="What Visualisation medium is used.")

    parser.add_argument('-g', '--graph', default="plotly",
                        choices=list(visual_mapper["dash"]["visual"].keys()),
                        help="What Graph medium is used (Only valid when using dash).")

    return  parser.parse_args()

if __name__ == "__main__":
    args = language_processor_args()
    if args.filename is not None:
        if args.visual == "networkx":
            args.graph = "networkx"
        elif args.visual == "plotly":
            args.graph = "plotly"

        process_input(args.filename, args.visual,args.graph)