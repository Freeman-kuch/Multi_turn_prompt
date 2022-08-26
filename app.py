import sys
import traceback
from datetime import datetime
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    TurnContext,
    MemoryStorage
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig, cosDB_config
from dialogs import UserProfileDialog
from bot import DialogBot
from botbuilder.azure import CosmosDbPartitionedStorage, CosmosDbPartitionedConfig

CONFIG = DefaultConfig()

SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error]: {error}", file=sys.stderr)
    traceback.print_exc()

    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )

        await context.send_activity(trace_activity)

    await CONVERSATION_STATE.delete(context)


ADAPTER.on_turn_error = on_error

MEMORY = MemoryStorage()  # this is a form of state management remodel it to cosmos db
COSDB = CosmosDbPartitionedConfig(cosDB_config.uri, cosDB_config.key, "multi_turn_prompt", "user_data")
cosdb_storage = CosmosDbPartitionedStorage(COSDB)
CONVERSATION_STATE = ConversationState(MEMORY)

DIALOG = UserProfileDialog(cosdb_storage)
BOT = DialogBot(CONVERSATION_STATE, cosdb_storage, DIALOG)  # when using a DB the user state will be from the DB


async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=HTTPStatus.OK)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
