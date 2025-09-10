import math

def result(volume, curved_surface_area, surface_area):
  return {
    'status': 200,
    'message': '',
    'data': {
      'volume': round(volume, 2),
      'curved_surface_area': round(curved_surface_area, 2),
      'surface_area': round(surface_area, 2)
    }
  }

def cube(side):
  volume = side ** 3
  curved_surface_area = 4 * (side ** 2)
  surface_area = 6 * (side ** 2)
  return result(volume, curved_surface_area, surface_area)
  
def sphere(radius):
  volume = (4/3) * math.pi * radius ** 3
  curved_surface_area = 0
  surface_area = 4 * math.pi * radius ** 2
  return result(volume, curved_surface_area, surface_area)
  
def cylinder(radius, height):
  volume = math.pi * radius ** 2 * height
  curved_surface_area = 2 * math.pi * radius * height
  surface_area = 2 * math.pi * radius * (radius + height)
  return result(volume, curved_surface_area, surface_area)
  
def cuboid(side, length, height):
  volume = side * length * height
  curved_surface_area = (2*height) * (side+length)
  surface_area = 2 * ((side*length) + (length*height) + (side*height))
  return result(volume, curved_surface_area, surface_area)

def prism(base_area, height, perimeter):
  volume = base_area * height
  lateral_surface_area = perimeter * height
  total_surface_area = 2 * base_area + lateral_surface_area
  return {
    'status': 200,
    'message': '',
    'data': {
      'volume': round(volume, 2),
      'lateral_surface_area': round(lateral_surface_area, 2),
      'total_surface_area': round(total_surface_area, 2)
    }
  }

def triangular_prism(base, height, length):
  base_area = 0.5 * base * height
  perimeter = base + height + math.sqrt(base**2 + height**2)
  return prism(base_area, length, perimeter)

def rectangular_prism(width, height, length):
  base_area = width * height
  perimeter = 2 * (width + height)
  return prism(base_area, length, perimeter)

def pentagonal_prism(side_length, height):
  # Regular pentagon
  apothem = side_length / (2 * math.tan(math.pi/5))
  base_area = 5 * side_length * apothem / 2
  perimeter = 5 * side_length
  return prism(base_area, height, perimeter)

def hexagonal_prism(side_length, height):
  # Regular hexagon
  apothem = side_length * math.sqrt(3) / 2
  base_area = 6 * side_length * apothem / 2
  perimeter = 6 * side_length
  return prism(base_area, height, perimeter)