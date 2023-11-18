from radcad import Model, Simulation, Experiment, Engine
import pandas as pd
from pydantic import create_model
import inspect
from inspect import Parameter
import plotly.express as px
from typing import List, Callable, Dict, Union, Any
#analysis agent imports
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
#vector database documentation agent imports
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


class Toolkit:
    """
    A class representing a toolkit for working with a cadCAD Python model.

    Attributes:
        model (radcad.Model): The cadCAD model.
        simulation (radcad.Simulation): The cadCAD simulation.
        experiment (radcad.Experiment): The cadCAD experiment.
        df (pandas.DataFrame): The dataframe to use for function execution.

    """
    def __init__(self, model: Model, simulation: Simulation, experiment: Experiment, df: pd.DataFrame, docs:str = '') -> None:
        self.model = model
        self.simulation = simulation
        self.experiment = experiment
        self.df = df
        self.function_schemas = self.get_function_schemas()
        self.params = self.model.params

    
    def get_function_schemas(self) -> List[Dict[str, Union[str, Any]]]:
        """
        Generates a schema for each function in the toolkit.

        The schema includes the function name, description, and parameters.

        Returns:
            list: A list of dictionaries representing the function schemas.

        """
        function_schemas = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and obj.__name__ != '__init__' and obj.__name__ != 'get_function_schemas':
                kw = {n: (o.annotation, ... if o.default == inspect.Parameter.empty else o.default)
                    for n, o in inspect.signature(obj).parameters.items()}
                s = create_model(f'Input for `{obj.__name__}`', **kw).schema()
                function_schemas.append(dict(name=obj.__name__, description=obj.__doc__, parameters=s))
        return function_schemas

    def change_param(self, param: str, value: float) -> str:
        """
        Changes the parameter of the cadCAD simulation and runs the simulation to update dataframe.

        Args:
            param (str): The name of the parameter to change. Must be a parameter of the model.
            value (float): The new value for the parameter.

        Returns:
            str: A message indicating the new parameter value and that the simulation dataframe has been updated.

        """
        Investor_list = [{'type': 'Private',
                        'InvestorBool': True,
                        'unlocked_at_listing': 25.0,
                        'lock_term_after_listing': 3,
                        'release_term': 24,
                        'perc_total_token_supply': 0.267,
                        'tokens': 0},
                        {'type': 'Public',
                        'InvestorBool': True,
                        'unlocked_at_listing': 0.0,
                        'lock_term_after_listing': 0,
                        'release_term': 6,
                        'perc_total_token_supply': 0.009,
                        'tokens': 0},
                        {'type': 'Team',
                        'InvestorBool': False,
                        'unlocked_at_listing': 0.0,
                        'lock_term_after_listing': 9,
                        'release_term': 36,
                        'perc_total_token_supply': 0.15,
                        'tokens': 0},
                        {'type': 'Liquidity',
                        'InvestorBool': False,
                        'unlocked_at_listing': 100.0,
                        'lock_term_after_listing': 0,
                        'release_term': 12,
                        'perc_total_token_supply': 0.05,
                        'tokens': 0},
                        {'type': 'Ecosystem',
                        'InvestorBool': False,
                        'unlocked_at_listing': 0.0,
                        'lock_term_after_listing': 0,
                        'release_term': 36,
                        'perc_total_token_supply': 0.524,
                        'tokens': 0}]
        if param not in self.model.params:
            return f'{param} is not a parameter of the model try choosing from {self.model.params.keys()}'
        value = float(value)
        self.simulation.model.params.update({
            param: [value]
        })
        self.experiment = Experiment(self.simulation)
        self.experiment.engine = Engine()
        result = self.experiment.run()
        def post_processing(df):
            df2 = df.copy()
            investor_types=[]
            for investor in df2['Investors'][0]:
                investor_types.append(investor['type'])
            #make a new dataframe called df2 with the column names as the investor types and the values as the tokens
            df3 = pd.DataFrame(columns=investor_types)
            for i in range(df2.shape[0]):
                for j in range(Investor_list.__len__()):
                    df3.loc[i, df['Investors'][i][j]['type']] = df2['Investors'][i][j]['tokens']

            # remove the investor column from df and add df2 into df)
            df2 = pd.concat([df3, df2['timestep']], axis=1)
            # df2.set_index('timestep', inplace=True)
            df2.rename(columns={'timestep': 'month'}, inplace=True)
            return df2
        # Convert the results to a pandas DataFrame
        df3 = pd.DataFrame(result)
        # Post-process the results
        df3 = post_processing(df3)
        self.df = df3
        return f'new {param} value is {value} and the simulation dataframe is updated'

    
    def model_info(self, param: str) -> Union[Dict[str, float], str]:
        """
        Returns quantitative values of current state of the simulation parameters.

        Args:
            param (str): The name of the parameter to retrieve. If 'all', returns all parameters. Must be a parameter of the model.

        Returns:
            Union[Dict[str, float], str]: A dictionary of parameter names and values, or a message indicating that the parameter is not part of the model.

        Raises:
            ValueError: If the parameter name is not part of the model.

        """
        if param == 'all':
            output=''
            for param in self.simulation.model.params:
                output= output +f'\n{param} is {self.simulation.model.params[param][0]}'
            return output
        elif param in self.simulation.model.params:
            return f'{param} value is {self.simulation.model.params[param][0]}'
        else:
            return f'{param} is not a parameter of the model try choosing from {self.model.params.keys()}'

    # pandas agent as a tool

    def analysis_agent(self, question: str) -> str:
        """
        Analyzes the dataframe and returns the answer to the question.

        Args:
            question (str): The question to ask the dataframe.

        Returns:
            str: The answer to the question.

        """
        pandas_agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
                                                    self.df,
                                                    verbose=True,
                                                    agent_type=AgentType.OPENAI_FUNCTIONS)
        answer = pandas_agent.run(question)
        return answer

    def long_term_memory(self, query: str) -> str:
        """
        Returns the documentation of the model.

        Args:
            query (dict): A sql query for a table with columns 'project', 'raised', 'sector', 'round', 'date'.S

        Returns:
            str: The answer to the question based on the model documentation.

        """
        info = 'M^ZERO, Nibiru, Trident Digital'


        return info

    def plotter(self, column_name: str) -> None:
        """
        Plots the column from the dataframe.

        Args:
            column_name (str): The name of the column to plot.

        Returns:
            None: The plot is displayed using the `fig.show()` function.

        """
        fig = px.line(self.df, x="month", y=[column_name])
        # change figure size to somethign smaller
        fig.update_layout(
            autosize=False,
            width=600,
            height=200,
            margin=dict(
                l=50,
                r=50,
                b=50,
                t=50,
                pad=4
            ),
        )
        fig.show()
        return None


        

