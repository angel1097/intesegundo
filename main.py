from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import threading
import subprocess
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db, firestore
from werkzeug.security import generate_password_hash, check_password_hash
import deteccion
import reconocimiento
import tensorflow as tf
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import analisis

app = Flask(__name__, static_folder="static")
app.secret_key = 'your_secret_key'  # Asegúrate de usar una clave secreta segura
CORS(app)

# Inicializa Firebase Admin SDK
cred = credentials.Certificate("config/credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cybiometrics-default-rtdb.firebaseio.com/'
})

# Obtén una referencia a Realtime Database
ref = db.reference()

# Configuración de la sesión
app.config.update(
    PERMANENT_SESSION_LIFETIME=600,  # Tiempo de vida de la sesión en segundos
    SESSION_COOKIE_SECURE=True,      # Asegúrate de usar HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Impide el acceso a la cookie desde JavaScript
    SESSION_COOKIE_SAMESITE='Lax'    # Protege contra ataques CSRF
)

@app.after_request
def after_request(response):
    # Añadir cabeceras de seguridad
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/registro_biometrico', methods=['POST'])
def registro_biometrico():
    nombre = request.form.get('nombre')
    id_trabajador = request.form.get('id_trabajador')

    if not nombre or not id_trabajador:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        hashed_id_trabajador = generate_password_hash(id_trabajador, method='pbkdf2:sha256')
        ref.child('usuarios').push({
            'nombre': nombre,
            'idTrabajador': hashed_id_trabajador
        })
        return redirect(url_for('bienvenida'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template("principal.html")

@app.route('/reingresarlogin')
def reingresarlogin():
    return render_template("principal.html")

@app.route('/menuPrincipal')
def menuPrincipal():
    return render_template("menuPrincipal.html")

@app.route('/panel')
def panel():
    return render_template("panel.html")

@app.route('/deteccion')
def deteccion_view():
    def run_deteccion():
        deteccion.iniciar_deteccion()

    threading.Thread(target=run_deteccion).start()
    return redirect(url_for('bienvenida'))

@app.route('/login_biometrico', methods=['POST'])
def login_biometrico():
    return redirect(url_for('reconocimiento_page'))

@app.route('/reconocimiento')
def reconocimiento_page():
    return render_template("reconocimiento.html")

@app.route('/bienvenida')
def bienvenida():
    return render_template("bienvenida.html")

@app.route('/registro_biometrico_script', methods=['POST'])
def registro_biometrico_script():
    def run_registro_biometrico():
        subprocess.run(["python", "registrobiometrico.py"])

    threading.Thread(target=run_registro_biometrico).start()
    return redirect(url_for('bienvenida'))

@app.route('/deteccion_view_post', methods=['POST'])
def deteccion_view_post():
    imagen_capturada = deteccion.iniciar_deteccion()
    if imagen_capturada:
        rostro_reconocido = reconocimiento.reconocer_rostro(imagen_capturada)
        if rostro_reconocido:
            return redirect(url_for('primer_filtro_rechazado'))
    return redirect(url_for('primer_filtro_autorizado'))

@app.route('/primer_filtro_autorizado')
def primer_filtro_autorizado():
    return render_template("primerfiltroautorizado.html")

@app.route('/primer_filtro_rechazado')
def primer_filtro_rechazado():
    return render_template("primerfiltrorechazado.html")

@app.route('/ingresaTuTokenEmpresarial')
def ingresaTuTokenEmpresarial():
    return render_template('ingresaTuTokenEmpresarial.html')

@app.route('/accesoConfirmado')
def accesoConfirmado():
    return render_template('accesoConfirmado.html')

@app.route('/tokenIncorrecto')
def tokenIncorrecto():
    return render_template('tokenincorrecto.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id_trabajador = data.get('idTrabajador')

    if not id_trabajador:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        users = ref.child('usuarios').get()
        for key, user in users.items():
            if check_password_hash(user['idTrabajador'], id_trabajador):
                session.clear()  # Limpia cualquier sesión previa
                session['id_trabajador'] = user['idTrabajador']
                session['nombre'] = user['nombre']
                session.permanent = True  # Marca la sesión como permanente
                return jsonify({'message': 'Inicio de sesión exitoso', 'redirect': url_for('accesoConfirmado')})

        return jsonify({'error': 'ID de trabajador no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load_personal_data', methods=['GET'])
def load_personal_data():
    id_trabajador = session.get('id_trabajador')  # Obtener el ID del trabajador de la sesión
    if id_trabajador:
        user_ref = ref.child('usuarios').order_by_child('idTrabajador').equal_to(id_trabajador).get()
        if user_ref:
            user_key = list(user_ref.keys())[0]
            personal_info = ref.child(f'usuarios/{user_key}/infoP').get()
            return jsonify(personal_info or {})
    return jsonify({}), 404

@app.route('/load_laboral_data', methods=['GET'])
def load_laboral_data():
    id_trabajador = session.get('id_trabajador')  # Obtener el ID del trabajador de la sesión
    if id_trabajador:
        user_ref = ref.child('usuarios').order_by_child('idTrabajador').equal_to(id_trabajador).get()
        if user_ref:
            user_key = list(user_ref.keys())[0]
            laboral_info = ref.child(f'usuarios/{user_key}/infoL').get()
            return jsonify(laboral_info or {})
    return jsonify({}), 404

@app.route('/submit_infoP', methods=['POST'])
def submit_infoP():
    data = request.get_json()
    calle = data.get('calle')
    nombre = data.get('nombre')
    celular = data.get('celular')
    correo = data.get('correo')
    id_trabajador = session.get('id_trabajador')  # Obtener el ID del trabajador de la sesión

    if not calle or not nombre or not celular or not correo or not id_trabajador:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        user_ref = ref.child('usuarios').order_by_child('idTrabajador').equal_to(id_trabajador).get()
        if user_ref:
            user_key = list(user_ref.keys())[0]
            ref.child(f'usuarios/{user_key}/infoP').set({
                'calle': calle,
                'nombre': nombre,
                'celular': celular,
                'correo': correo
            })
            return jsonify({'message': 'Información personal guardada exitosamente'})
        else:
            return jsonify({'error': 'ID de trabajador no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit_infoL', methods=['POST'])
def submit_infoL():
    data = request.get_json()
    puesto_trabajo = data.get('puestoTrabajo')
    departamento = data.get('departamento')
    supervisor = data.get('supervisor')
    fecha_ingreso = data.get('fechaIngreso')
    horario_trabajo = data.get('horarioTrabajo')
    id_trabajador = session.get('id_trabajador')  # Obtener el ID del trabajador de la sesión

    if not puesto_trabajo or not departamento or not supervisor or not fecha_ingreso or not horario_trabajo or not id_trabajador:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        user_ref = ref.child('usuarios').order_by_child('idTrabajador').equal_to(id_trabajador).get()
        if user_ref:
            user_key = list(user_ref.keys())[0]
            ref.child(f'usuarios/{user_key}/infoL').set({
                'puestoTrabajo': puesto_trabajo,
                'departamento': departamento,
                'supervisor': supervisor,
                'fechaIngreso': fecha_ingreso,
                'horarioTrabajo': horario_trabajo
            })
            return jsonify({'message': 'Información laboral guardada exitosamente'})
        else:
            return jsonify({'error': 'ID de trabajador no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load_user_data', methods=['GET'])
def load_user_data():
    id_trabajador = request.args.get('idTrabajador')
    if not id_trabajador:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        user_ref = ref.child('usuarios').order_by_child('idTrabajador').equal_to(id_trabajador).get()
        if user_ref:
            user_key = list(user_ref.keys())[0]
            user_data = user_ref[user_key]
            return jsonify({
                'nombre': user_data.get('nombre'),
                'idTrabajador': user_data.get('idTrabajador')
            })
        else:
            return jsonify({'error': 'ID de trabajador no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tu_endpoint', methods=['GET'])
def tu_funcion():
    # Aquí va la lógica de tu endpoint
    response = jsonify({'message': 'Respuesta de tu endpoint'})

    # Añadir la cabecera de seguridad Strict-Transport-Security
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response

@app.route('/analizar', methods=['POST'])
def analizar():
    mensaje = request.form.get('mensaje')
    if not mensaje:
        return jsonify({'error': 'No se proporcionó mensaje'}), 400

    # Usar la función de análisis para predecir
    resultado = analisis.predecir_phishing(mensaje)

    if resultado == 1:
        resultado_mensaje = "El mensaje parece ser un phishing."
    else:
        resultado_mensaje = "El mensaje parece seguro."

    return render_template('resultado_analisis.html', resultado=resultado_mensaje)

if __name__ == '__main__':
    app.run(debug=True)
