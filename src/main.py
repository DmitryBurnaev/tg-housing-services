"""
This code snippet defines a Telegram bot using the aiogram library to manage user addresses
in a conversation flow. The bot uses FSMContext to manage the state of the conversation
and provides a structured way for users to interact with address-related commands.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import markdown
import aiogram.utils.markdown as fmt
from aiogram.utils.formatting import Bold, as_list, as_marked_section, as_key_value, HashTag, Text

from src.config.app import TG_BOT_API_TOKEN, SupportedService, CITY_NAME_MAP
from src.db.storage import TGStorage
from src.providers.shutdowns import ShutDownProvider, ShutDownByServiceInfo

form_router = Router()


class UserAddressStatesGroup(StatesGroup):
    """
    Represents the states group for managing user addresses in the conversation flow.

    States:
        - address: State representing the initial address state.
        - add_address: State representing the state when the user wants to add an address.
        - remove_address: State representing the state when the user wants to remove an address.
    """

    address = State()
    add_address = State()
    remove_address = State()


@form_router.message(Command("address"))
async def command_address(message: Message, state: FSMContext) -> None:
    """
    Transition to state "set_address"
    """
    await state.set_state(UserAddressStatesGroup.address)
    await message.answer(
        "What do you want?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Add Address"),
                    KeyboardButton(text="Remove Address"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(UserAddressStatesGroup.address, F.text.casefold() == "add address")
async def add_address_command(message: Message, state: FSMContext) -> None:
    """
    Handle the 'add address' command from the user.
    Transition the user's state to 'add_address' state.

    Args:
        message (Message): The message object representing the user's input.
        state (FSMContext): The state context for the user.

    Returns:
        None
    """
    await state.set_state(UserAddressStatesGroup.add_address)
    await message.answer(
        "Ok, Sent me your address (without city, default - SPB)",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(UserAddressStatesGroup.address, F.text.casefold() == "remove address")
async def remove_address_command(message: Message, state: FSMContext) -> None:
    """
    Handle the "remove address" command from the user.
    Update the state to 'remove_address' and prompt the user to select an address to remove.
    In order to allow the user to select an address,
    the addresses are displayed as keyboard buttons.

    Args:
        message (Message): The message object representing the user's input.
        state (FSMContext): The FSMContext object to manage the state of the conversation.

    Returns:
        None
    """
    state_data = await state.get_data()
    await state.set_state(UserAddressStatesGroup.remove_address)
    await message.answer(
        "What address do you want to remove?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=address)
                    for address in state_data.get("addresses", None) or []
                ]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(UserAddressStatesGroup.add_address)
async def add_address_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the user input for adding a new address during the conversation flow.

    Parameters:
        - message (Message): The message object containing the user input.
        - state (FSMContext): The FSMContext object to manage the conversation state.

    Returns:
        None
    """
    new_address: str | None = message.text
    if new_address:
        addresses = await _get_addresses(state)
        addresses.append(new_address)
        await state.update_data(addresses=addresses)
        await state.set_state(state=None)

    echo_addresses = await _fetch_addresses(state)
    await message.answer(
        f"Ok, I'll remember your address, {markdown.bold(message.from_user.full_name)}! "
        f"{echo_addresses}",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(UserAddressStatesGroup.remove_address)
async def remove_address_handler(message: Message, state: FSMContext) -> None:
    """
    Handle the removal of an address from the user's list of addresses.
    Function removes the specified address from the user's list stored in the conversation state.
    It updates the state data accordingly and sends a confirmation message to the user.

    Parameters:
        - message (Message): The message object triggering the handler.
        - state (FSMContext): The current state of the conversation flow.

    Returns:
        None

    """
    new_addresses: list[str] = [
        address for address in await _get_addresses(state) if address != message.text
    ]
    await state.update_data({"addresses": new_addresses})

    echo_addresses = await _fetch_addresses(state)
    await message.answer(
        f"OK. Address '{message.text}' was removed!{echo_addresses}",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.set_state(state=None)
    await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())


@form_router.message(Command("info"))
async def info_handler(message: Message, state: FSMContext) -> None:
    """
    Handles showing user's current address and other common information
    Parameters:
        - message (Message): The message object.
        - state (FSMContext): The current state of the conversation.

    Returns:
        None
    """
    addresses = await _fetch_addresses(state)
    content = as_list(
        f"Hi, {markdown.bold(message.from_user.full_name)}!",
        addresses,
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs() | {"parse_mode": ParseMode.MARKDOWN})


@form_router.message(UserAddressStatesGroup.add_address)
async def add_address(message: Message, state: FSMContext) -> None:
    """
    Handles the user input to add a new address to the conversation flow.

    Parameters:
        - message (Message): The message object containing the user input.
        - state (FSMContext): The state context to manage the conversation flow.

    Returns:
        None
    """
    new_address: str = message.text
    addresses = await _get_addresses(state)
    addresses.append(new_address)
    await state.update_data(address=addresses)

    echo_addresses = await _fetch_addresses(state)
    await message.answer(
        f"Ok, I'll remember your address, {html.bold(message.from_user.full_name)}! "
        f"{echo_addresses}",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("clear"))
async def clear_handler(message: Message, state: FSMContext) -> None:
    """
    This handler clears the state of the conversation and sends a message to the user
    indicating that all data has been forgotten.

    Parameters:
        - message (Message): The message object triggering the handler
        - state (FSMContext): The current state of the conversation

    Returns:
        - None

    """
    await state.clear()
    await message.answer(
        f"Ok, I forgot all for you, {html.bold(message.from_user.full_name)}!",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("shutdowns"))
async def shutdowns_handler(message: Message, state: FSMContext) -> None:
    """
    Handle the 'shutdowns' command by fetching addresses from the current state and
    sending a response message to the user.

    Parameters:
        - message (Message): The message object triggering the command.
        - state (FSMContext): The current state of the conversation.

    Returns:
        - None
    """
    #     content = as_list(
    #         f"Hi, {markdown.bold(message.from_user.full_name)}!",
    #         _fetch_addresses(state),
    #         # as_marked_section(
    #         #     Bold("Failed:"),
    #         #     "Test 2",
    #         #     marker="⚠︎ ",
    #         # ),
    #         # as_marked_section(
    #         #     Bold("Summary:"),
    #         #     as_key_value("Total", 4),
    #         #     as_key_value("Success", 3),
    #         #     as_key_value("Failed", 1),
    #         #     marker="  ",
    #         # ),
    #         sep="\n\n",
    #     )
    addresses = await _fetch_addresses(state)
    shutdowns = await _fetch_shutdowns(state)
    content = as_list(
        "Ok, That's your information:",
        addresses,
        *shutdowns,
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs() | {"parse_mode": ParseMode.MARKDOWN})

    # print(f"Ok, That's your information:\n{echo_addresses}\n======{shutdowns}")
    # await message.answer(
    #     f"Ok, That's your information:\n{echo_addresses}\n======{shutdowns}",
    #     parse_mode=ParseMode.MARKDOWN,
    #     reply_markup=ReplyKeyboardRemove(),
    # )


async def _fetch_addresses(state: FSMContext) -> Text | str:
    """
    If addresses exist, it returns a marked section that displays the addresses,
    otherwise it returns the string "No address yet :(".

    Args:
        state: The state of the FSMContext.

    """
    if addresses := await _get_addresses(state):
        return as_marked_section("Your Addresses:", *addresses, marker="☑︎ ")

    return "No address yet :("


async def _fetch_shutdowns(state: FSMContext) -> list[Text | str]:
    if not (addresses := await _get_addresses(state)):
        return ["No address yet :("]

    shutdowns_by_service: list[ShutDownByServiceInfo] = ShutDownProvider.for_addresses(addresses)
    if not shutdowns_by_service:
        return ["No shutdowns :)"]

    result = []
    for shutdown_by_service in shutdowns_by_service:
        if not shutdown_by_service.shutdowns:
            continue

        title = f"Shutdown Info ({shutdown_by_service.service}):"
        as_key_values = []
        for shutdown_info in shutdown_by_service.shutdowns:
            as_key_values.append(as_key_value("Start", shutdown_info.start))
            as_key_values.append(as_key_value("End", shutdown_info.start))
            as_key_values.append(
                as_key_value(
                    "Address", f"{shutdown_info.raw_address} ({CITY_NAME_MAP[shutdown_info.city]})"
                )
            )

        result.append(as_marked_section(title, *as_key_values))

    return result
    #
    #
    # if shutdowns := ShutDownProvider.for_addresses(addresses):
    #
    #
    #
    # for address in addresses:
    #     if shutdowns := ShutDownProvider.for_address(address, service=SupportedService.ELECTRICITY):
    #
    #
    #
    #
    # shutdowns_msg = "\nFuture ShutDowns:"
    # for address in addresses:
    #     shutdowns_msg += f"\n => {address} <="
    #     if shutdowns := ShutDownProvider.for_address(address, service=SupportedService.ELECTRICITY):
    #         for sh in shutdowns:
    #             shutdowns_msg += rf"\n \- {sh}"
    #     else:
    #         shutdowns_msg += f"\n  No shutdowns detected :)"
    #
    # print(shutdowns_msg)
    # return shutdowns_msg


async def _get_addresses(state: FSMContext) -> list[str]:
    data = await state.get_data()
    return data.get("addresses") or []


async def main() -> None:
    """
    Initialize Bot instance with default bot properties which will be passed to all API calls
    """
    bot = Bot(token=TG_BOT_API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher(storage=TGStorage())
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
