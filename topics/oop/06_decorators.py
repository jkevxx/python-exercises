def decorator(func):
    def fund_modified():
        print("Before calling the function")
        func()
        print("After calling the function")
    return fund_modified


# def greeting():
#     print("Hi Kevin")


# greeting_modified = decorator(greeting)
# greeting_modified()

@decorator
def greeting():
    print("Hi Kevin")


greeting()
