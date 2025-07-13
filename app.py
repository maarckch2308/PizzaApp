from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)

pedidos = []

@app.route('/')
def index():
    return "Servidor Flask funcionando correctamente 🚀"

@app.route('/pedidos', methods=['POST'])
def registrar_pedido():
    data = request.get_json()
    pedido = {
        'id': len(pedidos) + 1,
        'mesa': data['mesa'],
        'fecha': datetime.now().isoformat(),
        'estado': 'pendiente',
        'pagado': data.get('pagado', False),
        'metodo_pago': data.get('metodo_pago', 'efectivo'),
        'items': data['items'],
        'para_resumen': False,  # Nuevo campo para resumen
    }
    pedidos.append(pedido)
    return jsonify({'mensaje': 'Pedido registrado', 'pedido': pedido}), 201

@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    estado = request.args.get('estado')
    para_resumen = request.args.get('para_resumen')

    resultado = pedidos

    if estado:
        resultado = [p for p in resultado if p['estado'] == estado]

    if para_resumen is not None:
        # Convertir string a bool
        para_resumen_bool = para_resumen.lower() == 'true'
        resultado = [p for p in resultado if p.get('para_resumen', False) == para_resumen_bool]

    return jsonify(resultado), 200

@app.route('/pedidos/<int:pedido_id>', methods=['PATCH'])
def actualizar_pedido(pedido_id):
    data = request.get_json()
    for pedido in pedidos:
        if pedido['id'] == pedido_id:
            # Actualizar los campos que se envíen
            if 'estado' in data:
                pedido['estado'] = data['estado']
            if 'pagado' in data:
                pedido['pagado'] = data['pagado']
            if 'metodo_pago' in data:
                pedido['metodo_pago'] = data['metodo_pago']
            if 'para_resumen' in data:
                pedido['para_resumen'] = data['para_resumen']
            return jsonify({'mensaje': 'Pedido actualizado', 'pedido': pedido}), 200
    return jsonify({'mensaje': 'Pedido no encontrado'}), 404

@app.route('/pedidos_por_dia', methods=['GET'])
def obtener_pedidos_agrupados():
    agrupado = defaultdict(list)
    for pedido in pedidos:
        fecha = pedido['fecha'][:10]  # YYYY-MM-DD
        agrupado[fecha].append(pedido)
    return jsonify(agrupado), 200

@app.route('/pedidos/<int:pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    global pedidos
    for pedido in pedidos:
        if pedido['id'] == pedido_id:
            pedidos = [p for p in pedidos if p['id'] != pedido_id]
            return jsonify({'mensaje': 'Pedido eliminado'}), 200
    return jsonify({'mensaje': 'Pedido no encontrado'}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
