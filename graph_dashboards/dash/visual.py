import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output
import dash_bio as dashbio

class DashBoard:
    def __init__(self,graph_visualiser):
        app = dash.Dash(__name__,suppress_callback_exceptions=True)
        self.app = app
        self.visualiser = graph_visualiser
        self.style = {}
        self.children = []
        self.parameters_calls = []
        self.callbacks = {}

    def run(self):
        self.app.layout = html.Div(style=self.style,children=self.children)
        for k,v in self.callbacks.items():
            if v["states"] == []:
                self.app.callback(v["outputs"],v["inputs"])(k)
            else:
                self.app.callback(v["outputs"],v["inputs"],v["states"])(k)
                

        self.app.run_server(debug=True)

    def add_callback(self,function,inputs,outputs,states=None):
        if states is None:
            states = []
        self.callbacks[function] = {"inputs" : inputs,"outputs" : outputs,"states" : states}
    
    def _create_element(self,*elements):
        self.children = self.children + [*elements]
        return elements

    def create_graph(self,identifier, graph, add=True, **kwargs):
        if graph is None:
            graph = self.visualiser._create_empty_figure()
        graph = dcc.Graph(id=identifier, figure=graph, **kwargs)
        if add:
            return self._create_element(graph)
        else:
            return graph
    
    def create_heading_1(self,identifier,children, add=True, **kwargs):
        heading = html.H1(id=identifier,children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_2(self,identifier,children, add=True, **kwargs):
        heading = html.H2(id=identifier,children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_3(self,identifier,children, add=True, **kwargs):
        heading = html.H3(id=identifier,children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_4(self,identifier,children, add=True, **kwargs):
        heading = html.H4(id=identifier,children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_5(self,identifier,children, add=True, **kwargs):
        heading = html.H5(id=identifier,children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_6(self,identifier,children, add=True, **kwargs):
        heading = html.H6(id=identifier,children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_div(self,identifier,text,add=True,**kwargs):
        div = html.Div(id = identifier,children=text, **kwargs)
        if add:
            return self._create_element(div)
        else:
            return [div]
    
    def create_button(self,identifier,name,add=True,**kwargs):
        button = html.Button(id=identifier,children=name)
        if add:
            return self._create_element(button)
        else:
            return [button]
            
    def create_input(self,identifier,name,value,add=True,**kwargs):
        label = html.Label(name)
        input_l = dcc.Input(id=identifier,value=value, **kwargs)
        if add:
            return self._create_element(label,input_l)
        else:
            return [label,input_l]

    def create_dropdown(self,identifier,name,options,add=True,**kwargs):
        dropdown = dcc.Dropdown(id=identifier,placeholder = name,options=options,**kwargs)
        if add:
            return self._create_element(dropdown)
        else:
            return [dropdown]

    def create_radio_item(self,identifier,name,options,value=None,add=True,**kwargs):
        label = html.Label(name)
        radio = dcc.RadioItems(id=identifier,options=options,value=value,**kwargs)
        if add:
            return self._create_element(label,radio)
        else:
            return [label,radio]

    def create_checklist(self,identifier,name,options,add=True,**kwargs):
        label = html.Label(name)
        checklist = dcc.Checklist(id=identifier,options=options,**kwargs)
        if add:
            return self._create_element(label,checklist)
        else:
            return [label,checklist]

    def create_slider(self,identifier,name,min_val, max_val, default_val = None, step=None, marks = None, add=True,**kwargs):
        label = html.Label(name)
        if default_val is None:
            default_val = max_val/2
        if marks is None:
            marks = {}
            marks[min_val] = str(min_val)
            marks[max_val] = str(max_val)
        if step is None:
            step = max_val/10
        slider = dcc.Slider(id=identifier,min=min_val,max=max_val,value=default_val,marks=marks,step=step,**kwargs)
        if add:
            return self._create_element(label,slider)
        else:
            return [label,slider]
    
    def create_sidebar(self,id,name,content,add=True,style={}):
        sidebar = html.Div([html.H2(name, className="display-4"),html.Hr(),*content],id=id,style=style,)
        if add:
            return self._create_element(sidebar)
        else:
            return [sidebar]
    
    def create_horizontal_row(self,add=True):
        if add:
            return self._create_element(html.Hr())
        else:
            return [html.Hr()]

    def create_line_break(self,add=True):
        if add:
            return self._create_element(html.Br())
        else:
            return [html.Br()]
        
    def create_alert(self,identifier,text,add=True, **kwargs):
        alert = dbc.Alert(id=identifier,children=text, **kwargs)
        if add:
            return self._create_element(alert)
        else:
            return [alert]

    def create_toggle_switch(self,identifier,name,value=False,add=True,**kwargs):
        switch = daq.ToggleSwitch(id=identifier,label=name,value=value,**kwargs)
        if add:
            return self._create_element(switch)
        else:
            return [switch]

    
    def create_color_picker(self,identifier,name,add=True,**kwargs):
        picker = daq.ColorPicker(id=identifier,label=name,**kwargs)
        if add:
            return self._create_element(picker)
        else:
            return [picker]


    def create_indicator(self,identifier,name,color="green",add=True,**kwargs):
        indicator = daq.Indicator(id=identifier,label=name,color=color,**kwargs)
        if add:
            return self._create_element(indicator)
        else:
            return [indicator]

    def create_numeric_input(self,identifier,name,min_val, max_val, default_val = None,add=True,**kwargs):
        if default_val is None:
            default_val = max_val/2

        label = html.Label(name)
        num_input = daq.NumericInput(id=identifier,min=min_val,max=max_val,value=default_val,**kwargs)
        if add:
            return self._create_element(label,num_input)
        else:
            return [label,num_input]
    
    def create_file_upload(self,identifier,name,graph_parent_id,add=True,**kwargs):
        upload_box = dcc.Upload(id=identifier,children=html.Div([dbc.Button(name, color="secondary", className="mr-1")]),multiple=True,**kwargs)
        if add:
            return self._create_element(upload_box)
        else:
            return [upload_box]

    def add_sequence_viewer(self,identifier,sequence,add=True,**kwargs):
        sequence_box = dashbio.SequenceViewer(id=identifier,sequence=sequence,**kwargs)
        if add:
            return self._create_element(sequence_box)
        else:
            return [sequence_box]

    
    def create_modal(self,modal_identifier,close_identifier,content_identifier,add=True):
        modal = html.Div([
                    html.Div([
                        html.Div(id=content_identifier,children=[]),
                        html.Hr(),
                        html.Button('Close', id=close_identifier)
                    ],
                        style={'textAlign': 'center', },
                        className='modal-content',
                    ),
                    ],
                        id=modal_identifier,
                        className='modal',
                        style={"display": "none"},
                    )

        if add:
            return self._create_element(modal)
        else:
            return [modal]

