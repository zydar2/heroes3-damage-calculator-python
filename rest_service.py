from flask import Flask, request, jsonify
from flask_cors import CORS
from damage_calculations import calculate_damage
from battle_params import BattleParams

app = Flask(__name__)
CORS(app)

@app.route('/calculate-damage', methods=['POST'])
def calculate_data():
    try:
        json_params: str = request.get_json(force=True)
        battle_params: BattleParams = BattleParams(json_params)
        damage = calculate_damage(battle_params)
        return jsonify(damage), 200
    except Exception as e:
        raise e


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
