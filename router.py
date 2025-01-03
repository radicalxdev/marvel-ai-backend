from flask import Flask, request, jsonify
from features.text_rewriter.core import executor

app = Flask(__name__)

@app.route('/rewrite', methods=['POST'])
def rewrite_text():
    data = request.json
    input_data = data.get('input_data')
    instruction = data.get('instruction')
    try:
        result = executor(input_data, instruction)
        return jsonify({"rewritten_text": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)