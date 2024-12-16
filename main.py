import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command

API_TOKEN = "8146850036:AAFsrvfEb-prk-W7TSy6t-jFPAfvbcgnKG4"

REQUIRED_CHANNELS = ["@Bosqichma_Bosqich_Rivojlanish", "@TOSHVIL_SPORT"]
admins = [1974800905]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

electors = [
    "Rovshan Gafurov",
    "Doniyor Rixsibayev",
    "Davron Xalikov",
    "Botirali Matkarimov",
    "Shuhrat Rahmatov",
    "O‘tkirbek Abdullayev",
    "Bekjon Yusupov",
    "Elyorjon Umaraliyev",
    "Ozod Xasanov",
    "Suxrob Sultanov",
    "Azizxon Kamolxonov",
    "Abulfazl Xafizov",
    "Oybek Toshpo‘latov",
    "Sherzod Sharopov",
    "Luiza Turabekova",
    "Shamsiddin Muratov",
    "Xurshid Bekmurodov",
    "Davron Abdukarimov",
    "Sanjar Shernozov",
    "Mirvoxid Mirabdullayev",
    "Boxodir Rashidov",
    "Shoxjaxon Asatillayev",
    "Murodjon Akbarov",
    "Sa’dullo Raxmatillayev",
    "Olga Xalikova",
    "Usmonjon Karimov",
    "Avzalxo‘ja Saidxo‘jayev",
    "Anvarbek Djunusov",
    "Farxod Babakalanov",
    "Sandar Djangabayev",
    "Jasur Umarov"
]


def save_user(user: types.User):
    try:
        with open("users.txt", "a+", encoding="utf-8") as file:
            file.seek(0)
            lines = file.readlines()
            user_ids = [line.split(",")[0] for line in lines]

            if str(user.id) not in user_ids:
                file.write(f"{user.id},{user.username or 'None'},{user.full_name}\n")
                return False
    except Exception as e:
        logging.error(f"Foydalanuvchini saqlashda xatolik: {e}")
    return True


def generate_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    for index, name in enumerate(electors, start=1):
        votes = get_votes_for_elector(name)
        button_text = f"{name} ({votes} ovoz)"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"vote_{index}"))
    return keyboard


def get_total_votes():
    total_votes = 0
    try:
        with open("all_votes.txt", "r", encoding="utf-8") as file:
            total_votes = len(file.readlines())
    except FileNotFoundError:
        pass
    return total_votes


def get_votes_for_elector(elector_name):
    count = 0
    try:
        file_name = f"vote_{elector_name}.txt"
        with open(file_name, "r", encoding="utf-8") as file:
            data = file.readlines()
            count = int(data[0])
    except FileNotFoundError:
        pass
    return count


async def check_subscription(user_id):
    not_subscribed_channels = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed_channels.append(channel)
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xatolik: {e}")
            not_subscribed_channels.append(channel)
    return not_subscribed_channels


async def get_channel_name(channel_id):
    try:
        chat = await bot.get_chat(channel_id)
        return chat.title
    except Exception as e:
        logging.error(f"Kanal nomini olishda xatolik: {e}")
        return None


async def generate_subscription_buttons(not_subscribed_channels):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for channel in not_subscribed_channels:
        channel_name = await get_channel_name(channel)
        if channel_name:
            button = InlineKeyboardButton(text=channel_name, url=f"t.me/{channel[1:]}")
            keyboard.add(button)
    return keyboard


@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    not_subscribed_channels = await check_subscription(user_id)
    k = save_user(message.from_user)
    if not k:
        for admin in admins:
            await bot.send_message(chat_id=admin, text=f"""
Yangi user🆕
ID: <a href='tg://user?id={message.from_user.id}'>{message.from_user.id}</a>
Username: @{message.from_user.username}
Ism-Familiya: {message.from_user.full_name}""", parse_mode='HTML')
    if not_subscribed_channels:
        keyboard = await generate_subscription_buttons(not_subscribed_channels)
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n",
            reply_markup=keyboard
        )
    else:
        if not electors:
            await message.answer("Saylanuvchilar ro'yxati bo'sh!")
            return

        with open('12.jpg', 'rb') as photo:
            await message.answer_photo(photo=photo, caption="Ovoz berish uchun quyidagi tugmalardan birini tanlang:",
                                       reply_markup=generate_keyboard())


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("vote_"))
async def process_vote(callback_query: types.CallbackQuery):
    vote = callback_query.data.split("_")[1]
    elector_name = electors[int(vote) - 1]
    file_name = f"vote_{elector_name}.txt"
    user_id = str(callback_query.from_user.id)

    has_voted = False
    try:
        with open("all_votes.txt", "r", encoding="utf-8") as file:
            data = file.readlines()
            voted_users = [line.split(",")[0] for line in data]
            if user_id in voted_users:
                has_voted = True
    except FileNotFoundError:
        pass

    if has_voted:
        await bot.answer_callback_query(
            callback_query.id,
            "Siz allaqachon ovoz bergansiz! Faqat bitta saylanuvchiga ovoz berish mumkin.",
            show_alert=True
        )
        return

    try:
        with open(file_name, "r") as file:
            data = file.readlines()
            count = int(data[0])
            voters = set(data[1:])
    except FileNotFoundError:
        count = 0
        voters = set()

    count += 1
    voters.add(user_id)

    with open(file_name, "w") as file:
        file.write(f"{count}\n")
        file.writelines(f"{voter}\n" for voter in voters)

    with open("all_votes.txt", "a+", encoding="utf-8") as file:
        file.write(f"{user_id},{elector_name}\n")

    await bot.answer_callback_query(callback_query.id, "Ovozingiz qabul qilindi!")
    await bot.edit_message_caption(
        caption=f"Ovozlar soni: {count}",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=generate_keyboard()
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
