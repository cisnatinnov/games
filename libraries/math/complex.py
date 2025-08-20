import math

def factorial(n):
  try:
    factorial_op = round(math.factorial(n), 2)
    response = {
      'status': 200,
      'message': '',
      'data': {
        'result': factorial_op
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response

def power(base, exp):
  try:
    power_op = round(math.pow(base, exp), 2)
    response = {
      'status': 200,
      'message': '',
      'data': {
        'result': power_op
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response

def sqrt(num):
  try:
    power_op = round(math.sqrt(num), 2)
    response = {
      'status': 200,
      'message': '',
      'data': {
        'result': power_op
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response

def log(num, base):
  try:
    if base:
      base = float(base)
      log_op = round(math.log(num, base), 2)
    
    log_op = round(math.log(num), 2)
    response = {
      'status': 200,
      'message': '',
      'data': {
        'result': log_op
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response

# Quadratic function solver
def quadratic(a, b, c):
  try:
    # Calculate the discriminant (b^2 - 4ac)
    discriminant = b**2 - 4*a*c

    # Check if discriminant is negative, zero, or positive
    if discriminant < 0:
      response = {
        'status': 400,
        'message': 'No real roots, discriminant is negative',
        'data': {}
      }
    elif discriminant == 0:
      # One real root
      x = -b / (2*a)
      response = {
        'status': 200,
        'message': '',
        'data': {
          'root': round(x, 2)
        }
      }
    else:
      # Two real roots
      root1 = (-b + math.sqrt(discriminant)) / (2*a)
      root2 = (-b - math.sqrt(discriminant)) / (2*a)
      response = {
        'status': 200,
        'message': '',
        'data': {
          'root1': round(root1, 2),
          'root2': round(root2, 2)
        }
      }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response
