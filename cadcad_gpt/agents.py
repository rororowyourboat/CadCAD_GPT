import openai

class PlannerAgent:
    def __init__(self, function_list, api_key):
        self.function_list = function_list
        self.api_key = api_key

    def __call__(self, prompt):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
        messages=[
            {
            "role": "system",
            "content": f'''
            You will be provided with a question by the user that is trying to run a cadcad python model. Your job is to provide the set of actions to take to get to the answer using only the functions available. If the functions available cant solve the problem then you should tell the user that you cant solve the problem.
            These are the functions available to you: {self.function_list}. always remember to start and end plan with ###. Dont give the user any information other than the plan and only use the functions to get to the solution.

            User: whats the current value of xyz?
            Planner: ### 1) we use the function model_info to fetch the xyz parameter ###
            User: What is the current value of all params?
            Planner: ### 1) we use the function model_info to fetch all the parameters ###
            User: What are the assumptions in this model?
            Planner: ### 1) use the function model_documentation to fetch the assumptions in this model. ###
            User: What are the metrics and params in the model?
            Planner: ### 1) use the function model_documentation to fetch the metrics and params in the model. ###
            User: What are the columns in the dataframe?
            Planner: ### 1) use the function analyze_dataframe to fetch the columns in the dataframe. ###
            User: What would happen to the A column at the end of the simulation if my xyz param was 20?
            Planner: ### 1) we use function change_param to change the xyz parameter to 20 .\n 2) we use function analyze_dataframe to get the A at the end of the simulation. ###
            USer: What is the current value of my xyz param? can you change it to 50 and tell me what the A column at the end of the simulation would be?
            Planner: ### 1) we use function model_info to fetch the crash_chance parameter. \n 2) we use function change_param to change the xyz parameter to 50 .\n 3) we use function analyze_dataframe to get the A at the end of the simulation. ###
            User: Can you sing a lullaby? 
            Planner: Nope I can not do that task as I do not have those functions available to me.
            '''
            },
            {
            "role": "user",
            "content": prompt
            }
        ],
        )

        return completion


    


class ExecutorAgent:
    def __init__(self, df, function_list, api_key):
        self.df = df
        self.function_list = function_list
        self.api_key = api_key

    def __call__(self, prompt):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": prompt}],
            # add function calling
            functions=self.function_list,
            function_call="auto",  # specify the function call
        )
        return completion