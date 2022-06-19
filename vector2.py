class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"x: {self.x}, y: {self.y}"

    def __mul__(self, scale):
        return Vector2(self.x * scale, self.y * scale)

    def Tuple(self):
        return self.x, self.y