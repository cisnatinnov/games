"""
Math operations blueprint.
Consolidates all math-related routes with proper validation and error handling.
"""
from flask import Blueprint, request, jsonify
from middleware.security import rate_limit, validate_positive_number, validate_non_negative_number, validate_integer

math_bp = Blueprint('math', __name__, url_prefix='/math')

# Import math functions
from libraries.math.simple import add, divide, multiply, subtract
from libraries.math.complex import factorial, log, power, quadratic, sqrt
from libraries.math.twoD import circle, rectangle, square, triangle
from libraries.math.threeD import (
    cube, cuboid, cylinder, sphere, 
    triangular_prism, rectangular_prism, 
    pentagonal_prism, hexagonal_prism
)
from libraries.math.statisticts import (
    mean_ungroup, mean_group, 
    median_ungroup, median_group, 
    mode_ungroup, mode_group, 
    standard_deviation
)

def _get_float_params(params, *param_names):
    """Helper to extract and validate float parameters."""
    values = []
    for name in param_names:
        val = params.get(name)
        if val is None:
            return None, f"Missing parameter: {name}"
        try:
            values.append(float(val))
        except (TypeError, ValueError):
            return None, f"Invalid parameter {name}: must be a number"
    return values, None

# ==================== Simple Math Operations ====================

