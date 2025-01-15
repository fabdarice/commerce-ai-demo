class Item:
    def __init__(self, name: str, price=None, deadline=None):
        self.name = name
        self.price = price
        self.deadline = deadline

    def __str__(self):
        return f"{self.name} - {self.price} - {self.deadline}"
