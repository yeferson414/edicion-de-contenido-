"""
Editor estilo Alex Hormozi — calculadora WhatsApp
- Elimina silencios > 0.35s
- Speed 1.1x
- Subtítulos centrados (zona media, no tapan pantalla dividida)
- Motion graphics Hormozi: texto bold amarillo, números grandes, golpes visuales
"""

import subprocess, os, re, textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio, numpy as np

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
INPUT  = "/home/user/edicion-de-contenido-/calculadora_whatsapp.mp4"
WORK   = "/home/user/edicion-de-contenido-/work2"
OUTPUT = "/home/user/edicion-de-contenido-/CALCULADORA_EDITADO.mp4"
os.makedirs(WORK, exist_ok=True)

W, H, FPS = 1080, 1920, 29.97

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0 and "Error" in r.stderr:
        print("  STDERR:", r.stderr[-500:])
    return r.stdout + r.stderr

def load_font(size, bold=False):
    for p in [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
    ]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ══════════════════════════════════════════════════════════════════════════════
# PASO 1 — Silences → cut → speed 1.1x
# ══════════════════════════════════════════════════════════════════════════════
print("🔍 Detectando silencios...")
raw = run(f'{FFMPEG} -i "{INPUT}" -af "silencedetect=noise=-33dB:d=0.35" -f null - 2>&1')

starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", raw)]
ends   = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", raw)]
duration = 162.86

GAP = 0.12
segments = []
cursor = 0.0
for s, e in zip(starts, ends):
    if s > cursor + 0.05:
        segments.append((cursor, s))
    cursor = max(cursor, e - GAP)
if cursor < duration:
    segments.append((cursor, duration))

print(f"   {len(segments)} segmentos | ~{sum(e-s for s,e in segments):.1f}s antes de speed")

# Cut segments
concat_f = f"{WORK}/concat.txt"
seg_files = []
for i, (s, e) in enumerate(segments):
    seg = f"{WORK}/seg{i:04d}.mp4"
    seg_files.append(seg)
    run(f'{FFMPEG} -y -ss {s:.4f} -to {e:.4f} -i "{INPUT}" '
        f'-c:v libx264 -preset ultrafast -crf 18 -c:a aac -b:a 160k "{seg}"')

with open(concat_f, "w") as f:
    for s in seg_files: f.write(f"file '{s}'\n")

no_sil = f"{WORK}/no_silence.mp4"
run(f'{FFMPEG} -y -f concat -safe 0 -i "{concat_f}" '
    f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{no_sil}"')

# Speed 1.1x (atempo for audio, setpts for video)
sped = f"{WORK}/sped.mp4"
run(f'{FFMPEG} -y -i "{no_sil}" '
    f'-filter_complex "[0:v]setpts=PTS/1.1[v];[0:a]atempo=1.1[a]" '
    f'-map "[v]" -map "[a]" '
    f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{sped}"')

print("   ✅ Silencios eliminados + 1.1x speed")

# Get new duration
dur_raw = run(f'{FFMPEG} -i "{sped}" 2>&1')
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", dur_raw)
new_dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)) if m else 130.0
print(f"   Nueva duración: {new_dur:.1f}s")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 2 — Subtítulos estilo Hormozi (zona central, no tapa pantallas)
# La pantalla dividida tiene: arriba calculadora (0–960px), abajo cara (960–1920px)
# Subtítulos van en la FRANJA CENTRAL: y ≈ 880–1050px (entre las dos mitades)
# ══════════════════════════════════════════════════════════════════════════════
print("📝 Generando subtítulos estilo Hormozi...")

# Subtítulos aproximados al contenido de una calculadora WhatsApp
subtitles_data = [
    (0.0,   3.5,  "Esta es la CALCULADORA\nde WhatsApp Business"),
    (4.0,   7.0,  "Vamos a ver cuánto\ncuesta tu operación"),
    (7.5,   11.0, "CONVERSACIONES al mes"),
    (11.5,  15.0, "Mensajes por conversación"),
    (15.5,  19.0, "Este es el COSTO REAL\nque debes calcular"),
    (20.0,  24.0, "Mira estos NÚMEROS 👇"),
    (25.0,  29.0, "Aquí está el resultado\ntotal mensual"),
    (30.0,  34.0, "Colombia vs otros países\n¡DIFERENCIA BRUTAL!"),
    (35.0,  39.0, "Si no optimizas\nestás PERDIENDO dinero"),
    (40.0,  45.0, "Cada conversación\nque no convierte = 💸"),
    (46.0,  50.0, "ESTOS son los campos\nque debes configurar"),
    (51.0,  55.0, "País · Volumen · Tipo\nde mensaje"),
    (56.0,  61.0, "El sistema te muestra\nel costo EXACTO"),
    (62.0,  67.0, "¿Ves la diferencia\nentre estos valores?"),
    (68.0,  73.0, "Aquí está el TRUCO\npara reducir costos"),
    (74.0,  79.0, "Automatiza SOLO\nlo que convierte"),
    (80.0,  85.0, "No pagues por\nconversaciones vacías"),
    (86.0,  91.0, "Esto es lo que hacemos\nen NEUROCHAT"),
    (92.0,  97.0, "Estructura rentable\ndesde el día 1"),
    (98.0,  104.0,"¿Quieres esto\npara tu negocio?"),
    (105.0, 112.0,"Sígueme para la\nPARTE 2 👇"),
    (113.0, 120.0,"@neurochat\n🤖 Automatización inteligente"),
]

