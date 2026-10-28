# Nextragency social posts

Public image host and template for the monthly Instagram carousel.

- `template/` : slide template (`carousel.html`, 1080x1350, 7 slides), logo PNGs, and `render.js` (Playwright screenshot script).
- `posts/YYYY-MM-topic/` : the rendered slides for each post. Metricool pulls them from here via raw.githubusercontent.com.

## Brand (Nextragency)
Charcoal #0B1314, Lime #C6FF3A, Silver #E7EBE8, Graphite #73857A, White #F4F6F0.
Headlines Sora, body Manrope (Inter used when those fonts are not installed).
Tagline: The Extra Step to Growth.

## Monthly run
1. Pick the month's topic (see `topics.md` if present).
2. Copy `template/carousel.html` and edit the slide copy. Keep the structure: cover, 5 content slides, CTA with full logo.
3. Render with `node template/render.js <html> <outdir>` and save the 7 PNGs to `posts/YYYY-MM-topic/`.
4. Push, then schedule through Metricool (blogId 7717514, Instagram, Asia/Beirut).
