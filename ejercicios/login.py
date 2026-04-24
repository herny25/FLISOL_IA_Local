import sqlite3

def login(usuario, password):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE username = '{usuario}' AND password = '{password}'"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()

    if result:
        return "Login exitoso"
    else:
        return "Credenciales incorrectas"


print(login("admin", "1234"))