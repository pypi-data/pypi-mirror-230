import openai

from ..data import Embedding, List, MetaData, QueryBuilder, Vector, VectorClient


class OpenAIEmbeddings(VectorClient):
    async def create_embeddings(
        self, texts: List[str], namespace: str
    ) -> List[Embedding]:
        response = openai.Embedding.acreate(  # type: ignore
            input=texts, model="text-embedding-ada-002"
        )
        vectors: List[Vector] = [response[i].embedding for i in response.data]  # type: ignore
        metadata: List[MetaData] = [
            {"text": text, "namespace": namespace} for text in texts
        ]
        return [Embedding(values=vectors[i], metadata=metadata[i]) for i in zip(vectors, metadata)]  # type: ignore

    async def upsert_embeddings(self, embeddings: List[Embedding]):
        response = await self.upsert(embeddings=embeddings)
        return response.upsertedCount

    async def similarity_search(
        self, text: str, namespace: str, top_k: int
    ) -> List[Embedding]:
        builder = QueryBuilder()
        embeddings = await self.create_embeddings(texts=[text], namespace=namespace)
        expr = (builder("namespace") == namespace).query
        response = await self.query(
            expr=expr,
            vector=embeddings[0].values,
            topK=top_k,
        )
        return [match.metadata["text"] for match in response.matches]  # type: ignore