srt_path = f"{WORK}/subs.srt"
def ts(s):
    h=int(s//3600); m=int((s%3600)//60); sc=s%60
    return f"{h:02d}:{m:02d}:{sc:06.3f}".replace(".",",")

with open(srt_path, "w") as f:
    for i,(s,e,t) in enumerate(subtitles_data, 1):
        f.write(f"{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n")

# Burn subtitles — zona central (MarginV apunta desde abajo de zona superior)
# Usamos Alignment=8 (top-center) con MarginV=870 para quedar en la franja media
subtitled = f"{WORK}/subtitled.mp4"
sub_filter = (
    f"subtitles={srt_path}:force_style='"
    f"FontName=DejaVu Sans Bold,"
    f"FontSize=18,"          # tamaño moderado para no tapar
    f"PrimaryColour=&H00FFFF00,"   # amarillo Hormozi
    f"OutlineColour=&H00000000,"
    f"BackColour=&HAA000000,"
    f"Bold=1,"
    f"Outline=4,"
    f"Shadow=3,"
    f"Alignment=8,"          # top-center
    f"MarginV=870,"          # desde arriba: queda en la franja central ~870–970px
    f"BorderStyle=4'"
)
run(f'{FFMPEG} -y -i "{sped}" -vf "{sub_filter}" '
    f'-c:v libx264 -preset fast -crf 18 -c:a copy "{subtitled}"')
print("   ✅ Subtítulos aplicados (zona central, no tapa pantallas)")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 3 — Motion Graphics estilo Hormozi
# Diseño: negro/amarillo, texto golpe, números grandes, fondo opaco parcial
# ══════════════════════════════════════════════════════════════════════════════
print("🎨 Generando motion graphics Hormozi...")

BG    = (8, 8, 8)
YEL   = (255, 214, 0)    # amarillo Hormozi
WHITE = (255, 255, 255)
RED   = (220, 30, 30)
GRAY  = (150, 150, 150)
CARD  = (18, 18, 18)

def grad(c1, c2):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y/H
        d.line([(0,y),(W,y)], fill=tuple(int(c1[k]+(c2[k]-c1[k])*t) for k in range(3)))
    return img

def pill(d, x, y, w, h, col, r=20):
    d.rounded_rectangle([x,y,x+w,y+h], radius=r, fill=col)

def ease_out(p): return 1-(1-min(1.0,p))**3

# --- MG 1: GOLPE DE NÚMERO (contador de conversaciones)
def mg_numero(frame_i, total, label, valor, color=YEL):
    img = grad(BG, (15,15,15))
    d   = ImageDraw.Draw(img)
    # stripes decorativas
    for i in range(0, W, 60):
        d.line([(i,0),(i,H)], fill=(255,255,255,12))
    d.rectangle([0,0,W,8], fill=color)
    d.rectangle([0,H-8,W,H], fill=color)

    p = ease_out(frame_i / (total*0.4))
    # número animado
    num_val = int(p * (int(valor.replace(",","").replace(".","")) if valor.replace(",","").replace(".","").isdigit() else 0))
    num_str = f"{num_val:,}" if num_val > 0 else valor
    num_str = valor if p >= 1.0 else num_str

    # card central
    pill(d, 60, H//2-260, W-120, 480, CARD, 32)
    d.rectangle([60, H//2-260, 60+8, H//2+220], fill=color)

    # label
    d.text((100, H//2-230), label.upper(), font=load_font(44, bold=True), fill=GRAY)
    # big number
    f_big = load_font(180, bold=True)
    bbox = d.textbbox((0,0), num_str, font=f_big)
    nx = (W - (bbox[2]-bbox[0])) // 2
    d.text((nx, H//2-160), num_str, font=f_big, fill=color)
    # unit
    d.text((100, H//2+60), "conversaciones/mes", font=load_font(40), fill=WHITE)

    # Hormozi stamp
    pill(d, 80, H-160, 320, 65, YEL, 33)
    d.text((110, H-148), "NEUROCHAT", font=load_font(38, bold=True), fill=BG)
    return np.array(img.convert("RGB"))

# --- MG 2: COMPARATIVA PAÍSES estilo tabla golpe
def mg_paises(frame_i, total):
    img = grad((5,5,5), (20,10,0))
    d   = ImageDraw.Draw(img)
    d.rectangle([0,0,W,8], fill=YEL)
    d.rectangle([0,H-8,W,H], fill=YEL)

    # título
    d.text((80, 80), "COSTO POR PAÍS", font=load_font(72, bold=True), fill=YEL)
    d.text((80, 165), "1.500 conv · 23 msg/conv", font=load_font(38), fill=GRAY)
    d.rectangle([80, 220, W-80, 228], fill=YEL)

    rows = [
        ("🇨🇴", "Colombia",  "$28/mes",   WHITE,  0.0),
        ("🇨🇱", "Chile",     "5x más",    YEL,    0.25),
        ("🇦🇷", "Argentina", "10x más",   RED,    0.45),
        ("🇵🇪", "Perú",      "hasta 30x", RED,    0.60),
    ]
    p_global = ease_out(frame_i / (total*0.8))
    y = 260
    for flag, pais, val, col, delay in rows:
        p2 = ease_out(max(0, (p_global - delay)/(1-delay+0.01)))
        xoff = int((1-p2)*W*0.8)
        pill(d, 60+xoff, y, W-120, 108, CARD, 18)
        d.text((88+xoff, y+18), flag, font=load_font(56), fill=WHITE)
        d.text((160+xoff, y+18), pais, font=load_font(52, bold=True), fill=WHITE)
        bbox = d.textbbox((0,0), val, font=load_font(60, bold=True))
        d.text((W-130-(bbox[2]-bbox[0])+xoff, y+16), val, font=load_font(60, bold=True), fill=col)
        y += 128

    d.text((80, y+30), "⚠️ Sin sistema eficiente =", font=load_font(44, bold=True), fill=WHITE)
    d.text((80, y+90), "DINERO PERDIDO", font=load_font(70, bold=True), fill=RED)

    pill(d, 80, H-160, 320, 65, YEL, 33)
    d.text((110, H-148), "NEUROCHAT", font=load_font(38, bold=True), fill=BG)
    return np.array(img.convert("RGB"))

# --- MG 3: ALERTA ROJA — NUEVO COBRO META
def mg_alerta(frame_i, total):
    img = grad((20,0,0), (5,5,5))
    d   = ImageDraw.Draw(img)
    d.rectangle([0,0,W,8], fill=RED)
    d.rectangle([0,H-8,W,H], fill=RED)

    p = ease_out(frame_i / (total*0.35))
    scale_y = int((1-p) * H * 0.5)

    d.text((W//2-120, 100+scale_y), "⚠️", font=load_font(200), fill=RED)
    d.text((80, 360+scale_y), "NUEVO COBRO", font=load_font(90, bold=True), fill=RED)
    d.text((80, 460+scale_y), "DE META", font=load_font(90, bold=True), fill=YEL)

    items = [
        ("AGO 2026", "Meta Business Agent cobrado"),
        ("OCT 2026", "Mensajes de servicio cobrados"),
        ("OCT 2026", "Mensajes de utilidad cobrados"),
    ]
    y = 600
    for fecha, desc in items:
        p3 = ease_out(max(0, p*3 - items.index((fecha,desc)))  )
        xoff = int((1-min(1,p3))*W*0.7)
        pill(d, 60+xoff, y, W-120, 100, CARD, 18)
        pill(d, 68+xoff, y+8, 220, 84, RED, 14)
        d.text((78+xoff, y+22), fecha, font=load_font(36, bold=True), fill=WHITE)
        d.text((305+xoff, y+22), desc, font=load_font(38, bold=True), fill=YEL)
        y += 120

    pill(d, 80, H-160, 320, 65, YEL, 33)
    d.text((110, H-148), "NEUROCHAT", font=load_font(38, bold=True), fill=BG)
    return np.array(img.convert("RGB"))

# --- MG 4: FORMULA HORMOZI — fórmula de eficiencia
def mg_formula(frame_i, total):
    img = grad(BG, (10,10,20))
    d   = ImageDraw.Draw(img)
    d.rectangle([0,0,W,8], fill=YEL)
    d.rectangle([0,H-8,W,H], fill=YEL)

    p = ease_out(frame_i / (total*0.5))

    d.text((80, 100), "LA FÓRMULA", font=load_font(80, bold=True), fill=YEL)
    d.text((80, 190), "para no perder $$$", font=load_font(48), fill=GRAY)
    d.rectangle([80, 260, W-80, 268], fill=YEL)

    formulas = [
        ("01", "Menos conversaciones,\nmás conversiones", WHITE),
        ("02", "Respuestas inteligentes\nque cierran solos", YEL),
        ("03", "Sistema que solo paga\npor lo que convierte", WHITE),
    ]
    y = 300
    for num, text, col in formulas:
        p2 = ease_out(max(0, p*3 - formulas.index((num,text,col))))
        xoff = int((1-min(1,p2))*W*0.9)
        pill(d, 60+xoff, y, W-120, 150, CARD, 24)
        pill(d, 68+xoff, y+15, 90, 90, YEL, 45)
        d.text((85+xoff, y+25), num, font=load_font(52, bold=True), fill=BG)
        lines = textwrap.wrap(text, width=24)
        for li, line in enumerate(lines):
            d.text((178+xoff, y+20+li*52), line, font=load_font(44, bold=True), fill=col)
        y += 178

    pill(d, 80, H-160, 320, 65, YEL, 33)
    d.text((110, H-148), "NEUROCHAT", font=load_font(38, bold=True), fill=BG)
    return np.array(img.convert("RGB"))

# Generate MG videos
BFPS = 30
mg_specs = [
    ("mg_numero.mp4",  mg_numero,  ("Conversaciones", "1500", YEL), 5),
    ("mg_alerta.mp4",  mg_alerta,  None,  5),
    ("mg_paises.mp4",  mg_paises,  None,  6),
    ("mg_formula.mp4", mg_formula, None,  5),
]

mg_paths = {}
for fname, fn, args, secs in mg_specs:
    path = f"{WORK}/{fname}"
    n = secs * BFPS
    writer = imageio.get_writer(path, fps=BFPS, codec="libx264", quality=9,
                                macro_block_size=None,
                                output_params=["-pix_fmt","yuv420p","-crf","18"])
    for i in range(n):
        if args:
            frame = fn(i, n, *args)
        else:
            frame = fn(i, n)
        writer.append_data(frame)
    writer.close()
    # add silent audio
    wa = path.replace(".mp4","_a.mp4")
    run(f'{FFMPEG} -y -i "{path}" -f lavfi -i anullsrc=r=48000:cl=stereo '
        f'-c:v copy -c:a aac -b:a 128k -shortest "{wa}"')
    mg_paths[fname] = wa
    print(f"   ✅ {fname}")

# ══════════════════════════════════════════════════════════════════════════════
# PASO 4 — Insertar MG en el video editado
# Tiempos en el video YA procesado (sin silencios + 1.1x)
# Insertamos entre secciones clave del video de calculadora
# ══════════════════════════════════════════════════════════════════════════════
print("🎬 Montando video final...")

inserts = [
    (8.0,   mg_paths["mg_alerta.mp4"]),   # al inicio, antes de mostrar calculadora
    (22.0,  mg_paths["mg_numero.mp4"]),   # cuando habla de conversaciones
    (50.0,  mg_paths["mg_paises.mp4"]),   # cuando menciona costos por país
    (85.0,  mg_paths["mg_formula.mp4"]),  # cierre: fórmula de eficiencia
]

prev = 0.0
final_segs = []
for ins_t, mg_path in inserts:
    if ins_t > prev:
        seg = f"{WORK}/fseg_{len(final_segs):03d}.mp4"
        run(f'{FFMPEG} -y -ss {prev:.4f} -to {ins_t:.4f} -i "{subtitled}" '
            f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{seg}"')
        final_segs.append(seg)
    final_segs.append(mg_path)
    prev = ins_t

# Resto del video
seg = f"{WORK}/fseg_{len(final_segs):03d}.mp4"
run(f'{FFMPEG} -y -ss {prev:.4f} -i "{subtitled}" '
    f'-c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "{seg}"')
final_segs.append(seg)

fc = f"{WORK}/final_concat2.txt"
with open(fc, "w") as f:
    for s in final_segs: f.write(f"file '{s}'\n")

run(f'{FFMPEG} -y -f concat -safe 0 -i "{fc}" '
    f'-c:v libx264 -preset medium -crf 18 -c:a aac -b:a 160k '
    f'-pix_fmt yuv420p "{OUTPUT}"')

info = run(f'{FFMPEG} -i "{OUTPUT}" 2>&1')
for line in info.split("\n"):
    if "Duration" in line or "Stream" in line:
        print(" ", line.strip())
print(f"\n✅ Listo: {OUTPUT}")
