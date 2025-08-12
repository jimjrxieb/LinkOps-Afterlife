import os, threading, torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

_ENGINE = os.getenv("LLM_ENGINE", "local").lower()
_MODEL = None; _TOKENIZER = None

def _device(): return "cuda" if torch.cuda.is_available() else "cpu"

def load_local_llm():
    global _MODEL, _TOKENIZER
    if _MODEL is not None: return
    model_id = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
    _TOKENIZER = AutoTokenizer.from_pretrained(model_id)
    _MODEL = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if _device()=="cuda" else torch.float32
    ).to(_device())

def generate_stream(prompt: str, max_new_tokens=256, temperature=0.7):
    if _ENGINE == "openai":
        # stream via OpenAI (small/cheap model)
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with client.chat.completions.stream(
            model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
            messages=[{"role":"user","content":prompt}],
            temperature=temperature,
            max_tokens=max_new_tokens
        ) as s:
            for event in s:
                if event.type == "content.delta":
                    yield event.delta
        return
    # local (default)
    load_local_llm()
    input_ids = _TOKENIZER(prompt, return_tensors="pt").input_ids.to(_device())
    streamer = TextIteratorStreamer(_TOKENIZER, skip_prompt=True, skip_special_tokens=True)
    kwargs = dict(input_ids=input_ids, max_new_tokens=max_new_tokens, do_sample=True,
                  temperature=temperature, top_p=0.95, streamer=streamer)
    threading.Thread(target=_MODEL.generate, kwargs=kwargs, daemon=True).start()
    for text in streamer: yield text