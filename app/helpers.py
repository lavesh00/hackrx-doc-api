import time, functools, logging, io, os, fitz, docx, mailparser
from typing import Callable

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("doc-api")

def timeit(fn: Callable):
    @functools.wraps(fn)
    async def wrapper(*args, **kw):
        start = time.time()
        result = await fn(*args, **kw) if callable(getattr(args[0], "__await__", None)) else fn(*args, **kw)
        log.info("%s executed in %.2f s", fn.__name__, time.time() - start)
        return result
    return wrapper

def log_request(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kw):
        log.info("Incoming query")
        return await fn(*args, **kw)
    return wrapper

def extract_text_from_any(blob: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext.endswith(".pdf"):
        with fitz.open(stream=blob, filetype="pdf") as doc:
            return "\n".join(p.get_text() for p in doc)
    if ext.endswith(".docx"):
        f = io.BytesIO(blob)
        doc = docx.Document(f)
        return "\n".join(p.text for p in doc.paragraphs)
    if ext.endswith((".eml", ".msg")):
        mail = mailparser.parse_from_bytes(blob)
        return mail.body
    raise ValueError("Unsupported format")
