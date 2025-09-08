import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename # --- ADDED ---
from libraries.math.complex import factorial, log, power, quadratic, sqrt
from libraries.math.simple import add, divide, multiply, subtract
from libraries.math.twoD import circle, rectangle, square, triangle
from libraries.math.threeD import cube, cuboid, cylinder, sphere
from libraries.securities import decode_morse, encode_morse
from libraries.ner import analyze_text, analyze_summarize, text_generator, analyze_sentiment
from chat import chat, generate_image, classify_image # --- MODIFIED: Added classify_image ---
from libraries.math.statisticts import mean_ungroup, mean_group, median_ungroup, median_group, mode_ungroup, mode_group, standard_deviation
import math

app = Flask(__name__, static_url_path='/static', static_folder='static')

base_dir = os.path.dirname(os.path.abspath(__file__))

aim_trainer_path = os.path.join(base_dir, "libraries/games/dist/aim_trainer.exe")
coin_catcher_path = os.path.join(base_dir, "libraries/games/dist/coin_catcher.exe")
clock_path = os.path.join(base_dir, "dist/dual_clock.exe")

# --- ADDED: Configuration for file uploads ---
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# --- END ADDED ---

@app.route('/')
def index():
  return send_from_directory('static', 'index.html')

@app.route("/chat", methods=['POST'])
def chat_op():
  data = request.get_json()
  text = data.get('text')
  resp = chat(text)
  return jsonify({
    "reply": resp
  })
  
@app.route("/image", methods=['POST'])
def image():
  data = request.get_json()
  text = data.get('text')
  resp = generate_image(text)
  return jsonify({
    "image": resp
  })

