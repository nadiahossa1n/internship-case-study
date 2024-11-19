from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load environment variables from .env file and get the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7, openai_api_key=openai_api_key)

# Initialize the agent with the CSV file
csv_path = "./home_depot_data_2021.csv"
agent_executor = create_csv_agent(
    llm=llm,
    path=csv_path,
    agent_type="openai-functions",
    verbose=True,
    allow_dangerous_code=True,
)

# Define the prompt template with a system message and history placeholder
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are a helpful AI sales assistant for Bao Distributors."
         "Use the conversation history for context to understand follow-up questions and provide consistent, coherent answers."
         "Use partial matching when searching for specific products and provide a concise summary including the product name, description, and URL."
         ),
        MessagesPlaceholder("history", n_messages=5),
    ]
)

# Define the route to handle questions
@app.route("/ask", methods=["POST"])
def ask_agent():
    global history
    question = request.json.get("question")
    if question:
        try:
            # Add the current question to history as a HumanMessage
            history.append(HumanMessage(content=question))

            # Prepare the prompt input with memory (history) and user question
            prompt_input = prompt_template.invoke({
                "history": history
            })

            # Pass the question to the agent and get a response
            response = agent_executor.invoke({
                "input": prompt_input
            })

            # Extract and store the response in history
            response_text = response.get("output", "No response from agent.")
            history.append(AIMessage(content=response_text))

            # Return the response to the user
            return jsonify({"response": response_text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No question provided"}), 400

# Run the app
if __name__ == "__main__":
    history = []  # Initialize an empty history list to store messages
    app.run(port=5000, debug=True)