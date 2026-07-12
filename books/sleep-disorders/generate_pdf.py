import os, markdown, subprocess, uuid, zipfile, re
from weasyprint import HTML, CSS
from ebooklib import epub

BOOK_TITLE = "The Sleep Reset: Reclaiming Rest When Your Brain Won't Turn Off"
BOOK_SUBTITLE = "A Compassionate Guide to Understanding and Overcoming Sleep Disorders"
AUTHOR_NAME = "Elena Voss, MSc"
SAFE_SLUG = "The-Sleep-Reset"
CHAPTERS_DIR = "/tmp/repo-update/books/sleep-disorders/chapters"
OUTPUT_DIR = "/tmp/repo-update/books/sleep-disorders"

CHAPTER_ORDER = ["foreword", "ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09", "ch10", "ch11", "resources"]

CHAPTER_TITLES = {
    "foreword": "Foreword: Why Sleep Matters More Than You Think",
    "ch01": "Chapter 1: The Sleep Crisis — Why You Can't Sleep and Why It Matters",
    "ch02": "Chapter 2: Understanding Your Sleep Architecture",
    "ch03": "Chapter 3: Insomnia — The Long Night",
    "ch04": "Chapter 4: Sleep Apnea and Breathing Disorders",
    "ch05": "Chapter 5: Restless Legs, Restless Nights — Movement Disorders",
    "ch06": "Chapter 6: Circadian Rhythm Disorders — When Your Body Clock Breaks",
    "ch07": "Chapter 7: The Anxiety-Sleep Loop",
    "ch08": "Chapter 8: Parasomnias — When Sleep Gets Strange",
    "ch09": "Chapter 9: The Science of Sleep Hygiene That Actually Works",
    "ch10": "Chapter 10: CBT-I and Other Evidence-Based Treatments",
    "ch11": "Chapter 11: Building Your Personal Sleep Recovery Plan",
    "resources": "Resources and Recommended Reading"
}

book_css = CSS(string=r"""
@page { size: 6in 9in; margin: 1in 0.7in;
  @bottom-center { content: counter(page); font-family: 'Georgia', serif; font-size: 9pt; color: #666; } }
@page :first { @bottom-center { content: none; } }
body { font-family: 'Georgia', 'Times New Roman', serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; text-align: justify; hyphens: auto; }
h1 { font-size: 24pt; font-weight: normal; text-align: center; margin-top: 2em; margin-bottom: 0.5em; page-break-before: always; page-break-after: avoid; }
h2 { font-size: 16pt; font-weight: normal; color: #2a2a2a; margin-top: 2em; margin-bottom: 0.8em; page-break-after: avoid; }
h3 { font-size: 13pt; font-weight: bold; color: #333; margin-top: 1.5em; margin-bottom: 0.5em; page-break-after: avoid; }
p { text-indent: 1.2em; margin: 0 0 0.6em 0; }
p.no-indent, .dedication p, .toc p { text-indent: 0; }
blockquote { margin: 1em 0 1em 1.5em; padding-left: 1em; border-left: 3px solid #c9a96e; font-style: italic; color: #444; }
.title-page { text-align: center; padding-top: 3em; page-break-after: always; }
.title-page .book-title { font-size: 28pt; font-weight: bold; line-height: 1.2; margin-bottom: 0.5em; }
.title-page .book-subtitle { font-size: 16pt; font-style: italic; color: #555; margin-bottom: 3em; }
.title-page .author { font-size: 14pt; margin-bottom: 0.3em; }
.title-page .author-bio { font-size: 10pt; color: #666; max-width: 70%; margin: 1em auto 0; line-height: 1.5; }
.copyright-page { page-break-after: always; font-size: 9pt; color: #666; text-align: center; padding-top: 2em; }
.copyright-page p { text-indent: 0; margin-bottom: 0.5em; }
.toc { page-break-before: always; page-break-after: always; }
.toc h1 { font-size: 20pt; margin-bottom: 1.5em; }
.toc-entry { display: flex; justify-content: space-between; padding: 0.3em 0; border-bottom: 1px dotted #ddd; font-size: 11pt; }
.chapter-number { font-weight: bold; color: #c9a96e; margin-right: 1em; }
.chapter-title-toc { flex: 1; }
.dedication { text-align: center; font-style: italic; font-size: 12pt; color: #555; padding-top: 4em; page-break-after: always; }
ul, ol { margin: 0.5em 0 0.5em 1.5em; }
li { margin-bottom: 0.3em; }
hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
.chapter-body { page-break-before: always; }
""")

