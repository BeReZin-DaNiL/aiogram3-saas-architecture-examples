
from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete

from app.database.models import User, UserProfile, Gender, Goal, FoodLog
from app.services.nutrition import calculate_nutrition

router = Router()

class UserRegister(StatesGroup):
    age = State()
    gender = State()
    weight = State()
    height = State()
    activity = State()
    goal = State()

def get_main_dashboard_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Распознать еду (Фото/Текст)", callback_data="dashboard_add_food")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="dashboard_profile")],
        [InlineKeyboardButton(text="📊 Дневник питания", callback_data="dashboard_diary")],
        [InlineKeyboardButton(text="📅 План питания", callback_data="dashboard_plan")],
        [InlineKeyboardButton(text="💎 Тарифы и Премиум", callback_data="upgrade_to_pro")],
        [
            InlineKeyboardButton(text="🎁 Пригласить друга", callback_data="dashboard_referral"),
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="dashboard_help")
        ]
    ])

async def show_main_dashboard(message: types.Message, session: AsyncSession, user_id: int):
    # Fetch user and profile
    stmt = select(User).options(selectinload(User.profile)).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.profile:
        # Fallback if profile missing (should not happen in normal flow)
        await message.answer("Ошибка: Профиль не найден. Введите /start для регистрации.")
        return

    dashboard_text = (
        "🥗 Добро пожаловать в SmartEats!\n\n"
        "Я — искусственный интеллект, который следит за твоим питанием.\n"
        "Больше не нужно считать калории вручную — доверь это мне.\n\n"
        "👇 Выбери действие в меню:"
    )
    
    await message.answer(dashboard_text, reply_markup=get_main_dashboard_keyboard())

@router.message(Command("reset"))
async def cmd_reset(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    
    # 1. Delete Food Logs (Dependent on User)
    await session.execute(delete(FoodLog).where(FoodLog.user_id == user_id))
    
    # 2. Delete User Profile (Dependent on User)
    await session.execute(delete(UserProfile).where(UserProfile.user_id == user_id))
    
    # 3. Delete User (Main record)
    await session.execute(delete(User).where(User.id == user_id))
    
    await session.commit()
    await state.clear()
    
    await message.answer("♻️ Твой профиль полностью удален. Напиши /start, чтобы зарегистрироваться заново.")

@router.message(Command("help"))
@router.callback_query(F.data == "dashboard_help")
async def cmd_help(event: types.Message | types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    text = (
        "🤖 Справка по боту\n\n"
        "Я помогу тебе следить за питанием и достигать целей.\n\n"
        "🔹 Основные команды:\n"
        "/start - Главное меню\n"
        "/profile - Мой профиль и настройки\n"
        "/premium - Тарифы и подписка\n"
        "/reset - Сброс всех данных (осторожно!)\n\n"
        "📸 Как пользоваться:\n"
        "Просто отправь мне фото еды или напиши, что ты съел, и я посчитаю калории.\n\n"
        "🆘 Поддержка:\n"
        "Если возникли вопросы, пишите: @support_bot"
    )
    
    if isinstance(event, types.Message):
        await event.answer(text, parse_mode="Markdown")
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_dashboard")]
        ])
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await event.answer()

@router.callback_query(F.data == "back_to_dashboard")
async def back_to_dashboard(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.delete()
    await show_main_dashboard(callback.message, session, callback.from_user.id)

@router.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext, session: AsyncSession):
    # Check if user already exists
    result = await session.execute(select(User).options(selectinload(User.profile)).where(User.id == message.from_user.id))
    user = result.scalar_one_or_none()
    
    if user and user.profile:
        # User registered, show dashboard
        await show_main_dashboard(message, session, message.from_user.id)
        return

    # If new user or incomplete profile, start registration
    if not user:
        referrer_id = None
        args = command.args
        if args and args.isdigit():
            ref_candidate = int(args)
            if ref_candidate != message.from_user.id:
                 # Check if referrer exists in DB
                 ref_check = await session.execute(select(User).where(User.id == ref_candidate))
                 if ref_check.scalar_one_or_none():
                     referrer_id = ref_candidate

        new_user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referrer_id=referrer_id
        )
        session.add(new_user)
        await session.commit()

        if referrer_id:
            try:
                await message.bot.send_message(
                    chat_id=referrer_id,
                    text="🎉 По вашей ссылке зарегистрировался новый пользователь! Вы получите бонус, когда он оплатит подписку."
                )
            except Exception:
                pass # Referrer might have blocked bot or other error
    
    await message.answer(
        "Привет! Я твой AI-нутрициолог 🍎.\nДавай рассчитаем твою идеальную норму калорий! 🚀\n\nДля начала, сколько тебе лет? (Напиши просто число, например: 25)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(UserRegister.age)

@router.message(UserRegister.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Хм, кажется, это не число 🧐. Пожалуйста, напиши возраст цифрами!")
        return
    
    age = int(message.text)
    if age < 10 or age > 100:
         await message.answer("Ого! 😯 Давай будем реалистами. Введи возраст от 10 до 100 лет.")
         return

    await state.update_data(age=age)
    
    gender_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male")],
        [InlineKeyboardButton(text="👩 Женский", callback_data="gender_female")]
    ])
    
    await message.answer("Отлично! 🔥\nТеперь укажи свой пол 🚻:", reply_markup=gender_kb)
    await state.set_state(UserRegister.gender)

