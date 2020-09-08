from .visual import DashBoard
from inspect import signature
from dash.dependencies import Input, Output,State
import dash
import base64
import os
import sys,os
sys.path.insert(0,os.path.expanduser(os.path.join(os.getcwd(),"graph_visualisation")))
from graph_visualisation.plotly.visual import PlotlyVisualiser
from graph_visualisation.cytoscape.visual import CytoscapeVisualiser
from collections import OrderedDict 


options_color = "#f8f9fa"
plotly_id_prefix = "plotly"
cyto_id_prefix = "cyto"
background_color = {"backgroundColor" : options_color}
hidden_style = background_color.copy()
hidden_style["display"] = "none"

not_modifier_identifiers = {"sidebar_id" : "sidebar",
                            "toolbox_id" : "toolbox"}

plotly_update_inputs = OrderedDict()
plotly_update_outputs = {"graph_id" : Output("plotly_graph","figure"),
                        "error_id" : Output("plotly_error_alert", "is_open"),
                        "error_content" : Output("plotly_error_alert","children")}

cyto_update_inputs = OrderedDict()
cyto_update_outputs = {"graph_id" : Output("cyto_graph","children"),
                        "error_id" : Output("cyto_error_alert", "is_open"),
                        "error_content" : Output("cyto_error_alert","children")}


load_inputs = {"file_upload_id" : Input("file_upload","contents")}
load_states = {"file_upload_fn" : State("file_upload","filename")}
load_outputs = {"title_id" : Output("title","children"),
                "graph_container_id" : Output("graph_container","children")}

graph_type_inputs = {"graph_type_dropdown_id" : Input("graph_type" , "value")}
graph_type_outputs = {"plotly_options_id" : Output("plotly_options","style"),
                      "plotly_div" : Output("plotly_div","children"),
                      "plotly_div_style" : Output("plotly_div","style"),
                      "cyto_options_id" : Output("cyto_options","style"),
                      "cyto_div" : Output("cyto_div","children"),
                      "cyto_div_style" : Output("cyto_div","style")}

graph_types = {"plotly" : PlotlyVisualiser,
               "cytoscape" : CytoscapeVisualiser}

def dash_runner(visualiser,name = ""):
    figure_layout_elements = {"autosize": True}
    figure = visualiser.build(layout_elements = figure_layout_elements, show = False)
    dashboard = DashBoard(visualiser)

    # Add Options
    plotly_form_elements,plotly_identifiers = _create_form_elements(PlotlyVisualiser(),dashboard,style=background_color,id_prefix=plotly_id_prefix)
    cyto_form_elements,cyto_identifiers = _create_form_elements(CytoscapeVisualiser(),dashboard,style=background_color,id_prefix=cyto_id_prefix)

    plotly_update_inputs.update(plotly_identifiers)
    cyto_update_inputs.update(cyto_identifiers)
    
    plotly_form_div = dashboard.create_div(graph_type_outputs["plotly_options_id"].component_id,plotly_form_elements,add=False,style=background_color)
    cytoscape_form_div = dashboard.create_div(graph_type_outputs["cyto_options_id"].component_id,cyto_form_elements,add=False,style=hidden_style)

    dashboard.create_sidebar(not_modifier_identifiers["sidebar_id"],"Options",plotly_form_div + cytoscape_form_div,style={})

    # Add a title.
    title = "Graph for " + _beautify_name(name)
    title = dashboard.create_heading_1(load_outputs["title_id"].component_id,title,add=False)

    # Add Graph
    plotly_graph = dashboard.create_graph(plotly_update_outputs["graph_id"].component_id,figure,add=False)
    cyto_graph = dashboard.create_div(cyto_update_outputs["graph_id"].component_id,[],add=False)
    # Cyto is different to plotly, you dont add it to a graph it standalone in the component list.
    plotly_div = dashboard.create_div(graph_type_outputs["plotly_div"].component_id, [plotly_graph], add=False)
    cyto_div = dashboard.create_div(graph_type_outputs["cyto_div"].component_id, cyto_graph, add=False,style=hidden_style)

    graph_container = dashboard.create_div(load_outputs["graph_container_id"].component_id, plotly_div+cyto_div, add=False)

    # Add all non-sidebar stuff to content.
    plotly_error = dashboard.create_alert(plotly_update_outputs["error_id"].component_id,"Error.",add=False,color="danger",dismissable=True,fade=True,is_open=False)
    cyto_error = dashboard.create_alert(cyto_update_outputs["error_id"].component_id,"Error.",add=False,color="danger",dismissable=True,fade=True,is_open=False)

    # Add Toolbox utility.
    toolbox_elements = dashboard.create_file_upload(load_inputs["file_upload_id"].component_id,"Upload Graph","graph_container",add=False)
    graph_picker_options = [{"label" : k,"value":k} for k in graph_types.keys()]
    toolbox_elements = toolbox_elements + dashboard.create_dropdown(graph_type_inputs["graph_type_dropdown_id"].component_id,"Graph Type",options=graph_picker_options, add=False)
    toolbox_div = dashboard.create_div(not_modifier_identifiers["toolbox_id"],toolbox_elements,add=False)

    final_elements = toolbox_div + title + plotly_error + cyto_error + graph_container
    dashboard.create_div("content",final_elements)

    # Bind the callbacks
    def update_plotly_graph_inner(*args):
        return update_plotly_graph(dashboard,args)
    def update_cyto_graph_inner(*args):
        return update_cyto_graph(dashboard,args)
    def load_graph_inner(contents,filename):
        return load_graph(dashboard,contents,filename)
    def change_graph_type_inner(graph_type):
        return change_graph_type(dashboard,graph_type)

    dashboard.add_callback(update_plotly_graph_inner,list(plotly_update_inputs.values()),list(plotly_update_outputs.values()))
    dashboard.add_callback(update_cyto_graph_inner,list(cyto_update_inputs.values()),list(cyto_update_outputs.values()))
    dashboard.add_callback(load_graph_inner,list(load_inputs.values()),list(load_outputs.values()),list(load_states.values()))
    dashboard.add_callback(change_graph_type_inner,list(graph_type_inputs.values()),list(graph_type_outputs.values()))
    dashboard.run()


