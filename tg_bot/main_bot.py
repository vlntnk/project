from aiogram import Bot, Dispatcher, types
import asyncio
import logging
from database.session import async_session
from database.db_models import Users
from sqlalchemy import select
from pydantic import EmailStr

TOKEN = '6900065075:AAFvC0mGYaCnuMABTNRDN3PzlCLVwHIyajU'


bot = Bot(token=TOKEN)
dispatcher = Dispatcher()


async def get_user(email: EmailStr):
    async with async_session() as session:
        try:
            user = await session.execute(select(Users).where(Users.email == email))
            user = user.scalars().first()
            await session.flush()
        except Exception as e:
            return None
        else:
            print(user)
            return user


@dispatcher.message()
async def echo(message: types.Message):
    user = await get_user(email=message.text)
    if user is None:
        await bot.send_message(
                chat_id=message.chat.id,
                text='no such user')
    else:
        await bot.send_message(
                chat_id=message.chat.id,
                text='you will receive notifications about sales nearby')


async def main():
    logging.basicConfig(level=logging.INFO)
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())






    # while True:
    # if int(minute := datetime.datetime.now().minute) % 2 == 0:
    #     await bot.send_message(
    #         chat_id=message.chat.id,
    #         text=f'it is {datetime.datetime.now()} now'
    #     )
    # print(minute)
    # await message.answer(text=message.text)