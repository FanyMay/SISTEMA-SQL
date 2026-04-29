import pyodbc

# Ver qué drivers tienes instalados
print("🔍 Drivers ODBC instalados:")
for driver in pyodbc.drivers():
    print(f"  - {driver}")

# Buscar específicamente el driver 17
if any('ODBC Driver 17' in d for d in pyodbc.drivers()):
    print("\n✅ ¡Driver 17 encontrado! Todo está bien.")
else:
    print("\n❌ No se encuentra el Driver 17. Revisa la instalación.")