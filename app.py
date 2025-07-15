from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from collections import defaultdict
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# 🔒 Usa una variable de entorno en producción
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['pedidosapp']
pedidos_collection = db['pedidos']


@app.route('/')
def index():
    return "Servidor Flask con MongoDB funcionando 🚀"


@app.route('/pedidos', methods=['POST'])
def registrar_pedido():
    data = request.get_json()
    pedido = {
        'mesa': data['mesa'],
        'fecha': datetime.now().isoformat(),
        'estado': 'pendiente',
        'pagado': data.get('pagado', False),
        'metodo_pago': data.get('metodo_pago', 'efectivo'),
        'items': data['items'],
        'para_resumen': False,
        'resumen_guardado': False
    }
    result = pedidos_collection.insert_one(pedido)
    pedido['_id'] = str(result.inserted_id)
    return jsonify({'mensaje': 'Pedido registrado', 'pedido': pedido}), 201


@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    estado = request.args.get('estado')
    para_resumen = request.args.get('para_resumen')

    filtro = {}
    if estado:
        filtro['estado'] = estado
    if para_resumen is not None:
        filtro['para_resumen'] = para_resumen.lower() == 'true'

    pedidos = list(pedidos_collection.find(filtro))
    for p in pedidos:
        p['_id'] = str(p['_id'])
    return jsonify(pedidos), 200


@app.route('/pedidos/<string:pedido_id>', methods=['PATCH'])
def actualizar_pedido(pedido_id):
    from bson.objectid import ObjectId
    data = request.get_json()
    actualizacion = {}

    if 'estado' in data:
        actualizacion['estado'] = data['estado']
        if data['estado'] == 'listo':
            actualizacion['para_resumen'] = True
            actualizacion['resumen_guardado'] = False
    if 'pagado' in data:
        actualizacion['pagado'] = data['pagado']
    if 'metodo_pago' in data:
        actualizacion['metodo_pago'] = data['metodo_pago']
    if 'para_resumen' in data:
        actualizacion['para_resumen'] = data['para_resumen']

    result = pedidos_collection.update_one({'_id': ObjectId(pedido_id)}, {'$set': actualizacion})
    if result.modified_count:
        return jsonify({'mensaje': 'Pedido actualizado'}), 200
    return jsonify({'mensaje': 'Pedido no encontrado'}), 404


@app.route('/pedidos/<string:pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    from bson.objectid import ObjectId
    result = pedidos_collection.delete_one({'_id': ObjectId(pedido_id)})
    if result.deleted_count:
        return jsonify({'mensaje': 'Pedido eliminado'}), 200
    return jsonify({'mensaje': 'Pedido no encontrado'}), 404


@app.route('/pedidos_por_dia', methods=['GET'])
def obtener_pedidos_agrupados():
    pedidos = list(pedidos_collection.find({}))
    agrupado = defaultdict(list)
    for p in pedidos:
        fecha = p['fecha'][:10]
        p['_id'] = str(p['_id'])
        agrupado[fecha].append(p)
    return jsonify(agrupado), 200


@app.route('/guardar_resumen_dia', methods=['POST'])
def guardar_resumen_dia():
    fecha_actual = datetime.now().isoformat()[:10]
    filtro = {
        'estado': 'listo',
        'para_resumen': True,
        'resumen_guardado': False,
        'fecha': {'$regex': f'^{fecha_actual}'}
    }
    result = pedidos_collection.update_many(filtro, {'$set': {'resumen_guardado': True}})
    return jsonify({'mensaje': f'{result.modified_count} pedidos marcados como resumen guardado'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
