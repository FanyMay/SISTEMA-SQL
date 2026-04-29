from flask import Flask, render_template, request, jsonify
import json
import os
import pyodbc

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_123'

# ⚠️ CONFIGURA AQUÍ TUS 3 BASES DE DATOS ⚠️
DATABASES = {
    'db1': {
        'nombre': 'School',
        'server': 'DESKTOP-F3M1EN1',  # Cambia por tu servidor
        'database': 'School',            # Cambia por el nombre de tu BD
        'driver': '{ODBC Driver 17 for SQL Server}'
    },
    'db2': {
        'nombre': 'School',
        'server': 'DESKTOP-F3M1EN1',  # Cambia por tu servidor
        'database': 'School',            # Cambia por el nombre de tu BD
        'driver': '{ODBC Driver 17 for SQL Server}'
    },
    'db3': {
        'nombre': 'School',
        'server': 'DESKTOP-F3M1EN1',  # Cambia por tu servidor
        'database': 'School',            # Cambia por el nombre de tu BD
        'driver': '{ODBC Driver 17 for SQL Server}'
    }
}

conexion_actual = None

def conectar_sql_server(config):
    try:
        # Cadena de conexión con autenticación Windows
        conn_str = (
            f"DRIVER={config['driver']};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        
        print(f"🔌 Conectando a: {config['server']} / {config['database']}")
        conn = pyodbc.connect(conn_str)
        print("✅ ¡Conexión exitosa!")
        return conn
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def cargar_consultas():
    if os.path.exists('consultas.json'):
        with open('consultas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    consultas = {}
    for i in range(1, 81):
        consultas[f'query_{i}'] = 'SELECT TOP 10 * FROM sys.tables'
    return consultas

def guardar_consultas(consultas):
    with open('consultas.json', 'w', encoding='utf-8') as f:
        json.dump(consultas, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html', databases=DATABASES, consultas=cargar_consultas(), enumerate=enumerate)

@app.route('/conectar', methods=['POST'])
def conectar():
    global conexion_actual
    db_key = request.json.get('db_key')
    config = DATABASES[db_key]
    
    # Cerrar conexión anterior si existe
    if conexion_actual:
        try:
            conexion_actual.close()
        except:
            pass
    
    conexion_actual = conectar_sql_server(config)
    
    if conexion_actual:
        return jsonify({'exito': True, 'mensaje': f'✅ Conectado a {config["nombre"]}'})
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
        
        # 🔧 CORRECCIÓN MEJORADA: Detectar cualquier consulta que devuelve datos
        sql_upper = sql.strip().upper()
        
        # Palabras que indican que la consulta devuelve datos
        devuelve_datos = any([
            sql_upper.startswith('SELECT'),
            sql_upper.startswith('WITH'),
            sql_upper.startswith('EXEC'),
            sql_upper.startswith('EXECUTE'),
            'RETURN' in sql_upper  # Para procedimientos
        ])
        
        # También verificar si el cursor tiene columnas (más confiable)
        tiene_columnas = cursor.description is not None
        
        if tiene_columnas and devuelve_datos:
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
            # Es INSERT, UPDATE, DELETE, etc.
            conexion_actual.commit()
            filas_afectadas = cursor.rowcount
            
            # Si rowcount es -1, mostrar mensaje genérico
            if filas_afectadas == -1:
                return jsonify({
                    'exito': True,
                    'tipo': 'info',
                    'mensaje': '✅ Consulta ejecutada correctamente (sin filas afectadas)'
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
    sql = request.json.get('sql')
    consultas[f'query_{idx}'] = sql
    guardar_consultas(consultas)
    return jsonify({'exito': True})

if __name__ == '__main__':
    print("🚀 Servidor iniciado en: http://localhost:5000")
    app.run(debug=True, port=5000)