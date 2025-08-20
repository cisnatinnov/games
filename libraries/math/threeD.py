import math

def cube(side):
  volume = side ** 3
  curved_surface_area = 4 * (side ** 2)
  surface_area = 6 * (side ** 2)
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': {
        'volume': round(volume, 2),
        'curved_surface_area': round(curved_surface_area, 2),
        'surface_area': round(surface_area, 2)
      }
    }
  }
  
def sphere(radius):
  volume = (4/3) * math.pi * radius ** 3
  surface_area = 4 * math.pi * radius ** 2
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': {
        'volume': round(volume, 2),
        'surface_area': round(surface_area, 2)
      }
    }
  }
  
def cylinder(radius, height):
  volume = math.pi * radius ** 2 * height
  curved_surface_area = 2 * math.pi * radius * height
  surface_area = 2 * math.pi * radius * (radius + height)
  return {
    'status': 200,
    'message': '',
    'data': {
      'volume': round(volume, 2),
      'curved_surface_area': round(curved_surface_area, 2),
      'surface_area': round(surface_area, 2)
    }
  }
  
def cuboid(side, length, height):
  volume = side * length * height
  curved_surface_area = (2*height) * (side+length)
  surface_area = 2 * ((side*length) + (length*height) + (side*height))
  return {
    'status': 200,
    'message': '',
    'data': {
      'volume': round(volume, 2),
      'curved_surface_area': round(curved_surface_area, 2),
      'surface_area': round(surface_area, 2)
    }
  }