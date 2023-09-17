import asyncio
import os
from typing import AsyncGenerator, List

from aiofauna import handle_errors, process_time, setup_logging  # type: ignore
from aiohttp import ClientSession, TCPConnector
from bs4 import BeautifulSoup  # pylint: disable=import-error

from ..bot.embeddings import Embedding, OpenAIEmbeddings

logger = setup_logging(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}
BAD_EXT = (
    "png",
    "jpg",
    "jpeg",
    "gif",
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "xls",
    "xlsx",
    "zip",
    "rar",
    "gz",
    "7z",
    "exe",
    "mp3",
    "mp4",
    "avi",
    "mkv",
    "mov",
    "wmv",
    "flv",
    "swf",
)

connector = TCPConnector(limit=1000)

logger = setup_logging(__name__)
embeddings = OpenAIEmbeddings(
    api_endpoint=os.environ.get("PINECONE_API_URL"), api_key=os.environ.get("PINECONE_API_KEY")  # type: ignore
)


@process_time
@handle_errors
async def sitemap(url: str, session: ClientSession) -> List[str]:
    urls: List[str] = []
    if not url.endswith("xml"):
        url = f"{url.rstrip('/')}/sitemap.xml"
    async with session.get(url) as response:
        text = await response.text()
        soup = BeautifulSoup(text, features="xml")
        for loc in soup.findAll("loc"):
            if loc.text.endswith(BAD_EXT):
                continue
            urls.append(loc.text)
            logger.info("Found url: %s", loc.text)
        for nested_sitemap in soup.findAll("sitemap"):
            urls.extend(await sitemap(nested_sitemap.loc.text, session))
    return urls


@process_time
@handle_errors
async def fetch_website(url: str, session: ClientSession, max_size: int = 40960) -> str:
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, features="lxml")
        tag = soup.find("div", class_="content")
        assert tag is not None
        data = tag.get_text(strip=True)
        logger.info("Fetched %s", url)
        logger.info("Length: %s", len(data))
        return data[:max_size]


async def sitemap_pipeline(
    url: str,
    namespace: str,
    session: ClientSession,
    chunk_size: int = 64,
):
    urls: List[str] = await sitemap(url, session)
    length: int = len(urls)
    inserted: int = 0
    while urls:
        try:
            chunk = urls[:chunk_size]
            urls = urls[chunk_size:]
            contents = await asyncio.gather(
                *[fetch_website(url, session) for url in chunk]
            )
            inserted += await embeddings.upsert_embeddings(
                [
                    Embedding(
                        values=content, metadata={"namespace": namespace, "text": text}
                    )
                    for content, text in zip(contents, chunk)
                ]
            )
            progress = inserted / length
            logger.info("Progress: %s", progress)
            yield progress
            if progress >= 1:
                yield 1
                logger.info(f"Succesfully inserted {inserted} documents")
                break
        except Exception as e:
            logger.error(e)
            continue


@process_time
@handle_errors
async def find_all_children(url: str, session: ClientSession) -> List[str]:
    async with session.get(url + "/index.html") as response:
        html: str = await response.text()
        soup = BeautifulSoup(html, features="lxml")
        results = soup.find_all("a", href=True)
        logger.info("Found %s results", len(results))
        responses: List[str] = []
        for result in results:
            if result["href"].startswith("http"):
                responses.append(result["href"])
            else:
                responses.append(f"{url.rstrip('/')}/{result['href'].lstrip('/')}")
        return responses


@process_time
@handle_errors
async def fetch_all_children_recursive(url: str, session: ClientSession) -> List[str]:
    urls = await find_all_children(url, session)
    for url in urls:
        urls.extend(await fetch_all_children_recursive(url, session))
    return urls


async def fetch_pipeline(
    url: str,
    namespace: str,
    session: ClientSession,
    chunk_size: int = 64,
):
    urls = await find_all_children(url, session)
    logger.info("Found %s urls", len(urls))
    logger.info("Fetching all children")
    length = len(urls)
    inserted = 0
    while urls:
        chunk = urls[:chunk_size]
        urls = urls[chunk_size:]
        try:
            contents = await asyncio.gather(
                *[fetch_website(url, session) for url in chunk]
            )
            inserted += await embeddings.upsert_embeddings(
                [
                    Embedding(
                        values=content, metadata={"namespace": namespace, "text": text}
                    )
                    for content, text in zip(contents, chunk)
                ]
            )
            progress = inserted / length
            logger.info("Progress: %s", progress)
            yield progress
            if progress >= 1:
                logger.info(f"Succesfully inserted {inserted} documents")
                break
        except Exception as e:
            logger.error(e)
            continue


async def website_loader(url: str, namespace: str) -> AsyncGenerator[float, None]:
    """Reads a website and returns a list of strings"""
    async with ClientSession(connector=connector, headers=HEADERS) as session:
        exts = ["sitemap.xml", "index.html", ""]
        for e in exts:
            response = await session.get(url + "/" + e)
            if response.status == 200:
                if e == "sitemap.xml":
                    async for progress in sitemap_pipeline(url, namespace, session):
                        yield progress
                else:
                    async for progress in fetch_pipeline(url, namespace, session):
                        yield progress
                break
        else:
            logger.error("Could not find a sitemap.xml or index.html file")
            raise Exception("Could not find a sitemap.xml or index.html file")
