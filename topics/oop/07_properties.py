class Person:
    def __init__(self, name, age):
        self.__name = name
        self.__age = age

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @name.deleter
    def name(self):
        del self.__name


person = Person("kevin", 23)

# we don't need to use ()
print(person.name)

person.name = "Keitaro"
print(person.name)

del person.name

print(person.name)
