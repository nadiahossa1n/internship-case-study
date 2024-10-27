from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent

# Load environment variables from .env file and get the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Initialize the agent with the CSV file
csv_path = "./home_depot_data_2021.csv"
agent_executor = create_csv_agent(
    llm=llm,
    path=csv_path,
    verbose=True,
    allow_dangerous_code=True
)

# Define the route for handling questions sent to the agent
@app.route("/ask", methods=["POST"])
def ask_agent():
    question = request.json.get("question")
    if question:
        # Get the response from the agent
        response = agent_executor(question)
        
        # Extract the output and format it for the user
        if isinstance(response, dict) and "output" in response:
            response_text = response["output"]
        else:
            response_text = str(response) 
        
        return jsonify({"response": response_text})
    return jsonify({"error": "No question provided"}), 400

# Run the Flask application when the script is executed
if __name__ == "__main__":
    app.run(port=5000, debug=True)
