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

CSS = """
:root { --bg:#F4F5F2; --surface:#FFFFFF; --text:#13201C; --muted:#33403B; --line:#E1E6E2; --primary:#0E5A4A; --primary-pressed:#0A4538; --on-primary:#FFFFFF; }
@media (prefers-color-scheme: dark) { :root { --bg:#0F1513; --surface:#18201D; --text:#E7ECEA; --muted:#A9B5B0; --line:#25302C; --primary:#4FB59A; --primary-pressed:#3E9A82; --on-primary:#0B1F1A; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font-family:"IBM Plex Sans Arabic","Readex Pro",system-ui,-apple-system,"Segoe UI",sans-serif; }
main { max-width:860px; margin:0 auto; padding:32px 16px 64px; display:flex; flex-direction:column; gap:20px; }
header { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.brand { display:flex; align-items:center; gap:12px; font-size:20px; font-weight:700; color:var(--text); text-decoration:none; }
.mark { width:40px; height:40px; border-radius:12px; background:var(--primary); color:var(--on-primary); display:flex; align-items:center; justify-content:center; font-weight:700; }
nav { display:flex; gap:16px; flex-wrap:wrap; font-size:15px; }
nav a, .doc a, .foot a { color:var(--primary); }
.langs { display:flex; gap:8px; }
.langs a { font-size:14px; padding:6px 12px; border:1px solid var(--line); border-radius:999px; color:var(--text); text-decoration:none; background:var(--surface); }
section { background:var(--surface); border:1px solid var(--line); border-radius:20px; padding:24px; display:flex; flex-direction:column; gap:12px; }
h1 { margin:0; font-family:"Readex Pro","IBM Plex Sans Arabic",sans-serif; font-size:24px; line-height:32px; }
h2 { margin:12px 0 0; font-size:18px; line-height:26px; }
p, li { margin:0; font-size:16px; line-height:26px; color:var(--muted); }
[lang=ar] ol { list-style-type:arabic-indic; }
ol, ul { margin:0; padding-inline-start:22px; display:flex; flex-direction:column; gap:6px; }
.cols { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:20px; }
.btn { display:inline-flex; align-items:center; min-height:44px; padding:0 18px; border-radius:14px; background:var(--primary); color:var(--on-primary); font-weight:600; text-decoration:none; align-self:flex-start; }
.btn:hover { background:var(--primary-pressed); }
.meta { font-size:14px; }
.foot { text-align:center; font-size:14px; color:var(--muted); }
"""

def page(path, title, desc, body):
    html = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/icon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Readex+Pro:wght@500;600;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<main>
<header>
  <a class="brand" href="/"><span class="mark" aria-hidden="true">سوا</span><span>Sawwa · سوا</span></a>
  <nav><a href="/privacy/">Privacy · الخصوصية</a><a href="/terms/">Terms · الشروط</a><a href="/delete-account/">Delete account · حذف الحساب</a></nav>
</header>
{body}
<p class="foot">© 2026 Sawwa · سوا</p>
</main>
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

def doc(path, ar_title, en_title, ar_md, en_md, ar_meta, en_meta, desc):
    body = f"""<div class="langs" dir="ltr"><a href="#ar">العربية</a><a href="#en">English</a></div>
<section id="ar" class="doc" dir="rtl" lang="ar"><h1>{ar_title}</h1><p class="meta">{ar_meta}</p>{md(ar_md)}</section>
<section id="en" class="doc" dir="ltr" lang="en"><h1>{en_title}</h1><p class="meta">{en_meta}</p>{md(en_md)}</section>"""
    page(path, f"{ar_title} · {en_title}", desc, body)

doc("privacy/index.html", "سياسة الخصوصية لسوا", "Sawwa Privacy Policy",
    "privacy-ar.md", "privacy-en.md",
    "النسخة ١ (الفترة التجريبية). إذا اختلفت النسختان، تُعتمد النسخة العربية.",
    "Version 1 (pilot). If the Arabic and English versions differ, the Arabic version prevails.",
    "How Sawwa collects, uses and protects your personal data.")
doc("terms/index.html", "الشروط والأحكام لسوا", "Sawwa Terms and Conditions",
    "terms-ar.md", "terms-en.md",
    "النسخة ١ (الفترة التجريبية). إذا اختلفت النسختان، تُعتمد النسخة العربية.",
    "Version 1 (pilot). If the Arabic and English versions differ, the Arabic version prevails.",
    "The terms for using the Sawwa carpooling app.")

page("delete-account/index.html", "حذف حسابك على سوا · Delete your Sawwa account",
     "How to delete your Sawwa account, and what we erase and keep.", """<div class="cols">
<section dir="rtl" lang="ar">
  <h1>حذف حسابك على سوا</h1>
  <p>من التطبيق: افتح «حسابي» ثم «حذف الحساب»، واكتب اسمك للتأكيد.</p>
  <p>مش معاك الموبايل القديم؟ نزّل سوا على أي موبايل، وسجّل دخول برقمك (هتبعت كود من واتساب نفس الرقم)، وبعدين احذف الحساب من «حسابي». أو اطلب الحذف من زر «كلم الدعم» في التطبيق.</p>
  <p>بعد الطلب، حسابك بيتخفي على طول، وعندك ١٤ يوم لو غيّرت رأيك. بعد ١٤ يوم بنمسح اسمك وصورتك وإشعاراتك وتعليقات التقييم. بنحتفظ برقمك واسمك وصور البطاقة ولوحات العربية للأمان ٦ شهور، ولا يشوفها إلا فريق سوا، وبعدين بتتمسح. الرحلات القديمة ودرجات التقييم بتفضل من غير اسمك أو رقمك.</p>
</section>
<section dir="ltr" lang="en">
  <h1>Delete your Sawwa account</h1>
  <p>In the app: open Account, then Delete account, and type your name to confirm.</p>
  <p>Don't have your old phone? Install Sawwa on any phone, sign in with your number (you send a code from that number's WhatsApp), then delete the account from Account. Or ask us through Contact support in the app.</p>
  <p>Your account is hidden at once, and you have 14 days to change your mind. After 14 days we erase your name, photo, notifications and rating comments. We keep your number, name, ID documents and car plates for 6 months for safety, seen only by the Sawwa team, then erase them. Past trips and rating scores stay without your name or number.</p>
</section>
</div>
<p class="foot"><a href="/privacy/">Privacy policy · سياسة الخصوصية</a></p>""")

home = (SRC / "home.html").read_text(encoding="utf-8")
head, body = home.split("</style>", 1)
(ROOT / "index.html").write_text(
    '<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<link rel="icon" href="/icon.png">\n' + head + "</style>\n</head>\n<body>\n" + body + "</body>\n</html>\n",
    encoding="utf-8")
print("built")