@router.callback_query(UserRegister.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender_map = {
        "gender_male": Gender.MALE,
        "gender_female": Gender.FEMALE
    }
    
    gender_key = callback.data
    if gender_key not in gender_map:
        await callback.answer("Ошибка выбора пола", show_alert=True)
        return

    # Clean up chat history
    if callback.message:
        await callback.message.delete()
    await callback.answer()

    await state.update_data(gender=gender_map[gender_key])
    await callback.message.answer("Супер! 😉\nТеперь напиши свой вес в кг (например, 70.5) ⚖️:")
    await state.set_state(UserRegister.weight)

@router.message(UserRegister.weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight_text = message.text.replace(',', '.')
        weight = float(weight_text)
        if weight <= 0 or weight > 300:
             raise ValueError
    except ValueError:
        await message.answer("Что-то не так с форматом 🤔. Напиши вес числом, например: 70 или 70.5")
        return

    await state.update_data(weight=weight)
    await message.answer("Принято! 👌\nКакой у тебя рост в см? (например, 175) 📏:")
    await state.set_state(UserRegister.height)

@router.message(UserRegister.height)
async def process_height(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Это не похоже на рост 🧐. Напиши числом в сантиметрах!")
        return
    
    height = int(message.text)
    if height < 50 or height > 300:
        await message.answer("Кажется, тут ошибка 😯. Введи реальный рост в см (от 50 до 300).")
        return

    await state.update_data(height=height)
    
    activity_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛋 Сидячий", callback_data="activity_1.2")],
        [InlineKeyboardButton(text="🚶 Малая активность", callback_data="activity_1.375")],
        [InlineKeyboardButton(text="🏃 Средняя", callback_data="activity_1.55")],
        [InlineKeyboardButton(text="🏋️ Высокая", callback_data="activity_1.725")]
    ])
    
    await message.answer("Почти готово! 🔥\nКакая у тебя активность в течение дня? 🏃‍♂️", reply_markup=activity_kb)
    await state.set_state(UserRegister.activity)

@router.callback_query(UserRegister.activity, F.data.startswith("activity_"))
async def process_activity(callback: CallbackQuery, state: FSMContext):
    try:
        activity_value = float(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("Ошибка выбора активности", show_alert=True)
        return

    # Clean up chat history
    if callback.message:
        await callback.message.delete()
    await callback.answer()

    await state.update_data(activity=activity_value)
    
    goal_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📉 Похудеть", callback_data="goal_lose")],
        [InlineKeyboardButton(text="⚖️ Удержать вес", callback_data="goal_maintain")],
        [InlineKeyboardButton(text="📈 Набрать массу", callback_data="goal_gain")]
    ])
    
    await callback.message.answer("И последний шаг! 🎯\nКакая у тебя цель? Чего хочешь достичь? 🏆", reply_markup=goal_kb)
    await state.set_state(UserRegister.goal)

