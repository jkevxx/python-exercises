class Animal():
    def sound(self):
        pass


class Cat(Animal):
    def sound(self):
        print("Meow")


class Dog(Animal):
    def sound(self):
        print("Woof")


cat = Cat()
cat.sound()
dog = Dog()
dog.sound()
