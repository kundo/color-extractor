from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import urlparse
from pyppeteer import launch
import colorgram
from pathlib import Path
from typing import Optional


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("template.html", {
        "request": request,
    })


@app.post("/", response_class=HTMLResponse)
async def extract(request: Request):
    form = await request.form()

    if "url" not in form or form["url"] == "":
        return templates.TemplateResponse("template.html", {
            "request": request,
            "url": "",
            "error": "Please fill in an url",
        })

    url = form["url"]

    if not url.startswith("http"):
        url = "https://" + url

    domain = urlparse(url).netloc
    path = Path("screenshots") / Path(f'{domain}.png')

    if not Path(path).exists():
        await write_screenshot(url, path)

    colors = colorgram.extract(path, 6)
    # colors = await extract_colors(path, 6)

    Path(path).unlink(missing_ok=True)

    return templates.TemplateResponse("template.html", {
        "request": request,
        "url": url.replace("https://", "").replace("http://", ""),
        "colors": colors,
    })


async def write_screenshot(url, path):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    await page.screenshot({
        "path": path,
        "fullPage": True,
    })
    await browser.close()


# async def extract_colors(path, num_colors):
#     from PIL import Image
#     from collections import Counter
#     colors = Counter()
#     im = Image.open(path).convert('RGB')
#     for i in range(im.width):
#         for j in range(im.height):
#             h = im.getpixel((i, j))
#             colors[h] += 1

#     im.close()

#     print(colors.most_common(num_colors))
