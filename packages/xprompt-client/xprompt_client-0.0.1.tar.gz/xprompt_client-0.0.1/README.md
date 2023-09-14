# XPrompt client

client for XPrompt


## Example
```
import xprmopt
api_key_response = xprompt.login(user_email='..', password='..')

xprompt.api_key = api_key_response['access_token']
xprompt.openai_api_key = ""


prompt = """tell me a joke"""

r = xprompt.OpenAIChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], temperature=0)
print(r)
```
