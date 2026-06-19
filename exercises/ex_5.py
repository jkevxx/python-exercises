matrix = []

numero_de_columna = 0

numero = 0

for fila in range(3):

    fila_newc = []

    for columna in range(1, 4):

        numero_de_columna += 1

        numero += 2

        if numero_de_columna % 2 == 0:

            fila_newc.append(0)

        else:

            fila_newc.append(numero)

    matrix.append(fila_newc)


for x in matrix:

    print(x)
