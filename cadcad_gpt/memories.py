# def analyze_dataframe(question):
#     '''Analyzes the dataframe and returns the answer to the question'''
#     # pandas_agent = agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)
#     pandas_agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
#     df,
#     verbose=True,
#     agent_type=AgentType.OPENAI_FUNCTIONS,
#     )
#     answer = pandas_agent.run(question)
    
#     return answer

# def model_documentation(question):
#     '''Returns the documentation of the model'''
#     vectorstore = FAISS.from_texts([docs], embedding=OpenAIEmbeddings())
#     retriever = vectorstore.as_retriever()

#     template = """Answer the question based only on the following context:
#     {context}

#     Question: {question}
#     """
#     prompt = ChatPromptTemplate.from_template(template)
#     model = ChatOpenAI()
#     chain = (
#         {"context": retriever, "question": RunnablePassthrough()} 
#         | prompt 
#         | model 
#         | StrOutputParser()
#     )
#     info = chain.invoke(question)

#     return info