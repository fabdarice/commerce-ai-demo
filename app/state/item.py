class Item:
    def __init__(self, name: str, price: float = 0.0, deadline: int = 0):
        self.name = name
        self.price = price
        self.deadline = deadline

    def __str__(self):
        return f"{self.name} - {self.price} - {self.deadline}"
