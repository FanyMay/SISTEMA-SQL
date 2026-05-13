from flask import Flask, render_template, request, jsonify
import json
import os
import pyodbc

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_123'

# Configuración de bases de datos
#Stefany\MSSQLSERVER2025
DATABASES = {
    'db1': {
        'nombre': 'School',
        'server': 'DESKTOP-F3M1EN1',
        'database': 'School',
        'driver': '{ODBC Driver 17 for SQL Server}',
        'conectada': False
    },
    'db2': {
        'nombre': 'Cliente',
        'server': 'DESKTOP-F3M1EN1',
        'database': 'cliente',
        'driver': '{ODBC Driver 17 for SQL Server}',
        'conectada': False
    },
    'db3': {
        'nombre': 'Adventure',
        'server': 'DESKTOP-F3M1EN1',
        'database': 'AdventureWorks2025',
        'driver': '{ODBC Driver 17 for SQL Server}',
        'conectada': False
    }
}

conexion_actual = None
db_actual_key = None

def conectar_sql_server(config):
    try:
        conn_str = (
            f"DRIVER={config['driver']};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        
        print(f"🔌 Conectando a: {config['server']} / {config['database']}")
        conn = pyodbc.connect(conn_str, timeout=10)
        print("✅ ¡Conexión exitosa!")
        return conn
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def cargar_consultas():
    """Carga las consultas desde consultas.json con la nueva estructura"""
    if os.path.exists('consultas.json'):
        with open('consultas.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Migrar formato antiguo a nuevo si es necesario
            for key in data:
                if isinstance(data[key], str):
                    data[key] = {"enunciado": "", "sql": data[key]}
            return data
    # Inicializar estructura nueva
    consultas = {}
    for i in range(1, 81):
        consultas[f'query_{i}'] = {"enunciado": "", "sql": "SELECT TOP 10 * FROM sys.tables"}
    return consultas

def guardar_consultas(consultas):
    with open('consultas.json', 'w', encoding='utf-8') as f:
        json.dump(consultas, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html', databases=DATABASES, consultas=cargar_consultas(), enumerate=enumerate)

@app.route('/conectar', methods=['POST'])
def conectar():
    global conexion_actual, db_actual_key
    
    for key in DATABASES:
        DATABASES[key]['conectada'] = False
    
    db_key = request.json.get('db_key')
    config = DATABASES[db_key]
    
    if conexion_actual:
        try:
            conexion_actual.close()
        except:
            pass
    
    conexion_actual = conectar_sql_server(config)
    
    if conexion_actual:
        DATABASES[db_key]['conectada'] = True
        db_actual_key = db_key
        return jsonify({'exito': True, 'mensaje': f'✅ Conectado a {config["nombre"]}', 'db_key': db_key})
    else:
        return jsonify({'exito': False, 'error': f'❌ Error al conectar a {config["nombre"]}'})

@app.route('/ejecutar', methods=['POST'])
def ejecutar():
    global conexion_actual
    
    if not conexion_actual:
        return jsonify({'exito': False, 'error': 'Primero selecciona y conecta una base de datos'})
    
    sql = request.json.get('sql', '')
    
    if not sql.strip():
        return jsonify({'exito': False, 'error': 'Escribe una consulta SQL'})
    
    try:
        cursor = conexion_actual.cursor()
        cursor.execute(sql)
        
        sql_upper = sql.strip().upper()
        es_select = sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')
        
        if es_select and cursor.description:
            encabezados = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            datos = [list(fila) for fila in filas]
            
            return jsonify({
                'exito': True,
                'tipo': 'select',
                'encabezados': encabezados,
                'datos': datos,
                'mensaje': f'✅ {len(datos)} filas obtenidas'
            })
        else:
            conexion_actual.commit()
            filas_afectadas = cursor.rowcount
            if filas_afectadas == -1:
                return jsonify({
                    'exito': True,
                    'tipo': 'info',
                    'mensaje': '✅ Consulta ejecutada correctamente'
                })
            else:
                return jsonify({
                    'exito': True,
                    'tipo': 'update',
                    'mensaje': f'✅ Filas afectadas: {filas_afectadas}'
                })
    except Exception as e:
        return jsonify({'exito': False, 'error': f'Error: {str(e)}'})

@app.route('/guardar_consulta', methods=['POST'])
def guardar_consulta():
    consultas = cargar_consultas()
    idx = request.json.get('idx')
    enunciado = request.json.get('enunciado', '')
    sql = request.json.get('sql', '')
    
    consultas[f'query_{idx}'] = {
        "enunciado": enunciado,
        "sql": sql
    }
    guardar_consultas(consultas)
    return jsonify({'exito': True})

@app.route('/obtener_consulta', methods=['POST'])
def obtener_consulta():
    consultas = cargar_consultas()
    idx = request.json.get('idx')
    consulta = consultas.get(f'query_{idx}', {"enunciado": "", "sql": ""})
    return jsonify({'exito': True, 'consulta': consulta})

@app.route('/bd_actual', methods=['GET'])
def bd_actual():
    return jsonify({'exito': True, 'db_key': db_actual_key})

if __name__ == '__main__':
    print("🚀 Servidor iniciado en: http://localhost:5000")
    app.run(debug=True, port=5000)