import base64
import os
from io import BytesIO
from playwright.async_api import async_playwright
from PIL import Image


class HTMLSnapper:
    def __init__(self, browser_endpoint: str = ''):
        self._browser_endpoint = browser_endpoint

    async def html_to_bytes(self, html: str):
        if not html:
            return None
        html = html.replace('\n', '').replace('\t', '')
        # html_template = 'snapshot_template.html'
        path = os.path.realpath(__file__)
        api_dir = os.path.dirname(path)
        html_template = f'{api_dir}/snapshot_template.html'
        with open(html_template) as html_file:
            content = html_file.read()
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            endpoint = self._browser_endpoint
            browser = await chromium.connect_over_cdp(endpoint) if endpoint else await chromium.launch()
            page = await browser.new_page()
            await page.set_content(content)
            math_input_loc = page.locator('#MathInput')
            await math_input_loc.evaluate("(element, value) => element.value = value", html)
            await page.wait_for_function('typeof typesetInput === "function"')
            await page.evaluate('typesetInput()')
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_selector('#status')
            math_preview_loc = page.locator('#MathPreview')
            data = await math_preview_loc.screenshot(scale='css')
            await page.close()
            await browser.close()
        return data

    async def html_to_encoded_image(self, html, archive_image=True):
        screen_shot_data = await self.html_to_bytes(html)
        if not screen_shot_data:
            return ''

        if not archive_image:
            image_uri = "data:image/jpg;base64," + base64.b64encode(screen_shot_data).decode()
            return image_uri

        bin_file = BytesIO(screen_shot_data)
        image = Image.open(bin_file)
        with BytesIO() as output:
            image.save(output, format='webp')
            screen_shot_data = output.getvalue()

        image_uri = "data:image/webp;base64," + base64.b64encode(screen_shot_data).decode()
        return image_uri
