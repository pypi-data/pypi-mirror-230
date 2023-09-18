from typing import Optional


def make_prompt(
    instruction: str, 
    text: str,
    history: list[tuple[str, str]] = [],
    response: Optional[str] = None,
):
    prompt = f'<s>[INST] <<SYS>>\n{instruction}\n<</SYS>>\n\n'

    for user_message, reply_message in history:
        prompt += f'{user_message.strip()} [/INST] {reply_message.strip()} </s><s>[INST] '

    prompt += f'{text.strip()} [/INST]'
    if response is not None:
        prompt += f' {response.strip()}'
    return prompt

