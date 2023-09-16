"""Example OctoAI service scaffold: Hello World."""
from octoai.service import Service


class HelloService(Service):
    """An OctoAI service extends octoai.service.Service."""

    def setup(self):
        """Perform intialization."""
        print("Setting up.")

    def infer(self, prompt: str) -> str:
        """Perform inference."""
        return prompt
