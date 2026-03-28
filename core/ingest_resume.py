import os
import PyPDF2
from core.llm_client import get_openai_client, get_config, build_chat_kwargs
from core.profile_manager import save_profile

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def bootstrap_master_profile(pdf_path: str):
    """Extracts text from an old PDF resume and uses the AI to structure it into the master JSON."""
    text = extract_text_from_pdf(pdf_path)
    
    prompt_path = os.path.join("prompts", "profile_bootstrap.txt")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    client = get_openai_client()
    config = get_config()
    
    kwargs = build_chat_kwargs(
        config=config,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Raw PDF Text:\n\n{text}"}
        ],
        temp_key="TEMPERATURE_ANALYSIS",
        response_format={"type": "json_object"}
    )
    
    response = client.chat.completions.create(**kwargs)
    
    result_json_str = response.choices[0].message.content
    import json
    try:
        profile_data = json.loads(result_json_str)
        save_profile(profile_data)
        return True
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM output: {e}")
        return False