@router.callback_query(UserRegister.goal, F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    goal_map = {
        "goal_lose": Goal.LOSE,
        "goal_maintain": Goal.MAINTAIN,
        "goal_gain": Goal.GAIN
    }
    
    goal_key = callback.data
    if goal_key not in goal_map:
        await callback.answer("Ошибка выбора цели", show_alert=True)
        return
    
    # Clean up chat history
    if callback.message:
        await callback.message.delete()
    await callback.answer()
    
    goal = goal_map[goal_key]
    await state.update_data(goal=goal)
    
    data = await state.get_data()
    
    # Calculate BMR (Mifflin-St Jeor)
    # Men: 10W + 6.25H - 5A + 5
    # Women: 10W + 6.25H - 5A - 161
    weight = data['weight']
    height = data['height']
    age = data['age']
    gender = data['gender']
    activity = data['activity']
    
    # Calculate nutrition
    nutrition = calculate_nutrition(
        weight=weight,
        height=height,
        age=age,
        gender=gender,
        activity=activity,
        goal=goal
    )
    
    daily_calories = nutrition['daily_calories']
    proteins = nutrition['proteins']
    fats = nutrition['fats']
    carbs = nutrition['carbs']

    # Check if profile already exists to update or create new
    user_id = callback.from_user.id
    result_profile = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    existing_profile = result_profile.scalar_one_or_none()
    
    if existing_profile:
        existing_profile.age = age
        existing_profile.gender = gender
        existing_profile.weight = weight
        existing_profile.height = height
        existing_profile.activity_level = activity
        existing_profile.goal = goal
        existing_profile.daily_calories = daily_calories
        # We don't overwrite allergies here as it's not part of the flow yet
    else:
        new_profile = UserProfile(
            user_id=user_id,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            activity_level=activity,
            goal=goal,
            daily_calories=daily_calories
        )
        session.add(new_profile)
    
    await session.commit()
    
    # Translate goal text
    goal_text_map = {
        Goal.LOSE: "Похудеть 📉",
        Goal.MAINTAIN: "Удержать вес ⚖️",
        Goal.GAIN: "Набрать массу 📈"
    }
    goal_text_display = goal_text_map.get(goal, "Быть в форме")

    # Show Completion Message with Macros and Strategy
    completion_text = (
        f"🎉 Расчет завершен!\n\n"
        f"Твой персональный план питания готов.\n"
        f"Чтобы достичь цели {goal_text_display}, придерживайся этих цифр:\n\n"
        f"🔥 Твоя норма: {daily_calories} ккал\n\n"
        f"🧬 Рекомендуемые БЖУ:\n"
        f"🥩 Белки: {proteins} г\n"
        f"🥑 Жиры: {fats} г\n"
        f"🍞 Углеводы: {carbs} г\n\n"
        f"🚀 Что делаем дальше?\n"
        f"Не жди понедельника! Пришли мне фото еды или напиши текстом, что ты съел. Я сразу это посчитаю!"
    )

    await callback.message.answer(completion_text, reply_markup=get_main_dashboard_keyboard())
    await state.clear()

# --- Dashboard Handlers ---

@router.callback_query(F.data == "dashboard_add_food")
async def dashboard_add_food(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Жду твое фото или текст! 📸")
    await callback.answer()

@router.callback_query(F.data == "dashboard_profile")
async def dashboard_profile(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    # Import here to avoid circular dependency if any
    from app.handlers.profile import send_profile_info
    await callback.message.delete()
    await send_profile_info(callback.message, session, callback.from_user.id)



# @router.callback_query(F.data == "dashboard_premium") -> Now handled by profile.py (upgrade_to_pro)

@router.message(Command("ref"))
async def cmd_ref(message: types.Message):
    bot_user = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_user.username}?start={message.from_user.id}"
    
    text = (
        f"🎁 **Приглашай друзей и получай рубли!**\n\n"
        f"Твоя персональная ссылка:\n`{ref_link}`\n"
        f"(Нажми, чтобы скопировать)\n\n"
        f"Ты получишь **10%** от всех их оплат на бонусный счет. Ими можно оплатить свою подписку!"
    )
    await message.answer(text, parse_mode="Markdown")

@router.callback_query(F.data == "dashboard_referral")
async def dashboard_referral(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    bot_user = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_user.username}?start={callback.from_user.id}"
    
    text = (
        f"🎁 **Приглашай друзей и получай рубли!**\n\n"
        f"Твоя персональная ссылка:\n`{ref_link}`\n"
        f"(Нажми, чтобы скопировать)\n\n"
        f"Ты получишь **10%** от всех их оплат на бонусный счет. Ими можно оплатить свою подписку!"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "dashboard_help")
async def dashboard_help(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_help_message(callback.message)
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    await send_help_message(message)

async def send_help_message(message: types.Message):
    await message.answer(
        "ℹ️ **Помощь**\n\n"
        "1. **Анализ еды**: Отправь фото или текст.\n"
        "2. **Профиль**: Настрой свои данные и цели.\n"
        "3. **Дневник**: Следи за калориями и БЖУ.\n\n"
        "Если есть вопросы, пиши в поддержку: @Danil_Berezin",
        parse_mode="Markdown"
    )
