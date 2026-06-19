
enteros = [1, 4, 5, 7, 23, 54, 34, 5, 4, 56, 8, 9, 78, 2,]

for i in range(len(enteros)):
    for j in range(len(enteros) - i - 1):
        if enteros[j] > enteros[j+1]:
            aux = enteros[j]
            enteros[j] = enteros[j+1]
            enteros[j+1] = aux

print(enteros)
