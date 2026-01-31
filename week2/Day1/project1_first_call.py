"""
Project 1: First OpenAI API Call
---------------------------------
This script demonstrates:
- Loading API keys from .env file
- Making a simple OpenAI API call
- Measuring response time
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def make_simple_call(prompt, temperature=0.7):
    """
    Make a simple call to OpenAI API

    Args:
        prompt: The user's message
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)

    Returns:
        tuple: (response_text, response_time_seconds)
    """
    print(f"\n{'='*60}")
    print(f"Making API call with temperature={temperature}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}\n")

    # Start timer
    start_time = time.time()

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4o model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=150  # Limit response length for faster results
    )

    # Calculate response time
    response_time = time.time() - start_time

    # Extract the response text
    response_text = response.choices[0].message.content

    return response_text, response_time


def main():
    print("\n🚀 Project 1: First OpenAI API Call\n")

    # Test 1: Default temperature (0.7)
    prompt = "Explain what a token is in LLMs in one sentence."
    response, elapsed = make_simple_call(prompt, temperature=0.7)

    print(f"Response:\n{response}\n")
    print(f"⏱️  Response Time: {elapsed:.2f} seconds")

    # Test 2: Try with temperature 0.0 (deterministic)
    print("\n\n" + "="*60)
    print("Now trying with temperature=0.0 (deterministic)")
    print("="*60)

    prompt2 = "What are the three primary colors?"
    response2, elapsed2 = make_simple_call(prompt2, temperature=0.0)

    print(f"Response:\n{response2}\n")
    print(f"⏱️  Response Time: {elapsed2:.2f} seconds")

    # Test 3: Try with temperature 1.0 (creative)
    print("\n\n" + "="*60)
    print("Now trying with temperature=1.0 (creative)")
    print("="*60)

    response3, elapsed3 = make_simple_call(prompt2, temperature=1.0)

    print(f"Response:\n{response3}\n")
    print(f"⏱️  Response Time: {elapsed3:.2f} seconds")

    print("\n✅ Project 1 Complete!")
    print("\nTry running this script multiple times and notice:")
    print("- Temperature 0.0 gives the same answer every time")
    print("- Temperature 1.0 gives different, more creative answers")


if __name__ == "__main__":
    main()
