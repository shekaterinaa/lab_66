from flask import Flask, jsonify, request
import socket  
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'instance': '5001'})

@app.route('/process', methods=['GET'])  
def process():
    return jsonify({"instance_id": get_instance_id(5001)}), 200  

def get_instance_id(port):
    hostname = socket.gethostname()
    return f"{hostname}:{port}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)







