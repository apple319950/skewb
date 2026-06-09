import json
from pathlib import Path

from skewb_tnoodle import SkewbTNoodle
from run_excel import generate_scrambles, inverse_alg


def get_case_colors(alg: str):
    """
    回傳 30 格顏色。
    順序跟你原本畫圖順序一致：
    6 個面，每面 5 格。
    """
    skewb = SkewbTNoodle()
    skewb.apply_alg(alg)

    scheme = [skewb.color_scheme[ch] for ch in skewb.FACE_ORDER]

    colors = []

    for face in range(6):
        for sticker in range(5):
            color = scheme[skewb.image[face][sticker]]
            colors.append(color)

    return colors


def export_geometry(output_path="skewb_geometry.json"):
    """
    輸出固定的 Skewb 幾何形狀。
    所有 case 共用同一份 geometry。
    """
    skewb = SkewbTNoodle()

    width, height = skewb.get_preferred_size()
    transforms = skewb.get_face_transforms()
    base_paths = skewb.get_face_paths()

    polygons = []

    for face in range(6):
        trans = transforms[face]

        for sticker in range(5):
            pts = skewb.apply_transform(base_paths[sticker], trans)

            polygons.append({
                "face": face,
                "sticker": sticker,
                "points": pts
            })

    data = {
        "width": width,
        "height": height,
        "polygons": polygons
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"幾何資料已輸出：{output_path}")


def create_json_dataset_no_png(
    scrambles,
    output_dir="skewb_5step_dataset",
    json_name="cases.json",
    depth=5,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = []

    for idx, solution_alg in enumerate(scrambles, start=1):
        scramble_alg = inverse_alg(solution_alg)

        colors = get_case_colors(scramble_alg)

        cases.append({
            "scramble": scramble_alg,
            "case": f"Skewb {depth}-step #{idx:03d}",
            "solution": solution_alg,
            "note": "",
            "colors": colors,
            "depth": depth
        })

    json_path = output_dir / json_name

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

    print(f"{depth}-step 完成，共 {len(cases)} 題")
    print(f"JSON 已輸出：{json_path}")


if __name__ == "__main__":
    # 只需要輸出一次，放在專案根目錄
    export_geometry("skewb_geometry.json")

    for depth in [2, 3, 4, 5]:
        scrambles = generate_scrambles(max_depth=depth)

        create_json_dataset_no_png(
            scrambles=scrambles,
            output_dir=f"skewb_{depth}step_dataset",
            json_name="cases.json",
            depth=depth,
        )