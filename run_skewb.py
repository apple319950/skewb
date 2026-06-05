from skewb_tnoodle import SkewbTNoodle

# 你在這裡輸入打亂
alg = "L"

skewb = SkewbTNoodle()
skewb.apply_alg(alg)

# 輸出 SVG
skewb.save_svg("out.svg")

# 如果你有安裝 cairosvg，也可以輸出 PNG
# skewb.save_png("out.png")

print("完成，已輸出 out.svg")
print("30 格顏色順序：")
print(skewb.get_color_list_in_draw_order())