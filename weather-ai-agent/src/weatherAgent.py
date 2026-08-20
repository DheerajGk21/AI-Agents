from dotenv import load_dotenv
from google import genai
import weather as weather
from config import GEMINI_API_KEY


# --- Create a Client -----
client = genai.Client(api_key=GEMINI_API_KEY)

# --- Get Location input from user -----
user_input = input("You : ")

# --- Ask Gemini to understand the user -----
location_interaction = client.interactions.create(
    model="gemini-3.7-flash",
    input=user_input,
    environment="remote",
    tools=[
        {"type": "code_execution"},  # Enable default code execution
        weather.weather_tool_desc,  # Add custom function
    ],
)

# --- Check if weather is fetched (has get_weather() been executed) -----
weather_result = {}
if location_interaction.status == "requires_action":
    # Will contain the functions executed
    executed_calls = {
        step.call_id
        for step in location_interaction.steps
        if step.type == "function_result"
    }

    # Will contain the functions that has to be executed
    pending_calls = [
        step
        for step in location_interaction.steps
        if step.type == "function_call" and step.id not in executed_calls
    ]

    # If there are functions to be executed, call the function (Gemini wont call the function automatically)
    if pending_calls:
        call = pending_calls[0]
        print("Function to call: ", call.name)
        print("Arguments: ", call.arguments)

        weather_result = weather.get_weather(call.arguments["location"])
        print("\n weather_result : ", weather_result)

# --- Use the fetched data to generate the weather response -----
final_interaction = client.interactions.create(
    model="gemini-3.7-flash",
    previous_interaction_id=location_interaction.id,  # Reference the location_interaction ID
    environment=location_interaction.environment_id,
    system_instruction="If there are no responses, then specify it. Dont assume.",
    input=[
        {
            "type": "function_result",
            "name": weather.weather_tool_desc["name"],
            "result": weather_result,
        }
    ],
)

print("Agent : ", final_interaction.output_text)
