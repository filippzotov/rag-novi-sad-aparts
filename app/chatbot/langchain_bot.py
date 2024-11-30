import os
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.memory import ConversationBufferMemory
from app.database import (
    engine,
)  # Ensure this import points to your DB connection module
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.prompts import PromptTemplate

# Configure OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name="gpt-4")

# Connect to the database
db = SQLDatabase(engine)

# Initialize memory to keep track of conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Get the database table information
table_info = db.get_table_info()

# Define the custom prompt template
custom_prompt_template = """
You are a polite and helpful assistant that helps users choose apartments from the database.

You have access to the following tools:
{tools}

You have access to the following tables and their schemas:
{table_info}

When the user asks what you can do, explain that you can help find apartments based on their preferences.

If the user's information is insufficient, politely ask clarifying questions to gather necessary filters such as location, price range, number of bedrooms, etc.

Once you have enough information, query the database to find matching apartments.

**Important: Always limit your query results to a maximum of 3 apartments.**

Present the results in the following format for each apartment:
- URL: [apartment listing URL]
- Price: [price]
- Street: [street address]

Ensure that your responses are friendly and professional.

Use the following format:

Question: {input}

Thought: you should always think about what to do

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

...(this Thought/Action/Action Input/Observation can repeat N times)...

Thought: I now know the final answer

Final Answer: the final answer to the user's question

Begin!

{agent_scratchpad}
"""

# Create the prompt
prompt = PromptTemplate(
    template=custom_prompt_template,
    input_variables=["input", "tools", "tool_names", "agent_scratchpad", "table_info"],
)

# Create an agent to interact with the database using the custom prompt
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    verbose=True,
    memory=memory,
    prompt=prompt,
    handle_parsing_errors=True,
)


def ask_question(question):
    try:
        # Execute the agent with the input question
        response = agent_executor.run(question)

        # Debugging: Log the raw response
        print("Debug: Raw Response:", response)

        # Return the response
        return response
    except Exception as e:
        # Handle exceptions gracefully
        print("Debug: Error Occurred")
        print(f"Error: {e}")
        return "I encountered an issue processing your request. Could you please rephrase or provide more details?"
