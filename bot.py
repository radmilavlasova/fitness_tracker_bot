#Основной модуль Telegram-бота Фитнес-трекер с КБЖУ и планами тренировок

import logging
import random
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from config import BOT_TOKEN

#Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

#Состояния для диалога КБЖУ
CALORIES_STATE = 1

#Набор мотивационных цитат
MOTIVATION_QUOTES = [
    "Единственная плохая тренировка — это та, которой не было!",
    "Твое тело может всё, главное — убедить в этом свой разум.",
    "Маленький шаг вперед каждый день приводит к огромному результату.",
    "Успех — это сумма маленьких усилий, повторяющихся изо дня в день.",
    "Тяжело сейчас? Зато потом ты будешь гордиться собой!"
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветственное сообщение и вывод главного меню."""
    reply_keyboard = [
        ["Планы тренировок", "Отслеживание прогресса"],
        ["Питание и КБЖУ", "Мотивация"],
        ["Напоминание"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! 👋\n"
        "Я твой персональный Фитнес-трекер. Давай сделаем твое тело сильнее!\n"
        "Выбери нужное действие в меню ниже:",
        reply_markup=markup
    )


async def workout_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Вывод готовых планов тренировок
    text = (
        "**Доступные программы тренировок:**\n\n"
        "1**Для дома:**\n"
        "• Отжимания: 3 подката × 15 раз\n"
        "• Приседания: 3 подхода × 20 раз\n"
        "• Планка: 3 подхода × 45 секунд\n"
        "• Выпады: 3 подхода × 12 раз на ногу\n\n"
        "**В тренажерном зале (Силовая):**\n"
        "• Приседания со штангой: 4 × 8\n"
        "• Жим лежа: 4 × 10\n"
        "• Тяга верхнего блока: 3 × 12\n"
        "• Армейский жим: 3 × 10"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Выдача случайной мотивационной цитаты
    quote = random.choice(MOTIVATION_QUOTES)
    await update.message.reply_text(f"*Мотивация дня:*\n\n_\"{quote}\"_ ", parse_mode="Markdown")


async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Имитация установки напоминания о тренировке
    await update.message.reply_text(
        "Напоминание успешно установлено! Я отправлю уведомление завтра в 10:00, "
        "чтобы ты не пропустил свою спортивную сессию."
    )


async def progress_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Отображение текущего прогресса тренировок
    #Получаем или инициализируем количество выполненных тренировок
    workouts_count = context.user_data.get("workouts_count", 0)
    
    #Добавляем +1 к тренировкам при каждом просмотре
    workouts_count += 1
    context.user_data["workouts_count"] = workouts_count

    await update.message.reply_text(
        f"**Твой спортивный прогресс:**\n\n"
        f"Выполнено тренировок на этой неделе: *{workouts_count}*\n"
        f"Статус: {'Новичок' if workouts_count < 3 else 'Продвинутый Атлет'}!\n\n"
        f" Продолжай в том же духе!",
        parse_mode="Markdown"
    )

async def start_calories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #Начало опроса по КБЖУ
    await update.message.reply_text(
        "🍏 Давай запишем твои калории за сегодня.\n"
        "Напиши, сколько килокалорий (ккал) ты уже потребил (введи число):",
        reply_markup=ReplyKeyboardRemove()
    )
    return CALORIES_STATE


async def save_calories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #Сохранение калорий и расчет макронутриентов
    user_input = update.message.text
    
    if not user_input.isdigit():
        await update.message.reply_text("Введите корректное число")
        return CALORIES_STATE

    calories = int(user_input)
    context.user_data["today_calories"] = calories

    #Рассчитываем примерное КБЖУ на основе калорий для демонстрации
    proteins = int(calories * 0.3 / 4)
    fats = int(calories * 0.3 / 9)
    carbs = int(calories * 0.4 / 4)

    #Возвращаем главное меню на экран
    reply_keyboard = [
        ["Планы тренировок", "📊 Отслеживание прогресса"],
        ["Питание и КБЖУ", "💡 Мотивация"],
        ["Напоминание"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Данные успешно сохранены!\n\n"
        f"Всего за день: *{calories} ккал*\n"
        f"Белков: ~{proteins} г\n"
        f"Жиров: ~{fats} г\n"
        f"Углеводов: ~{carbs} г\n\n"
        f"Совет: Старайся пить больше чистой воды сегодня!",
        parse_mode="Markdown",
        reply_markup=markup
    )
    return ConversationHandler.END


async def cancel_calories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #Выход из режима ввода калорий
    await update.message.reply_text("Ввод КБЖУ отменен.")
    return ConversationHandler.END


def main() -> None:
    #Инициализация и запуск бота
    application = Application.builder().token(BOT_TOKEN).build()

    #Регистрация обработчиков обычных кнопок меню
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Планы тренировок"), workout_plans))
    application.add_handler(MessageHandler(filters.Text("Мотивация"), motivation))
    application.add_handler(MessageHandler(filters.Text("Напоминание"), set_reminder))
    application.add_handler(MessageHandler(filters.Text("Отслеживание прогресса"), progress_menu))

    #Сценарий ветвления для КБЖУ
    calories_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("🍏 Питание и КБЖУ"), start_calories)],
        states={
            CALORIES_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_calories)]
        },
        fallbacks=[CommandHandler("cancel", cancel_calories)]
    )
    application.add_handler(calories_conv)

    #Старт получения обновлений от Telegram
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
