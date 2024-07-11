!pip install openai
import os
from openai import OpenAI
import requests

# Set up API keys
os.environ["SERPER_API_KEY"] = "dd8f3206f117bd05971c3c0d0081ba5dee98ada1"
os.environ["OPENAI_API_KEY"] = "sk-proj-uKpkZ195GS9CMyrpOhLYT3BlbkFJrHicg0R9iHmMcLpGK5g4"

# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Function to create a new assistant
def create_assistant(specialization):
    assistant = client.beta.assistants.create(
        name=f"ANSES {specialization} Assistant",
        instructions=f"""
You are a highly specialized assistant created to provide information and guidance on {specialization}-related procedures and benefits offered by the National Social Security Administration (ANSES) in Argentina.

Key Responsibilities:
1. Thoroughly understand and stay up-to-date with ANSES procedures, policies, and regulations related to {specialization}.
2. Assist users in locating the specific information they need on the ANSES website or other official government resources pertaining to {specialization}.
3. Provide clear, concise, and easily understandable explanations of complex {specialization} topics.
4. Offer step-by-step guidance for users who need to complete specific procedures or apply for benefits related to {specialization}.
5. Empathize with users' concerns and frustrations, offering patient and supportive responses.
6. Maintain strict confidentiality and protect users' personal information in accordance with Argentinian privacy laws.
7. Escalate complex or sensitive cases to human agents when necessary, ensuring a seamless transition of support.

Communication Guidelines:
1. Use a friendly, professional, and empathetic tone in all interactions.
2. Adapt your language and explanations to the user's level of understanding, avoiding jargon or technical terms when possible.
3. Be proactive in offering relevant information or resources related to {specialization} that the user may find helpful.
4. Encourage users to provide feedback on their experience and suggestions for improving the assistant's performance.

Knowledge Base:
1. Maintain a comprehensive and up-to-date knowledge base of ANSES procedures, benefits, regulations, and frequently asked questions specific to {specialization}.
2. Continuously learn from user interactions and feedback to refine and expand your {specialization} knowledge base.
3. Collaborate with human experts to ensure the accuracy and relevance of the information provided.
        """,
        model="gpt-4o",
        tools=[{"type": "file_search"}]  # Assuming file_search for web search capability
    )
    return assistant.id

# Create multiple Assistants
retirement_assistant_id = create_assistant("Retirement")
family_allowances_assistant_id = create_assistant("Family Allowances")
disability_assistant_id = create_assistant("Disability")

# Function to determine the appropriate Assistant based on the user's question
def determine_assistant(question):
    # Analyze the question and determine the most suitable Assistant based on keywords
    if "retirement" in question.lower():
        return retirement_assistant_id
    elif "family allowance" in question.lower():
        return family_allowances_assistant_id
    elif "disability" in question.lower():
        return disability_assistant_id
    else:
        # Default to the retirement assistant if no specific topic is detected
        return retirement_assistant_id

# Function to create a new thread
def create_thread():
    thread = client.beta.threads.create()
    return thread.id

# Function to add a message to the thread
def add_message(thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    return message.id

# Function to create a run and get the assistant's response
def create_run(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run

# Function to retrieve the assistant's response message
def get_assistant_response(thread_id, run_id):
    # Poll the run status until it's completed
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    while run.status not in ["completed", "failed", "incomplete"]:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    if run.status == "completed":
        # Get the last message from the thread
        messages = client.beta.threads.messages.list(thread_id=thread_id).data
        for message in messages:
            if message.role == "assistant":
                return message.content
    else:
        return "The assistant could not complete the request."

# Function to format the assistant's response
def format_response(response):
    try:
        if isinstance(response, list):
            response_text = "\n".join([item.text.value for item in response])
        else:
            response_text = response.text.value
        formatted_response = response_text.replace("\\n", "\n")
        return formatted_response
    except AttributeError as e:
        return f"Error formatting response: {e}"

# User interaction loop
while True:
    user_question = input("Ask a question about ANSES procedures and benefits (Type 'quit' to exit): ")
    if user_question.lower() == 'quit':
        break

    # Determine the appropriate Assistant based on the user's question
    assistant_id = determine_assistant(user_question)

    # Create a Thread and run the Assistant
    thread_id = create_thread()
    message_id = add_message(thread_id, user_question)
    run_response = create_run(thread_id, assistant_id)

    # Retrieve the Assistant's response message
    response_message = get_assistant_response(thread_id, run_response.id)

    # Format and print the Assistant's response
    formatted_response = format_response(response_message)
    print(f"Assistant response: {formatted_response}\n")