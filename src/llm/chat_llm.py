import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class ChatBot:
    _model = None
    _tokenizer = None

    @classmethod
    def _load_model(cls):
        if cls._model is None:
            print(f"Loading model {cls.MODEL_ID}...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            cls._tokenizer = AutoTokenizer.from_pretrained(cls.MODEL_ID, use_auth_token=cls.HF_TOKEN)
            cls._tokenizer.pad_token = cls._tokenizer.eos_token
            cls._model = AutoModelForCausalLM.from_pretrained(
                cls.MODEL_ID,
                quantization_config=bnb_config,
                device_map="auto",
                use_auth_token=cls.HF_TOKEN
            )
            print("Model loaded successfully.")

    def __init__(self, model_id=None, hf_token=None):
        if model_id: self.MODEL_ID = model_id
        if hf_token: self.HF_TOKEN = hf_token
        self._load_model()

    def generate_response(self, prompt: str, max_new_tokens: int = 150, temperature: float = 0.7):
        """
        Генерирует ответ на основе prompt.
        Возвращает строку с текстом ответа.
        """
        if self._model is None or self._tokenizer is None:
            raise RuntimeError("Model not loaded")

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id
            )
        text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return text

if __name__ == "__main__":
    bot = ChatBot()
    prompt = "Ты медицинский ассистент. Задай уточняющий вопрос по симптомам: головная боль и слабость."
    response = bot.generate_response(prompt)
    print("Bot:", response)