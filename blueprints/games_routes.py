"""
Games and tools routes blueprint for launching games and other utilities.
"""
import os
import subprocess
from flask import Blueprint, jsonify

games_bp = Blueprint('games', __name__, url_prefix='/')

# Game paths - defined at module level
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
aim_trainer_path = os.path.join(base_dir, "libraries/games/dist/aim_trainer.exe")
coin_catcher_path = os.path.join(base_dir, "libraries/games/dist/coin_catcher.exe")
clock_path = os.path.join(base_dir, "dist/dual_clock.exe")

@games_bp.route("/aim_trainer")
def aim_trainer():
    if not os.path.exists(aim_trainer_path):
        return jsonify({"status": 404, "message": "Aim Trainer not found"}), 404
    subprocess.Popen([aim_trainer_path])
    return jsonify({"status": 200, "message": "Aim Trainer Launched!"})

@games_bp.route("/coin_catcher")
def coin_catcher():
    if not os.path.exists(coin_catcher_path):
        return jsonify({"status": 404, "message": "Coin Catcher not found"}), 404
    subprocess.Popen([coin_catcher_path])
    return jsonify({"status": 200, "message": "Coin Catcher Launched!"})

@games_bp.route("/dual_clock")
def dual_clock():
    if not os.path.exists(clock_path):
        return jsonify({"status": 404, "message": "Dual Clock not found"}), 404
    subprocess.Popen([clock_path])
    return jsonify({"status": 200, "message": "Dual Clock Launched!"})
