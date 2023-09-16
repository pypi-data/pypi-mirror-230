import itertools
import logging
import uuid
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

logger = logging.getLogger(__name__)


def chunk(iterator: Iterable, size: int) -> Iterable[tuple]:
    it = iter(iterator)

    return iter(lambda: tuple(itertools.islice(it, size)), ())


def get_existed_point_ids(
    qdrant: QdrantClient,
    index: str,
    id_field: str = "id",
    limit: int = 10000,
) -> set[str | int]:
    offset = None

    ids = set()
    while True:
        records, offset = qdrant.scroll(
            collection_name=index,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        ids = ids.union(x.payload[id_field] for x in records)

        if not offset:
            break

    return ids


def batch_create_embeddings(
    docs: Iterable[dict],
    embedding_fn: Callable[[list[str]], list[list[float]]],
    format_fn: Callable[[dict], str],
    batch_size: int = 16,
    max_workers: int = 10,
) -> list[tuple[int, list[float]]]:
    def _create_embeddings(ordered_batch):
        indices, batch = zip(*ordered_batch, strict=True)
        try:
            embeddings = embedding_fn(batch, format_fn)

        except Exception:
            logger.exception("failed to embed batch")

            return False, zip(indices, batch, strict=True)

        return True, list(zip(indices, embeddings, strict=True))

    min_split_batch_size = 2

    futures = []
    ordered_embeddings = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for ordered_batch in chunk(enumerate(docs), size=batch_size):
            futures += [executor.submit(_create_embeddings, ordered_batch)]

        while futures:
            future = futures.pop(0)

            success, payload_or_result = future.result()
            if success:
                ordered_embeddings += payload_or_result
                continue

            indices, batch = zip(*payload_or_result, strict=True)
            size = len(indices)
            if size >= min_split_batch_size:
                size //= 2
                logger.info("trying to divide batch into size %d", size)
                futures += [
                    executor.submit(
                        _create_embeddings,
                        zip(indices[:size], batch[:size], strict=True),
                    ),
                ]
                futures += [
                    executor.submit(
                        _create_embeddings,
                        zip(indices[size:], batch[size:], strict=True),
                    ),
                ]
                continue

            logging.warning(
                "failed to create embedding for batch, ids: %s",
                ", ".join(f'{x["id"]}({len(x["content"])})' for x in batch),
            )

    ordered_embeddings.sort(key=lambda x: x[0])

    return ordered_embeddings


def index_vectors(
    client: QdrantClient,
    index: str,
    docs: list[dict],
    embeddings: list[list[float]],
    vector: str | None = None,
) -> None:
    def _get_vector(embedding):
        if not vector:
            return embedding

        return {
            vector: embedding,
        }

    if len(docs) != len(embeddings):
        msg = "mismatched lengths of documents and embeddings: %d != %d"
        raise ValueError(msg, len(docs), len(embeddings))

    points = [
        PointStruct(
            id=uuid.uuid4().hex,
            vector=_get_vector(embedding),
            payload=doc,
        )
        for embedding, doc in zip(embeddings, docs, strict=True)
    ]
    client.upsert(collection_name=index, wait=True, points=points)


def batch_index_vectors(  # noqa: PLR0913
    client: QdrantClient,
    index: tuple[str, str],
    docs: list[dict],
    embedding_fn: Callable[[list[str]], list[list[float]]],
    format_fn: Callable[[dict], str],
    index_chunk_size: int = 256,
    embedding_chunk_size: int = 16,
) -> None:
    index_name, vector_name = index

    for batch in chunk(docs, size=index_chunk_size):
        batch_embeddings = batch_create_embeddings(
            batch,
            embedding_fn=embedding_fn,
            format_fn=format_fn,
            batch_size=embedding_chunk_size,
        )
        if len(batch_embeddings) != len(batch):
            logger.warning(
                "%d / %d docs failed to create embeddings",
                len(batch) - len(batch_embeddings),
                len(batch),
            )

        if not batch_embeddings:
            continue

        indices, embeddings = zip(*batch_embeddings, strict=True)
        filtered_batch = [batch[i] for i in indices]

        logger.info("update %d embeddings to qdrant", len(indices))
        index_vectors(client, index_name, filtered_batch, embeddings, vector_name)
