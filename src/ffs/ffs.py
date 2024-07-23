import requests
import uuid
import itertools
import json
import sys
import distro
from .pow import get_config, get_answer_token, get_requirements_token
from .turnstile import process_turnstile

def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

    cookies = {
        '__Host-next-auth.csrf-token': 'a06d73c86a4cf02ed908290aaa47a72ffdb913759b744b6c0717df67f9ff9444%7Cb7f82de68d69728c529ee7d4744b16845da19e595db7ea842cb880623682d2af',
        '__Secure-next-auth.callback-url': 'https%3A%2F%2Fonramp.unified-8.api.openai.com',
        'oai-did': 'ad56e64f-32ef-4ee7-99b5-db8878487808',
        '_cfuvid': '.ee7jffZMkMOWsNe1AIbhY9uZl_4dg2AE4jrqKceFKg-1719805430643-0.0.1.1-604800000',
        'cf_clearance': 'zy77998K7lTjcxkKeW6YtEcHvqIMtoR78e8IuHe6eNw-1719805431-1.0.1.1-pPEDuP3RJhWhtYzCVnNc932YkI2uV6mxBi_AH_nuGRzHNfK2qUb7fsM8wlkMrqO7.5KNUo1DGXEOMlFqnz.E3w',
        '__cf_bm': 'UiYzLIzenGvXx5.5TExiG_sZRv_ifBN.xi0YR9SErkk-1719822731-1.0.1.1-.IeyxqRayo7hcIOnOh0WYJ2joY4M2B8sAaqnsX5CyteNWKXLB1RFs6bBpaQQdPC6C5YPcmYU4qpGTpLk.7NkkA',
        '__cflb': '0H28vzvP5FJafnkHxisu1nLHt2UxLuYScHq1WwGRq3j',
        '_dd_s': 'rum=0&expire=1719824174047',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.8',
        'content-type': 'application/json',
        'oai-device-id': f'{uuid.uuid4()}',
        'oai-language': 'en-US',
        'origin': 'https://chatgpt.com',
        'priority': 'u=1, i',
        'referer': 'https://chatgpt.com/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': user_agent,
    }

    config = get_config(user_agent)
    pow_req = get_requirements_token(config)
    r = requests.post(
        'https://chatgpt.com/backend-anon/sentinel/chat-requirements',
        cookies=cookies,
        headers=headers,
        json={'p': pow_req},
    )

    resp = r.json()
    turnstile = resp.get('turnstile', {})
    turnstile_required = turnstile.get('required')
    pow_conf = resp.get("proofofwork", {})

    if turnstile_required:
        turnstile_dx = turnstile.get("dx")
        turnstile_token = process_turnstile(turnstile_dx, pow_req)

    headers['openai-sentinel-chat-requirements-token'] = resp.get('token')
    headers['openai-sentinel-proof-token'] = get_answer_token(pow_conf.get("seed"), pow_conf.get("difficulty"), config)
    headers['openai-sentinel-turnstile-token'] = turnstile_token

    arg = ' '.join(sys.argv[1:])
    prompt = f"Answer with only the actual command without any intro or explanation. Parse the command for errors, typos, wrongness, etc., and return the rectified version in plain text: {arg}"

    json_data = {
        'action': 'next',
        'messages': [
            {
                'id': str(uuid.uuid4()),
                'author': {
                    'role': 'user',
                },
                'content': {
                    'content_type': 'text',
                    'parts': [prompt],
                },
                'metadata': {},
            },
        ],
        'parent_message_id': str(uuid.uuid4()),
        'model': 'text-davinci-002-render-sha',
        'timezone_offset_min': -330,
        'suggestions': [],
        'history_and_training_disabled': False,
        'conversation_mode': {
            'kind': 'primary_assistant',
        },
        'force_paragen': False,
        'force_paragen_model_slug': '',
        'force_nulligen': False,
        'force_rate_limit': False,
        'reset_rate_limits': False,
        'websocket_request_id': str(uuid.uuid4()),
        'force_use_sse': True,
        'conversation_origin': None,
    }

    response = requests.post('https://chatgpt.com/backend-anon/conversation', headers=headers, cookies=cookies, json=json_data)
    response_text = response.text.splitlines()
    
    for first, second in itertools.pairwise(line for line in response_text if line.strip()):
        if "[DONE]" in second:
            result = json.loads(first.partition(":")[2])['message']['content']['parts'][0]
            # Remove any markdown or code block formatting
            cleaned_result = result.strip().strip('`').replace('```bash', '').replace('```', '').strip()
            print(cleaned_result)
            break

if __name__ == '__main__':
    main()
