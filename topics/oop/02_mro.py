class A:
    def talk(self):
        print("Hi, from A")


class B(A):
    # def talk(self):
    #     print("Hi, from B")
    pass


class C(A):
    def talk(self):
        print("Hi, from C")


class D(B, C):
    # def talk(self):
    #     print("Hi, from D")
    pass


d = D()
# d.talk()
# print(B.mro())
print(B.talk(d))
