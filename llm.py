from openai import OpenAI
import os
from prompt import SYSTEM_PROMPT

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def generate_brief(news_items):
    text_input = "\n".join([
        f"{n['title']}\n{n['summary']}\n{n['link']}\n"
        for n in news_items
    ])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text_input}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content
