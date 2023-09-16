import math
class FindArea:
    def __init__(self):
        pass
    def triangle(self, a, b, c):
        if a**2+b**2 == c**2:
            return 1/2*a*b
        elif a**2+c**2 == b**2:
            return 1/2*(a*c)
        elif b**2+c**2 == a**2:
            return 1/2*b*c
        else:
            p = (a+b+c)/2
            return math.sqrt(p*(p-a)*(p-b)*(p-c))
    def circle(self, R):
        return math.pi*R**2

