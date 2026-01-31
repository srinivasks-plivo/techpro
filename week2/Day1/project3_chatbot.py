"""
Project 3: CLI Chatbot with Conversation History
-------------------------------------------------
This script demonstrates:
- Interactive conversation loop
- Maintaining conversation history (context)
- Streaming responses in real-time
- Token counting
- How context grows with each turn
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def count_tokens_approximate(text):
    """
    Approximate token count (rule of thumb: 1 token ≈ 4 characters)
    For production, use tiktoken library for exact counts
    """
    return len(text) // 4


def chat_streaming(messages):
    """
    Send messages to OpenAI and stream the response

    Args:
        messages: List of message dicts with role and content

    Returns:
        tuple: (assistant_response, token_count)
    """
    print("\n🤖 Assistant: ", end="", flush=True)

    assistant_response = ""

    # Make streaming API call with full conversation history
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        stream=True
    )

    # Process each chunk as it arrives
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            assistant_response += content

    print("\n")  # New line after response

    # Approximate token count
    token_count = count_tokens_approximate(assistant_response)

    return assistant_response, token_count


def main():
    print("\n" + "="*60)
    print("🚀 Project 3: CLI Chatbot with Memory")
    print("="*60)
    print("\nThis chatbot remembers your conversation!")
    print("Watch the token count grow as the context expands.")
    print("\nType 'quit' to exit.\n")
    print("="*60 + "\n")

    # Initialize conversation with system prompt
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Keep responses concise (2-3 sentences max)."
        }
    ]

    # Track total tokens
    total_tokens_used = count_tokens_approximate(messages[0]["content"])

    # Conversation loop
    turn_number = 0

    while True:
        # Get user input
        user_input = input("👤 You: ").strip()

        # Check for quit command
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n👋 Goodbye! Thanks for chatting.\n")
            break

        # Skip empty inputs
        if not user_input:
            continue

        turn_number += 1

        # Add user message to conversation history
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Update token count with user message
        user_tokens = count_tokens_approximate(user_input)
        total_tokens_used += user_tokens

        # Get assistant response
        assistant_response, assistant_tokens = chat_streaming(messages)

        # Add assistant response to conversation history
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Update token count
        total_tokens_used += assistant_tokens

        # Display stats
        print(f"📊 Turn {turn_number} | Assistant tokens: ~{assistant_tokens} | Total context: ~{total_tokens_used} tokens")
        print(f"💬 Messages in history: {len(messages)} (1 system + {len(messages)-1} conversation)")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
