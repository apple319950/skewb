from pathlib import Path
from PIL import Image, ImageDraw
from skewb_tnoodle import SkewbTNoodle


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def get_unique_png_path(output_dir: Path, base_name="case") -> Path:
    """
    產生不重複的 PNG 檔名
    case.png
    case_001.png
    case_002.png
    ...
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{base_name}.png"
    if not path.exists():
        return path

    index = 1
    while True:
        path = output_dir / f"{base_name}_{index:03d}.png"
        if not path.exists():
            return path
        index += 1


def render_skewb_png(alg: str, output_png_path: Path, scale=4):
    skewb = SkewbTNoodle()
    skewb.apply_alg(alg)

    width, height = skewb.get_preferred_size()

    img = Image.new("RGB", (width * scale, height * scale), "white")
    draw = ImageDraw.Draw(img)

    transforms = skewb.get_face_transforms()
    base_paths = skewb.get_face_paths()
    scheme = [skewb.color_scheme[ch] for ch in skewb.FACE_ORDER]

    for face in range(6):
        trans = transforms[face]

        for sticker in range(5):
            pts = skewb.apply_transform(base_paths[sticker], trans)
            pts_scaled = [(x * scale, y * scale) for x, y in pts]

            fill_color = hex_to_rgb(scheme[skewb.image[face][sticker]])

            draw.polygon(
                pts_scaled,
                fill=fill_color,
                outline=(0, 0, 0)
            )

    img.save(output_png_path)


# ===============================
# 主程式
# ===============================

algs = [
    "r' z2 r' z r z' r"

]

output_dir = Path("output_cases")

for i, alg in enumerate(algs, start=1):
    output_png = get_unique_png_path(output_dir, base_name="case")
    render_skewb_png(alg, output_png, scale=4)

    skewb = SkewbTNoodle()
    skewb.apply_alg(alg)

    print(f"[{i}] 公式：{alg}")
    print(f"    已輸出：{output_png}")
    print(f"    30 格顏色順序：{skewb.get_color_list_in_draw_order()}")
    print()