import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

FFMPEG = imageio.plugins.ffmpeg.get_exe()
os.environ["PATH"] = os.path.dirname(FFMPEG) + ":" + os.environ.get("PATH", "")

W, H = 1080, 1920  # vertical reel format
FPS = 30

# ─── Color palette ───────────────────────────────────────────────────────────
BG_DARK      = (10, 10, 20)
ACCENT_GREEN = (0, 230, 120)
ACCENT_RED   = (255, 60, 80)
ACCENT_GOLD  = (255, 200, 0)
WHITE        = (255, 255, 255)
GRAY         = (160, 160, 180)
CARD_BG      = (20, 22, 40)
OVERLAY      = (0, 0, 0, 180)

def load_font(size, bold=False):
    paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_gradient_bg(img, color1=BG_DARK, color2=(5, 15, 35)):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

def draw_grid_lines(draw):
    for x in range(0, W, 80):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
    for y in range(0, H, 80):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)

def draw_centered_text(draw, text, y, font, color=WHITE, max_width=900):
    lines = textwrap.wrap(text, width=32)
    line_h = font.size + 10
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y + i * line_h), line, font=font, fill=color)
    return len(lines) * line_h

def draw_pill(draw, x, y, w, h, color, radius=30):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=color)

def make_base_frame():
    img = Image.new("RGB", (W, H))
    draw_gradient_bg(img)
    draw = ImageDraw.Draw(img)
    draw_grid_lines(draw)
    # top bar
    draw.rectangle([0, 0, W, 6], fill=ACCENT_GREEN)
    # bottom bar
    draw.rectangle([0, H-6, W, H], fill=ACCENT_GREEN)
    return img, draw

def frame_to_array(img):
    return np.array(img.convert("RGB"))

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════

