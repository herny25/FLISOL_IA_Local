#!/usr/bin/env python3
"""
Agente con SKILLS DE DESARROLLADOR.
Puede: leer/escribir código, buscar en proyectos, ejecutar tests,
consultar git, analizar archivos, ejecutar Python en sandbox.
"""
import json
import os
import re
import subprocess
import tempfile
import datetime
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
#MODELO     = "dev-assistant:latest"  # usa el modelo personalizado de Skill 1
MODELO     = "llama3.1:8b"
MAX_PASOS  = 10
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))


def ruta(nombre_archivo):
    return os.path.join(BASE_DIR, os.path.basename(nombre_archivo))


# ══════════════════════════════════════════════════════════════
#  HERRAMIENTAS PARA DEVS
# ══════════════════════════════════════════════════════════════

HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "leer_archivo",
            "description": "Lee el contenido de un archivo. Pasa SOLO el nombre.",
            "parameters": {
                "type": "object",
                "properties": {"ruta": {"type": "string"}},
                "required": ["ruta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escribir_archivo",
            "description": "Crea o sobreescribe un archivo. Pasa SOLO el nombre del archivo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ruta": {"type": "string"},
                    "contenido": {"type": "string"}
                },
                "required": ["ruta", "contenido"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_directorio",
            "description": "Lista archivos del directorio actual del proyecto.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_codigo",
            "description": "Busca un texto o patrón en todos los archivos del proyecto. Útil para encontrar funciones, variables, TODOs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patron":    {"type": "string", "description": "Texto a buscar"},
                    "extension": {"type": "string", "description": "Extensión a filtrar, ej: '.py', '.js' (opcional)"}
                },
                "required": ["patron"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analizar_codigo",
            "description": "Analiza un archivo de código: cuenta líneas, funciones, comentarios, detecta TODOs y FIXMEs.",
            "parameters": {
                "type": "object",
                "properties": {"ruta": {"type": "string"}},
                "required": ["ruta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutar_python",
            "description": "Ejecuta codigo Python en sandbox y retorna el output. Util para probar snippets rapidos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codigo": {"type": "string", "description": "Codigo Python a ejecutar"}
                },
                "required": ["codigo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutar_bash",
            "description": "Ejecuta un comando bash seguro. Solo lectura: ls, cat, echo, pwd, date, wc, head, tail, grep, find, which.",
            "parameters": {
                "type": "object",
                "properties": {
                    "comando": {"type": "string"}
                },
                "required": ["comando"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_info",
            "description": "Muestra estado de git: archivos modificados, ultimos commits, rama actual.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fecha_hora",
            "description": "Retorna la fecha y hora actual.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def ejecutar_herramienta(nombre, args):
    try:
        if nombre == "leer_archivo":
            with open(ruta(args["ruta"]), "r", encoding="utf-8") as f:
                contenido = f.read()
            return contenido[:3000] + ("\n... (truncado)" if len(contenido) > 3000 else "")

        elif nombre == "escribir_archivo":
            path = ruta(args["ruta"])
            with open(path, "w", encoding="utf-8") as f:
                f.write(args["contenido"])
            return f"Archivo guardado: {path} ({len(args['contenido'])} caracteres)"

        elif nombre == "listar_directorio":
            items = []
            for item in sorted(os.listdir(BASE_DIR)):
                full = os.path.join(BASE_DIR, item)
                tipo = "[DIR]" if os.path.isdir(full) else "[FILE]"
                items.append(f"{tipo} {item}")
            return "\n".join(items)

        elif nombre == "buscar_en_codigo":
            patron = args["patron"]
            ext    = args.get("extension", "")
            include = f"--include='*{ext}'" if ext else ""
            cmd = (
                f"grep -rn '{patron}' {BASE_DIR} {include} "
                f"--exclude-dir='.git' --exclude-dir='node_modules' "
                f"--exclude-dir='__pycache__' --exclude-dir='venv' 2>/dev/null"
            )
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = result.stdout.strip()
            if not output:
                return f"Sin coincidencias para '{patron}'"
            lineas = output.split("\n")[:30]
            return "\n".join(lineas)

        elif nombre == "analizar_codigo":
            path = ruta(args["ruta"])
            with open(path, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            total    = len(lineas)
            vacias   = sum(1 for l in lineas if not l.strip())
            coments  = sum(1 for l in lineas if l.strip().startswith(("#", "//", "/*", "*")))
            funcs    = sum(1 for l in lineas if re.search(r'^\s*(def |function |const .+ = \(|async )', l))
            imports  = sum(1 for l in lineas if re.match(r'^\s*(import |from |require\()', l))
            todos    = [f"L{i+1}: {l.strip()}" for i,l in enumerate(lineas)
                        if any(x in l for x in ['TODO', 'FIXME', 'XXX', 'HACK'])]

            reporte = (
                f"Analisis de: {path}\n"
                f"{'-'*50}\n"
                f"Total lineas:      {total}\n"
                f"Lineas de codigo:  {total - vacias - coments}\n"
                f"Comentarios:       {coments}\n"
                f"Lineas vacias:     {vacias}\n"
                f"Funciones/metodos: {funcs}\n"
                f"Imports:           {imports}\n"
                f"TODOs/FIXMEs:      {len(todos)}"
            )
            if todos:
                reporte += "\n\nPendientes:\n" + "\n".join(todos[:10])
            return reporte

        elif nombre == "ejecutar_python":
            codigo = args["codigo"]
            # Decodificar escapes unicode que el modelo a veces inyecta
            try:
                codigo = codigo.encode().decode('unicode_escape')
            except Exception:
                pass  # si falla, usar el código original
            
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
                f.write(codigo)
                tmp = f.name
            try:
                result = subprocess.run(
                    ["python3", tmp],
                    capture_output=True, text=True, timeout=10
                )
                output = result.stdout or result.stderr or "(sin output)"
                return f"Output:\n{output[:1500]}"
            except subprocess.TimeoutExpired:
                return "ERROR: Timeout (10 segundos)"
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)

        elif nombre == "ejecutar_bash":
            cmd = args["comando"].strip()
            PERMITIDOS = ["ls", "cat", "echo", "pwd", "date", "wc", "head",
                          "tail", "grep", "find", "which", "ps"]
            primer = cmd.split()[0]
            if primer not in PERMITIDOS:
                return f"Comando no permitido: {primer}. Solo: {', '.join(PERMITIDOS)}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=5,
                cwd=BASE_DIR
            )
            return (result.stdout or result.stderr or "(sin salida)")[:1500]

        elif nombre == "git_info":
            output = []
            for label, cmd in [
                ("Rama actual",     "git branch --show-current"),
                ("Archivos modificados", "git status --short"),
                ("Ultimos 5 commits", "git log --oneline -5"),
            ]:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
                output.append(f"[{label}]\n{r.stdout.strip() or '(vacio)'}")
            return "\n\n".join(output)

        elif nombre == "fecha_hora":
            return datetime.datetime.now().strftime("%A, %d de %B de %Y - %H:%M:%S")

        else:
            return f"Herramienta desconocida: {nombre}"

    except Exception as e:
        return f"ERROR: {e}"


# ══════════════════════════════════════════════════════════════
#  AGENTE ReAct
# ══════════════════════════════════════════════════════════════

def ejecutar_agente(tarea):
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres un agente que EJECUTA acciones usando herramientas. "
                "NUNCA describas lo que vas a hacer. NUNCA escribas JSON en tu "
                "respuesta. DIRECTAMENTE llama a las herramientas una por una. "
                "Puedes leer y escribir código, buscar en proyectos, ejecutar "
                "Python y bash, y consultar git. "
                "Cuando escribas archivos, pasa SOLO el nombre (ej: 'test.py'), "
                "nunca rutas como /path/to/. "
                "Para tareas con múltiples pasos: llama a la primera herramienta, "
                "espera el resultado, luego llama a la siguiente. "
                "Al final, da una respuesta CORTA en español confirmando qué hiciste."
            )
        },
        {"role": "user", "content": tarea}
    ]

    print(f"\n  TAREA: {tarea}\n")

    for paso in range(MAX_PASOS):
        resp = requests.post(OLLAMA_URL, json={
            "model":    MODELO,
            "messages": mensajes,
            "tools":    HERRAMIENTAS,
            "stream":   False
        }).json()

        msg = resp["message"]

        if msg.get("tool_calls"):
            mensajes.append(msg)
            print(f"  PASO {paso+1}")
            for call in msg["tool_calls"]:
                nombre = call["function"]["name"]
                args   = call["function"]["arguments"]
                if isinstance(args, str):
                    args = json.loads(args)
                args_str = json.dumps(args, ensure_ascii=False)[:80]
                print(f"    TOOL: {nombre}({args_str})")
                resultado = ejecutar_herramienta(nombre, args)
                preview   = resultado[:100].replace('\n', ' | ')
                print(f"    RESULT: {preview}")
                mensajes.append({"role": "tool", "content": resultado})
        else:
            print(f"  PASO {paso+1} - Respuesta final\n")
            return msg["content"]

    return "Limite de pasos alcanzado"


DEMOS = {
    "1": "Que fecha es hoy? Responde en formato amigable.",
    "2": "Lista los archivos del directorio actual y dime que hay.",
    "3": "Analiza el archivo 'agente.py' y dame un reporte completo.",
    "4": "Ejecuta este codigo Python: for i in range(5): print(f'Numero: {i*2}')",
    "5": "Busca todas las lineas que contengan 'def ' en archivos .py del directorio.",
    "6": (
        "Crea un archivo llamado 'fibonacci.py' con una funcion que "
        "calcule los primeros 10 numeros de Fibonacci. Luego ejecutalo "
        "con ejecutar_python para verificar que funciona."
    ),
}


if __name__ == "__main__":
    print("=" * 65)
    print("  Agente DevAssistant - con skills de programador")
    print("=" * 65)
    print(f"\n  Modelo: {MODELO}")
    print(f"  Directorio: {BASE_DIR}\n")

    print("Demos disponibles:")
    for num, tarea in DEMOS.items():
        print(f"  {num}. {tarea[:70]}{'...' if len(tarea) > 70 else ''}")

    opcion = input("\nQue demo ejecutar? (1-6, 'all' para todas, Enter para demo 6): ").strip()

    if opcion == "all":
        demos_correr = list(DEMOS.values())
    elif opcion in DEMOS:
        demos_correr = [DEMOS[opcion]]
    else:
        demos_correr = [DEMOS["6"]]

    for tarea in demos_correr:
        print("\n" + "=" * 65)
        respuesta = ejecutar_agente(tarea)
        print(f"  RESPUESTA FINAL:\n")
        for linea in respuesta.split("\n"):
            print(f"     {linea}")
        print()