def build_html():
    parts = []
    parts.append(f'<div class="title-page"><div class="book-title">{BOOK_TITLE}</div><div class="book-subtitle">{BOOK_SUBTITLE}</div><div class="author">{AUTHOR_NAME}</div><div class="author-bio">Elena Voss, MSc, is a researcher and writer specializing in sleep health and neuroscience. Combining clinical research with practical lived experience, she has helped hundreds of people understand and transform their relationship with sleep.</div></div>')
    parts.append(f'<div class="copyright-page"><p><strong>{BOOK_TITLE}</strong></p><p>{BOOK_SUBTITLE}</p><br><p>Copyright &copy; 2026 Elena Voss</p><p>All rights reserved.</p><br><p>No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the publisher.</p><br><p>This book is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified health provider with any questions regarding your sleep health.</p></div>')
    parts.append('<div class="dedication"><p>For everyone who has stared at the ceiling at 3 a.m.,<br>wondering if sleep would ever come.</p><br><p>Your rest is not lost.<br>It is waiting for you on the other side of understanding.</p></div>')

    toc_items = [
        ("Foreword", ""),
        ("1. The Sleep Crisis", ""),
        ("2. Understanding Your Sleep Architecture", ""),
        ("3. Insomnia — The Long Night", ""),
        ("4. Sleep Apnea and Breathing Disorders", ""),
        ("5. Restless Legs, Restless Nights", ""),
        ("6. Circadian Rhythm Disorders", ""),
        ("7. The Anxiety-Sleep Loop", ""),
        ("8. Parasomnias", ""),
        ("9. Sleep Hygiene That Actually Works", ""),
        ("10. CBT-I and Other Treatments", ""),
        ("11. Building Your Sleep Recovery Plan", ""),
        ("Resources", "")
    ]
    toc_html = '<div class="toc">\n<h1>Contents</h1>\n'
    for item, _ in toc_items:
        toc_html += f'<div class="toc-entry"><span><span class="chapter-title-toc">{item}</span></span></div>\n'
    toc_html += '</div>'
    parts.append(toc_html)

    for ch_id in CHAPTER_ORDER:
        fp = os.path.join(CHAPTERS_DIR, ch_id + ".md")
        title = CHAPTER_TITLES.get(ch_id, ch_id)
        if os.path.exists(fp):
            with open(fp) as f:
                md = f.read()
            html = markdown.markdown(md, extensions=["extra"])
            parts.append(f'<div class="chapter-body">\n<h1>{title}</h1>\n{html}\n</div>')
        else:
            parts.append(f'<h1>{title}</h1><p>[Chapter content pending]</p>')

    html_str = f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{BOOK_TITLE}</title></head><body>\n' + '\n'.join(parts) + '\n</body></html>'
    return html_str

html_content = build_html()
with open(os.path.join(OUTPUT_DIR, "book.html"), "w") as f:
    f.write(html_content)
HTML(string=html_content, base_url=OUTPUT_DIR).write_pdf(os.path.join(OUTPUT_DIR, f"{SAFE_SLUG}.pdf"), stylesheets=[book_css])
sz = os.path.getsize(os.path.join(OUTPUT_DIR, f"{SAFE_SLUG}.pdf"))
print(f"PDF generated! Size: {sz // 1024} KB")


# ===== EPUB GENERATION =====

