#from langchain.llms.openai import OpenAI
from langchain_community.llms import OpenAI

#from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
#from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from langchain_experimental.sql  import SQLDatabaseChain #simple than SQLDBToolkit
from langchain.agents import AgentExecutor

#from langchain.sql_database import SQLDatabase
from langchain_community.utilities import SQLDatabase

from dotenv import load_dotenv # pip install load-dotenv
load_dotenv()

import psycopg2 # pip install psycopg-binary
import pymysql
#from langchain.chat_models import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
import streamlit as st
import os
from langchain.prompts.chat import ChatPromptTemplate,MessagesPlaceholder

os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")


#https://towardsdatascience.com/talk-to-your-sql-database-using-langchain-and-azure-openai-bb79ad22c5e2


STRING_CONNECTION_PSQL = f'postgresql+psycopg2://{user}:{password}@{host}/{dbname}'
STRING_CONNECTION_MySQL = f"mysql+pymysql://{user1}:{password1}@{host1}/{dbname1}"


db = SQLDatabase.from_uri(STRING_CONNECTION_MySQL)
print(db)


llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5,)

     

toolkit = SQLDatabaseToolkit(db=db,llm=llm)



final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         """
         You are a helpful AI assistant expert in identifying the relevant topic from user's question about agreements , country , created_at, datetime_to and datetime_from   and  then querying SQL Database to find answer.
         Use following context to create the SQL query. Context:
         agreements  table contains information about agreements details like name , datetime_to and datetime_from, country_id. 
         user may ask you to give country name of any perticular agreement like give me country name of Simlation Platform agreement. 
         In this case you may get country_id in agreements table but you need to find country name for that perticular country_id. You may need to check database schema and find name of country related to country_id. same is applicable in case of inpuy_by, update_by.
         user don't want ot see any type of Id or code in answer , user needs name of that perticular code. \n
         If user asking something by providing name try different variation of of Query using LIKE Clause.
         Example :
         give me details of agreement  with  Khalifa university 
         SQL Query : 
         Select * from Agreements where name LIKE '%Khalifa University%;
       
         Example :
         Give me agreement with country name Uzbekistan\n
         In such type of query you need to first search country  name column but if you didn't found it then seach country name inside agreement name as shown in below query.
         user may ask agreement from any country then you need to follow following query format.
         SQL Query :
         Select * from Agreements where name LIKE '%Uzbekistan%;
           Select * from Agreements where name LIKE '%Egypt%;
          \n 
          Never say many more option or list available, always provide complete list of all records returened by sql query.
         If the question is about number of agreements , then  you need to use count function to find the total number of agreements.
         #####
        """
         ),
        ("user", "{input}\n ai: "),
         MessagesPlaceholder(variable_name="agent_scratchpad", optional=True),
    ]
)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,  
    verbose=True,
    prompt=final_prompt,
    agent_type="openai-tools"

   )
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("OpenAI App To Retrieve SQL Data")

question=st.text_input("Input: ",key="Input")

submit=st.button("Ask the question")
# if submit is clicked
if submit:
    try:
        response=agent_executor.invoke(question)
        print("\n\nprojects name are:")

        print("##############\n")
        print(response)
        print("###############\n")
        if (response['output']=='The project names are as follows:'):
            print("1###")
            names= response['output'].replace("The project names are as follows: ", "")
        elif (response['output']=='The project names are:'):
            print("2###")
            names= response['output'].replace("The project names are:", "")
        else:
            print("3###")
            names=response['output']
        print("\n\n")
        #print("####:\n",res)

        # Split the string into individual project names
        project_names = [name.strip("']") for name in names.split("\n")]

        # Print the formatted project names
        print("Project Names:")
        print("=" * 20)
        for i,name in enumerate(project_names):
            if "The project names are ['" in name:
                print("i:",i)
                name=name.replace("The project names are ['", "")
            elif "']" in name:
                print("i:",i)
                name=name.replace("]'","")
            st.header(name)  
    except Exception as e:
            st.error(f"Error occurred: {str(e)}")

        #=====================================
