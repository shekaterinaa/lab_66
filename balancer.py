from flask import Flask, request, jsonify, render_template
import requests
from threading import Thread
import time

app = Flask(__name__)


instances = []
current_index = 0


def health_check():
    while True:
        for instance in instances[:]:
            try:
                response = requests.get(f"http://{instance}/health")
               
                if response.status_code != 200:
                    print(f"Убираем недоступный инстанс: {instance}")
                    instances.remove(instance)
            except requests.exceptions.RequestException:
                print(f"Ошибка подключения, убираем инстанс: {instance}")
                instances.remove(instance)

        
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html', instances=instances)

@app.route('/process')
def process():
    global current_index
    if not instances:
        return jsonify({"error": "Нет доступных "}), 500
    instance = instances[current_index]
    current_index = (current_index + 1) % len(instances)
    response = requests.get(f"http://{instance}/process")
    return jsonify(response.json())

@app.route('/health')
def health():
    health_status = {}
    for instance in instances:
        try:
            response = requests.get(f"http://{instance}/health")
            health_status[instance] = response.json() 
        except requests.exceptions.RequestException:
            health_status[instance] = {"status": "unreachable"}  
    
    return jsonify({"instances": health_status, "active_count": len(instances)}), 200

@app.route('/add_instance', methods=['POST'])
def add_instance():
    data = request.json
    instance = f"{data['ip']}:{data['port']}"
    instances.append(instance)
    return jsonify({"message": "Инстанс добавлен."}), 201

@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    data = request.json
    index = data['index']
    if 0 <= index < len(instances):
        removed = instances.pop(index)
        return jsonify({"message": f"Удален инстанс {removed}."}), 200
    return jsonify({"error": "Недопустимый индекс."}), 400


@app.route('/<path:path>', methods=["GET", "POST"])
def catch_all(path):
    global current_index
    if not instances:
        return jsonify({"error": "Нет доступных инстансов"}), 500
    
    instance = instances[current_index]
    current_index = (current_index + 1) % len(instances)
    
   
    if request.method == "GET":
        response = requests.get(f"http://{instance}/{path}", params=request.args)
    else:
        response = requests.post(f"http://{instance}/{path}", json=request.json)
    
    return jsonify(response.json())


thread = Thread(target=health_check, daemon=True)
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


