# -*- coding: utf-8 -*-
"""Build cv-da.pdf and cv-en.pdf straight from index.html.

The website is the single source of truth: Danish comes from the markup,
English from the EN dictionary in the inline script. Run after any text change:

    py -3 build_cv.py
"""
import html
import os
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, FrameBreak, KeepInFrame,
                                ListFlowable, ListItem, NextPageTemplate,
                                PageTemplate, Paragraph, Spacer)
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "index.html")
PHOTO_SRC = os.path.join(HERE, "foto.jpg")
PHOTO_SQ = os.path.join(HERE, ".foto_square.jpg")

NAVY = HexColor("#132436")
ACCENT = HexColor("#1c6ea4")
SKY = HexColor("#6fb3dd")
SLATE = HexColor("#3c4a56")
LIGHT = HexColor("#c9d3dc")
LIGHT2 = HexColor("#9fb1bf")
LINE = HexColor("#e2ddd3")
WHITE = HexColor("#ffffff")

PAGE_W, PAGE_H = A4
SIDEBAR_W = 62 * mm
MARGIN = 14


# --------------------------------------------------------------------------
# 1. Pull the content out of the website
# --------------------------------------------------------------------------
def clean(fragment):
    """HTML fragment -> reportlab-safe inline markup (only <b> survives)."""
    s = re.sub(r"<em[^>]*>.*?</em>", "", fragment, flags=re.S)   # drop the "speciale" pill
    s = s.replace("<strong>", "\x01").replace("</strong>", "\x02")
    s = s.replace("<b>", "\x01").replace("</b>", "\x02")
    s = re.sub(r"<[^>]+>", "", s)                                # strip every other tag
    s = html.unescape(s)                                         # &amp; -> &
    s = s.replace("&", "&amp;")                                  # re-escape for reportlab
    s = s.replace("\x01", "<b>").replace("\x02", "</b>")
    return re.sub(r"\s+", " ", s).strip()


def load():
    src = open(SRC, encoding="utf-8").read()

    da = {}
    # capture the element's full body by matching its own closing tag
    for m in re.finditer(r'<(\w+)[^>]*\bdata-i18n="([^"]+)"[^>]*>(.*?)</\1>', src, re.S):
        da.setdefault(m.group(2), clean(m.group(3)))

    block = re.search(r"var EN = \{(.*?)\n    \};", src, re.S).group(1)
    en = {}
    for m in re.finditer(r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', block):
        val = m.group(2).encode().decode("unicode_escape")
        en[m.group(1)] = clean(val)

    return da, en


# --------------------------------------------------------------------------
# 2. Render
# --------------------------------------------------------------------------
LABELS = {
    "da": dict(profile="PROFIL", fields="FAGOMRÅDER", exp="ERFARING",
               earlier="TIDLIGERE KARRIERE", contact="KONTAKT", langs="SPROG",
               strengths="KOMPETENCER", snapshot="NØGLETAL", spec="SPECIALE",
               langlist=["Dansk — modersmål", "Engelsk — flydende"],
               footer="CV", place="København, Danmark"),
    "en": dict(profile="PROFILE", fields="FIELDS", exp="EXPERIENCE",
               earlier="EARLIER CAREER", contact="CONTACT", langs="LANGUAGES",
               strengths="KEY STRENGTHS", snapshot="AT A GLANCE", spec="SPECIALISM",
               langlist=["Danish — native", "English — fluent"],
               footer="CV", place="Copenhagen, Denmark"),
}

STRENGTHS = {
    "da": ["Identitet & adgangsstyring (IAM)", "Access governance & attestering",
           "Privilegerede adgange (PAM)", "Katalogtjenester, autentifikation & MFA",
           "Joiner-mover-leaver & provisionering", "NIS2, GDPR, ISO 27xxx & revisionsparathed",
           "Produktejerskab: vision, roadmap, prioritering", "Program- og projektstyring",
           "Rådgivning på direktionsniveau", "AI i udviklingsarbejdet"],
    "en": ["Identity & access management (IAM)", "Access governance & certification",
           "Privileged access management (PAM)", "Directory services, authentication & MFA",
           "Joiner-mover-leaver & provisioning", "NIS2, GDPR, ISO 27xxx & audit readiness",
           "Product ownership: vision, roadmap, priorities", "Programme & project management",
           "Advice at executive level", "AI in development work"],
}

JOBS = [
    ("2018 – 2026", "tl1.role", "ID CONNECT A/S", "tl1.desc", []),
    ("2014 – 2018", None, "MICRO FOCUS", "tl2.desc", []),
    ("2008 – 2014", None, "SYMANTEC", "tl3.desc", ["sub.1", "sub.2", "sub.3"]),
]
JOB_ROLES = {1: "Territory Manager, NetIQ Denmark", 2: "Enterprise Account Manager"}
EARLIER = ["2007 – 2008", "2004 – 2007", "2000 – 2004", "1994 – 2000"]


def square_photo():
    im = Image.open(PHOTO_SRC).convert("RGB")
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, min(int((h - side) * 0.32), h - side))
    im.crop((left, top, left + side, top + side)).save(PHOTO_SQ, quality=92)


