#!/usr/bin/env python3
"""Builds the Sawwa site from _src/*.md. Run: python3 _src/build.py (needs pandoc)."""
import pathlib, subprocess, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"

def md(name):
    text = (SRC / name).read_text(encoding="utf-8")
    # Every section heading becomes an h2, whatever level the source uses.
    text = re.sub(r"^#{1,6} ", "## ", text, flags=re.M)
    # Arabic sources number lists with Arabic-Indic digits, which pandoc does not see as lists.
    # Use ASCII digits so they become real lists; CSS shows them in Arabic-Indic again.
    text = re.sub(r"^([٠-٩]+)\.", lambda m: m.group(1).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")) + ".", text, flags=re.M)
    # A list right after a paragraph line needs a blank line before it.
    text = re.sub(r"([^\n])\n(1\. )", r"\1\n\n\2", text)
    return subprocess.run(["pandoc", "-f", "markdown-auto_identifiers", "-t", "html5"],
                          input=text, capture_output=True, text=True, check=True).stdout

HOME = (SRC / "home.html").read_text(encoding="utf-8")
# The doc pages reuse the home page's tokens, header, footer and language switch.
BASE_CSS = HOME.split("<style>", 1)[1].split("</style>", 1)[0]
SCRIPT = HOME[HOME.index("<script>"):HOME.index("</script>") + len("</script>")]

DOC_CSS = """
.doc-hero { padding-block: 24px 40px; }
.doc-hero h1 { font-family: var(--display); font-weight: 700; font-size: clamp(30px, 5vw, 46px); line-height: 1.25; margin: 14px 0 10px; text-wrap: balance; }
.doc-hero .lede { margin: 0; font-size: 17px; }
.back { font-size: 15px; text-decoration: none; }
.doc-band { background: var(--surface); border-block: 1px solid var(--line); padding-block: 48px 64px; }
.doc-grid { display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 48px; align-items: start; }
.toc { position: sticky; top: 24px; display: flex; flex-direction: column; gap: 2px; font-size: 14px; line-height: 1.5; }
.toc b { font-family: var(--display); font-weight: 600; font-size: 13px; color: var(--muted); margin-bottom: 8px; }
.toc a { color: var(--muted); text-decoration: none; padding: 6px 12px; border-inline-start: 2px solid var(--line); }
.toc a:hover { color: var(--brand); border-color: var(--brand); }
.prose { max-width: 44em; }
.prose h2 { font-size: clamp(20px, 2.4vw, 24px); margin: 40px 0 10px; scroll-margin-top: 16px; }
.prose h2:first-child { margin-top: 0; }
.prose p { margin: 0 0 12px; color: var(--muted); }
.prose ol, .prose ul { margin: 0 0 12px; padding-inline-start: 24px; color: var(--muted); display: flex; flex-direction: column; gap: 8px; }
.prose li::marker { color: var(--brand); font-weight: 600; }
[lang=ar] .prose ol { list-style-type: arabic-indic; }
.prose strong { color: var(--ink); }
.cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.card { background: var(--bg); border: 1px solid var(--line); border-radius: 20px; padding: 24px; }
.card h2 { font-size: 22px; margin: 0 0 8px; }
.card p { margin: 0; color: var(--muted); }
.timeline { list-style: none; margin: 32px 0 0; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.timeline li { border-top: 3px solid var(--brand); padding-top: 14px; }
.timeline li:last-child { border-color: var(--line); }
.timeline b { display: block; font-family: var(--display); font-size: 18px; margin-bottom: 4px; }
.timeline p { margin: 0; color: var(--muted); font-size: 15px; }
@media (max-width: 820px) {
  .doc-grid, .cards, .timeline { grid-template-columns: 1fr; }
  .doc-grid { gap: 24px; }
  .toc { position: static; display: none; }
}
"""

def page(path, title, desc, ar, en):
    html = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Readex+Pro:wght@500;600;700&display=swap">
<style>{BASE_CSS}{DOC_CSS}</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="/"><span class="mark" aria-hidden="true">سوا</span><span>Sawwa · سوا</span></a>
    <div class="tools"><button class="switch theme" id="theme-switch" type="button" aria-label="Light or dark mode" title="Light or dark mode"><svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z"/></svg></button><button class="switch" id="lang-switch" type="button"><span class="lang-ar">English</span><span class="lang-en">العربية</span></button></div>
  </div>
</header>
<main>
  <div class="lang-ar" lang="ar" dir="rtl">{ar}</div>
  <div class="lang-en" lang="en" dir="ltr">{en}</div>
</main>
<footer><div class="wrap">
  <span><span class="lang-ar">© ٢٠٢٦ فريق سوا</span><span class="lang-en">© 2026 The Sawwa team</span></span>
  <nav>
    <a href="/privacy/"><span class="lang-ar">سياسة الخصوصية</span><span class="lang-en">Privacy policy</span></a>
    <a href="/terms/"><span class="lang-ar">الشروط والأحكام</span><span class="lang-en">Terms</span></a>
    <a href="/delete-account/"><span class="lang-ar">حذف الحساب</span><span class="lang-en">Delete your account</span></a>
  </nav>
</div></footer>
{SCRIPT}
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

def hero(lang, pill, title, lede):
    back = "→ الرئيسية" if lang == "ar" else "← Home"
    return f"""<section class="doc-hero"><div class="wrap">
  <a class="back" href="/">{back}</a><br>
  <span class="pill" style="margin-top:20px">{pill}</span>
  <h1>{title}</h1>
  <p class="lede">{lede}</p>
</div></section>"""

def article(lang, mdfile, prefix):
    html = md(mdfile)
    toc = []
    def repl(m):
        n = len(toc) + 1
        text = re.sub(r"<[^>]+>", "", m.group(1))
        toc.append(f'<a href="#{prefix}{n}">{text}</a>')
        return f'<h2 id="{prefix}{n}">{m.group(1)}</h2>'
    html = re.sub(r"<h2>(.*?)</h2>", repl, html)
    label = "المحتويات" if lang == "ar" else "Contents"
    return f"""<section class="doc-band"><div class="wrap doc-grid">
  <nav class="toc" aria-label="{label}"><b>{label}</b>{''.join(toc)}</nav>
  <div class="prose">{html}</div>
</div></section>"""

def doc(path, slug, t, desc):
    page(path, f"{t['ar_title']} · {t['en_title']}", desc,
         hero("ar", t["ar_pill"], t["ar_title"], t["ar_meta"]) + article("ar", f"{slug}-ar.md", "ar-"),
         hero("en", t["en_pill"], t["en_title"], t["en_meta"]) + article("en", f"{slug}-en.md", "en-"))

AR_META = "النسخة ١ (الفترة التجريبية). إذا اختلفت النسختان، تُعتمد النسخة العربية."
EN_META = "Version 1 (pilot). If the Arabic and English versions differ, the Arabic version prevails."
doc("privacy/index.html", "privacy", dict(ar_title="سياسة الخصوصية", en_title="Privacy policy",
    ar_pill="خصوصيتك", en_pill="Your privacy", ar_meta=AR_META, en_meta=EN_META),
    "How Sawwa collects, uses and protects your personal data.")
doc("terms/index.html", "terms", dict(ar_title="الشروط والأحكام", en_title="Terms and conditions",
    ar_pill="قواعد الاستخدام", en_pill="Using Sawwa", ar_meta=AR_META, en_meta=EN_META),
    "The terms for using the Sawwa carpooling app.")

DEL_AR = hero("ar", "حسابك", "حذف حسابك على سوا", "تقدر تحذف حسابك في أي وقت من التطبيق، وده اللي بيحصل بعدها.") + """
<section class="doc-band"><div class="wrap">
  <div class="cards">
    <div class="card"><h2>من التطبيق</h2><p>افتح «حسابي» ثم «حذف الحساب»، واكتب اسمك للتأكيد.</p></div>
    <div class="card"><h2>مش معاك الموبايل القديم؟</h2><p>نزّل سوا على أي موبايل، وسجّل دخول برقمك (هتبعت كود من واتساب نفس الرقم)، وبعدين احذف الحساب من «حسابي». أو اطلب الحذف من زر «كلم الدعم» في التطبيق.</p></div>
  </div>
  <ol class="timeline">
    <li><b>على طول</b><p>حسابك بيتخفي، وعندك ١٤ يوم لو غيّرت رأيك.</p></li>
    <li><b>بعد ١٤ يوم</b><p>بنمسح اسمك وصورتك وإشعاراتك وتعليقات التقييم.</p></li>
    <li><b>بعد ٦ شهور</b><p>بنمسح رقمك واسمك وصور البطاقة ولوحات العربية، اللي بنحتفظ بيها للأمان ولا يشوفها إلا فريق سوا. الرحلات القديمة ودرجات التقييم بتفضل من غير اسمك أو رقمك.</p></li>
  </ol>
</div></section>"""
DEL_EN = hero("en", "Your account", "Delete your Sawwa account", "You can delete your account any time from the app. Here's what happens next.") + """
<section class="doc-band"><div class="wrap">
  <div class="cards">
    <div class="card"><h2>In the app</h2><p>Open Account, then Delete account, and type your name to confirm.</p></div>
    <div class="card"><h2>Don't have your old phone?</h2><p>Install Sawwa on any phone, sign in with your number (you send a code from that number's WhatsApp), then delete the account from Account. Or ask us through Contact support in the app.</p></div>
  </div>
  <ol class="timeline">
    <li><b>Right away</b><p>Your account is hidden, and you have 14 days to change your mind.</p></li>
    <li><b>After 14 days</b><p>We erase your name, photo, notifications and rating comments.</p></li>
    <li><b>After 6 months</b><p>We erase your number, name, ID documents and car plates, kept until then for safety and seen only by the Sawwa team. Past trips and rating scores stay without your name or number.</p></li>
  </ol>
</div></section>"""
page("delete-account/index.html", "حذف حسابك على سوا · Delete your Sawwa account",
     "How to delete your Sawwa account, and what we erase and keep.", DEL_AR, DEL_EN)

head, body = HOME.split("</style>", 1)
(ROOT / "index.html").write_text(
    '<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<link rel="icon" href="/icon.png">\n' + head + "</style>\n</head>\n<body>\n" + body + "</body>\n</html>\n",
    encoding="utf-8")
print("built")