@math_bp.route('/simple/add', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def add_op():
    params = request.args
    result, error = _get_float_params(params, 'a', 'b')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = add(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/simple/subtract', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def subtract_op():
    params = request.args
    result, error = _get_float_params(params, 'a', 'b')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = subtract(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/simple/multiply', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def multiply_op():
    params = request.args
    result, error = _get_float_params(params, 'a', 'b')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = multiply(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/simple/divide', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def divide_op():
    params = request.args
    result, error = _get_float_params(params, 'a', 'b')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    # Additional validation for division
    if result[1] == 0:
        return jsonify({'status': 400, 'message': 'Division by zero is not allowed'}), 400
    resp = divide(*result)
    return jsonify(resp), resp['status']

# ==================== Complex Math Operations ====================

@math_bp.route('/complex/factorial', methods=['GET'])
@rate_limit(max_requests=500, window_seconds=3600)
def factorial_op():
    n_str = request.args.get('n')
    if n_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter n'}), 400
    n, error = validate_integer(n_str, 'n', min_val=0, max_val=170)
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = factorial(n)
    return jsonify(resp), resp['status']

@math_bp.route('/complex/power', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def power_op():
    params = request.args
    result, error = _get_float_params(params, 'base', 'exp')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = power(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/complex/sqrt', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def sqrt_op():
    num_str = request.args.get('num')
    if num_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter num'}), 400
    num, error = validate_non_negative_number(num_str, 'num')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = sqrt(num)
    return jsonify(resp), resp['status']

@math_bp.route('/complex/log', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def log_op():
    num_str = request.args.get('num')
    if num_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter num'}), 400
    
    num, error = validate_positive_number(num_str, 'num')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    
    base = request.args.get('base')
    if base:
        base_val, error = validate_positive_number(base, 'base')
        if error:
            return jsonify({'status': 400, 'message': error}), 400
        # Validate base is not 1
        if base_val == 1:
            return jsonify({'status': 400, 'message': 'Base cannot be 1'}), 400
    else:
        base_val = None
    
    resp = log(num, base_val)
    return jsonify(resp), resp['status']

@math_bp.route('/complex/quadratic', methods=['GET'])
@rate_limit(max_requests=500, window_seconds=3600)
def quadratic_op():
    params = request.args
    result, error = _get_float_params(params, 'a', 'b', 'c')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    # Validate a is not zero
    if result[0] == 0:
        return jsonify({'status': 400, 'message': 'Coefficient a cannot be zero'}), 400
    resp = quadratic(*result)
    return jsonify(resp), resp['status']

# ==================== 2D Shapes ====================

@math_bp.route('/2d/rectangle', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def rectangle_op():
    params = request.args
    result, error = _get_float_params(params, 'width', 'height')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if result[0] <= 0 or result[1] <= 0:
        return jsonify({'status': 400, 'message': 'Width and height must be positive'}), 400
    resp = rectangle(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/2d/circle', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def circle_op():
    radius_str = request.args.get('radius')
    if radius_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter radius'}), 400
    radius, error = validate_positive_number(radius_str, 'radius')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = circle(radius)
    return jsonify(resp), resp['status']

@math_bp.route('/2d/square', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def square_op():
    side_str = request.args.get('side')
    if side_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter side'}), 400
    side, error = validate_positive_number(side_str, 'side')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = square(side)
    return jsonify(resp), resp['status']

@math_bp.route('/2d/triangle', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def triangle_op():
    params = request.args
    result, error = _get_float_params(params, 'width', 'height', 'side')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if any(v <= 0 for v in result):
        return jsonify({'status': 400, 'message': 'All dimensions must be positive'}), 400
    resp = triangle(*result)
    return jsonify(resp), resp['status']

# ==================== 3D Shapes ====================

@math_bp.route('/3d/cube', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def cube_op():
    side_str = request.args.get('side')
    if side_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter side'}), 400
    side, error = validate_positive_number(side_str, 'side')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = cube(side)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/sphere', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def sphere_op():
    radius_str = request.args.get('radius')
    if radius_str is None:
        return jsonify({'status': 400, 'message': 'Missing parameter radius'}), 400
    radius, error = validate_positive_number(radius_str, 'radius')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    resp = sphere(radius)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/cylinder', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def cylinder_op():
    params = request.args
    result, error = _get_float_params(params, 'radius', 'height')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if result[0] <= 0 or result[1] <= 0:
        return jsonify({'status': 400, 'message': 'Radius and height must be positive'}), 400
    resp = cylinder(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/cuboid', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def cuboid_op():
    params = request.args
    result, error = _get_float_params(params, 'side', 'length', 'height')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if any(v <= 0 for v in result):
        return jsonify({'status': 400, 'message': 'All dimensions must be positive'}), 400
    resp = cuboid(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/triangular_prism', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def triangular_prism_op():
    params = request.args
    result, error = _get_float_params(params, 'base', 'height', 'length')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if any(v <= 0 for v in result):
        return jsonify({'status': 400, 'message': 'All dimensions must be positive'}), 400
    resp = triangular_prism(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/rectangular_prism', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def rectangular_prism_op():
    params = request.args
    result, error = _get_float_params(params, 'width', 'height', 'length')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if any(v <= 0 for v in result):
        return jsonify({'status': 400, 'message': 'All dimensions must be positive'}), 400
    resp = rectangular_prism(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/pentagonal_prism', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def pentagonal_prism_op():
    params = request.args
    result, error = _get_float_params(params, 'side', 'height')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if result[0] <= 0 or result[1] <= 0:
        return jsonify({'status': 400, 'message': 'Side and height must be positive'}), 400
    resp = pentagonal_prism(*result)
    return jsonify(resp), resp['status']

@math_bp.route('/3d/hexagonal_prism', methods=['GET'])
@rate_limit(max_requests=1000, window_seconds=3600)
def hexagonal_prism_op():
    params = request.args
    result, error = _get_float_params(params, 'side', 'height')
    if error:
        return jsonify({'status': 400, 'message': error}), 400
    if result[0] <= 0 or result[1] <= 0:
        return jsonify({'status': 400, 'message': 'Side and height must be positive'}), 400
    resp = hexagonal_prism(*result)
    return jsonify(resp), resp['status']

# ==================== Statistics Operations ====================

@math_bp.route('/stats/mean', methods=['POST'])
@rate_limit(max_requests=500, window_seconds=3600)
def mean_op():
    from flask import request as req
    data = req.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    try:
        if 'numbers' in data:  # Ungrouped data
            numbers = data['numbers']
            if not isinstance(numbers, list) or len(numbers) == 0:
                return jsonify({'status': 400, 'message': 'Numbers must be a non-empty list'}), 400
            result = mean_ungroup(numbers)
        else:  # Grouped data
            lower_bound = data.get('lower_bound')
            class_width = data.get('class_width')
            frequencies = data.get('frequencies')
            if not all([lower_bound, class_width, frequencies]):
                return jsonify({'status': 400, 'message': 'Missing required parameters for grouped data'}), 400
            result = mean_group(lower_bound, class_width, frequencies)
        return jsonify({'status': 200, 'data': {'result': result}})
    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500

@math_bp.route('/stats/median', methods=['POST'])
@rate_limit(max_requests=500, window_seconds=3600)
def median_op():
    from flask import request as req
    data = req.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    try:
        if 'numbers' in data:
            numbers = data['numbers']
            if not isinstance(numbers, list) or len(numbers) == 0:
                return jsonify({'status': 400, 'message': 'Numbers must be a non-empty list'}), 400
            result = median_ungroup(numbers)
        else:
            lower_bound = data.get('lower_bound')
            class_width = data.get('class_width')
            frequencies = data.get('frequencies')
            if not all([lower_bound, class_width, frequencies]):
                return jsonify({'status': 400, 'message': 'Missing required parameters for grouped data'}), 400
            result = median_group(lower_bound, class_width, frequencies)
        return jsonify({'status': 200, 'data': {'result': result}})
    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500

@math_bp.route('/stats/mode', methods=['POST'])
@rate_limit(max_requests=500, window_seconds=3600)
def mode_op():
    from flask import request as req
    data = req.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    try:
        if 'numbers' in data:
            numbers = data['numbers']
            if not isinstance(numbers, list) or len(numbers) == 0:
                return jsonify({'status': 400, 'message': 'Numbers must be a non-empty list'}), 400
            result = mode_ungroup(numbers)
        else:
            lower_bound = data.get('lower_bound')
            class_width = data.get('class_width')
            frequencies = data.get('frequencies')
            if not all([lower_bound, class_width, frequencies]):
                return jsonify({'status': 400, 'message': 'Missing required parameters for grouped data'}), 400
            result = mode_group(lower_bound, class_width, frequencies)
        return jsonify({'status': 200, 'data': {'result': result}})
    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500

@math_bp.route('/stats/stdev', methods=['POST'])
@rate_limit(max_requests=500, window_seconds=3600)
def stdev_op():
    from flask import request as req
    data = req.get_json()
    if not data:
        return jsonify({'status': 400, 'message': 'Invalid JSON'}), 400
    
    try:
        numbers = data.get('numbers', [])
        if not isinstance(numbers, list) or len(numbers) < 2:
            return jsonify({'status': 400, 'message': 'Need at least 2 numbers'}), 400
        result = standard_deviation(numbers)
        return jsonify({'status': 200, 'data': {'result': result}})
    except Exception as e:
        return jsonify({'status': 500, 'message': str(e)}), 500
