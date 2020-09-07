from cmd import Cmd
 
class PlotlyRunner(Cmd):
    def __init__(self,visualiser):
        super(PlotlyRunner, self).__init__()
        self.visualiser = visualiser
        self.visualiser_options = self._generate_options()

    prompt = 'plr> '
    intro = "PlotlyVisualiser Type ? to list commands\n Type build to build graph."
    
    def do_build(self,inp):
        print("Would you like to prune the graph?")
        print("Pruning the graph aims to simplify the graph by removing unwanted nodes.")
        y_n = input("Y/N")
        if y_n.lower() == "y":
            self.visualiser._graph.prune_graph()
        
        try:
            self.visualiser.build()
        except Exception as ex:
            print(ex)

    def help_build(self):
        print('Builds the graph.')
        print('Takes all the information provided beforehand and builds the custom graph.')
        print('Type build <fn optional> to build. provide optional filename and will save graph as image.')

    def do_set_preset(self,inp):
        try:
            self.visualiser_options["presets"][inp]()
        except KeyError:
            print(f'{inp} is not a valid preset.')

    def help_set_preset(self):
        print('Choose a preset for the graph.')
        print('The presets are designed to give specific views of the graph or a subgraph.')
        print('Type set_preset <preset_name> to set a preset.')
        print('Possible Presets:')
        for k in self.visualiser_options["presets"].keys():
            print(k)

    def do_set_layout(self,inp):
        try:
            self.visualiser_options["layouts"][inp]()
        except KeyError:
            print(f'{inp} is not a valid layout.')

    def help_set_layout(self):
        print('Choose how the visual graph is laid out.')
        print('The layouts set the actualy positional data for the nodes in the graph.')
        print('Type set_layout <layout_name> to set a layout.')
        print('Possible Layouts:')
        for k in self.visualiser_options["layouts"].keys():
            print(k)

    def do_set_misc(self,inp):
        try:
            l = inp.split()
            if len(l) ==2:
                self.visualiser_options["misc"][l[0]](l[1])
            else:
                self.visualiser_options["misc"][inp]()
        except KeyError:
            print(f'{inp} is not a valid option.')
        except TypeError as ex:
            print(ex)

    def help_set_misc(self):
        print('Miscellaneous settings for the graph')
        print('The misc settings are a range of differing options that can be applied to the graph away from layout and preset.')
        print('Type set_misc <misc_name> to set a setting.')
        print('Possible Misc Settings:')
        for k in self.visualiser_options["misc"].keys():
            print(k)

    def do_exit(self, inp):
        return True
    
    def help_exit(self):
        print('exit the application. Shorthand: x q Ctrl-D.')
  
    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)
 
        print("Unknown Input: {}".format(inp))
 
    do_EOF = do_exit
    help_EOF = help_exit

    def _generate_options(self):
        blacklist_functions = [self.visualiser.build,
                               self.visualiser.misc_node_settings,
                               self.visualiser.misc_edge_settings,
                               self.visualiser.edge_pos]

        options = {"presets" : {"full_graph_preset" : self.visualiser.set_full_graph_preset,
                                "interaction_preset" : self.visualiser.set_interaction_preset,
                                "parts_preset" : self.visualiser.set_parts_preset,
                                "functional_preset" : self.visualiser.set_functional_preset},
                    "layouts" : {"spring_layout" : self.visualiser.set_spring_layout,
                                 "circular_layout" : self.visualiser.set_circular_layout,
                                 "kamada_kawai_layout" : self.visualiser.set_kamada_kawai_layout,
                                 "planar_layout" : self.visualiser.set_planar_layout,
                                 "shell_layout" : self.visualiser.set_shell_layout,
                                 "spiral_layout" : self.visualiser.set_spiral_layout,
                                 "spectral_layout" : self.visualiser.set_spectral_layout,
                                 "random_layout" : self.visualiser.set_random_layout,
                                 "graphviz_layout" : self.visualiser.set_graphviz_layout,
                                 "pydot_layout" : self.visualiser.set_pydot_layout},
                    "misc" : {}}

        for func_str in dir(self.visualiser):
            if func_str[0] == "_":
                continue
            func = getattr(self.visualiser,func_str,None)
            if (func is None or 
                func in options["presets"].values() or 
                func in options["layouts"].values() or 
                func in options["misc"].values() or func in blacklist_functions):
                continue
            
            if func_str.split("_")[-1] == "preset":
                if func_str not in options["presets"]:
                    options["presets"][func_str] = func
            elif func_str.split("_")[-1] == "layout":
                if func_str not in options["layouts"]:
                    options["layouts"][func_str] = func
            else:
                options["misc"][func_str] = func

        return options

def plotly_runner(plotly_visualiser,title=None):
    runner = PlotlyRunner(plotly_visualiser)
    runner.cmdloop()




