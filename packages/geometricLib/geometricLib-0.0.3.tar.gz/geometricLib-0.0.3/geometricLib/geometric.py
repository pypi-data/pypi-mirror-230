import math

class GeometryCalculator:

    #вычисляет площадь круга
    @staticmethod
    def circle_area(radius):
        return math.pi * radius ** 2

    # вычисляет площадь треугольника по трем сторонам
    @staticmethod
    def triangle_area(side1, side2, side3):
        s = (side1 + side2 + side3) / 2
        return math.sqrt(s * (s - side1) * (s - side2) * (s - side3))
