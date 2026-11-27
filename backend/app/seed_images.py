"""Generates local, brand-coloured product illustrations (SVG) so demo listings always show a
relevant image without network access. Output: backend/static/seed/<slug>.svg"""
from pathlib import Path
STATIC = Path(__file__).resolve().parents[1] / "static" / "seed"
P, D, Y, W = "#5421A8", "#35106F", "#FFD84D", "#FFFFFF"
keys = "".join(f'<path d="M{x} 330 V420" fill="none"/>' for x in range(230, 630, 60))
black = "".join(f'<rect x="{x}" y="250" width="30" height="95" rx="5" fill="{D}"/>' for x in (215, 275, 395, 455, 515))
GLYPHS = {
 "guitar": f'<g transform="rotate(35 400 300)"><rect x="384" y="70" width="32" height="200" rx="6" fill="{D}"/><rect x="375" y="40" width="50" height="50" rx="10" fill="{Y}"/><circle cx="400" cy="300" r="62" fill="{P}"/><circle cx="400" cy="385" r="90" fill="{P}"/><circle cx="400" cy="350" r="26" fill="{D}"/><rect x="372" y="415" width="56" height="12" rx="5" fill="{Y}"/></g>',
 "camera": f'<rect x="330" y="165" width="90" height="50" rx="10" fill="{Y}"/><rect x="240" y="200" width="320" height="210" rx="28" fill="{P}"/><circle cx="400" cy="305" r="78" fill="{W}"/><circle cx="400" cy="305" r="44" fill="{D}"/><circle cx="385" cy="290" r="10" fill="{W}" stroke="none"/><rect x="480" y="225" width="50" height="26" rx="6" fill="{Y}"/>',
 "bike": f'<circle cx="270" cy="370" r="85" fill="none"/><circle cx="530" cy="370" r="85" fill="none"/><path d="M270 370 L370 250 L490 250 L530 370 M370 250 L410 370 L270 370 M410 370 L490 250" fill="none"/><path d="M490 250 L470 200 L520 200 M340 235 L400 235" fill="none"/><circle cx="410" cy="370" r="14" fill="{Y}"/>',
 "books": f'<rect x="230" y="390" width="340" height="56" rx="8" fill="{P}"/><rect x="250" y="330" width="300" height="56" rx="8" fill="{Y}"/><rect x="270" y="270" width="260" height="56" rx="8" fill="{W}"/><path d="M300 400 v36 M300 340 v36 M320 280 v36" fill="none"/>',
 "headphones": f'<path d="M280 350 C280 170 520 170 520 350" fill="none" stroke-width="20"/><rect x="250" y="330" width="62" height="120" rx="28" fill="{P}"/><rect x="488" y="330" width="62" height="120" rx="28" fill="{P}"/><rect x="262" y="360" width="20" height="60" rx="10" fill="{Y}" stroke="none"/><rect x="518" y="360" width="20" height="60" rx="10" fill="{Y}" stroke="none"/>',
 "jacket": f'<path d="M330 150 L255 190 L205 385 L270 400 L292 290 L292 445 L508 445 L508 290 L530 400 L595 385 L545 190 L470 150 L400 215 Z" fill="{P}"/><path d="M400 215 V445" fill="none" stroke="{Y}"/>',
 "keyboard": f'<rect x="170" y="250" width="460" height="170" rx="16" fill="{W}"/>{keys}{black}',
 "cooker": f'<rect x="250" y="215" width="300" height="50" rx="24" fill="{Y}"/><rect x="270" y="255" width="260" height="190" rx="28" fill="{P}"/><rect x="215" y="310" width="55" height="26" rx="10" fill="{D}"/><rect x="530" y="310" width="55" height="26" rx="10" fill="{D}"/><rect x="335" y="320" width="130" height="50" rx="10" fill="{W}"/><circle cx="360" cy="410" r="10" fill="{Y}"/><circle cx="440" cy="410" r="10" fill="{Y}"/>',
 "treadmill": f'<path d="M190 430 L560 430 L600 390 L250 390 Z" fill="{P}"/><rect x="190" y="430" width="370" height="26" rx="8" fill="{D}"/><path d="M540 400 L500 200" fill="none" stroke-width="16"/><rect x="440" y="150" width="130" height="62" rx="12" fill="{Y}"/><path d="M440 190 H350" fill="none"/>',
 "watch": f'<rect x="345" y="110" width="110" height="380" rx="40" fill="{D}"/><rect x="290" y="195" width="220" height="210" rx="56" fill="{W}"/><path d="M400 300 V240 M400 300 L445 325" fill="none"/><rect x="510" y="270" width="18" height="50" rx="8" fill="{Y}"/>',
 "sunglasses": f'<rect x="215" y="260" width="150" height="110" rx="45" fill="{D}"/><rect x="435" y="260" width="150" height="110" rx="45" fill="{D}"/><path d="M365 290 Q400 265 435 290 M215 285 L170 265 M585 285 L630 265" fill="none"/><path d="M245 290 l40 -12" fill="none" stroke="{W}"/>',
 "sneakers": f'<path d="M200 410 V290 Q255 295 300 245 L360 290 L500 325 Q610 345 610 410 Z" fill="{P}"/><rect x="190" y="410" width="430" height="34" rx="17" fill="{W}"/><path d="M330 285 L360 325 M365 300 L395 335 M400 312 L428 345" fill="none" stroke="{Y}"/>',
 "boardgames": f'<rect x="220" y="200" width="360" height="240" rx="18" fill="{P}"/><rect x="220" y="200" width="360" height="60" rx="18" fill="{Y}"/><rect x="290" y="300" width="90" height="90" rx="16" fill="{W}"/><circle cx="315" cy="325" r="8" fill="{D}"/><circle cx="335" cy="345" r="8" fill="{D}"/><circle cx="355" cy="365" r="8" fill="{D}"/><circle cx="470" cy="345" r="36" fill="{W}"/>',
 "tablet": f'<rect x="200" y="160" width="400" height="290" rx="26" fill="{D}"/><rect x="225" y="185" width="350" height="240" rx="10" fill="{W}"/><path d="M270 380 C330 250 400 400 470 260" fill="none" stroke="{P}" stroke-width="12"/><path d="M640 190 L560 420" fill="none" stroke="{Y}" stroke-width="16"/>',
 "airfryer": f'<rect x="270" y="150" width="260" height="300" rx="70" fill="{P}"/><circle cx="400" cy="235" r="36" fill="{W}"/><path d="M400 235 L420 215" fill="none"/><rect x="310" y="320" width="180" height="90" rx="22" fill="{D}"/><rect x="530" y="355" width="60" height="22" rx="10" fill="{Y}"/>',
 "pots": f'<ellipse cx="280" cy="320" rx="24" ry="52" fill="#7DC383"/><ellipse cx="440" cy="290" rx="26" ry="58" fill="#7DC383"/><ellipse cx="605" cy="350" rx="20" ry="42" fill="#7DC383"/><path d="M215 380 H345 L328 470 H232 Z" fill="{Y}"/><path d="M360 340 H520 L498 470 H382 Z" fill="{P}"/><path d="M560 400 H650 L638 470 H572 Z" fill="{W}"/>',
 "placeholder": f'<rect x="260" y="240" width="280" height="200" rx="16" fill="{P}"/><rect x="245" y="195" width="310" height="60" rx="14" fill="{Y}"/><path d="M400 195 V440" fill="none"/>',
}
def svg(glyph: str, label: str) -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img"><title>' + label + '</title>'
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F3ECFF"/><stop offset="1" stop-color="#FFF4C2"/></linearGradient></defs>'
      '<rect width="800" height="600" fill="url(#g)"/><circle cx="400" cy="300" r="230" fill="#fff" opacity=".55"/>'
      f'<g stroke="{D}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">{glyph}</g></svg>')
def generate() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)
    for slug, glyph in GLYPHS.items(): (STATIC / f"{slug}.svg").write_text(svg(glyph, slug), encoding="utf-8")