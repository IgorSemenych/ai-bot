from crewai import Agent, Task, Crew
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8720081257:AAGpSKdG_K19CN0HLIsWUHBebr9Od-ZrsUc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START command received")
    await update.message.reply_text("Бот запущений ✅")

def run_crewai(user_input):
    writer = Agent(
        role="Сценарист",
        goal="Створювати сильні рекламні концепти, які одразу чіпляють увагу.",
        backstory=(
            "Ти досвідчений рекламний сценарист. "
            "Ти мислиш hook'ом, емоцією, контрастом і вірусністю. "
            "Ти не любиш банальні ідеї та завжди шукаєш сильний перший удар у перші 3 секунди."
        ),
        verbose=True
    )

    director = Agent(
        role="Режисер",
        goal="Перетворювати концепт у production-ready відеосценарій.",
        backstory=(
            "Ти досвідчений режисер рекламних роликів. "
            "Ти мислиш кадрами, монтажем, ритмом, світлом, атмосферою і рухом камери. "
            "Ти переводиш абстрактну ідею в чітку структуру по секундах."
        ),
        verbose=True
    )

    producer = Agent(
        role="Креативний продюсер",
        goal="Вибрати найсильніше рішення і зробити фінальний production-ready пакет.",
        backstory=(
            "Ти креативний продюсер, який мислить результатом. "
            "Ти відсікаєш слабке, підсилюєш сильне і формуєш фінальний пакет, "
            "який можна віддати в продакшн або AI-генерацію."
        ),
        verbose=True
    )

    task_writer = Task(
        description=f"""
На основі запиту нижче придумай 3 різні рекламні концепти.

Запит:
{user_input}

Вимоги:
- кожна ідея має мати сильний hook у перші 3 секунди
- стиль мислення: сучасна реклама, динаміка, емоція, візуальна сила
- не пиши довгі пояснення
- пиши українською

Формат відповіді строго:
КОНЦЕПТ 1
Назва:
Hook:
Коротка ідея:

КОНЦЕПТ 2
Назва:
Hook:
Коротка ідея:

КОНЦЕПТ 3
Назва:
Hook:
Коротка ідея:
""",
        expected_output="""
3 окремі рекламні концепти у чіткій короткій структурі.
""",
        agent=writer
    )

    task_director = Task(
        description="""
Візьми найсильніший концепт сценариста і перетвори його у production-ready відеосценарій.

Зроби строго:
1. Назва концепту
2. Чому саме цей концепт обрано
3. Сценарій по секундах
4. Опис кадрів
5. Рух камери
6. Візуальний стиль
7. Текст на екрані / VO
8. Фінальний кадр

ВАЖЛИВО:
- це має бути дуже конкретно
- без довгої аналітики
- тільки те, що реально потрібно для створення ролика
- пиши українською
""",
        expected_output="""
Чіткий режисерський сценарій по секундах у production-ready форматі.
""",
        agent=director,
        context=[task_writer]
    )

    task_producer = Task(
        description="""
На основі сценариста і режисера підготуй фінальний production-ready пакет.

Формат відповіді строго:

1. ФІНАЛЬНО ОБРАНА ІДЕЯ
2. ЧОМУ ВОНА ПРАЦЮЄ
3. СЦЕНАРІЙ ПО СЕКУНДАХ
4. РЕЖИСЕРСЬКЕ БАЧЕННЯ
5. AI-ПРОМПТ ДЛЯ ГЕНЕРАЦІЇ ВІДЕО
6. AI-ПРОМПТ ДЛЯ KEY VISUAL / STORYBOARD
7. ПОКРОКОВИЙ ПЛАН РЕАЛІЗАЦІЇ

Вимоги:
- промпти мають бути англійською мовою
- весь інший текст українською
- результат має бути придатним для реального продакшну
- не пиши зайву теорію
""",
        expected_output="""
Фінальний production-ready пакет: ідея, сценарій, режисура, AI-промпти, план реалізації.
""",
        agent=producer,
        context=[task_writer, task_director]
    )

    crew = Crew(
        agents=[writer, director, producer],
        tasks=[task_writer, task_director, task_producer],
        verbose=True
    )

    result = crew.kickoff()
    return str(result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("MESSAGE RECEIVED:", update.message.text)
    try:
        response = run_crewai(update.message.text)
        response = str(response)

        # Telegram має ліміт на довжину повідомлення
        chunk_size = 3500
        for i in range(0, len(response), chunk_size):
            await update.message.reply_text(response[i:i + chunk_size])

    except Exception as e:
        print("CREW ERROR:", repr(e))
        await update.message.reply_text(f"Помилка AI: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("BOT STARTED 🚀")
app.run_polling()