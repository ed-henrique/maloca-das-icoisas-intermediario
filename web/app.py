from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import re
import pytz
import os

utc = pytz.UTC

# Inicialização do Flask
app = Flask(__name__)

# Inicialização do Firebase Admin
cred = credentials.Certificate(
    r"/app/config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Configurações do MQTT
MQTT_BROKER = os.getenv('MOSQUITTO')
MQTT_PORT = 1883
MQTT_TOPIC = 'pacientes_pos_cirurgicos/monitoramento'


def esta_de_cabeca_para_baixo(x, y, z):
    margem_erro = 0.05

    if z + 0.95 < margem_erro and x < margem_erro and y < margem_erro:
        return True
    else:
        return False


def on_message(client, userdata, msg):
    try:
        data = msg.payload.decode('utf-8')

        if data == 'ALERT':
            return

        payload = {
            "temperatura": float(re.search(r"Temperature: ([\d.]+)", data).group(1)),
            "batimento_cardiaco": int(re.search(r"Heart Rate: (\d+)", data).group(1)),
            "movimento_x": float(re.search(r"Accel X: ([\d.-]+)", data).group(1)),
            "movimento_y": float(re.search(r"Accel Y: ([\d.-]+)", data).group(1)),
            "movimento_z": float(re.search(r"Accel Z: ([\d.-]+)", data).group(1)),
        }

        paciente_id = str(payload.get('paciente', 1))

        dados_atualizados = {
            'timestamp': firestore.SERVER_TIMESTAMP,
            'movimento_x': payload.get('movimento_x'),
            'movimento_y': payload.get('movimento_y'),
            'movimento_z': payload.get('movimento_z'),
            'temperatura': payload.get('temperatura'),
            'batimento_cardiaco': payload.get('batimento_cardiaco'),
        }

        conds = [
            dados_atualizados['batimento_cardiaco'] > 130,
            dados_atualizados['temperatura'] > 37.8,
            esta_de_cabeca_para_baixo(
                dados_atualizados['movimento_x'], dados_atualizados['movimento_y'], dados_atualizados['movimento_z']),
        ]

        if True in conds:
            client.publish(MQTT_TOPIC, b"ALERT")

        # Atualiza ou cria o documento do paciente no Firestore
        db.collection('pacientes').document(
            paciente_id).collection('dados').add(dados_atualizados)
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")


def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")


# Inicializa e conecta o cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.on_publish = on_publish
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_start()

# Rota para buscar dados do paciente com filtragem por período


@app.route('/pacientes', methods=['GET'])
def get_pacientes():
    try:
        paciente_id = '1'
        periodo_inicio = request.args.get('periodo_inicio')
        periodo_fim = request.args.get('periodo_fim')

        if not paciente_id:
            return jsonify({'erro': 'Parâmetro "paciente" é obrigatório.'}), 400
        if not periodo_inicio or not periodo_fim:
            return jsonify({'erro': 'Parâmetros "periodo_inicio" e "periodo_fim" são obrigatórios.'}), 400

        # Busca o documento do paciente
        doc_ref = db.collection('pacientes').document(
            str(paciente_id)).collection('dados')
        doc = doc_ref.get()

        periodo_inicio_novo = utc.localize(
            datetime.fromisoformat(periodo_inicio))
        periodo_fim_novo = utc.localize(datetime.fromisoformat(periodo_fim))

        filtered = []
        for record in doc:
            ts = record.get('timestamp')
            if isinstance(ts, datetime) and periodo_inicio_novo <= ts <= periodo_fim_novo:
                # Converte timestamp para string ISO
                filtered.append(record.to_dict())

        dado_retorno = filtered

        print(dado_retorno)
        return jsonify(dado_retorno), 200

    except Exception as e:
        return jsonify({'erro': f'Erro ao buscar dados: {e}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