def slide_gancho():
    img, draw = make_base_frame()
    f_big  = load_font(90, bold=True)
    f_med  = load_font(58, bold=True)
    f_sub  = load_font(42)

    # Big warning icon
    draw_pill(draw, W//2-90, 220, 180, 180, ACCENT_RED, 90)
    draw.text((W//2-52, 252), "⚠", font=load_font(100, bold=True), fill=WHITE)

    draw.text((80, 450), "ATENCIÓN", font=f_big, fill=ACCENT_RED)
    draw.text((80, 560), "NEGOCIOS CON", font=f_med, fill=WHITE)
    draw.text((80, 630), "WHATSAPP", font=f_big, fill=ACCENT_GREEN)

    lines = textwrap.wrap("Todo negocio que hoy usa WhatsApp con automatizaciones va a recibir una factura que no esperaba.", width=28)
    y = 770
    f_q = load_font(46)
    for line in lines:
        draw.text((80, y), line, font=f_q, fill=(220, 220, 220))
        y += 58

    draw.text((80, y + 20), "Esta es la noticia.", font=load_font(50, bold=True), fill=ACCENT_GOLD)

    # Meta logo placeholder
    draw_pill(draw, 80, H-220, 200, 70, (40, 40, 60), 35)
    draw.text((110, H-210), "META  📢", font=load_font(36, bold=True), fill=ACCENT_GREEN)

    draw.text((80, H-120), "@neurochat", font=load_font(38, bold=True), fill=ACCENT_GREEN)
    return img

def slide_contexto():
    img, draw = make_base_frame()
    f_title = load_font(70, bold=True)
    f_body  = load_font(44)
    f_tag   = load_font(36, bold=True)

    draw_pill(draw, 80, 100, 340, 70, (30, 60, 30), 35)
    draw.text((120, 112), "CONTEXTO", font=f_tag, fill=ACCENT_GREEN)

    draw.text((80, 210), "Meta publicó un", font=f_title, fill=WHITE)
    draw.text((80, 295), "CAMBIO DE", font=load_font(80, bold=True), fill=ACCENT_RED)
    draw.text((80, 385), "PRECIOS", font=load_font(80, bold=True), fill=ACCENT_RED)

    # card
    draw_pill(draw, 60, 510, W-120, 420, CARD_BG, 30)
    body = "Meta actualizó su documentación oficial de WhatsApp Business sin aviso masivo, sin campaña, sin correo a los negocios.\n\nSolo lo publicó en su página de desarrolladores y asumió que tú lo ibas a leer."
    y = 540
    for para in body.split("\n\n"):
        lines = textwrap.wrap(para, width=30)
        for line in lines:
            draw.text((90, y), line, font=f_body, fill=(210, 210, 230))
            y += 56
        y += 20

    # WhatsApp icon area
    draw_pill(draw, W//2-120, 980, 240, 240, (0, 150, 60), 120)
    draw.text((W//2-70, 1030), "💬", font=load_font(120), fill=WHITE)

    draw.text((80, 1270), "Sin aviso.", font=load_font(64, bold=True), fill=ACCENT_GOLD)
    draw.text((80, 1350), "Sin campaña.", font=load_font(64, bold=True), fill=ACCENT_GOLD)
    draw.text((80, 1430), "Sin correo.", font=load_font(64, bold=True), fill=ACCENT_GOLD)

    draw.text((80, H-120), "@neurochat", font=load_font(38, bold=True), fill=ACCENT_GREEN)
    return img

def slide_golpes():
    img, draw = make_base_frame()
    f_title = load_font(68, bold=True)
    f_date  = load_font(54, bold=True)
    f_body  = load_font(38)
    f_tag   = load_font(34, bold=True)

    draw_pill(draw, 80, 80, 380, 70, (60, 20, 20), 35)
    draw.text((120, 92), "3 GOLPES  🥊", font=f_tag, fill=ACCENT_RED)

    draw.text((80, 185), "Las fechas que", font=f_title, fill=WHITE)
    draw.text((80, 265), "te afectan", font=f_title, fill=ACCENT_RED)

    golpes = [
        {
            "num": "01",
            "fecha": "1 AGO 2026",
            "titulo": "Meta Business Agent",
            "desc": "Pagas por tokens. ~4-5¢ USD por conversación.",
            "color": ACCENT_RED,
        },
        {
            "num": "02",
            "fecha": "1 OCT 2026",
            "titulo": "Mensajes de Servicio",
            "desc": "Respuestas automáticas 24h dejan de ser GRATIS.",
            "color": ACCENT_GOLD,
        },
        {
            "num": "03",
            "fecha": "1 OCT 2026",
            "titulo": "Mensajes de Utilidad",
            "desc": "Dentro de ventana 24h: gratis desde jul/25. Ahora cobrados.",
            "color": (255, 140, 0),
        },
    ]

    y = 370
    for g in golpes:
        draw_pill(draw, 60, y, W-120, 155, CARD_BG, 22)
        # number badge
        draw_pill(draw, 75, y+18, 72, 72, g["color"], 36)
        draw.text((95, y+24), g["num"], font=load_font(40, bold=True), fill=(10,10,10))
        # date
        draw.text((165, y+18), g["fecha"], font=f_date, fill=g["color"])
        # title
        draw.text((165, y+72), g["titulo"], font=load_font(36, bold=True), fill=WHITE)
        # desc
        lines = textwrap.wrap(g["desc"], width=36)
        for i, line in enumerate(lines):
            draw.text((165, y+110 + i*36), line, font=load_font(30), fill=GRAY)
        y += 175

    draw.text((80, H-120), "@neurochat", font=load_font(38, bold=True), fill=ACCENT_GREEN)
    return img

def slide_impacto():
    img, draw = make_base_frame()
    f_title = load_font(68, bold=True)
    f_num   = load_font(110, bold=True)
    f_body  = load_font(40)
    f_tag   = load_font(34, bold=True)

    draw_pill(draw, 80, 80, 380, 70, (20, 50, 80), 35)
    draw.text((120, 92), "IMPACTO REAL  💸", font=f_tag, fill=ACCENT_GOLD)

    draw.text((80, 185), "¿Cuánto es en", font=f_title, fill=WHITE)
    draw.text((80, 265), "tu bolsillo?", font=f_title, fill=ACCENT_GOLD)

    # example card
    draw_pill(draw, 60, 370, W-120, 300, CARD_BG, 28)
    draw.text((90, 390), "E-commerce ejemplo:", font=load_font(36, bold=True), fill=GRAY)
    draw.text((90, 440), "1.500 conv/mes · 23 msg/conv", font=load_font(38), fill=WHITE)
    draw.text((90, 495), "Colombia →", font=load_font(44, bold=True), fill=WHITE)
    draw.text((400, 488), "~$28 USD/mes", font=load_font(50, bold=True), fill=ACCENT_GREEN)
    draw.text((90, 560), "Chile · Argentina · Perú →", font=load_font(38, bold=True), fill=WHITE)
    draw.text((90, 608), "5x a 30x MÁS", font=load_font(52, bold=True), fill=ACCENT_RED)

    # divider
    draw.rectangle([80, 710, W-80, 714], fill=ACCENT_GREEN)

    draw.text((80, 740), "El problema no es", font=load_font(52, bold=True), fill=WHITE)
    draw.text((80, 808), "solo el monto.", font=load_font(52, bold=True), fill=ACCENT_RED)

    lines = textwrap.wrap("Si no tienes un sistema eficiente, estás pagando por conversaciones que no convierten nada. Cada mensaje sin respuesta inteligente es dinero que se va.", width=28)
    y = 900
    for line in lines:
        draw.text((80, y), line, font=f_body, fill=(210, 210, 230))
        y += 54

    # money emoji row
    draw.text((80, y+30), "💸 💸 💸", font=load_font(80), fill=ACCENT_GOLD)

    draw.text((80, H-120), "@neurochat", font=load_font(38, bold=True), fill=ACCENT_GREEN)
    return img

def slide_cta():
    img, draw = make_base_frame()
    f_title = load_font(72, bold=True)
    f_body  = load_font(44)
    f_tag   = load_font(34, bold=True)

    # top decoration
    draw_pill(draw, 80, 80, 280, 70, (20, 60, 40), 35)
    draw.text((120, 92), "PARTE 2  👇", font=f_tag, fill=ACCENT_GREEN)

    draw.text((80, 195), "Sígueme.", font=load_font(100, bold=True), fill=ACCENT_GREEN)

    lines = textwrap.wrap("En la parte 2 te muestro cómo en Neurochat estructuramos la estrategia para que nuestros clientes sean los más rentables dentro del nuevo modelo de Meta.", width=27)
    y = 350
    for line in lines:
        draw.text((80, y), line, font=f_body, fill=(220, 220, 240))
        y += 58

    draw.rectangle([80, y+20, W-80, y+24], fill=ACCENT_GREEN)

    draw.text((80, y+50), "¿Qué verás?", font=load_font(56, bold=True), fill=ACCENT_GOLD)

    puntos = [
        "✅  Estructura de automatización rentable",
        "✅  Cómo reducir conversaciones pagadas",
        "✅  Estrategia Neurochat paso a paso",
    ]
    y2 = y + 125
    for p in puntos:
        draw.text((80, y2), p, font=load_font(40, bold=True), fill=WHITE)
        y2 += 66

    # brand card
    draw_pill(draw, 60, y2+30, W-120, 200, CARD_BG, 28)
    draw.text((W//2-200, y2+55), "🤖  NEUROCHAT", font=load_font(58, bold=True), fill=ACCENT_GREEN)
    draw.text((W//2-260, y2+125), "Automatización inteligente", font=load_font(40), fill=GRAY)

    draw.text((80, H-130), "Síguenos →", font=load_font(46, bold=True), fill=WHITE)
    draw.text((340, H-130), "@neurochat", font=load_font(46, bold=True), fill=ACCENT_GREEN)
    return img

# ═══════════════════════════════════════════════════════════════════════════
# BUILD VIDEO
# ═══════════════════════════════════════════════════════════════════════════

slides_config = [
    (slide_gancho,   6),   # seconds
    (slide_contexto, 7),
    (slide_golpes,   10),
    (slide_impacto,  9),
    (slide_cta,      7),
]

output_path = "/home/user/edicion-de-contenido-/reel_neurochat_whatsapp.mp4"

ffmpeg_bin = FFMPEG
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_bin
writer = imageio.get_writer(
    output_path,
    fps=FPS,
    codec="libx264",
    quality=9,
    ffmpeg_log_level="error",
    macro_block_size=None,
    output_params=["-pix_fmt", "yuv420p", "-crf", "18"],
)

print("Generando slides...")
total_frames = sum(sec * FPS for _, sec in slides_config)
written = 0

for fn, secs in slides_config:
    print(f"  → {fn.__name__} ({secs}s)...")
    slide_img = fn()
    frame = frame_to_array(slide_img)
    n_frames = secs * FPS
    for _ in range(n_frames):
        writer.append_data(frame)
    written += n_frames

writer.close()
print(f"\n✅ Video listo: {output_path}")
print(f"   Frames: {written}  |  Duración: {written/FPS:.1f}s  |  Formato: 1080×1920 vertical")
