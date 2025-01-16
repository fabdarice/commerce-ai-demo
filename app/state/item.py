class Item:
    def __init__(self, name: str, product_id: str, price=None, delivery_time=None):
        self.name = name
        self.price = price
        self.delivery_time = delivery_time
        self.product_id = product_id

    def __str__(self):
        return f"{self.name} - {self.price} - {self.delivery_time} - {self.product_id}"
