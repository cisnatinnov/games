import math

def result(area, perimeter):
  return {
    'status': 200,
    'message': '',
    'data': {
      'area': area,
      'perimeter': perimeter
    }
  }

def rectangle(width, height):
  area = width * height
  perimeter = 2 * (width + height)
  return result(area, perimeter)
  
def circle(radius):
  area = math.pi * radius ** 2
  perimeter = 2 * math.pi * radius
  return result(area, perimeter)
  
def square(side):
  area = side ** 2
  perimeter = 4 * side
  return result(area, perimeter)
  
def triangle(width, height, side):
  area = (1 / 2 * width) * height
  perimeter = width + height + side
  return result(area, perimeter)