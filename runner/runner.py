from google.adk.runners import InMemorySessionService, Runner

from agents_loop.agent import mahjong_loop_agent
from agents_seq.agent import mahjong_sequential_agent


async def create_session(
    app_name: str, user_id: str, session_id: str
) -> InMemorySessionService:
    session_service_stateful = InMemorySessionService()
    print("✅ New InMemorySessionService created for state demonstration.")

    # Define initial state data - user prefers Celsius initially
    # initial_state = {}

    # Create the session, providing the initial state
    # session_stateful = await session_service_stateful.create_session(
    #     app_name=app_name,  # Use the consistent app name
    #     user_id=user_id,
    #     session_id=session_id,
    #     state=initial_state,
    # )

    return session_service_stateful


async def get_sequential_runner(app_name: str, user_id: str, session_id: str) -> Runner:
    # Create runner for each query to avoid session conflicts
    session_service = await create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    return Runner(
        agent=mahjong_sequential_agent,
        app_name=app_name,
        session_service=session_service,
    )


async def get_loop_runner(app_name: str, user_id: str, session_id: str) -> Runner:
    session_service = await create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    return Runner(
        agent=mahjong_loop_agent, app_name=app_name, session_service=session_service
    )
