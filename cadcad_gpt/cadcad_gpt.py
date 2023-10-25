from typing import List, Dict
from radcad import Experiment, Model, Simulation
from utils import print_color, plan_parser
from agents import PlannerAgent, ExecutorAgent
from tools import Toolkit
import json
import pandas as pd


class CadCAD_GPT:
    def __init__(self, model: Model, simulation: Simulation, experiment: Experiment, docs: str, api_key: str):
        """initializing the cadcad_gpt object using radcad model, simulation and experiment objects, documentation of the model and openai api key"""
        self.model = model
        self.simulation = simulation
        self.experiment = experiment
        self.docs = docs
        self.api_key = api_key
        self.df = pd.DataFrame(self.experiment.run())
        #create toolkit object
        self.toolkit = Toolkit(self.model, self.simulation, self.experiment, self.df)
        #bring the function schema list from toolkit for agents to use
        self.function_list = self.toolkit.function_list
        #create planner and executor agents
        self.planner_agent = PlannerAgent(self.function_list, self.api_key)
        self.executor_agent = ExecutorAgent(self.df, self.function_list, self.api_key)
        

    def __call__(self, user_input: str):
        #send user input to planner agent
        reply = self.planner_agent(user_input).choices[0].message.content
        plan_list = plan_parser(reply)
        #if there is no plan then return the response from the planner agent
        if plan_list == []:
            return reply
        
        #if plan_list is not empty then print the plan and pass it one by one to the executor agent
        print_color("Planner Agent:", "32")
        print('I have made a plan to follow:')
        for plan in plan_list:
            print(plan)
        print('\n')

        for plan in plan_list:
            print_color("Executor Agent:", "31")
            print('Thought: My task is to', plan)
            #send plan to executor agent
            message = self.executor_agent(plan).choices[0].message

            #if message.content is None then it means the executor agent has called a function
            if (message.content==None):
                function_name = message['function_call']['name']
                function_args = json.loads(message['function_call']['arguments'])
                print('Action: I should call', function_name, 'function with these',
                      function_args, 'arguments')
                print('Observation: ', eval(f'self.toolkit.{function_name}')(**function_args))
                #reflect the changes made by the tools to the model, simulation, experiment and df.
                self.df = self.toolkit.df
                self.model = self.toolkit.model
                self.simulation = self.toolkit.simulation
                self.experiment = self.toolkit.experiment
            #if message.content is not None then there is no function call and the executor agent has replied with a response
            else:
                print('Response: ', message.content)