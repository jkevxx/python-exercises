class Person:
    def __init__(self, name, age, nationality):
        self.name = name
        self.age = age
        self.nationality = nationality

    def talk(self):
        print("Hi, I'm talking a little bit")


class Artist:
    def __init__(self, skill):
        self.skill = skill

    def show_skill(self):
        return f"my skill is: {self.skill}"


class EmployeeArtist(Person, Artist):
    def __init__(self, name, age, nationality, skill, salary, company):
        Person.__init__(self, name, age, nationality)
        Artist.__init__(self, skill)
        self.salary = salary
        self.company = company

    # def show_skill(self):
    #     print("I haven't ha")

    # def introduce(self):
    #     (f"{super().show_skill()}")

    def introduce(self):
        print(
            f"Hi, I'm {self.name} and {self.show_skill()} and I work in {self.company}")


kevin = EmployeeArtist("Kevin", 23, "Mexican", "Sing", 20000, "OnceStudios")
kevin.introduce()

# inheritance = issubclass(EmployeeArtist, Artist) #True
# inheritance = issubclass(EmployeeArtist, Person)  # True
# inheritance = issubclass(Artist, Person)  # False
# print(inheritance)

# instance = isinstance(kevin, EmployeeArtist)  # True
# instance = isinstance(kevin, Artist)  # True
instance = isinstance(kevin, Person)  # True
print(instance)
