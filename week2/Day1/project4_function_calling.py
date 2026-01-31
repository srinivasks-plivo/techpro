"""
Project 4: Function Calling (Tools)
------------------------------------
This script demonstrates:
- How LLMs can decide to call functions based on user queries
- Defining tools/functions for the AI to use
- The AI choosing when to use tools vs answering directly
- Processing function results and continuing the conversation

This is the foundation for voice AI that can DO things, not just talk!
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================
# DEFINE ACTUAL FUNCTIONS (these do the real work)
# ============================================================

def get_current_time():
    """Returns the current time"""
    now = datetime.now()
    return {
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%A, %B %d, %Y"),
        "timezone": "Local time"
    }


def get_weather(location):
    """
    Mock weather function (returns fake data)
    In production, this would call a real weather API
    """
    # Fake weather data for demo purposes
    weather_data = {
        "tokyo": {"temp": 72, "condition": "Partly cloudy", "humidity": 65},
        "new york": {"temp": 55, "condition": "Rainy", "humidity": 80},
        "london": {"temp": 48, "condition": "Foggy", "humidity": 90},
        "san francisco": {"temp": 68, "condition": "Sunny", "humidity": 55},
    }

    location_lower = location.lower()

    # Return weather if we have it, otherwise make up generic data
    if location_lower in weather_data:
        return weather_data[location_lower]
    else:
        return {
            "temp": 70,
            "condition": "Clear",
            "humidity": 50,
            "note": f"Mock data for {location}"
        }


# ============================================================
# DEFINE TOOL SCHEMAS (tells the AI what functions exist)
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time and date",
            "parameters": {
                "type": "object",
                "properties": {},  # No parameters needed
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city or location to get weather for (e.g., 'Tokyo', 'New York')"
                    }
                },
                "required": ["location"]
            }
        }
    }
]


# Map function names to actual functions
available_functions = {
    "get_current_time": get_current_time,
    "get_weather": get_weather
}


def chat_with_tools(user_message, messages):
    """
    Send a message and handle any function calls

    Args:
        user_message: The user's input
        messages: Conversation history

    Returns:
        tuple: (assistant_response, messages)
    """
    # Add user message to history
    messages.append({
        "role": "user",
        "content": user_message
    })

    print(f"\n👤 You: {user_message}")

    # Make API call with tools available
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"  # Let the model decide when to use tools
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Check if the model wants to call functions
    if tool_calls:
        print("\n🔧 AI is calling functions...\n")

        # Add the assistant's response (with tool calls) to messages
        messages.append(response_message)

        # Process each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"   📞 Calling: {function_name}")
            print(f"   📋 Arguments: {function_args}")

            # Call the actual function
            function_to_call = available_functions[function_name]

            if function_name == "get_current_time":
                function_response = function_to_call()
            elif function_name == "get_weather":
                function_response = function_to_call(
                    location=function_args.get("location")
                )

            print(f"   ✅ Result: {json.dumps(function_response, indent=6)}\n")

            # Add function response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(function_response)
            })

        # Get final response from the model (it will use function results)
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        final_message = second_response.choices[0].message.content
        messages.append({
            "role": "assistant",
            "content": final_message
        })

        print(f"🤖 Assistant: {final_message}\n")
        return final_message, messages

    else:
        # No function call needed, just a normal response
        assistant_message = response_message.content
        messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        print(f"🤖 Assistant: {assistant_message}\n")
        print("   ℹ️  (No functions were called - AI answered directly)\n")
        return assistant_message, messages


def main():
    print("\n" + "="*60)
    print("🚀 Project 4: Function Calling (Tools)")
    print("="*60)
    print("\nThis chatbot can call functions to get real data!")
    print("Try asking about:")
    print("  • 'What time is it?'")
    print("  • 'What's the weather in Tokyo?'")
    print("  • 'Tell me a joke' (no function needed)")
    print("\nType 'quit' to exit.\n")
    print("="*60 + "\n")

    # Initialize conversation
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to tools. Use them when appropriate to provide accurate information."
        }
    ]

    # Run some automated tests first
    print("🧪 AUTOMATED TESTS\n")
    print("="*60)

    # Test 1: Time function
    print("\nTEST 1: Time query (should call get_current_time)")
    print("-" * 60)
    _, messages = chat_with_tools("What time is it?", messages)

    # Test 2: Weather function
    print("\nTEST 2: Weather query (should call get_weather)")
    print("-" * 60)
    _, messages = chat_with_tools("What's the weather in Tokyo?", messages)

    # Test 3: Normal question (no function)
    print("\nTEST 3: General question (should NOT call functions)")
    print("-" * 60)
    _, messages = chat_with_tools("Tell me a joke", messages)

    # Test 4: Complex query requiring function
    print("\nTEST 4: Complex query")
    print("-" * 60)
    _, messages = chat_with_tools("Is it rainy in London right now?", messages)

    print("\n" + "="*60)
    print("✅ Automated tests complete!")
    print("="*60)

    # Now interactive mode
    print("\n💬 INTERACTIVE MODE")
    print("="*60)
    print("Now you can chat freely. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("👤 You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye!\n")
                break

            if not user_input:
                continue

            _, messages = chat_with_tools(user_input, messages)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            break


if __name__ == "__main__":
    main()
