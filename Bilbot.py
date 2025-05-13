from flask import Flask, render_template, request, jsonify
from langchain_ollama import OllamaLLM

app = Flask(__name__)

# Create the LLM using LLaMA 3
llm = OllamaLLM(model="Bilbot") # replace this with actual model name

# Store conversation history
conversation_history = []

# Function to load convex hull-related keywords from a file
def load_bilbot_keywords(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            keywords = [line.strip().lower() for line in file.readlines() if line.strip()]
        return keywords
    except FileNotFoundError:
        print("Error: Bilbot-Data.txt not found. Using default keywords.")
        return ["linear search", "binary search"]  # Fallback keyword

# Load convex hull keywords from the file
bilbot_keywords = load_bilbot_keywords("Bilbot-Data.txt")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    user_input = request.json.get("message", "").strip() if request.json else ""
    
    if not user_input:
        return jsonify({"response": "Please enter a message."})

    if user_input.lower() in ["hi", "hey", "what's up"]:
        return jsonify({"response": "Hello Pal! Nice to see you! How can I help you?"})

    if user_input.lower() == "x":
        return jsonify({"response": "Bilbot is ready! Type 'x' to quit.\n"})

    try:
        # Check if the conversation is on-topic
        if not conversation_history and not any(word in user_input.lower() for word in bilbot_keywords):
            return jsonify({"response": "Stay on the topic of linear and binary search only, Pal."})

        # Check for emotional or unrelated questions first
        if any(word in user_input.lower() for word in ["feel", "sad", "happy", "love", "emotion"]):
            if "feel" in user_input.lower():
                return jsonify({"response": "Hmm.. I really can't feel any emotions, Pal. I'm only a chatbot that specializes in linear and binary search algorithms."})
            else:
                return jsonify({"response": "Sorry, Pal. I really don't know what you just typed. Try asking me about linear and binary search algorithms."})

        # Handle general "algorithm" questions
        if "algorithm" in user_input.lower() and not any(word in user_input.lower() for word in bilbot_keywords):
            return jsonify({"response": "Uh.. sorry to disappoint you, pal. But I can only tell you about linear and binary search algorithms. Try searching for more."})

        # Append user question to conversation history
        conversation_history.append(f"You: {user_input}")

        # Keep only the last 10 exchanges for efficiency
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]

        # Format the conversation for context
        context = "\n".join(conversation_history) + "\nBilbot:"

        # Query LLaMA 3 with full conversation history
        result = llm.invoke(context)

        # Store bot response
        conversation_history.append(f"Bilbot: {result}")

        return jsonify({"response": result})

    except Exception as e:
        return jsonify({"response": f"Error: {e}"})

if __name__ == '__main__':
    app.run(debug=True)