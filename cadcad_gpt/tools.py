from radcad import Model, Simulation, Experiment, Engine
import pandas as pd
from pydantic import create_model
import inspect, json
from inspect import Parameter


class Toolkit:
    def __init__(self, model:Model, simulation:Simulation, experiment:Experiment, df:pd.DataFrame):
        self.model = model
        self.simulation = simulation
        self.experiment = experiment
        self.df = df
        self.function_list = [
        {
            "name": "change_param",
            "description": "Changes the parameter of the cadcad simulation and returns dataframe as a global object. The parameter must be in this list:" + str(model.params.keys()),
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "parameter to change. choose from the list" + str(self.model.params.keys()),
                    },
                    "value": {
                        "type": "string",
                        "description": "value to change the parameter to, eg. 0.1",
                    },
                },
                "required": ["param", "value"],
            },
        },
        {
            "name": "model_info",
            "description": "quantitative values of current state of the simulation parameters. If no param is specified the argument should be 'all'",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "type of information to print. choose from the list: " + str(self.model.params.keys()),
                    },
                },
                "required": ["param"],
            },
        },
        {
            "name": "analyze_dataframe",
            "description": "Use this whenever a quantitative question is asked about the dataframe. The question should be taken exactly as asked by the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question asked by user that can be answered by an LLM dataframe agent",
                    },
                },
                "required": ["question"],
            },
        },
        {
            "name": "model_documentation",
            "description": "use when asked about documentation of the model has information about what the model is, assumptions made, mathematical specs, differential model specs etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question asked by user that can be answered by an LLM dataframe agent",
                    },
                },
                "required": ["question"],
            },
        }
    ]

    def schema(f):
        kw = {n:(o.annotation, ... if o.default==Parameter.empty else o.default)
            for n,o in inspect.signature(f).parameters.items()}
        s = create_model(f'Input for `{f.__name__}`', **kw).schema()
        return dict(name=f.__name__, description=f.__doc__, parameters=s)

    def change_param(self, param:str, value:float)->str:
        '''Changes the parameter of the cadcad simulation and returns dataframe as a global object. The parameter must be in this list:'''
        if param not in self.model.params:
            return f'{param} is not a parameter of the model'
        value = float(value)
        self.simulation.model.params.update({
            param: [value]
        })
        self.experiment = Experiment(self.simulation)
        self.experiment.engine = Engine()
        result = self.experiment.run()
        # Convert the results to a pandas DataFrame
        self.df = pd.DataFrame(result)
        return f'new {param} value is {value} and the simulation dataframe is updated'

    
    def model_info(self, param:str)->str:
        '''quantitative values of current state of the simulation parameters. If no param is specified the argument should be 'all' '''
        if param == 'all':
            return self.simulation.model.params
        elif param in self.simulation.model.params:
            return f'{param} = {self.simulation.model.params[param]}'
        else:
            return f'{param} is not a parameter of the model'

    # pandas agent as a tool

    
    def analyze_dataframe(self, question:str)->str:
        '''Use this whenever a quantitative question is asked about the dataframe. The question should be taken exactly as asked by the user'''
        # Implement your logic here to analyze the dataframe based on the user's question
        return question
    
    def model_documentation(self, question:str)->str:
        '''use when asked about documentation of the model has information about what the model is, assumptions made, mathematical specs, differential model specs etc.'''
        # Implement your logic here to provide documentation based on the user's question
        return question


