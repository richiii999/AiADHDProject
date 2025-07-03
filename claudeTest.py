import anthropic

key = ''
with open('./LLM/ClaudeKey.txt') as f: key = f.readline()[:-1]

client = anthropic.Anthropic(api_key=key)

message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)

print(message.content[0].text)