# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# enable logging for Microsoft Agents library
# for more information, see README.md for Quickstart Agent
import logging
ms_agents_logger = logging.getLogger("microsoft_agents")
ms_agents_logger.addHandler(logging.StreamHandler())
ms_agents_logger.setLevel(logging.INFO)

import sys
import asyncio

from dotenv import load_dotenv

from microsoft_agents.activity import ActivityTypes, load_configuration_from_env

from .util.copilotstudioclient import CopilotStudioClient

logger = logging.getLogger(__name__)

load_dotenv()


def create_client():
    client = CopilotStudioClient()
    return client.client


async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda s=string: sys.stdout.write(s + " ")
    )
    return await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)


async def ask_question(copilot_client, conversation_id):
    query = (await ainput("\n>>>: ")).lower().strip()
    if query in ["exit", "quit"]:
        print("Exiting...")
        return
    if query:
        replies = copilot_client.ask_question(query, conversation_id)
        async for reply in replies:
            if reply.type == ActivityTypes.message:
                print(f"\n{reply.text}")
                if reply.suggested_actions:
                    for action in reply.suggested_actions.actions:
                        print(f" - {action.title}")
            elif reply.type == ActivityTypes.end_of_conversation:
                print("\nEnd of conversation.")
                sys.exit(0)
        await ask_question(copilot_client, conversation_id)



async def main():
    copilot_client = create_client()
    act = copilot_client.start_conversation(True)
    print("\nSuggested Actions: ")
    async for action in act:
        if action.text:
            print(action.text)
    await ask_question(copilot_client, action.conversation.id)


asyncio.run(main())
