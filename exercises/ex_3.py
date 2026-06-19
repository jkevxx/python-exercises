def anagramas(str1: str, str2: str):
    str1 = str1.replace(' ', '').lower()
    str2 = str2.replace(' ', '').lower()

    if len(str1) != len(str2):
        return False
    else:
        str1_ord = sorted(str1)
        str2_ord = sorted(str2)
        print(str1_ord)
        print(str2_ord)

        return str1_ord == str2_ord


str1 = 'gato'  # amor
str2 = 'toga'  # roma

print(anagramas(str1, str2))
