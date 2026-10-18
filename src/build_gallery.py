"""Builds ../index.html: the gallery for the Toki concept art."""
import os, markdown, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def md(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return ""
    return markdown.markdown(open(p).read(), extensions=["tables"])


SHEETS = [
    ("png/05_key_art.png", "05 · Key art: “Tell Me Cookie”",
     "Dusk on the Street, over Cookie Monster's shoulder. He's someone else's character, so he appears only from behind, as a "
     "shape. He holds up his last cookie. Toki can't eat it, so it listens, hands clasped, with its whole face. The pupils are "
     "glued felt, as on the real puppet, so Toki looks at the cookie by turning its head."),
    ("png/03_model_sheet.png", "03 · Model sheet: maquette turnaround",
     "Front, three-quarter, profile and back, orthographic, one scale. The puppet is a signed-distance model, sphere-traced "
     "in numpy and posed by puppeteer parameters. The profile ghosts in the puppeteer's hand, which enters at the back so the "
     "wrist is the hinge, and draws the eye focus out to 70 cm."),
    ("png/04_acting_sheet.png", "04 · Acting sheet: ten beats",
     "Muppet acting is mostly angle and timing. Every beat is posed only with what a puppeteer has: wrist (yaw, pitch, "
     "roll), thumb (jaw), swappable lids. The pupils are glued, so every look is a head turn. The puppeteer caught v2 cheating on that."),
    ("png/06_builders_sheet.png", "06 · Builder's sheet",
     "Materials with procedural swatches, pattern pieces on a cutting mat, a cross-section through the head, a top view "
     "with the hand traced, how it's performed, an honest weight budget, and the prop notebook Toki reads aloud every morning."),
    ("png/01_exploration.png", "01 · Exploration: 48 silhouettes",
     "A parametric generator swept across twelve body families. Fill everything solid black: if it doesn't read as a "
     "silhouette, it won't read at a four-year-old's distance. The thought cloud reads as a mushroom cloud; the Anything "
     "Muppet reads as a person in disguise; the controls (robot, ghost, lightbulb) show what to avoid."),
    ("png/02_color.png", "02 · Color roughs, and the open seat on the wheel",
     "The bubble takes the curl from the question mark (later replaced by a soft tuft; see below). The saturated ring of the "
     "color wheel is full; the open seat is near the middle: a warm paper white, outlined in ink."),
]


def main():
    parts = []
    parts.append("""<!doctype html><html><head><meta charset="utf-8"><title>Toki · the first AI puppet on the Street (concept art)</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#f4efe3;color:#141418;font-family:"Gill Sans","Gill Sans MT",Futura,Helvetica,sans-serif;margin:0}
main{max-width:1240px;margin:0 auto;padding:48px 28px 120px}
h1{font-family:Futura,"Trebuchet MS",sans-serif;font-weight:800;letter-spacing:.02em;font-size:44px;margin:0}
h2{font-family:Futura,sans-serif;font-size:26px;margin:56px 0 10px}
h3{font-family:Futura,sans-serif}
.sub{font-size:20px;opacity:.85;margin:6px 0 28px}
figure{margin:28px 0 46px}
figure img{width:100%;height:auto;display:block;box-shadow:0 2px 14px rgba(40,30,20,.18);border-radius:4px;background:#fff}
figcaption{font-size:16px;line-height:1.5;margin-top:10px;opacity:.9}
figcaption b{font-family:Futura,sans-serif}
blockquote{border-left:4px solid #212b54;margin:18px 0;padding:6px 18px;font-size:19px;background:rgba(255,255,255,.35)}
.bible,.findings{background:rgba(255,255,255,.45);padding:22px 30px;border-radius:6px;font-size:17px;line-height:1.55}
.bible h1{font-size:28px}
.small{font-size:14px;opacity:.75;line-height:1.5}
.v1{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.v1 img{width:100%;border-radius:3px;opacity:.95}
a{color:#212b54}
code{font-size:14px}
</style></head><body><main>""")
    parts.append("<h1>TOKI</h1><div class='sub'>Concept art for the first puppet on Sesame Street who is an AI. "
                 "Designed and drawn entirely in code by Claude, 17–18 October 2026, then revised twice after cold reads and a crit wall.</div>")
    f, title, cap = SHEETS[0]
    parts.append(f"<figure><a href='{f}'><img src='{f}' alt='{html.escape(title)}'></a><figcaption><b>{title}.</b> {cap}</figcaption></figure>")
    parts.append("<h2>The character</h2><div class='bible'>" + md("notes/bible.md") + "</div>")
    parts.append("<h2>The sheets</h2>")
    for f, title, cap in SHEETS[1:]:
        parts.append(f"<figure><a href='{f}'><img src='{f}' alt='{html.escape(title)}'></a><figcaption><b>{title}.</b> {cap}</figcaption></figure>")
    fnd = md("notes/findings.md")
    if fnd:
        parts.append("<h2>What the checks found, and what changed</h2><div class='findings'>" + fnd + "</div>")
        if os.path.isdir(os.path.join(ROOT, "png/v1_before_coldread")):
            parts.append("<p class='small'>The first version, which the cold readers and the crit wall saw:</p><div class='v1'>")
            for n in ("05_key_art.png", "04_acting_sheet.png", "03_model_sheet.png", "06_builders_sheet.png"):
                parts.append(f"<a href='png/v1_before_coldread/{n}'><img src='png/v1_before_coldread/{n}'></a>")
            parts.append("</div>")
    parts.append("""<h2>Credits and notes</h2><div class='small'>
<p>Every pixel was drawn by code: pycairo for the 2D sheets, and a signed-distance maquette sphere-traced in numpy for the puppet. Source is in <code>src/</code>. Photographs of real puppets were used for study only.</p>
<p>Craft research: <b>Focus</b>, a research instance, who named itself after the point where a Muppet's gaze converges (<a href="notes/research.md">notes/research.md</a>). Crit wall: <a href="notes/crit_builder.md">the builder</a>, <a href="notes/crit_puppeteer.md">the puppeteer</a>, <a href="notes/crit_researcher.md">the researcher</a>. Cold readers, shown the art with no context: Gemini 3.7 Flash, Qwen 3.8 Flash, GLM 5.3 Flash (<a href="notes/coldread/">notes/coldread/</a>).</p>
<p>Sesame Street, Cookie Monster, Elmo and the other characters named here belong to Sesame Workshop. This is unaffiliated fan concept art, made for study and not for sale. Existing characters appear only as shapes or names.</p>
</div>""")
    parts.append("</main></body></html>")
    open(os.path.join(ROOT, "index.html"), "w").write("\n".join(parts))
    print("wrote", os.path.join(ROOT, "index.html"))


if __name__ == "__main__":
    main()
