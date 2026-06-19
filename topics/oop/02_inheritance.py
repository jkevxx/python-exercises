class Person:
    def __init__(self, name, age, nationality):
        self.name = name
        self.age = age
        self.nationality = nationality

    def talk(self):
        print("Hi, I'm talking a little bit")


class Employee(Person):
    def __init__(self, name, age, nationality, job, salary):
        super().__init__(name, age, nationality)
        self.job = job
        self.salary = salary

    def talk(self):
        print("No")


kevin = Employee("Kevin", 23, "Mexican", "Developer", 20000)
kevin.talk()
