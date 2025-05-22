from openai import OpenAI
import json

async def gptRequest(reviews, item_title):
    if not reviews or not isinstance(reviews, list):
        return "Не удалось найти отзывы для анализа."
        
    try:
        client = OpenAI(api_key="sk-hajk2txR7GVQfWLNzwuwibW3Hgjbq7qQ", base_url="https://api.proxyapi.ru/openai/v1")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Ты анализируешь отзывы на маркетплейсах, твоя задача — кратко выделить плюсы и минусы, а затем дать итоговое мнение о продукте. "
                        "Плюсы и минусы должны быть краткими, не повторяй их несколько раз, а только один раз. "
                        "В конце добавь итоговую рекомендацию по покупке товара."},
                {"role": "user",
                 "content": "\n".join(str(review) for review in reviews if review)}
            ]
        )
        analysis_result = completion.choices[0].message.content
        
        print(analysis_result)
        return analysis_result
    except Exception as e:
        print(f"Error in gptRequest: {str(e)}")
        return "Произошла ошибка при анализе отзывов. Пожалуйста, попробуйте позже."

if __name__ == "__main__":
    gptRequest()