def update_plotly_graph(dashboard,*args):
    if not isinstance(dashboard.visualiser,PlotlyVisualiser):
        raise dash.exceptions.PreventUpdate()
    args = args[0]
    old_settings = dashboard.visualiser.copy_settings()
    for index,setter_str in enumerate(args):
        if setter_str is not None:
            try:
                setter = getattr(dashboard.visualiser,setter_str,None)
                parameter = None
            except TypeError:
                # Must be a input element rather than a checkbox.
                # With annonymous implementation this is tough.
                to_call = list(plotly_update_inputs.keys())[index]
                parameter = setter_str
                setter = getattr(dashboard.visualiser,to_call,None)                    
            if setter is not None:
                try:
                    if parameter is not None:
                        setter(parameter)
                    else:
                        setter()
                except Exception as ex:
                    return reverse_graph(dashboard, old_settings,ex)

    try:
        figure = dashboard.visualiser.build(show=False)
        figure.update_layout(transition_duration=500)
        return figure,False,"No Error"
    except Exception as ex:
        return reverse_graph(dashboard, old_settings,ex)
    

def update_cyto_graph(dashboard,*args):
    if not isinstance(dashboard.visualiser,CytoscapeVisualiser):
        raise dash.exceptions.PreventUpdate()
    args = args[0]
    old_settings = dashboard.visualiser.copy_settings()
    for index,setter_str in enumerate(args):
        if setter_str is not None:
            try:
                setter = getattr(dashboard.visualiser,setter_str,None)
                parameter = None
            except TypeError:
                # Must be a input element rather than a checkbox.
                # With annonymous implementation this is tough.
                to_call = list(cyto_update_inputs.keys())[index]
                parameter = setter_str
                setter = getattr(dashboard.visualiser,to_call,None)                    
            if setter is not None:
                try:
                    if parameter is not None:
                        setter(parameter)
                    else:
                        setter()
                except Exception as ex:
                    return reverse_graph(dashboard, old_settings,ex)

    try:
        figure = dashboard.visualiser.build(show=False)
        #figure.update_layout(transition_duration=500)
        return [figure],False,["No Error"]
    except Exception as ex:
        return reverse_graph(dashboard, old_settings,ex)

def load_graph(dashboard,contents,filename):
    if filename is None or contents is None:
        raise dash.exceptions.PreventUpdate()
    else:
        contents = contents[0]
        filename = filename[0]
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        decoded = decoded.decode('utf-8')
        if os.path.isfile(filename):
            os.remove(filename)
        f = open(filename,"a+")
        for l in str(decoded).splitlines():
            f.write(l + "\n")
        f.close()

        dashboard.visualiser = PlotlyVisualiser(filename)
        dashboard.visualiser._graph.prune_graph()
        figure = dashboard.visualiser.build(show=False)
        
        figure = dashboard.create_graph("plotly_graph",figure,add=False)
        title = _beautify_filename(filename)
        os.remove(filename)
        return title,figure

def change_graph_type(dashboard,graph_type):
    if graph_type is None or isinstance(dashboard.visualiser,graph_types[graph_type]):
        raise dash.exceptions.PreventUpdate()
    
    empty_figure = dashboard.visualiser._create_empty_figure()
    dashboard.visualiser = graph_types[graph_type](dashboard.visualiser._graph)
    dashboard.visualiser._graph.prune_graph()
    figure = dashboard.visualiser.build(show=False)

    if graph_type == "plotly":
        plotly_options_style = {}
        plotly_div_children = dashboard.create_graph(plotly_update_outputs["graph_id"].component_id,figure,add=False) 
        plotly_div_style = {}
        cyto_options_style = {'display': 'none'}
        cyto_div_children = dashboard.create_div(cyto_update_outputs["graph_id"].component_id,[empty_figure],add=False) 
        cyto_div_style = {'display': 'none'}
    else :
        plotly_options_style = {'display': 'none'}
        plotly_div_children = dashboard.create_graph(plotly_update_outputs["graph_id"].component_id,empty_figure,add=False) 
        plotly_div_style = {'display': 'none'}
        cyto_options_style = {}
        cyto_div_children = dashboard.create_div(cyto_update_outputs["graph_id"].component_id,[figure],add=False)
        cyto_div_style = {}

    return plotly_options_style,plotly_div_children,plotly_div_style,cyto_options_style,cyto_div_children,cyto_div_style


