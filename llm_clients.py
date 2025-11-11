import asyncio
import httpx


async def call_ollama(prompt, url, model="llama3", max_tokens=512):
    if not url:
        url = "http://localhost:11434"
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response") or data.get("output") or str(data)
            return {"text": text.strip(), "usage": {}}
    except Exception as e:
        return {"text": f"[ollama error] {str(e)}", "usage": {}}


async def call_hf(prompt, api_key, model="mistralai/Mistral-7B-Instruct-v0.3", max_tokens=512):
    if not api_key:
        return {"text": "[huggingface] missing API key", "usage": {}}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) and "generated_text" in result[0]:
                text = result[0]["generated_text"]
            else:
                text = str(result)
            return {"text": text.strip(), "usage": {}}
    except Exception as e:
        return {"text": f"[huggingface error] {str(e)}", "usage": {}}


async def call_mistral(prompt, api_key, model="mistral-tiny", max_tokens=512):
    if not api_key:
        return {"text": "[mistral] missing API key", "usage": {}}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            return {"text": text.strip(), "usage": data.get("usage", {})}
    except Exception as e:
        return {"text": f"[mistral error] {str(e)}", "usage": {}}



async def call_openai(prompt, api_key, max_tokens=512):
    await asyncio.sleep(0.01)
    return {"text": "[openai simulated reply]", "usage": {}}

async def call_gemini(prompt, api_key, max_tokens=512):
    await asyncio.sleep(0.01)
    return {"text": "[gemini simulated reply]", "usage": {}}

async def call_claude(prompt, api_key, max_tokens=512):
    await asyncio.sleep(0.01)
    return {"text": "[claude simulated reply]", "usage": {}}