# --- ADDED: New route for handling image classification uploads ---
@app.route("/classify_image", methods=['POST'])
def classify_image_op():
  if 'file' not in request.files:
    return jsonify({"error": "No file part"}), 400
  
  file = request.files['file']
  
  if file.filename == '':
    return jsonify({"error": "No selected file"}), 400
  
  prompt = request.form.get('prompt', "Describe this image in detail.")

  if file:
    filename = secure_filename(file.filename or "uploaded_file")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    description = classify_image(prompt, filepath)
    
    image_url = f'/uploads/{filename}'

    return jsonify({
        "description": description,
        "image_url": image_url
    })
  
  return jsonify({"error": "File processing failed"}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
# --- END ADDED ---

@app.route("/aim_trainer")
def aim_trainer():
  subprocess.Popen([aim_trainer_path])
  return "Aim Trainer Launched!"

@app.route("/coin_catcher")
def coin_catcher():
  subprocess.Popen([coin_catcher_path])
  return "Coin Catcher Launched!"

@app.route("/dual_clock")
def dual_clock():
  subprocess.Popen([clock_path])
  return "Dual Clock Launched!"

# Route for basic NER
@app.route('/ner/tagging', methods=['POST'])
def ner_tagging():
  data = request.get_json()
  text = data.get('text')
  resp = analyze_text(text)
  return jsonify(resp), resp['status']

@app.route('/ner/sentiment', methods=['POST'])
def ner_sentiment():
  data = request.get_json()
  text = data.get('text')
  resp = analyze_sentiment(text)
  return jsonify(resp), resp['status']

@app.route('/ner/summarize', methods=['POST'])
def ner_summarize():  
  data = request.get_json()
  text = data.get('text')
  resp = analyze_summarize(text)
  return jsonify(resp), resp['status']

@app.route('/ner/generator', methods=['POST'])
def ner_generator():
  data = request.get_json()
  text = data.get('text')
  resp = text_generator(text)
  return jsonify(resp), resp['status']

# Simple math operations
@app.route('/math/simple/add', methods=['GET'])
def add_op():
  a_str = request.args.get('a')
  b_str = request.args.get('b')
  if a_str is None or b_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters a or b'}), 400
  a = float(a_str)
  b = float(b_str)
  resp = add(a, b)
  return jsonify(resp), resp['status']

@app.route('/math/simple/subtract', methods=['GET'])
def subtract_op():
  a_str = request.args.get('a')
  b_str = request.args.get('b')
  if a_str is None or b_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters a or b'}), 400
  a = float(a_str)
  b = float(b_str)
  resp = subtract(a, b)
  return jsonify(resp), resp['status']

@app.route('/math/simple/multiply', methods=['GET'])
def multiply_op():
  a_str = request.args.get('a')
  b_str = request.args.get('b')
  if a_str is None or b_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters a or b'}), 400
  a = float(a_str)
  b = float(b_str)
  resp = multiply(a, b)
  return jsonify(resp), resp['status']

@app.route('/math/simple/divide', methods=['GET'])
def divide_op():
  a_str = request.args.get('a')
  b_str = request.args.get('b')
  if a_str is None or b_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters a or b'}), 400
  a = float(a_str)
  b = float(b_str)
  resp = divide(a, b)
  return jsonify(resp), resp['status']

# Complex math operations
@app.route('/math/complex/factorial', methods=['GET'])
def factorial_op():
  n_str = request.args.get('n')
  if n_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter n'}), 400
  n = int(n_str)
  resp = factorial(n)
  return jsonify(resp), resp['status']

@app.route('/math/complex/power', methods=['GET'])
def power_op():
  base_str = request.args.get('base')
  exp_str = request.args.get('exp')
  if base_str is None or exp_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters base or exp'}), 400
  base = float(base_str)
  exp = float(exp_str)
  resp = power(base, exp)
  return jsonify(resp), resp['status']

@app.route('/math/complex/sqrt', methods=['GET'])
def sqrt_op():
  num_str = request.args.get('num')
  if num_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter num'}), 400
  num = float(num_str)
  resp = sqrt(num)
  return jsonify(resp), resp['status']

@app.route('/math/complex/log', methods=['GET'])
def log_op():
  num_str = request.args.get('num')
  if num_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter num'}), 400
  num = float(num_str)
  base = request.args.get('base')
  resp = log(num, base)
  return jsonify(resp), resp['status']

# Quadratic function solver
@app.route('/math/complex/quadratic', methods=['GET'])
def quadratic_op():
  # Get the coefficients a, b, and c from the query parameters
  a_str = request.args.get('a')
  b_str = request.args.get('b')
  c_str = request.args.get('c')
  if a_str is None or b_str is None or c_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters a, b, or c'}), 400
  a = float(a_str)
  b = float(b_str)
  c = float(c_str)

  resp = quadratic(a, b, c)
  return jsonify(resp), resp['status']

# 2D Shapes
@app.route('/math/2d/rectangle', methods=['GET'])
def rectangle_op():
  width_str = request.args.get('width')
  height_str = request.args.get('height')
  if width_str is None or height_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters width or height'}), 400
  width = float(width_str)
  height = float(height_str)
  resp = rectangle(width, height)
  return jsonify(resp), resp['status']

@app.route('/math/2d/circle', methods=['GET'])
def circle_op():
  radius_str = request.args.get('radius')
  if radius_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter radius'}), 400
  radius = float(radius_str)
  resp = circle(radius)
  return jsonify(resp), resp['status']

@app.route('/math/2d/square', methods=['GET'])
def square_op():
  side_str = request.args.get('side')
  if side_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter side'}), 400
  side = float(side_str)
  resp = square(side)
  return jsonify(resp), resp['status']

@app.route('/math/2d/triangle', methods=['GET'])
def triangle_op():
  width_str = request.args.get('width')
  height_str = request.args.get('height')
  side_str = request.args.get('side')
  if width_str is None or height_str is None or side_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters width, height, or side'}), 400
  width = float(width_str)
  height = float(height_str)
  side = float(side_str)
  resp = triangle(width, height, side)
  return jsonify(resp), resp['status']

# 3D Shapes
@app.route('/math/3d/cube', methods=['GET'])
def cube_op():
  side_str = request.args.get('side')
  if side_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter side'}), 400
  side = float(side_str)
  resp = cube(side)
  return jsonify(resp), resp['status']

@app.route('/math/3d/sphere', methods=['GET'])
def sphere_op():
  radius_str = request.args.get('radius')
  if radius_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter radius'}), 400
  radius = float(radius_str)
  resp = sphere(radius)
  return jsonify(resp), resp['status']

@app.route('/math/3d/cylinder', methods=['GET'])
def cylinder_op():
  radius_str = request.args.get('radius')
  height_str = request.args.get('radius')
  if radius_str is None or height_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameter radius'}), 400
  radius = float(radius_str)
  height = float(height_str)
  resp = cylinder(radius, height)
  return jsonify(resp), resp['status']

@app.route('/math/3d/cuboid', methods=['GET'])
def cuboid_op():
  side_str = request.args.get('side')
  length_str = request.args.get('length')
  height_str = request.args.get('height')
  # Check if all required parameters are provided
  if side_str is None or length_str is None or height_str is None:
    return jsonify({'status': 400, 'message': 'Missing parameters side or length'}), 400
  side = float(side_str)
  length = float(length_str)
  height = float(height_str)
  resp = cuboid(side, length, height)
  return jsonify(resp), resp['status']

@app.route('/bmi', methods=['POST'])
def bmi():
  data = request.get_json()
  weight = data.get('weight')
  height = data.get('height')/100
  bmi = weight / (height*height)
  x = float("{:.2f}".format(bmi))
  
  if(x>0):
    if(x<=16):
      result = "You are very underweight"
    elif(x<=18.5):
      result = "You are underweight"
    elif(x<=25):
      result = "Congrats! You are Healthy"
    elif(x<=30):
      result = "You are overweight"
    else: 
      result = "You are very overweight"
  else:
    return jsonify({
      'status': 401,
      'message': "enter valid details"
    }), 401
    
  return jsonify({
    'status': 200,
    'message': '',
    'data': {
      'bmi': x,
      'result': result
    }
  }), 200

@app.route('/decode_morse', methods=['POST'])
def decode_morse_op():
  data = request.get_json()
  morse = data.get('morse')
  resp = decode_morse(morse)
  return jsonify(resp), 200

@app.route('/encode_morse', methods=['POST'])
def encode_morse_op():
  data = request.get_json()
  text = data.get('text')
  resp = encode_morse(text)
  return jsonify(resp), 200

@app.route('/scientific_calc')
def scientific_calc():
  expr = request.args.get('expr', '')
  try:
    # Safe eval: allow only math functions/constants
    allowed_names = {
      k: getattr(math, k) for k in [
        'sin', 'cos', 'tan', 'log', 'sqrt', 'exp', 'fabs', 'factorial', 'pi', 'e', 'pow'
      ]
    }
    allowed_names['abs'] = abs
    allowed_names['^'] = pow
    # Replace ^ with ** for exponentiation
    expr = expr.replace('^', '**')
    # Evaluate expression
    result = eval(expr, {"__builtins__": None}, allowed_names)
    return jsonify({'status': 200, 'result': result})
  except Exception as ex:
    return jsonify({'status': 400, 'message': f'Error: {str(ex)}'})

# Statistics operations
@app.route('/math/stats/mean', methods=['POST'])
def mean_op():
  try:
    data = request.get_json()
    if 'numbers' in data:  # Ungrouped data
      numbers = data['numbers']
      result = mean_ungroup(numbers)
    else:  # Grouped data
      lower_bound = data.get('lower_bound')
      class_width = data.get('class_width')
      frequencies = data.get('frequencies')
      result = mean_group(lower_bound, class_width, frequencies)
    return jsonify({'status': 200, 'data': {'result': result}})
  except Exception as e:
    return jsonify({'status': 500, 'message': str(e)}), 500

@app.route('/math/stats/median', methods=['POST'])
def median_op():
  try:
    data = request.get_json()
    if 'numbers' in data:  # Ungrouped data
      numbers = data['numbers']
      result = median_ungroup(numbers)
    else:  # Grouped data
      lower_bound = data.get('lower_bound')
      class_width = data.get('class_width')
      frequencies = data.get('frequencies')
      result = median_group(lower_bound, class_width, frequencies)
    return jsonify({'status': 200, 'data': {'result': result}})
  except Exception as e:
    return jsonify({'status': 500, 'message': str(e)}), 500

@app.route('/math/stats/mode', methods=['POST'])
def mode_op():
  try:
    data = request.get_json()
    if 'numbers' in data:  # Ungrouped data
      numbers = data['numbers']
      result = mode_ungroup(numbers)
    else:  # Grouped data
      lower_bound = data.get('lower_bound')
      class_width = data.get('class_width')
      frequencies = data.get('frequencies')
      result = mode_group(lower_bound, class_width, frequencies)
    return jsonify({'status': 200, 'data': {'result': result}})
  except Exception as e:
    return jsonify({'status': 500, 'message': str(e)}), 500

@app.route('/math/stats/stdev', methods=['POST'])
def stdev_op():
  try:
    data = request.get_json()
    numbers = data.get('numbers', [])
    if not numbers or len(numbers) < 2:
      return jsonify({'status': 400, 'message': 'Need at least 2 numbers'}), 400
    result = standard_deviation(numbers)
    return jsonify({'status': 200, 'data': {'result': result}})
  except Exception as e:
    return jsonify({'status': 500, 'message': str(e)}), 500

if __name__ == "__main__":
  app.run(debug=True, threaded=True)