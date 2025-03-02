from openai import OpenAI

def gptRequest(reviews):
    client = OpenAI(api_key="sk-hajk2txR7GVQfWLNzwuwibW3Hgjbq7qQ", base_url="https://api.proxyapi.ru/openai/v1")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "Ты анализируешь отзывы на маркетплейсах, твоя задача — кратко выделить плюсы и минусы, а затем дать итоговое мнение о продукте. "
                    "Плюсы и минусы должны быть краткими, не повторяй их несколько раз, а только один раз. "
                    "В конце добавь итоговую рекомендацию по покупке товара."},
            {"role": "user",
             "content": "\n".join(reviews)}
        ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

if __name__ == "__main__":
    gptRequest()