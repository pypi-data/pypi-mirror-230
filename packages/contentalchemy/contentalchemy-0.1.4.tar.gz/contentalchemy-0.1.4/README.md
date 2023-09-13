# Introduction

Why do we start this repo?

- Image processing: Snap HTML contents embedded math notations.

# Image snapper:

## Config: 

ENV VARS:

CA_HEADLESS_URL: default is empty, you should set it a headless browser 

(I.e: Browserless, Browserstack, Chrominum, Chrome Stabe)

## Code snippets:

```python
from contentalchemy.images.sync_api.snapper import HTMLSnapper


html_str = "<p>abc</p>"
snapper = HTMLSnapper()
original_encoded = snapper.html_to_encoded_image(html_str)
```