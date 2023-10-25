from radcad import Model, Simulation, Experiment, Engine
import pandas as pd
from pydantic import create_model
import inspect
from inspect import Parameter
import plotly.express as px
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
    def __init__(self, model:Model, simulation:Simulation, experiment:Experiment, df:pd.DataFrame):
        self.model = model
        self.simulation = simulation
        self.experiment = experiment
        self.df = df
        self.function_list =  [self.schema(f) for f in self.parse_functions()]  


    def schema(self,f):
        kw = {n:(o.annotation, ... if o.default==inspect.Parameter.empty else o.default)
            for n,o in inspect.signature(f).parameters.items()}
        s = create_model(f'Input for `{f.__name__}`', **kw).schema()
        return dict(name=f.__name__, description=f.__doc__, parameters=s)

    def parse_functions(self):
        parsed_functions = [getattr(self, method_name) for method_name in dir(self)
                            if callable(getattr(self, method_name))
                            and not method_name.startswith('__')
                            and method_name not in ('schema', 'parse_functions', 'model')]
        return parsed_functions
    
    # tools as functions

    def change_param(self, param:str, value:float)->str:
        '''Changes the parameter of the cadcad simulation and runs the simulation to update dataframe. '''
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

    def analyze_dataframe(self,question:str)->str:
        '''Analyzes the dataframe and returns the answer to the question'''
        pandas_agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
        self.df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        )
        answer = pandas_agent.run(question)
        
        return answer

    def model_documentation(self,question:str)->str:
        '''Returns the documentation of the model'''
        vectorstore = FAISS.from_texts([self.docs], embedding=OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()

        template = """Answer the question based only on the following context:
        {context}

        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI()
        chain = (
            {"context": retriever, "question": RunnablePassthrough()} 
            | prompt 
            | model 
            | StrOutputParser()
        )
        info = chain.invoke(question)

        return info

    def plotter(self,column_name:str)->str:
        '''Plots the column from the dataframe'''
        fig = px.line(self.df, x="timestep", y=[column_name])
        fig.show()

