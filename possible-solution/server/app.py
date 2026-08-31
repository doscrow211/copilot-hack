# Create a base Flask server

import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Secure CORS - restrict to specific origins
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

@app.after_request
def after_request(response):
    """
    Enable CORS with origin validation
    """
    origin = request.headers.get('Origin')
    if origin in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


# Load model from JSON file (safer than pickle)
# Replace pickle with a safer format like joblib or ONNX for production
def load_model():
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'model.json')
        with open(model_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to load model: {str(e)}")

model = load_model()

# Model takes two parameters - day of week and airport id, then returns a prediction of flight delay
@app.route('/predict', methods=['GET'])
def predict():
    """
    Takes two parameters - day of week and airport id, then returns a prediction of flight delay
    """
    try:
        # Validate and convert parameters
        day_of_week = request.args.get('day_of_week')
        airport_id = request.args.get('airport_id')
        
        # Validate inputs
        if not day_of_week or not airport_id:
            return jsonify({'error': 'Missing required parameters: day_of_week and airport_id'}), 400
        
        # Convert to int with validation
        try:
            day_of_week = int(day_of_week)
            airport_id = int(airport_id)
        except ValueError:
            return jsonify({'error': 'Invalid input: day_of_week and airport_id must be integers'}), 400
        
        # Validate ranges
        if not (0 <= day_of_week <= 6):
            return jsonify({'error': 'day_of_week must be between 0 and 6'}), 400
        
        if airport_id < 0:
            return jsonify({'error': 'airport_id must be a positive integer'}), 400
        
        # TODO: Replace with actual model prediction logic
        # For now, returning placeholder - use joblib or ONNX for real models
        prediction = model.get('predictions', {}).get(f'{day_of_week}_{airport_id}', [0.5, 0.5])
        
        return jsonify({'certainty': prediction[0], 'delay': prediction[1]})
    
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Create a new route called airports with method of get
@app.route('/airports', methods=['GET'])
def airports():
    try:
        # Use absolute path for security
        airports_path = os.path.join(os.path.dirname(__file__), 'airports.csv')
        
        with open(airports_path, 'r') as f:
            airports_data = f.readlines()
        
        # Remove first line (header)
        if airports_data:
            airports_data.pop(0)
        
        # Parse and validate airport data
        result = []
        for airport in airports_data:
            try:
                parts = airport.strip().split(',')
                if len(parts) >= 2:
                    airport_id = int(parts[0])
                    airport_name = parts[1]
                    result.append({'id': airport_id, 'name': airport_name})
            except (ValueError, IndexError):
                app.logger.warning(f"Skipping malformed airport entry: {airport}")
                continue
        
        # Sort by name
        result = sorted(result, key=lambda k: k['name'])
        
        return jsonify(result)
    
    except FileNotFoundError:
        app.logger.error("airports.csv not found")
        return jsonify({'error': 'Airports data not available'}), 500
    except Exception as e:
        app.logger.error(f"Airports retrieval error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Debug mode should be disabled in production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)