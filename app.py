from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir acceso desde otros dispositivos en la red

# Base de datos en memoria (puedes luego migrar a SQLite)
pedidos = []  # Lista para almacenar pedidos

@app.route('/')
def index():
    return "Servidor Flask en Heroku funcionando correctamente 🚀"

@app.route('/pedidos', methods=['POST'])
def registrar_pedido():
    data = request.get_json()
    pedido = {
        'id': len(pedidos) + 1,
        'mesa': data['mesa'],
        'fecha': datetime.now().isoformat(),
        'estado': 'pendiente',
        'items': data['items'],
    }
    pedidos.append(pedido)
    return jsonify({'mensaje': 'Pedido registrado', 'pedido': pedido}), 201

@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    estado = request.args.get('estado')
    if estado:
        resultado = [p for p in pedidos if p['estado'] == estado]
    else:
        resultado = pedidos
    return jsonify(resultado), 200

@app.route('/pedidos/<int:pedido_id>', methods=['PATCH'])
def actualizar_estado(pedido_id):
    for pedido in pedidos:
        if pedido['id'] == pedido_id:
            pedido['estado'] = 'listo'
            return jsonify({'mensaje': 'Estado actualizado', 'pedido': pedido}), 200
    return jsonify({'mensaje': 'Pedido no encontrado'}), 404

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

