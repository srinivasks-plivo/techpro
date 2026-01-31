"""
Project 2: Streaming Responses
-------------------------------
This script demonstrates:
- Using OpenAI's streaming API
- Printing tokens as they arrive (character by character effect)
- Measuring time-to-first-token (TTFT) vs total time
- Understanding why TTFT matters for voice AI
"""

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def streaming_call(prompt, temperature=0.7):
    """
    Make a streaming call to OpenAI API

    Args:
        prompt: The user's message
        temperature: Controls randomness

    Returns:
        tuple: (full_response, time_to_first_token, total_time)
    """
    print(f"\n{'='*60}")
    print(f"Streaming API call with temperature={temperature}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}\n")
    print("Response (streaming): ", end="", flush=True)

    # Start timer
    start_time = time.time()
    first_token_time = None
    full_response = ""

    # Make streaming API call
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=150,
        stream=True  # Enable streaming!
    )

    # Process each chunk as it arrives
    for chunk in stream:
        # Check if there's content in this chunk
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content

            # Record time to first token
            if first_token_time is None:
                first_token_time = time.time() - start_time

            # Print the content immediately (creates typing effect)
            print(content, end="", flush=True)

            # Add to full response
            full_response += content

    # Calculate total time
    total_time = time.time() - start_time

    print("\n")  # New line after response

    return full_response, first_token_time, total_time


def non_streaming_call(prompt, temperature=0.7):
    """
    Make a non-streaming call for comparison

    Args:
        prompt: The user's message
        temperature: Controls randomness

    Returns:
        tuple: (response, total_time)
    """
    print(f"\n{'='*60}")
    print(f"Non-streaming API call (for comparison)")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}\n")
    print("Waiting for response...", end="", flush=True)

    start_time = time.time()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=150
    )

    total_time = time.time() - start_time
    response_text = response.choices[0].message.content

    print(f"\n\nResponse: {response_text}\n")

    return response_text, total_time


def main():
    print("\n🚀 Project 2: Streaming Responses\n")

    # Test prompt
    prompt = "Explain why streaming is important for voice AI in 2-3 sentences."

    # First, show non-streaming (wait for full response)
    print("\n📦 TEST 1: Non-Streaming (traditional way)")
    print("=" * 60)
    _, non_stream_time = non_streaming_call(prompt)
    print(f"⏱️  Total Time: {non_stream_time:.2f} seconds")
    print("Notice: You had to wait for the ENTIRE response before seeing anything!\n")

    # Now show streaming
    print("\n⚡ TEST 2: Streaming (modern way)")
    print("=" * 60)
    _, ttft, total_time = streaming_call(prompt)

    print(f"\n⏱️  Time to First Token (TTFT): {ttft:.2f} seconds")
    print(f"⏱️  Total Time: {total_time:.2f} seconds")

    print("\n" + "="*60)
    print("🎯 KEY INSIGHT FOR VOICE AI:")
    print("="*60)
    print(f"With streaming, we can start speaking in {ttft:.2f} seconds!")
    print(f"Without streaming, we'd wait {total_time:.2f} seconds before speaking.")
    print(f"That's a {total_time - ttft:.2f} second improvement in perceived latency!")
    print("\nFor voice conversations, this makes the difference between")
    print("feeling natural vs feeling like you're talking to a robot.")

    # Test with a longer prompt to make the difference more obvious
    print("\n\n" + "="*60)
    print("TEST 3: Longer response to see streaming advantage")
    print("="*60)

    long_prompt = "List 5 reasons why low latency matters in voice AI applications."
    _, ttft_long, total_long = streaming_call(long_prompt, temperature=0.7)

    print(f"\n⏱️  Time to First Token: {ttft_long:.2f} seconds")
    print(f"⏱️  Total Time: {total_long:.2f} seconds")
    print(f"⚡ Latency Improvement: {total_long - ttft_long:.2f} seconds saved!")

    print("\n✅ Project 2 Complete!")
    print("\nYou now understand:")
    print("- How streaming works (tokens arrive incrementally)")
    print("- Time-to-first-token (TTFT) is when voice AI can start speaking")
    print("- Streaming dramatically reduces perceived latency")


if __name__ == "__main__":
    main()
