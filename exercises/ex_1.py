
items = ['A', 'B', 'C', 'D', 'E']

new_items = []
# ❌ wrong way
# for item in items:
#     if item == 'B':
#         items.remove('B')
#     else:
#         print(item)

for item in items:
    if item == 'B':
        continue
    else:
        print(item)
        new_items.append(item)
