import asyncio

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner

from agents.agents import (
    create_session,
    get_final_output_json_generator_agent,
    get_mahjong_supervisor_agent,
    run,
)


async def main():
    query = "Please create a mahjong score problem where the answer is 3 han and 50 fu."

    app_name = "mahjong_question_generator_agent"
    user_id = "user_id"
    session_id = "session_id_1"

    session_service_stateful = await create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    root_agent = SequentialAgent(
        name="mahjong_supervisor_agent",
        sub_agents=[
            get_mahjong_supervisor_agent(),
            get_final_output_json_generator_agent(),
        ],
    )
    runner_root_stateful = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service_stateful,  # Use the NEW stateful session service
    )

    result = await run(
        runner=runner_root_stateful,
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        query=query,
    )
    print("--------------query-------------------")
    print(f"query: {query}")
    print("--------------result------------------")
    print(result)
    print("--------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
