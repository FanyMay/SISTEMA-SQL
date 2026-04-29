import pyodbc

# Cambia SOLO estos valores
server = 'DESKTOP-F3M1EN1'  # Tu servidor
database = 'School'                # O el nombre de tu BD

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("✅ ¡Conexión exitosa a SQL Server con autenticación Windows!")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
    