def reverse_graph(dashboard,old_settings,error_str = ""):
    for setting in old_settings:
        if setting is not None:
            setting()
    figure = dashboard.visualiser.build(show=False)
    error_string = "Error: " + str(error_str)
    return figure,True,error_string


def _create_form_elements(visualiser,dashboard,style = {},id_prefix = ""):
    options = _generate_options(visualiser)
    removal_words = ["Add","Set","Misc"]
    elements = []
    identifiers = {}
    misc_div = []
    for k,v in options.items():
        removal_words = ["Add","Set","Misc"]
        display_name = _beautify_name(k)
        identifier = id_prefix + "_" + k
        element = []
        miscs = []
        # The misc section is a special option set as they are all independant options.
        if "Misc" in display_name:
            # Create a heading (DisplayName)
            miscs = dashboard.create_heading_4(id_prefix + "_misc_settings","Misc Settings",add=False)
            for k1,v1 in v.items():
                misc_identifer = id_prefix + "_" + k1
                removal_words = removal_words + [word for word in display_name.split(" ")]
                name = _beautify_name(k1)
                name = "".join("" if i in removal_words else i + " " for i in name.split())
                miscs = miscs + dashboard.create_toggle_switch(misc_identifer,name,add=False)
                miscs = miscs + dashboard.create_line_break(add=False)
                identifiers[k1] = Input(misc_identifer,"value")
            
            misc_div = dashboard.create_div(id_prefix + "_misc_container",miscs,add=False,style=style)
            continue

        elif isinstance(v,(int,float)):
            min_v = v/2
            max_v = v*2
            element = dashboard.create_slider(identifier ,display_name,min_v,max_v,default_val=v,add=False)
            identifiers[k] =  Input(identifier,"value")

        elif isinstance(v,dict):
            removal_words = removal_words + [word for word in display_name.split(" ")]
            inputs = []
            for k1,v1 in v.items():
                label = _beautify_name(k1)
                label = "".join("" if i in removal_words else i + " " for i in label.split())
                inputs.append({"label" : label, "value" : k1})

            element = dashboard.create_radio_item(identifier,display_name,inputs,add=False)
            identifiers[k] = Input(identifier,"value")

        breaker = dashboard.create_horizontal_row(False)
        elements = elements + dashboard.create_div(identifier + "_container",element,add=False,style=style)
        elements = elements + breaker 
    
    return elements + misc_div, identifiers


def _beautify_name(name):
    name_parts = name.split("_")
    name = "".join([p.capitalize() + " " for p in name_parts])
    return name

def _beautify_filename(filename):
    clipped_name = filename.split(os.path.sep)[-1].split(".")[0]
    name_parts = clipped_name.split("_")
    
    name = "".join([p.capitalize() + " " for p in name_parts])
    return name

def _generate_options(visualiser):
    blacklist_functions = ["build",
                           "misc_node_settings",
                           "misc_edge_settings",
                           "edge_pos",
                           "node_text_preset",
                           "edge_text_preset",
                           "node_color_preset",
                           "edge_color_preset",
                           "layout",
                           "copy_settings"]

    options = {"preset" : {},
               "layout" : {}}

    for func_str in dir(visualiser):
        if func_str[0] == "_":
            continue
        func = getattr(visualiser,func_str,None)

        if func is None or func_str in blacklist_functions or not callable(func):
            continue
        
        if len(signature(func).parameters) > 0:
            # When there is parameters a slider will be used.
            # Some Paramterised setters will return there default val if one isnt provided.
            default_val = func()
            if default_val is None:
                default_val = 1

            if func_str.split("_")[0] == "misc":
                option_name = "misc"
                if option_name not in options.keys():
                    options[option_name] = {func_str : default_val}
                else:
                    options[option_name][func_str] = default_val
            else:
                options[func_str] = default_val
        else:
            # When no params radiobox.
            if func_str.split("_")[-1] == "preset":
                option_name = "preset"

            elif func_str.split("_")[-1] == "layout":
                option_name = "layout"
            
            elif func_str.split("_")[0] == "misc":
                option_name = "misc"

            elif "node" in func_str:
                option_name = "node" + "_" + func_str.split("_")[-1]
                
            elif "edge" in func_str:
                option_name = "edge" + "_" + func_str.split("_")[-1]
            else:
                option_name = "misc"
            
            if option_name not in options.keys():
                options[option_name] = {func_str : func}
            else:
                options[option_name][func_str] = func

    return options

