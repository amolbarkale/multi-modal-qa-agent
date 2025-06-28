# Local LLaVA backend (no HF Inference API)
# -----------------------------------------
# Runs llava-hf/llava-1.5-7b-hf locally using transformers.
# Loads the model the first time the server starts and
# answers multimodal questions coming from the existing frontend.
#
# ENV VARS (optional)
#   HF_LAVA_MODEL   – any compatible LLaVA checkpoint (default: llava-hf/llava-1.5-7b-hf)
#   LAVA_MAX_TOKENS – max_new_tokens for generation (default: 128)
# -------------------------------------------------------------

import os
import io
import base64
import logging
import requests
from typing import List, Dict

from PIL import Image
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

import torch
from transformers import (
    AutoProcessor,
    LlavaForConditionalGeneration,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llava_local_backend")

HF_MODEL = os.getenv("HF_LAVA_MODEL", "llava-hf/llava-1.5-7b-hf")
MAX_TOKENS = int(os.getenv("LAVA_MAX_TOKENS", "128"))

logger.info("Loading LLaVA model %s (this can take a few minutes the first time)…", HF_MODEL)

# Choose device map and quantization strategy based on available hardware
device_map = "auto" if torch.cuda.is_available() else {"": "cpu"}

load_kwargs = {
    "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
    "device_map": device_map,
}

try:
    if torch.cuda.is_available():
        # Use 8-bit quantization only when a CUDA device is present (requires bitsandbytes)
        model = LlavaForConditionalGeneration.from_pretrained(
            HF_MODEL,
            **load_kwargs,
            load_in_8bit=True,
        )
    else:
        # CPU / other backends – load the full-precision model to avoid bitsandbytes dependency
        model = LlavaForConditionalGeneration.from_pretrained(
            HF_MODEL,
            **load_kwargs,
        )
except TypeError:
    # Fallback for older transformers versions that do not accept load_in_8bit
    model = LlavaForConditionalGeneration.from_pretrained(
        HF_MODEL,
        **load_kwargs,
    )

processor = AutoProcessor.from_pretrained(HF_MODEL)
logger.info("Model loaded and ready on %s", model.device)

app = Flask(__name__)
CORS(app)


# ---------- helper functions --------------------------------------------------

def pil_from_bytes(b: bytes) -> Image.Image:
    return Image.open(io.BytesIO(b)).convert("RGB")


def build_conversation(image: Image.Image, question: str) -> List[Dict]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": question},
            ],
        }
    ]


# ---------- routes ------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "model": HF_MODEL,
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    question = data.get("question", "What is in this image?")
    image_url = data.get("image_url")
    image_data = data.get("image_data")  # base64 string

    if not image_url and not image_data:
        return jsonify({"error": "Provide image_url or image_data"}), 400

    try:
        if image_data:
            # strip prefix if present
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]
            image_bytes = base64.b64decode(image_data)
        else:
            resp = requests.get(image_url, timeout=20)
            resp.raise_for_status()
            image_bytes = resp.content
        img = pil_from_bytes(image_bytes)
    except Exception as e:
        logger.exception("Failed to load image: %s", e)
        return jsonify({"error": "Could not load image."}), 400

    try:
        # build conversation prompt
        conv = build_conversation(img, question)
        prompt_inputs = processor.apply_chat_template(
            conv,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device, model.dtype)

        proc_inputs = processor(images=img, return_tensors="pt").to(model.device, model.dtype)
        # merge dicts
        inputs = {**prompt_inputs, **proc_inputs}

        with torch.no_grad():
            gen_ids = model.generate(
                **inputs,
                max_new_tokens=MAX_TOKENS,
                do_sample=True,
                temperature=0.2,
            )
        answer = processor.batch_decode(gen_ids, skip_special_tokens=True)[0]
        # remove prompt part until "ASSISTANT:" if present
        if "ASSISTANT:" in answer:
            answer = answer.split("ASSISTANT:", 1)[1].strip()

        return jsonify({
            "success": True,
            "response": answer,
            "model_used": HF_MODEL,
            "local_inference": True,
        })
    except Exception as e:
        logger.exception("LLaVA generation failed: %s", e)
        return jsonify({"error": f"Generation failed: {e}"}), 500


if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    logger.info("Starting local LLaVA QA agent on http://localhost:5000 …")
    app.run(debug=True, host="0.0.0.0", port=5000) 