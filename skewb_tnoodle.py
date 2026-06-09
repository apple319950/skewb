import math
import argparse
from pathlib import Path


class SkewbTNoodle:
    """
    依照 TNoodle 官方 SkewbPuzzle.java 實作的 Python 版
    - 輸入 scramble
    - 輸出官方風格的 Skewb SVG 圖
    """

    FACE_ORDER = "URFDLBO"   # 官方畫圖與顏色順序
    MOVE_AXES = "rBRbLzyx"      # 速解通用轉動

    DEFAULT_COLOR_SCHEME = {
        "U": "#ffffff",  # WHITE
        "R": "#0000ff",  # BLUE
        "F": "#ff0000",  # RED
        "D": "#ffff00",  # YELLOW
        "L": "#00ff00",  # GREEN
        "B": "#ff8000",  # ORANGE
        "O": "#000000",  # BLACK
    }

    PIECE_SIZE = 30
    GAP = 3
    SQRT3_OVER_2 = math.sqrt(3) / 2

    def __init__(self, color_scheme=None):
        self.color_scheme = dict(self.DEFAULT_COLOR_SCHEME)
        if color_scheme:
            self.color_scheme.update(color_scheme)
        self.reset()

    # =========================================================
    # 狀態
    # =========================================================

    def reset(self):
        # image[face][sticker]，官方是 6 面、每面 5 塊
        # face index: U R F D L B = 0 1 2 3 4 5
        # sticker index:
        #   1   2
        #     0
        #   3   4
        #self.image = [[face for _ in range(5)] for face in range(6)]
        self.image = [
            [6, 2, 6, 2, 6],  # U_C 改成 D 色
            [6, 6, 6, 6, 6],
            [6, 4, 6, 4, 6],
            [6, 5, 6, 5, 6],
            [0, 0, 0, 0, 0],
            [6, 6, 1, 6, 1],
        ]

    def copy_image(self):
        return [row[:] for row in self.image]

    # =========================================================
    # 官方 move 邏輯
    # =========================================================

    def _swap(self, f1, s1, f2, s2, f3, s3):
        temp = self.image[f1][s1]
        self.image[f1][s1] = self.image[f2][s2]
        self.image[f2][s2] = self.image[f3][s3]
        self.image[f3][s3] = temp

    def _routate(self, f1, s1, f2, s2, f3, s3, f4, s4):
        temp = self.image[f1][s1]
        self.image[f1][s1] = self.image[f2][s2]
        self.image[f2][s2] = self.image[f3][s3]
        self.image[f3][s3] = self.image[f4][s4]
        self.image[f4][s4] = temp

    def _turn_once(self, axis):
        # axis: 0-r, 1-B, 2-R, 3-b, 4-L
        if axis == 0:   # R
            self._swap(2, 0, 3, 0, 1, 0)
            self._swap(2, 4, 3, 2, 1, 3)
            self._swap(2, 2, 3, 1, 1, 4)
            self._swap(2, 3, 3, 4, 1, 1)
            self._swap(4, 4, 5, 3, 0, 4)

        elif axis == 1:  # U
            self._swap(0, 0, 1, 0, 5, 0)
            self._swap(0, 2, 1, 2, 5, 1)
            self._swap(0, 4, 1, 4, 5, 2)
            self._swap(0, 1, 1, 1, 5, 3)
            self._swap(4, 1, 2, 2, 3, 4)

        elif axis == 2:  # R
            self._swap(1, 0, 0, 0, 2, 0)
            self._swap(1, 1, 0, 4, 2, 2)
            self._swap(1, 3, 0, 2, 2, 1)
            self._swap(1, 2, 0, 3, 2, 4)
            self._swap(4, 2, 3, 2, 5, 1)

        elif axis == 3:  # B
            self._swap(1, 0, 3, 0, 5, 0)
            self._swap(1, 4, 3, 4, 5, 3)
            self._swap(1, 3, 3, 3, 5, 1)
            self._swap(1, 2, 3, 2, 5, 4)
            self._swap(0, 2, 2, 4, 4, 3)

        elif axis == 4:  # L
            self._swap(4, 0, 5, 0, 3, 0)
            self._swap(4, 3, 5, 4, 3, 3)
            self._swap(4, 1, 5, 3, 3, 1)
            self._swap(4, 4, 5, 2, 3, 4)
            self._swap(2, 3, 0, 1, 1, 4)

        elif axis == 5:  # z
            self._routate(2, 0, 0, 0, 5, 0, 3, 0)
            self._routate(2, 1, 0, 1, 5, 4, 3, 1)
            self._routate(2, 2, 0, 2, 5, 3, 3, 2)
            self._routate(2, 3, 0, 3, 5, 2, 3, 3)
            self._routate(2, 4, 0, 4, 5, 1, 3, 4)
            self._routate(4, 2, 4, 1, 4, 3, 4, 4)
            self._routate(1, 1, 1, 2, 1, 4, 1, 3)
        
        elif axis == 6:  # y
            self._routate(2, 0, 1, 0, 5, 0, 4, 0)
            self._routate(2, 1, 1, 1, 5, 4, 4, 1)
            self._routate(2, 2, 1, 2, 5, 3, 4, 2)
            self._routate(2, 3, 1, 3, 5, 2, 4, 3)
            self._routate(2, 4, 1, 4, 5, 1, 4, 4)
            self._routate(0, 2, 0, 1, 0, 3, 0, 4)
            self._routate(3, 1, 3, 2, 3, 4, 3, 3)

        elif axis == 7:  # x
            self._routate(1, 0, 0, 0, 4, 0, 3, 0)
            self._routate(1, 2, 0, 1, 4, 3, 3, 4)
            self._routate(1, 4, 0, 2, 4, 1, 3, 3)
            self._routate(1, 1, 0, 3, 4, 4, 3, 2)
            self._routate(1, 3, 0, 4, 4, 2, 3, 1)
            self._routate(2, 2, 2, 1, 2, 3, 2, 4)
            self._routate(5, 1, 5, 2, 5, 4, 5, 3)

        else:
            raise ValueError("axis 必須是 合法軸")

    def apply_move(self, move):
        """
        官方 notation:
        R, U, L, B, R', U', L', B'

        注意：
        官方 Java 裡 pow=1 是正轉，pow=2 代表反轉
        所以 X' 等於把正轉做兩次
        """
        move = move.strip().replace("’", "'")
        if not move:
            return


        if move.endswith("'") or move.endswith("2"):
            base = move[:-1]
        else:
            base = move
        
        ROTATIONS = "xyz"
        if base in ROTATIONS:
            if move.endswith("'"):
                pow_times = 3 
            elif move.endswith("2"):
                pow_times = 2
            else:
                pow_times = 1
        else:
            pow_times = 2 if move.endswith("'") else 1            

        if base not in self.MOVE_AXES:
            raise ValueError(f"未知動作：{move}，只支援 R U L B 與其 '")

        axis = self.MOVE_AXES.index(base)
        for _ in range(pow_times):
            self._turn_once(axis)

    def apply_alg(self, alg):
        alg = alg.strip().replace("’", "'")
        if not alg:
            return

        for move in alg.split():
            self.apply_move(move)

    # =========================================================
    # 官方展開圖幾何
    # =========================================================

    @classmethod
    def get_preferred_size(cls):
        width = math.ceil((3 * cls.GAP + 8 * cls.PIECE_SIZE + 1) * cls.SQRT3_OVER_2)
        height = math.ceil(2 * cls.GAP + 6 * cls.PIECE_SIZE + 1)
        return width, height

    @classmethod
    def get_face_transforms(cls):
        ps = cls.PIECE_SIZE
        gap = cls.GAP
        s = cls.SQRT3_OVER_2

        # 對應 Java:
        # new Transform(a, b, c, d, e, f)
        # SVG affine:
        # x' = a*x + c*y + e
        # y' = b*x + d*y + f
        return [
            (ps * s, -ps / 2, ps * s,  ps / 2, (ps * 4 + gap * 1.5) * s, ps),                    # U
            (ps * s, -ps / 2, 0,       ps,      (ps * 7 + gap * 3) * s, ps * 1.5),               # R
            (ps * s, -ps / 2, 0,       ps,      (ps * 5 + gap * 2) * s, ps * 2.5 + 0.5 * gap),   # F
            (0,       ps,     -ps * s, -ps / 2, (ps * 3 + gap * 1) * s, ps * 4.5 + 1.5 * gap),   # D
            (ps * s,  ps / 2, 0,       ps,      (ps * 3 + gap * 1) * s, ps * 2.5 + 0.5 * gap),   # L
            (ps * s,  ps / 2, 0,       ps,      ps * s,               ps * 1.5),                  # B
        ]

    @staticmethod
    def get_face_paths():
        """
        官方 getFacePaths() 對應的五塊 local coordinates
        sticker index:
        0 = center
        1 = upper-left
        2 = upper-right
        3 = lower-left
        4 = lower-right
        """
        return [
            [(-1, 0), (0, 1), (1, 0), (0, -1)],   # 0 center diamond
            [(-1, 0), (-1, -1), (0, -1)],         # 1 UL
            [(0, -1), (1, -1), (1, 0)],           # 2 UR
            [(-1, 0), (-1, 1), (0, 1)],           # 3 DL
            [(0, 1), (1, 1), (1, 0)],             # 4 DR
        ]

    @staticmethod
    def apply_transform(points, transform):
        a, b, c, d, e, f = transform
        out = []
        for x, y in points:
            x2 = a * x + c * y + e
            y2 = b * x + d * y + f
            out.append((x2, y2))
        return out

    @staticmethod
    def points_to_svg(points):
        return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)

    # =========================================================
    # 輸出
    # =========================================================

    def to_svg_string(self):
        width, height = self.get_preferred_size()
        transforms = self.get_face_transforms()
        base_paths = self.get_face_paths()

        # face index -> face letter -> hex color
        scheme = [self.color_scheme[ch] for ch in self.FACE_ORDER]

        polygons = []
        for face in range(6):
            trans = transforms[face]
            for sticker in range(5):
                pts = self.apply_transform(base_paths[sticker], trans)
                fill = scheme[self.image[face][sticker]]
                polygon = (
                    f'<polygon points="{self.points_to_svg(pts)}" '
                    f'style="fill:{fill};stroke:#000;stroke-width:1" />'
                )
                polygons.append(polygon)

        svg = (
            f'<svg width="{width}" height="{height}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            + "".join(polygons) +
            "</svg>"
        )
        return svg

    def save_svg(self, path="skewb.svg"):
        svg = self.to_svg_string()
        Path(path).write_text(svg, encoding="utf-8")
        return path


    def get_color_list_in_draw_order(self):
        """
        依官方 drawScramble() 的輸出順序回傳 30 格顏色
        順序:
        U(0..4), R(0..4), F(0..4), D(0..4), L(0..4), B(0..4)
        """
        scheme = [self.color_scheme[ch] for ch in self.FACE_ORDER]
        out = []
        for face in range(6):
            for sticker in range(5):
                out.append(scheme[self.image[face][sticker]])
        return out


# =========================================================
# CLI
# =========================================================

def main():
    parser = argparse.ArgumentParser(description="依照 TNoodle 官方邏輯畫 Skewb")
    parser.add_argument(
        "scramble",
        nargs="*",
        help="例如: R U B' L R'"
    )
    parser.add_argument("--svg", default="skewb.svg", help="輸出的 SVG 檔名")
    parser.add_argument("--png", default="", help="若要同時輸出 PNG，填檔名，例如 skewb.png")
    args = parser.parse_args()

    alg = "".join(args.scramble)

    skewb = SkewbTNoodle()
    skewb.apply_alg(alg)

    svg_path = skewb.save_svg(args.svg)
    print(f"SVG 已輸出：{svg_path}")

    if args.png:
        png_path = skewb.save_png(args.png)
        print(f"PNG 已輸出：{png_path}")

    print("30 格顏色順序：")
    print(skewb.get_color_list_in_draw_order())


if __name__ == "__main__":
    main()