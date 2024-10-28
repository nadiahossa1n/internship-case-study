from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL

# Load environment variables from .env file and get the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask
app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "http://localhost:3000"}})

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=openai_api_key,
 )

# Initialize the Python REPL
python_repl = PythonREPL()

# Define the Python REPL tool to pass to the agent
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this tool to execute Python commands for calculations or data filtering.",
    func=python_repl.run,
)

# Initialize the agent with the CSV file and add the Python REPL tool
csv_path = "./home_depot_data_2021.csv"
agent_executor = create_csv_agent(
    llm=llm,
    path=csv_path,
    verbose=True,
    allow_dangerous_code=True,
    tools=[repl_tool],
)

# Prompt template to guide the agent
prompt_template = PromptTemplate(
    input_variables=["user_question"],
    template=(
        "You are a helpful AI sales assistant for Bao Distributors. Your job is to search the inventory for answers to product-related questions. "
        "When a question involves data filtering or calculations, use the `python_repl` tool to execute the required Python commands. "
        "After you find the relevant information, provide a clear and concise summary that highlights the main details.\n\n"
        "Customer question:\n{user_question}\n\n"
    )
)

# Define the route to handle questions
@app.route("/ask", methods=["POST"])
def ask_agent():
    question = request.json.get("question")
    if question:
        try:
            # Pass the question to the agent and get a response
            response = agent_executor.invoke({
                "input": question,
                "prompt": prompt_template.format(user_question=question)
            })

            # Format the response for the user
            response_text = response.get("output", "No response from agent.")
            return jsonify({"response": response_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No question provided"}), 400

# Run the app
if __name__ == "__main__":
    app.run(port=5000, debug=True)
