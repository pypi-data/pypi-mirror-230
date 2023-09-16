"""Example OctoAI service scaffold: Flan-T5-Small."""

import os

from octoai.service import Service, volume_path

"""
Flan-T5 is an instruction-finetuned version of T5, a text-to-text
transformer language model.
"""

_MODEL_NAME = "google/flan-t5-small"
_MODEL_REVISION = "2d036ee774a9cb8d7e03c9f2e78ae0a16343a9d9"


class T5Service(Service):
    """An OctoAI service extends octoai.service.Service."""

    def setup(self):
        """Download model weights to disk."""
        os.environ["HUGGINGFACE_HUB_CACHE"] = volume_path()
        from transformers import T5ForConditionalGeneration, T5Tokenizer

        self.tokenizer = T5Tokenizer.from_pretrained(
            _MODEL_NAME,
            revision=_MODEL_REVISION,
            local_files_only=True,
        )
        self.model = T5ForConditionalGeneration.from_pretrained(
            _MODEL_NAME,
            revision=_MODEL_REVISION,
            local_files_only=True,
        )

    def store_assets(self) -> None:
        """Download model assets."""
        os.environ["HUGGINGFACE_HUB_CACHE"] = volume_path()
        from transformers import T5ForConditionalGeneration, T5Tokenizer

        T5Tokenizer.from_pretrained(_MODEL_NAME, revision=_MODEL_REVISION)
        T5ForConditionalGeneration.from_pretrained(
            _MODEL_NAME,
            revision=_MODEL_REVISION,
        )

    def infer(self, prompt: str) -> str:
        """Perform inference with the model."""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs)
        response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)

        return response[0]
