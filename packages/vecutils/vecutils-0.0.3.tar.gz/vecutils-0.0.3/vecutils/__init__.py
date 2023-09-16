from collections.abc import Callable

import httpx


class Vectorizer:
    def __init__(self, url: str, model: str) -> None:
        self.url = url
        self.model = model

    def create_embeddings(
        self,
        docs: list[dict | str],
        format_fn: Callable[[dict], str] | None,
        timeout: int = 60,
    ) -> list[list[float]]:
        response = httpx.post(
            self.url,
            json={
                "input": list(map(format_fn, docs)) if callable(format_fn) else docs,
                "model": self.model,
            },
            timeout=timeout,
        )

        return [x["embedding"] for x in response.json()["data"]]