def build(lang, txt, out_path):
    L = LABELS[lang]

    name_s = ParagraphStyle("n", fontName="Helvetica-Bold", fontSize=16.5, leading=19,
                            textColor=WHITE, spaceAfter=2)
    role_s = ParagraphStyle("r", fontName="Helvetica-Bold", fontSize=8.8, leading=11.6,
                            textColor=SKY, spaceAfter=0)
    sbh_s = ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=8.6, leading=11,
                           textColor=WHITE, spaceBefore=0, spaceAfter=5, letterSpacing=0.6)
    sbb_s = ParagraphStyle("sb", fontName="Helvetica", fontSize=8.1, leading=11,
                           textColor=LIGHT)
    h2_s = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.6, leading=13.5,
                          textColor=NAVY, spaceBefore=10, spaceAfter=5, letterSpacing=0.5)
    body_s = ParagraphStyle("b", fontName="Helvetica", fontSize=8.9, leading=12,
                            textColor=SLATE, spaceAfter=4)
    fh_s = ParagraphStyle("fh", fontName="Helvetica-Bold", fontSize=9.8, leading=12,
                          textColor=NAVY, spaceBefore=7, spaceAfter=2)
    meta_s = ParagraphStyle("m", fontName="Helvetica-Bold", fontSize=8.2, leading=10.5,
                            textColor=ACCENT, spaceAfter=3)
    bul_s = ParagraphStyle("bu", fontName="Helvetica", fontSize=8.5, leading=11,
                           textColor=SLATE, spaceAfter=1.5, leftIndent=10)

    def bullets(items, style=bul_s, indent=10, after=5, colour=ACCENT):
        return ListFlowable(
            [ListItem(Paragraph(t, style), leftIndent=indent, value="•") for t in items],
            bulletType="bullet", start="•", leftIndent=indent,
            bulletColor=colour, spaceBefore=0, spaceAfter=after)

    def chrome(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, SIDEBAR_W, PAGE_H, stroke=0, fill=1)
        if doc.page == 1:
            size = 27 * mm
            px, py = (SIDEBAR_W - size) / 2, PAGE_H - 17 * mm - size
            p = canvas.beginPath()
            p.circle(px + size / 2, py + size / 2, size / 2)
            canvas.saveState()
            canvas.clipPath(p, stroke=0, fill=0)
            try:
                canvas.drawImage(PHOTO_SQ, px, py, width=size, height=size, mask="auto")
            except Exception:
                pass
            canvas.restoreState()
            canvas.setStrokeColor(ACCENT)
            canvas.setLineWidth(1.5)
            canvas.circle(px + size / 2, py + size / 2, size / 2, stroke=1, fill=0)
        canvas.setFont("Helvetica", 7.2)
        canvas.setFillColor(HexColor("#9aa6ae"))
        canvas.drawString(SIDEBAR_W + MARGIN, 7.5 * mm,
                          "Jørgen Østergaard — " + L["footer"])
        canvas.drawRightString(PAGE_W - MARGIN, 7.5 * mm, "%d" % doc.page)
        canvas.restoreState()

    doc = BaseDocTemplate(out_path, pagesize=A4, leftMargin=0, rightMargin=0,
                          topMargin=0, bottomMargin=0,
                          title="Jørgen Østergaard — CV",
                          author="Jørgen Østergaard")
    f_side = Frame(6, 11.5 * mm, SIDEBAR_W - 12, PAGE_H - 22.5 * mm, id="s",
                   leftPadding=8, rightPadding=8, topPadding=4, bottomPadding=3)
    main_kw = dict(leftPadding=0, rightPadding=0, topPadding=4, bottomPadding=3)
    f_main = Frame(SIDEBAR_W + MARGIN, 11.5 * mm, PAGE_W - SIDEBAR_W - MARGIN - 14,
                   PAGE_H - 22.5 * mm, id="m", **main_kw)
    f_main2 = Frame(SIDEBAR_W + MARGIN, 11.5 * mm, PAGE_W - SIDEBAR_W - MARGIN - 14,
                    PAGE_H - 22.5 * mm, id="m2", **main_kw)
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[f_side, f_main], onPage=chrome),
        PageTemplate(id="Later", frames=[f_main2], onPage=chrome),
    ])

    # ---------------- sidebar ----------------
    groups = [
        [Spacer(1, 38 * mm),
         Paragraph("JØRGEN", name_s), Paragraph("ØSTERGAARD", name_s),
         Paragraph(txt["hero.h1"], role_s)],
        [Paragraph(L["contact"], sbh_s),
         bullets([L["place"], "+45 5363 6732", "ostergaard.jorgen@gmail.com",
                  "ostergaardjorgen.github.io", "linkedin.com/in/ostergaardjorgen"],
                 sbb_s, 9, 0, LIGHT2)],
        [Paragraph(L["langs"], sbh_s), bullets(L["langlist"], sbb_s, 9, 0, LIGHT2)],
        [Paragraph(L["strengths"], sbh_s), bullets(STRENGTHS[lang], sbb_s, 9, 0, LIGHT2)],
        [Paragraph(L["snapshot"], sbh_s),
         bullets(["%s %s" % (txt["fact.%dn" % i], txt["fact.%dl" % i]) for i in (1, 2, 3)],
                 sbb_s, 9, 0, LIGHT2)],
    ]
    avail_w = f_side._width - f_side._leftPadding - f_side._rightPadding
    avail_h = f_side._height - f_side._topPadding - f_side._bottomPadding

    class _Canv:
        def __getattr__(self, n):
            return lambda *a, **k: 0
    dummy = _Canv()

    def height(flows):
        tot = 0.0
        for i, fl in enumerate(flows):
            if not hasattr(fl, "canv"):
                fl.canv = dummy
            try:
                tot += fl.wrap(avail_w, 10000)[1]
            finally:
                if getattr(fl, "canv", None) is dummy:
                    del fl.canv
            if i < len(flows) - 1:
                tot += fl.getSpaceAfter()
        return tot

    hs = [height(g) for g in groups]
    gap = max(7.0, (avail_h - sum(hs) - 1) / (len(groups) - 1))
    side = []
    for i, g in enumerate(groups):
        if i:
            side.append(Spacer(1, gap))
        side.extend(g)

    # ---------------- main ----------------
    main = [Paragraph(L["profile"], h2_s), Paragraph(txt["hero.tagline"], body_s),
            Paragraph(L["fields"], h2_s)]
    for i in (1, 2, 3, 4):
        head = txt["a%d.h3" % i]
        if i in (1, 2):
            head += '  <font size="6.6" color="#1c6ea4">▪ %s</font>' % L["spec"]
        main.append(Paragraph(head, fh_s))
        main.append(bullets([txt["a%d.li%d" % (i, n)] for n in range(1, 7)]))

    main.append(Paragraph(L["exp"], h2_s))
    for idx, (period, role_key, org, desc_key, subs) in enumerate(JOBS):
        role = txt[role_key] if role_key else JOB_ROLES[idx]
        main.append(Paragraph(role, fh_s))
        main.append(Paragraph("%s &nbsp;–&nbsp; %s" % (org, period), meta_s))
        main.append(Paragraph(txt[desc_key], body_s))
        if subs:
            main.append(bullets([txt[k] for k in subs]))

    main.append(Paragraph(L["earlier"], h2_s))
    main.append(bullets(["<b>%s</b> &nbsp;–&nbsp; %s" % (EARLIER[i], txt["ey.%d" % (i + 1)])
                         for i in range(4)]))

    boxed = [KeepInFrame(avail_w, avail_h, side, mode="shrink", mergeSpace=1)]
    doc.build(boxed + [FrameBreak(), NextPageTemplate("Later")] + main)
    return out_path


if __name__ == "__main__":
    square_photo()
    da, en = load()
    for lang, txt in (("da", da), ("en", en)):
        out = os.path.join(HERE, "Jorgen-Ostergaard-cv-%s.pdf" % ("dk" if lang == "da" else "en"))
        build(lang, txt, out)
        print("wrote", os.path.basename(out))
    os.remove(PHOTO_SQ)
