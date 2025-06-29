import asyncio
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from tools.calculation import (
    calculate_mahjong_score,
    check_hand_validity,
)

MODEL = "gemini-2.5-pro"

async def test_subagent():
    # Create a simple test agent with just the tools
    test_agent = Agent(
        model=MODEL,
        name="test_calculator_agent",
        instruction="Test the mahjong score calculator.",
        description="Test agent for debugging tool registration.",
        tools=[check_hand_validity, calculate_mahjong_score],
    )
    print(f"✅ Test Agent '{test_agent.name}' created.")
    
    # Create session
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        state={},
    )
    
    # Create runner
    runner = Runner(
        agent=test_agent,
        app_name="test_app",
        session_service=session_service,
    )
    print(f"✅ Runner created for test agent.")
    
    # Test query
    content = types.Content(role="user", parts=[types.Part(text="Test the calculate_mahjong_score function with any hand.")])
    
    print("\n>>> Testing calculate_mahjong_score function...")
    async for event in runner.run_async(
        user_id="test_user", 
        session_id="test_session", 
        new_message=content
    ):
        if event.content and event.content.parts:
            parts_text = "\n".join([part.text for part in event.content.parts if hasattr(part, 'text') and part.text])
            if parts_text:
                print(f"[{event.author}]: {parts_text}")
        
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
                print(f"<<< Final Response: {final_response_text}")
                break

if __name__ == "__main__":
    asyncio.run(test_subagent())