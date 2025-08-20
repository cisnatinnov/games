def add(a, b):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': a + b
    }
  }

def subtract(a, b):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': a - b
    }
  }

def multiply(a, b):
  return {
    'status': 200,
    'message': '',
    'data': {
      'result': a * b
    }
  }

def divide(a, b):
  if b == 0:
    return {
      'status': 400,
      'message': 'Division by zero is not allowed!',
      'data': {}
    }

  return {
    'status': 200,
    'message': '',
    'data': {
      'result': a / b
    }
  }