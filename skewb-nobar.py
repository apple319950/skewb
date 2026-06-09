import itertools

# 建立元素組
elements = ['r', 'R', 'b', 'B', "r'", "R'", "b'", "B'"]
valid_perms = []

# 產生符合條件的排列（恰好4個元素，且不能有衝突）
for p in itertools.permutations(elements, 4):
    s = set(p)
    if any(n in s and n + "'" in s for n in ['r', 'R', 'b', 'B']):
        continue
    valid_perms.append(p)

# 總數應該是 384 筆
print(f"總共有 {len(valid_perms)} 筆排列，請按下空白鍵（或直接 Enter）查看下一筆，按 q 離開\n")

# 等待使用者按鍵逐筆顯示
for i, perm in enumerate(valid_perms, 1):
    key = input(f"[第 {i} 筆] {' '.join(perm)}   ⏎下一筆，輸入 q 離開：")
    if key.lower() == 'q':
        print("已手動中止")
        break

