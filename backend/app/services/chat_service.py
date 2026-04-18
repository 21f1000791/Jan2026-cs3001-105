import os
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from flask import current_app

class ChatService:
    @staticmethod
    def chat_with_database(user_query: str):
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            return "System Error: GROQ_API_KEY is missing."

        try:
            # 1. Grab the absolute path to the instance folder where your REAL DB lives
            db_path = os.path.join(current_app.instance_path, "community_ops.db")
            
            # Safety check so you know if the path is wrong!
            if not os.path.exists(db_path):
                return f"System Error: Could not find database at {db_path}"

            db_uri = f"sqlite:///{db_path}"
            db = SQLDatabase.from_uri(db_uri)

            # 2. Use Llama-3.3 70B on Groq
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=api_key, 
                temperature=0
            )

            # 3. Create Agent with auto-error recovery
            agent_executor = create_sql_agent(
                llm, 
                db=db, 
                agent_type="tool-calling", 
                verbose=True,
                handle_parsing_errors=True # <--- This makes the AI much smarter at recovering from SQL typos
            )

            # 4. The System Prompt
            system_prompt = (
                f"You are a Data Analyst Assistant for Community Ops managers. "
                f"Answer the user's question by writing and executing a SQLite query. "
                f"If the user asks a general knowledge question unrelated to the database, politely decline. "
                f"User Question: {user_query}"
            )

            response = agent_executor.invoke({"input": system_prompt})
            return response.get("output", "I could not find an answer in the database.")

        except Exception as e:
            print(f"LangChain Error: {e}")
            return "I encountered an error querying the database. Please try rephrasing your question."