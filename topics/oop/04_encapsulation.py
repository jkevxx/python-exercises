class Person():
    def __init__(self):
        self.name = "Kevin"
        self._dni = "12345678A"
        self.__money = "3000"

    def money(self):
        print(self.__money)


person = Person()
print(person.name)
print(person._dni)
print(person.money())
