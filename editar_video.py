"""
Edición completa del VIDEO 1 WHATSAPP:
1. Elimina silencios > 0.4s
2. Agrega subtítulos llamativos (drawtext, estilo reel)
3. Inserta tomas de apoyo gráficas animadas en momentos clave
"""

import subprocess, os, re, json, textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio, numpy as np

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
INPUT  = "/home/user/edicion-de-contenido-/VIDEO1_WHATSAPP.mp4"
WORK   = "/home/user/edicion-de-contenido-/work"
OUTPUT = "/home/user/edicion-de-contenido-/VIDEO1_EDITADO.mp4"
os.makedirs(WORK, exist_ok=True)

W, H, FPS = 1080, 1920, 29.97

# ─── helpers ──────────────────────────────────────────────────────────────────
def run(cmd, **kw):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-800:])
    return r.stdout + r.stderr

def load_font(size, bold=False):
    for p in [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ══════════════════════════════════════════════════════════════════════════════
# PASO 1 — Detectar y eliminar silencios
# ══════════════════════════════════════════════════════════════════════════════
print("🔍 Detectando silencios...")
raw = run(f'{FFMPEG} -i "{INPUT}" -af "silencedetect=noise=-35dB:d=0.4" -f null - 2>&1')

# Parse silence intervals
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", raw)]
ends   = [float(x) for x in re.findall(r"silence_end: ([\d.]+)",   raw)]
duration = 300.57  # 5:00.57

# Build kept segments (non-silent parts, trim silence to 0.15s gap)
GAP = 0.15  # keep tiny natural pause
segments = []
cursor = 0.0
for s, e in zip(starts, ends):
    if s > cursor:
        segments.append((cursor, s))
    cursor = max(cursor, e - GAP)
if cursor < duration:
    segments.append((cursor, duration))

print(f"   {len(segments)} segmentos de voz | duración estimada: {sum(e-s for s,e in segments):.1f}s")

# Write concat file
concat_file = f"{WORK}/concat.txt"
seg_files   = []
for i, (s, e) in enumerate(segments):
    seg = f"{WORK}/seg{i:04d}.mp4"
    seg_files.append(seg)
    run(f'{FFMPEG} -y -ss {s:.4f} -to {e:.4f} -i "{INPUT}" '
        f'-c:v libx264 -preset ultrafast -crf 18 -c:a aac -b:a 160k "{seg}"')

with open(concat_file, "w") as f:
    for seg in seg_files:
        f.write(f"file '{seg}'\n")

no_silence = f"{WORK}/no_silence.mp4"
print("✂️  Concatenando segmentos sin silencio...")
run(f'{FFMPEG} -y -f concat -safe 0 -i "{concat_file}" '
    f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{no_silence}"')
print("   ✅ Silencios eliminados")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 2 — Generar tomas de apoyo (motion graphics)
# ══════════════════════════════════════════════════════════════════════════════
print("🎨 Generando tomas de apoyo...")

BG   = (10, 10, 20)
GREEN= (0, 230, 120)
RED  = (255, 60, 80)
GOLD = (255, 200, 0)
WHITE= (255, 255, 255)
GRAY = (160, 160, 180)
CARD = (20, 22, 40)

def grad_frame(c1=BG, c2=(5,15,35)):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        d.line([(0,y),(W,y)], fill=tuple(int(c1[k]+(c2[k]-c1[k])*t) for k in range(3)))
    return img

def pill(d, x, y, w, h, col, r=28):
    d.rounded_rectangle([x,y,x+w,y+h], radius=r, fill=col)

def make_broll_fecha(fecha, titulo, desc, color, frame_idx, total_frames):
    """Animated card: slides in from bottom"""
    img = grad_frame()
    d   = ImageDraw.Draw(img)
    # grid
    for x in range(0,W,80): d.line([(x,0),(x,H)], fill=(255,255,255,6))
    for y in range(0,H,80): d.line([(0,y),(W,y)], fill=(255,255,255,6))
    d.rectangle([0,0,W,6], fill=color)
    d.rectangle([0,H-6,W,H], fill=color)

    progress = min(1.0, frame_idx / (total_frames * 0.3))
    ease = 1 - (1 - progress)**3
    card_y = int(H*0.2 + (1-ease)*H*0.6)

    pill(d, 60, card_y, W-120, 480, CARD, 36)
    # date badge
    pill(d, 90, card_y+30, 340, 80, color, 40)
    d.text((110, card_y+42), fecha, font=load_font(44, bold=True), fill=(10,10,10))
    # title
    d.text((90, card_y+130), titulo, font=load_font(58, bold=True), fill=WHITE)
    # desc lines
    y2 = card_y + 210
    for line in textwrap.wrap(desc, width=26):
        d.text((90, y2), line, font=load_font(44), fill=GRAY)
        y2 += 56
    # icon
    d.text((W-180, card_y+160), "📅", font=load_font(100), fill=color)
    # neurochat tag
    pill(d, 80, H-160, 300, 65, (20,50,30), 33)
    d.text((110, H-148), "@neurochat", font=load_font(34, bold=True), fill=GREEN)
    return np.array(img.convert("RGB"))

def make_broll_precio(frame_idx, total_frames):
    """Price comparison animation"""
    img = grad_frame((5, 5, 15), (15, 5, 30))
    d   = ImageDraw.Draw(img)
    for x in range(0,W,80): d.line([(x,0),(x,H)], fill=(255,255,255,5))
    d.rectangle([0,0,W,6], fill=GOLD)
    d.rectangle([0,H-6,W,H], fill=GOLD)

    progress = min(1.0, frame_idx / (total_frames * 0.35))
    ease = 1 - (1-progress)**3

    d.text((80, 120), "💸  COSTO REAL", font=load_font(56, bold=True), fill=GOLD)
    d.text((80, 190), "por país", font=load_font(48), fill=GRAY)
    d.rectangle([80, 250, W-80, 254], fill=GOLD)

    paises = [
        ("🇨🇴 Colombia",  "$28/mes",   GREEN,  1.0),
        ("🇨🇱 Chile",     "5x más",    GOLD,   0.85),
        ("🇦🇷 Argentina", "10x más",   RED,    0.7),
        ("🇵🇪 Perú",      "hasta 30x", RED,    0.55),
    ]
    y = 300
    for flag, val, col, delay in paises:
        p2 = min(1.0, max(0.0, (ease - (1-delay)) / delay))
        e2 = 1 - (1-p2)**2
        xoff = int((1-e2) * W * 0.6)
        pill(d, 60+xoff, y, W-120, 100, CARD, 22)
        d.text((90+xoff, y+20), flag, font=load_font(44, bold=True), fill=WHITE)
        bbox = d.textbbox((0,0), val, font=load_font(50, bold=True))
        d.text((W-120-bbox[2]+xoff, y+18), val, font=load_font(50, bold=True), fill=col)
        y += 120

    d.text((80, y+30), "1.500 conv · 23 msg/conv", font=load_font(38), fill=GRAY)
    pill(d, 80, H-160, 300, 65, (20,50,30), 33)
    d.text((110, H-148), "@neurochat", font=load_font(34, bold=True), fill=GREEN)
    return np.array(img.convert("RGB"))

def make_broll_warning(frame_idx, total_frames):
    """Animated warning: NO AVISO MASIVO"""
    img = grad_frame((20, 5, 5), (10, 10, 20))
    d   = ImageDraw.Draw(img)
    d.rectangle([0,0,W,6], fill=RED)
    d.rectangle([0,H-6,W,H], fill=RED)

    progress = min(1.0, frame_idx / (total_frames * 0.4))
    ease = 1-(1-progress)**3
    alpha_scale = ease

    # big warning
    y_base = int(H*0.15 + (1-ease)*200)
    d.text((W//2-120, y_base), "⚠️", font=load_font(220), fill=RED)

    items = ["❌  Sin aviso masivo", "❌  Sin campaña", "❌  Sin correo", "✅  Solo en docs técnicos"]
    colors = [RED, RED, RED, GREEN]
    y2 = y_base + 280
    for i, (item, col) in enumerate(zip(items, colors)):
        p3 = min(1.0, max(0.0, ease*4 - i))
        e3 = 1-(1-min(1,p3))**2
        xoff = int((1-e3)*W*0.7)
        d.text((80+xoff, y2), item, font=load_font(50, bold=True), fill=col)
        y2 += 80

    pill(d, 80, H-160, 300, 65, (20,50,30), 33)
    d.text((110, H-148), "@neurochat", font=load_font(34, bold=True), fill=GREEN)
    return np.array(img.convert("RGB"))

# Generate b-roll video files
BROLL_FPS = 30
broll_specs = [
    ("broll_fecha1.mp4", "make_broll_fecha", ("1 AGO 2026", "Meta Business Agent", "Cobran por tokens. ~4-5¢ USD por conversación típica.", RED), 5),
    ("broll_fecha2.mp4", "make_broll_fecha", ("1 OCT 2026", "Mensajes de Servicio", "Las respuestas automáticas dentro de ventana 24h dejan de ser GRATIS.", GOLD), 5),
    ("broll_fecha3.mp4", "make_broll_fecha", ("1 OCT 2026", "Mensajes de Utilidad", "Gratis desde jul/2025. Desde octubre: cobrados.", (255,140,0)), 5),
    ("broll_precio.mp4", "make_broll_precio", None, 6),
    ("broll_warning.mp4", "make_broll_warning", None, 5),
]

fn_map = {
    "make_broll_fecha": make_broll_fecha,
    "make_broll_precio": make_broll_precio,
    "make_broll_warning": make_broll_warning,
}

broll_paths = {}
for fname, fn_name, args, secs in broll_specs:
    path = f"{WORK}/{fname}"
    broll_paths[fname] = path
    n = secs * BROLL_FPS
    writer = imageio.get_writer(path, fps=BROLL_FPS, codec="libx264", quality=9,
                                macro_block_size=None,
                                output_params=["-pix_fmt","yuv420p","-crf","18"])
    fn = fn_map[fn_name]
    for i in range(n):
        if args:
            frame = fn(*args, i, n)
        else:
            frame = fn(i, n)
        writer.append_data(frame)
    writer.close()
    # add silent audio track
    with_audio = path.replace(".mp4", "_a.mp4")
    run(f'{FFMPEG} -y -i "{path}" -f lavfi -i anullsrc=r=48000:cl=stereo '
        f'-c:v copy -c:a aac -b:a 128k -shortest "{with_audio}"')
    broll_paths[fname] = with_audio
    print(f"   ✅ {fname}")

print("🎨 Tomas de apoyo generadas")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 3 — Subtítulos llamativos
# ══════════════════════════════════════════════════════════════════════════════
print("📝 Creando subtítulos...")

# Script-based subtitle file (timed to estimated positions after silence removal)
# Approx new duration ~270s after silence removal
# These are approximate - based on the script sections
subtitles = [
    (0.0,   4.0,  "Todo negocio que usa WhatsApp\ncon automatizaciones..."),
    (4.0,   7.5,  "...va a recibir una\nFACTURA que no esperaba ⚠️"),
    (8.0,   13.0, "Meta publicó un cambio de precios\nsin aviso masivo"),
    (13.0,  18.0, "Sin campaña. Sin correo.\nSolo en su página de desarrolladores."),
    (19.0,  24.0, "3 fechas que te van a afectar\nsi tienes automatizaciones activas 📅"),
    (25.0,  31.0, "1 AGO 2026 →\nMeta Business Agent: COBRADO 💸"),
    (31.0,  38.0, "Conversación típica:\n~4 a 5 centavos de dólar"),
    (39.0,  46.0, "1 OCT 2026 →\nMensajes de Servicio: COBRADO 💸"),
    (46.0,  54.0, "1 OCT 2026 →\nMensajes de Utilidad: COBRADO 💸"),
    (55.0,  62.0, "¿Cuánto significa eso?\nDepende de tu país y volumen 🌎"),
    (63.0,  70.0, "E-commerce · 1.500 conversaciones/mes\n23 mensajes por conversación"),
    (71.0,  77.0, "Colombia → ~$28 USD/mes 🇨🇴"),
    (78.0,  85.0, "Chile · Argentina · Perú\n→ de 5x a 30x MÁS 🔥"),
    (86.0,  95.0, "El problema no es el monto.\nEs no tener un sistema eficiente."),
    (96.0,  103.0,"Cada mensaje sin respuesta\ninteligente es dinero que se va 💸"),
    (104.0, 113.0,"Sígueme. En la parte 2 te muestro\ncómo estructuramos la estrategia"),
    (114.0, 122.0,"Para que nuestros clientes sean\nlos MÁS RENTABLES del nuevo modelo"),
    (123.0, 130.0,"@neurochat 🤖\nAutomatización inteligente"),
]

# Write SRT
srt_path = f"{WORK}/subtitulos.srt"
def ts(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".",",")

with open(srt_path, "w") as f:
    for i, (start, end, text) in enumerate(subtitles, 1):
        f.write(f"{i}\n{ts(start)} --> {ts(end)}\n{text}\n\n")

print("   ✅ SRT generado")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 4 — Burn subtítulos sobre video sin silencios
# ══════════════════════════════════════════════════════════════════════════════
print("🔥 Quemando subtítulos en el video...")

font_path = ""
for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
    if os.path.exists(p):
        font_path = p
        break

subtitled = f"{WORK}/with_subs.mp4"

# Style: white bold text with black outline + semi-transparent green bg bar
sub_filter = (
    f"subtitles={srt_path}:force_style='"
    f"FontName=DejaVu Sans Bold,"
    f"FontSize=22,"
    f"PrimaryColour=&H00FFFFFF,"
    f"OutlineColour=&H00000000,"
    f"BackColour=&H99000000,"
    f"Bold=1,"
    f"Outline=3,"
    f"Shadow=2,"
    f"Alignment=2,"
    f"MarginV=120,"
    f"BorderStyle=4'"
)

run(f'{FFMPEG} -y -i "{no_silence}" '
    f'-vf "{sub_filter}" '
    f'-c:v libx264 -preset fast -crf 18 -c:a copy "{subtitled}"')
print("   ✅ Subtítulos aplicados")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 5 — Insertar tomas de apoyo en momentos clave
# ══════════════════════════════════════════════════════════════════════════════
print("🎬 Insertando tomas de apoyo...")

# Insert b-rolls at approximate timestamps in the edited video
# warning at ~12s, fechas at ~25s/36s/46s, precio at ~62s
inserts = [
    (12.0,  broll_paths["broll_warning.mp4"]),
    (27.0,  broll_paths["broll_fecha1.mp4"]),
    (38.0,  broll_paths["broll_fecha2.mp4"]),
    (49.0,  broll_paths["broll_fecha3.mp4"]),
    (63.0,  broll_paths["broll_precio.mp4"]),
]

# Build a concat list: split main video around insertions
prev_end = 0.0
final_segments = []

for ins_time, broll_path in inserts:
    # Segment before insert
    if ins_time > prev_end:
        seg = f"{WORK}/final_seg_{len(final_segments):03d}.mp4"
        run(f'{FFMPEG} -y -ss {prev_end:.4f} -to {ins_time:.4f} -i "{subtitled}" '
            f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{seg}"')
        final_segments.append(seg)
    # B-roll
    final_segments.append(broll_path)
    prev_end = ins_time  # resume main video after b-roll ends

# Remaining main video
seg = f"{WORK}/final_seg_{len(final_segments):03d}.mp4"
run(f'{FFMPEG} -y -ss {prev_end:.4f} -i "{subtitled}" '
    f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{seg}"')
final_segments.append(seg)

# Final concat
final_concat = f"{WORK}/final_concat.txt"
with open(final_concat, "w") as f:
    for s in final_segments:
        f.write(f"file '{s}'\n")

run(f'{FFMPEG} -y -f concat -safe 0 -i "{final_concat}" '
    f'-c:v libx264 -preset medium -crf 18 -c:a aac -b:a 160k '
    f'-pix_fmt yuv420p "{OUTPUT}"')

print(f"\n✅ Video final: {OUTPUT}")
r = run(f'{FFMPEG} -i "{OUTPUT}" 2>&1')
for line in r.split("\n"):
    if "Duration" in line or "Stream" in line:
        print(" ", line.strip())
