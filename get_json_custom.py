import json
from pathlib import Path

from skewb_tnoodle import SkewbTNoodle
from run_excel import inverse_alg


def get_case_colors(alg: str):
    """
    取得某個 alg 轉完後的 30 格顏色資料
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


def create_custom_json_dataset(
    scrambles,
    output_dir="skewb_custom_dataset",
    json_name="cases.json",
    case_prefix="Custom"
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = []

    for idx, scramble_alg in enumerate(scrambles, start=1):
        colors = get_case_colors(scramble_alg)

        case_data = {
            "scramble": scramble_alg,
            "case": f"{case_prefix} #{idx:03d}",
            "solution": inverse_alg(scramble_alg),
            "note": "",
            "colors": colors,
            "depth": len(scramble_alg.split())
        }

        cases.append(case_data)

    json_path = output_dir / json_name

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

    print(f"完成，共產生 {len(cases)} 題")
    print(f"JSON 已輸出：{json_path}")


CUSTOM_SCRAMBLES = [
    #底1順
    "r' B r'",
    "r R r' R' B'",
    "B' r' B r' B",
    "r' B r' B'",
    "B' r' B r'",
    "r R r' R' B",
    "B' r' B r' B'",
    #底1順1逆
    "r' B r' B",
    #底1逆
    "B r' B",
    "B' R' B R r",
    "r B r' B r'",
    "B r' B r",
    "r B r' B",
    "B' R' B R r'",
    "r B r' B r",

    #對底
    "r R r R B' R r'",
    "r' B r B'",
    "B r' B' r",
    "r' B r B' r",
    "B r' B' r B'",
    "r' B r B' r'",
    "B r' B' r B",
    "r R r R B' R",
    #"R' r' R' r' b' r'",
    "R' r' R' r' z' r' R'",

    #對1順
    "B r",
    "r R r' R' B r",
    "B R r R'",
    "B r B",
    "R' B' R' r' R'",
    "B r B'",
    "r' B r",
    #對1順1逆
    "R' B' R' r' R' B'",
    #對1逆
    "r' B'",
    "B' R' B R r' B'",
    "r' R' B' R",
    "r' B' r'",
    "R r R B R",
    "r' B' r",
    "B r' B'",

    #2上
    "B' r",
    "r B'",
    "B' r' R r' R'",
    "r B R' B R",
    "R' B' R r",
    "R r R' B'",

    "R' B' R B' r'",
    "R r R' r B",
    "r R' B' R",
    "B' R r R'",
    "r' R' B' R B'",
    "B R r R' r",
]

set_name = "half_opp"

if __name__ == "__main__":
    create_custom_json_dataset(
        scrambles=CUSTOM_SCRAMBLES,
        output_dir="dataset",
        json_name=f"{set_name}.json",
        case_prefix=f"Skewb {set_name}"
    )