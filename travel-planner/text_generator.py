import os
import time
import requests
import openai
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from config import (
    OPENAI_API_KEY,
    GROQ_API_KEY,
    LLM_PROVIDER,
    HUGGINGFACE_LLAMA_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    OPENAI_4O_MINI_MODEL
)

GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

class TextGenerator:
    def __init__(self):
        """
        LLM_PROVIDER can be one of:
         - "openai-3.5"     => GPT-3.5-turbo
         - "openai-4"       => GPT-4
         - "openai-4o-mini" => GPT-4o-mini
         - "huggingface"    => local HF model
         - "groq"           => Groq LLM
        """
        self.provider = LLM_PROVIDER.lower()

        if self.provider == "openai-3.5":
            openai.api_key = OPENAI_API_KEY
            self.openai_model_name = "gpt-3.5-turbo"
            print("[TextGenerator] Using OpenAI GPT-3.5")

        elif self.provider == "openai-4":
            openai.api_key = OPENAI_API_KEY
            self.openai_model_name = "gpt-4"
            print("[TextGenerator] Using OpenAI GPT-4")

        elif self.provider == "openai-4o-mini":
            openai.api_key = OPENAI_API_KEY
            self.openai_model_name = OPENAI_4O_MINI_MODEL
            print("[TextGenerator] Using OpenAI GPT-4o-mini")

        elif self.provider == "huggingface":
            print(f"[TextGenerator] Loading local HuggingFace model: {HUGGINGFACE_LLAMA_MODEL} ...")
            self.tokenizer = AutoTokenizer.from_pretrained(HUGGINGFACE_LLAMA_MODEL)
            self.model = AutoModelForCausalLM.from_pretrained(
                HUGGINGFACE_LLAMA_MODEL,
                device_map="auto",
                torch_dtype=torch.float16
            )
            self.generation_config = GenerationConfig(
                max_new_tokens=512,
                temperature=TEMPERATURE
            )
            print("[TextGenerator] Model loaded successfully (HF).")

        elif self.provider == "groq":
            if not GROQ_API_KEY:
                raise ValueError("No GROQ_API_KEY found in environment/config.")
            self.groq_model = GROQ_DEFAULT_MODEL
            print(f"[TextGenerator] Using Groq model: {self.groq_model}")

        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")

    def generate_chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        # Text based on provider
        if self.provider in ("openai-3.5", "openai-4", "openai-4o-mini"):
            return self._generate_openai(system_prompt, user_prompt)
        elif self.provider == "huggingface":
            return self._generate_huggingface(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._generate_groq(system_prompt, user_prompt)
        else:
            return "Error: Provider not implemented!"

    def _generate_openai(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        try:
            response = openai.chat.completions.create(
                model=self.openai_model_name,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[OpenAI Error] {str(e)}")
            return "Error: unable to get response from OpenAI."

    def _generate_huggingface(self, system_prompt: str, user_prompt: str) -> str:
        combined_prompt = f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"
        inputs = self.tokenizer(combined_prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.generation_config.max_new_tokens,
                temperature=self.generation_config.temperature
            )

        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "Assistant:" in text:
            text = text.split("Assistant:")[-1]
        return text.strip()

    def _generate_groq(self, system_prompt: str, user_prompt: str) -> str:
        url = GROQ_ENDPOINT
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        payload = {
            "model": self.groq_model,
            "messages": messages,
            "max_completion_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE
        }

        max_retries = 5
        backoff_seconds = 2.0

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=90)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()

            except requests.exceptions.HTTPError as http_err:
                # If 429 rate limit, try again
                if response.status_code == 429 and attempt < max_retries - 1:
                    print(f"[Groq Rate Limit] Attempt {attempt+1}/{max_retries} - waiting {backoff_seconds:.1f}s")
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                    continue
                else:
                    print(f"[Groq HTTP Error] {http_err}")
                    print(f"Response content: {response.text}")
                    return "Error: unable to get response from Groq."
            except Exception as e:
                print(f"[Groq Error] {str(e)}")
                return "Error: unexpected issue in Groq request."

        return "Error: max retries exceeded for Groq"