def generate_epub():
    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(BOOK_TITLE)
    book.set_language('en')
    book.add_author(AUTHOR_NAME)

    cover_path = os.path.join(OUTPUT_DIR, f"{SAFE_SLUG}-Cover.jpg")
    if cover_path and os.path.exists(cover_path):
        with open(cover_path, 'rb') as f:
            book.set_cover("cover.jpg", f.read())

    style = 'body{font-family:Georgia,serif;line-height:1.6}p{text-indent:1.2em;margin:0 0 .6em}h1{text-align:center;font-size:1.8em;font-weight:normal;margin-top:2em}h2{font-size:1.4em;color:#2a2a2a;margin-top:1.5em}h3{font-size:1.2em;margin-top:1.2em}blockquote{margin:1em 0 1em 1.5em;padding-left:1em;border-left:3px solid #c9a96e;font-style:italic}'
    css = epub.EpubItem(uid="style", file_name="style/default.css", media_type="text/css", content=style)
    book.add_item(css)

    tp = epub.EpubHtml(title="Title Page", file_name="title.xhtml")
    tp.content = f'<html><body style="text-align:center;padding-top:30%"><h1>{BOOK_TITLE}</h1><h2 style="font-style:italic;color:#555">{BOOK_SUBTITLE}</h2><p style="margin-top:3em;text-indent:0">{AUTHOR_NAME}</p></body></html>'
    book.add_item(tp)

    cr = epub.EpubHtml(title="Copyright", file_name="copy.xhtml")
    cr.content = f'<html><body style="text-align:center;font-size:.8em;color:#666;padding-top:20%"><p style="text-indent:0"><strong>{BOOK_TITLE}</strong></p><p style="text-indent:0">{BOOK_SUBTITLE}</p><br/><p style="text-indent:0">Copyright &copy; 2026 {AUTHOR_NAME}</p><p style="text-indent:0">All rights reserved.</p></body></html>'
    book.add_item(cr)

    ch_pages = []
    for cid in CHAPTER_ORDER:
        fp = os.path.join(CHAPTERS_DIR, f"{cid}.md")
        if not os.path.exists(fp):
            continue
        with open(fp) as f:
            md = f.read()
        body = markdown.markdown(md, extensions=["extra"])
        title = CHAPTER_TITLES.get(cid, cid)
        ch = epub.EpubHtml(title=title, file_name=f"{cid}.xhtml")
        ch.content = f'<html><body><h1>{title}</h1>{body}</body></html>'
        ch.add_item(css)
        book.add_item(ch)
        ch_pages.append(ch)

    book.toc = [
        (epub.Section('Front Matter'), [epub.Link("title.xhtml", "Title Page", "title"),
            epub.Link("copy.xhtml", "Copyright", "copy")]),
        (epub.Section('Chapters'), [epub.Link(f"{cid}.xhtml", CHAPTER_TITLES.get(cid, cid), cid) for cid in CHAPTER_ORDER])
    ]

    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    book.spine = [tp, cr] + ch_pages

    epub_path = os.path.join(OUTPUT_DIR, f"{SAFE_SLUG}.epub")
    epub.write_epub(epub_path, book, {})
    sz = os.path.getsize(epub_path) / 1024
    print(f"EPUB generated: {epub_path} ({sz:.0f} KB)")

    with zipfile.ZipFile(epub_path) as z:
        opf = z.read('EPUB/content.opf').decode('utf-8')
        refs = re.findall(r'idref="([^"]+)"', opf)
        seen = set(refs)
        assert len(refs) == len(seen), f"Duplicates: {[r for r in refs if refs.count(r) > 1]}"
        nav_count = len(re.findall(r'properties="nav"', opf))
        assert nav_count == 1, f"Expected 1 nav item, got {nav_count}"
        ncx_in_manifest = 'id="ncx"' in opf
        assert ncx_in_manifest, "NCX not found in manifest"
        print("✅ EPUB validation passed")

generate_epub()
