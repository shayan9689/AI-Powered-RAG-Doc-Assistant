class FakeEmbedder:
    model_name = "fake-embedder"
    _vocab = (
        "alpha",
        "beta",
        "cats",
        "dogs",
        "one",
        "two",
        "apple",
        "banana",
        "quantum",
        "physics",
    )

    def embed_query(self, text: str) -> list[float]:
        tokens = set(text.lower().split())
        return [1.0 if word in tokens else 0.0 for word in self._vocab] + [0.05]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


class FakeLLM:
    provider = "fake"
    model_name = "fake-llm"

    def __init__(self) -> None:
        self.called = False
        self.calls: list[tuple[str, str]] = []
        self.last_system_prompt = ""
        self.last_user_prompt = ""
        self.response = "Grounded answer from the evidence."

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.called = True
        self.calls.append((system_prompt, user_prompt))
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        if "standalone search query" in system_prompt.lower():
            follow = user_prompt.split("Follow-up:")[-1]
            follow = follow.split("Standalone")[0].strip()
            return follow
        return self.response
