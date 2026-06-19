class Phone:
    def __init__(self, brand, model, camera):
        self.brand = brand
        self.model = model
        self.camera = camera

    def call(self):
        print(f"You're making a call from {self.model}")

    def hangUp(self):
        print(f"You're hang up from {self.model}")


phone1 = Phone("Samsung", "S23", "48MP")
phone1.call()
