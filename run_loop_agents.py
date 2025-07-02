import asyncio

from google.adk.agents import LoopAgent
from google.adk.runners import Runner

from agents.agent import (
    CheckStatusAndEscalate,
    create_session,
    get_final_output_json_generator_agent,
    get_mahjong_supervisor_agent,
    run,
)


async def main():
    query = "Please create a mahjong score problem where the answer is 2 han and 60 fu."

    app_name = "mahjong_question_generator_agent"
    user_id = "user_id"
    session_id = "session_id_1"

    session_service_stateful = await create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    root_agent = LoopAgent(
        name="mahjong_supervisor_agent",
        max_iterations=5,
        sub_agents=[
            get_mahjong_supervisor_agent(),
            get_final_output_json_generator_agent(),
            CheckStatusAndEscalate(name="StopChecker", expected_han=3, expected_fu=50),
        ],
    )
    runner_root_stateful = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service_stateful,
    )

    result = await run(
        runner=runner_root_stateful,
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
