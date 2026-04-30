import os
import re
import shutil
from urllib.parse import urlparse

from playwright.async_api import async_playwright
import asyncio

from bale_downloader.config import WEBPAGE_OUTPUT_DIR, WEBPAGE_PDF_TIMEOUT_MS


class Webpage:
    def __init__(self):
        os.makedirs(WEBPAGE_OUTPUT_DIR, exist_ok=True)

    def get_content(self, url: str) -> tuple[str, str | None, list[str], list[str]]:
        self._clean_output_dir()
        title, pdf_path = asyncio.run(self._save_as_pdf(url))
        print("PDF saved", flush=True)
        message = f"📄 {title}\n{url}"
        return (message, None, [pdf_path], [])

    def _clean_output_dir(self):
        if os.path.exists(WEBPAGE_OUTPUT_DIR):
            shutil.rmtree(WEBPAGE_OUTPUT_DIR)
        os.makedirs(WEBPAGE_OUTPUT_DIR, exist_ok=True)

    def _sanitize_filename(self, title: str) -> str:
        sanitized = re.sub(r'[^\w\s\-.]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        return sanitized[:100] or "page"

    async def _save_as_pdf(self, url: str) -> tuple[str, str]:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print("Browser launched", flush=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 900},
                locale="en-US",
            )
            page = await context.new_page()

            await page.goto(url, wait_until="networkidle", timeout=WEBPAGE_PDF_TIMEOUT_MS)

            title = await page.title() or parsed.netloc
            filename = self._sanitize_filename(title) + ".pdf"
            pdf_path = os.path.join(WEBPAGE_OUTPUT_DIR, filename)

            await page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "0.4in", "bottom": "0.4in", "left": "0.4in", "right": "0.4in"},
            )

            await browser.close()

        return title, pdf_path
