import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

TOKEN = getenv("BOT_TOKEN")

form_router = Router()


class UserAddressStatesGroup(StatesGroup):
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
        f"What do you want?",
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
    await state.set_state(UserAddressStatesGroup.add_address)
    await message.answer("Ok, Sent me your address (without city, default - SPB)", reply_markup=ReplyKeyboardRemove(),)


@form_router.message(UserAddressStatesGroup.address, F.text.casefold() == "remove address")
async def remove_address_command(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    await state.set_state(UserAddressStatesGroup.remove_address)
    await message.answer(
        f"What address do you want to remove?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=address)
                    for address in state_data.get("address", None) or []
                ]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(UserAddressStatesGroup.add_address)
async def add_address_handler(message: Message, state: FSMContext) -> None:
    new_address: str = message.text
    state_data = await state.get_data()
    addresses = state_data.get("address", None) or []
    addresses.append(new_address)
    echo_addresses = "\n - ".join(addresses)
    await state.update_data(address=addresses)
    await state.set_state(state=None)
    await message.answer(
        f"Ok, I'll remember your address, {html.bold(message.from_user.full_name)}! "
        f"\nYour Addresses:\n{echo_addresses}",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(UserAddressStatesGroup.remove_address)
async def remove_address_handler(message: Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    new_addresses: list[str] = [
        address for address in state_data.get("address", None) or [] if address != message.text
    ]
    await state.update_data(address=new_addresses)
    await state.set_state(None)
    await message.answer(f"OK. Address '{message.text}' was removed")


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
    Allow user to cancel any action
    """
    echo_addresses = await _fetch_addresses(state)
    if echo_addresses:
        msg = f"I remember your address:\n{echo_addresses}"
    else:
        msg = f"I don't remember any your address. Could you add a first one?"

    await message.answer(
        f"Hi, {html.bold(message.from_user.full_name)}!\n{msg}",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(UserAddressStatesGroup.add_address)
async def add_address(message: Message, state: FSMContext) -> None:
    new_address: str = message.text
    state_data = await state.get_data()
    addresses = state_data.get("address", None) or []
    addresses.append(new_address)
    echo_addresses = "\n - ".join(addresses)
    await state.update_data(address=addresses)
    await state.set_state(state=None)
    await message.answer(
        f"Ok, I'll remember your address, {html.bold(message.from_user.full_name)}! "
        f"\nYour Addresses:\n{echo_addresses}",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("clear"))
async def clear_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    await state.clear()
    await message.answer(
        f"Ok, I forgot all for you, {html.bold(message.from_user.full_name)}!",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("shutdowns"))
async def shutdowns_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    echo_addresses = await _fetch_addresses(state)
    await message.answer(
        f"Ok, I'll return future shutdowns for your addresses:\n{echo_addresses}",
        reply_markup=ReplyKeyboardRemove(),
    )


async def _fetch_addresses(state: FSMContext) -> str:
    data = await state.get_data()
    echo_addresses = ""
    if addresses := data.get("addresses") or []:
        echo_addresses = "\n - "
        echo_addresses += "\n - ".join(addresses)

    return echo_addresses


async def main() -> None:
    """
    Initialize Bot instance with default bot properties which will be passed to all API calls
    """
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
