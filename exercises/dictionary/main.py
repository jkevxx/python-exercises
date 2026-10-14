# Create a dictionary that will let you add a student and their grade

students = [
    {"name": "Kevin", "grade": 9}
]

stop = False

while not stop:
    current_name = input("Write the name: ")
    current_grade = input("Write the grade: ")
    students.append({"name": current_name, "grade": current_grade})
    print(students)
    want_more = input("Do you want to add another? Y/N ")
    if (want_more != "Y"):
        stop = True
