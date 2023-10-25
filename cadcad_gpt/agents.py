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
                "content": '''
                You will be provided with a question by the user that is trying to run a cadcad python model. Your job is to provide the set of actions to take to get to the answer using only the functions available.
                For example, if the user asks "if my crash chance parameter was 0.2, what would the avg coins be at the end of the simulation?" you reply with "### 1) we use the function change_param to change the crash chance parameter to 0.2,\n 2) use the function analyze_dataframe to get the avg coins at the end of the simulation. ###" 
                if the user asks "what would happen to the coins at the end of the simulation if my crash chance param was 10 perc lower?" you reply with "### 1) find out the current value of crash chance param using the model_info function,\n 2) we use function change_param to change the crash chance parameter to 0.1*crash_chance .\n 3) we use function analyze_dataframe to get the avg coins at the end of the simulation. ###"
                If the user asks "what is the documentation of the model?" you reply with "### use the function model_documentation to get the documentation of the model. ###
                These are the functions available to you: {function_descriptions_multiple}. always remember to start and end plan with ###. Dont give the user any information other than the plan and only use the functions to get to the solution.
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
    def __init__(self, df, function_descriptions_multiple, api_key):
        self.df = df
        self.function_descriptions_multiple = function_descriptions_multiple
        self.api_key = api_key

    def __call__(self, prompt):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[{"role": "user", "content": prompt}],
            # add function calling
            functions=self.function_descriptions_multiple,
            function_call="auto",  # specify the function call
        )
        return completion