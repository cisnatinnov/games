import math

def rectangle(width, height):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': {
        'area': width * height,
        'perimeter': 2 * (width + height)
      }
    }
  }
  
def circle(radius):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': {
        'area': math.pi * radius ** 2,
        'circumference': 2 * math.pi * radius
      }
    }
  }
  
def square(side):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': {
        'area': side ** 2,
        'perimeter': 4 * side
      }
    }
  }
  
def triangle(width, height, side):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': {
        'area': (1 / 2 * width) * height,
        'perimeter': width + height + side
      }
    }
  }