# 🚀 Guía Completa — De cero a IA local con skills

> De Windows sin nada instalado hasta un asistente de IA con skills de programador,
> completamente local, gratis y sin internet.

---

## Contenido de este paquete

```
material-taller/
├── README.md                       ← este archivo
├── config/
│   └── config.yaml                 ← configuración de Continue (VS Code)
├── ejercicios/
│   └── agente.py                   ← agente con skills de desarrollador
└── skills/
    └── Modelfile-dev               ← modelo personalizado de Ollama
```

---

## Orden recomendado de instalación

1. **WSL2** (Fase 1)
2. **Ollama + Llama 3.1 8B** (Fase 2)
3. **Python + VS Code + Continue** (Fase 3)
4. **Estructura del proyecto** (Fase 4)
5. **Skills** (Fase 5):
   - Skill 1: `skills/Modelfile-dev`
   - Skill 2: `config/config.yaml`
   - Skill 3: `ejercicios/agente.py`

---

## Fase 1 — Instalar WSL2

### 1.1 PowerShell como Administrador

```powershell
wsl --install
```

Reinicia Windows. Cuando arranque, configura Ubuntu.

### 1.2 Verificar

```powershell
wsl --list --verbose
# Debe mostrar Ubuntu · VERSION 2
```

---

## Fase 2 — Ollama + Llama 3.1 8B

Todo desde la terminal de Ubuntu (WSL).

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Configurar CORS para el chat web
# Teniendo en cuenta que las respuestas se generan de manera más tardía
# Caso contrario seguir haciendo uso de la terminal

echo 'export OLLAMA_ORIGINS="*"' >> ~/.bashrc
echo 'export OLLAMA_HOST="0.0.0.0:11434"' >> ~/.bashrc
source ~/.bashrc

# Iniciar Ollama
ollama serve &

# Descargar el modelo (4.7 GB, tarda 10-60 min)
ollama pull llama3.1:8b

# Verificar
ollama list
ollama run llama3.1:8b "Hola"   # prueba rápida, escribe /bye para salir
```

---

## Fase 3 — Python + VS Code + Continue

### Python (en WSL)

```bash
sudo apt install python3 python3-pip -y
pip install requests --break-system-packages
```

### VS Code (en Windows)

Descarga desde https://code.visualstudio.com/

### Extensiones en VS Code

1. **WSL** (del autor Microsoft) — permite trabajar con archivos de WSL
2. **Continue** (del autor Continue) — el asistente de IA en el IDE

---

## Fase 4 — Crear el proyecto

En WSL:

```bash
cd ~
mkdir -p taller-ia/ejercicios taller-ia/skills taller-ia/config
cd taller-ia
code .          # abre VS Code en modo WSL
```

Verifica que VS Code dice "WSL: Ubuntu" abajo a la izquierda en verde.

---

## Fase 5 — Agregar las 3 Skills

### Skill 1 — Modelfile con system prompt

1. Copia `skills/Modelfile-dev` de este paquete a `~/taller-ia/skills/`
2. En terminal:
   ```bash
   cd ~/taller-ia/skills
   ollama create dev-assistant -f Modelfile-dev
   ```
3. Prueba:
   ```bash
   ollama run dev-assistant "Explícame qué es un closure en JavaScript"
   ```

### Skill 2 — Custom commands en Continue

1. Copia el contenido de `config/config.yaml` de este paquete
2. Pégalo en tu archivo de Continue:
   - **Windows:** `C:\Users\TuUsuario\.continue\config.yaml`
   - Desde WSL: `code "/mnt/c/Users/$(whoami)/.continue/config.yaml"` (ajusta usuario)
3. Guarda con `Ctrl+S`
4. En VS Code: `Ctrl+Shift+P` → `Reload Window`
5. Prueba:
   - Abre cualquier archivo de código
   - Selecciona una función
   - `Ctrl+L` → escribe `/revisar` → Enter

### Skill 3 — Tools para devs en agente.py

1. Copia `ejercicios/agente.py` de este paquete a `~/taller-ia/ejercicios/`
2. Ejecuta:
   ```bash
   cd ~/taller-ia/ejercicios
   python3 agente.py
   ```
3. Elige la demo 6 para ver el agente crear un archivo Python y ejecutarlo

---

## Comandos útiles en Continue (después de Skill 2)

Selecciona código en VS Code, presiona `Ctrl+L` y escribe:

| Comando | Qué hace |
|---|---|
| `/revisar` | Busca bugs y sugiere mejoras |
| `/tests` | Genera tests unitarios |
| `/explicar` | Explica el código paso a paso |
| `/optimizar` | Optimiza para rendimiento y legibilidad |
| `/docstring` | Agrega documentación |
| `/seguridad` | Analiza vulnerabilidades |
| `/refactor` | Aplica clean code y SOLID |
| `/traducir` | Traduce el código a otro lenguaje |

---

## Demos del agente.py (Skill 3)

| Demo | Descripción | Dificultad |
|---|---|---|
| 1 | Obtener fecha actual | 🟢 |
| 2 | Listar archivos del directorio | 🟢 |
| 3 | Analizar un archivo de código | 🟡 |
| 4 | Ejecutar código Python | 🟡 |
| 5 | Buscar patrones en el código | 🟠 |
| 6 | Crear archivo Python y ejecutarlo | 🔴 |

---

## Solución de problemas

### "connection refused"
Ollama no está corriendo:
```bash
ollama serve &
```

### "model not found: dev-assistant"
No creaste el modelo personalizado:
```bash
cd ~/taller-ia/skills
ollama create dev-assistant -f Modelfile-dev
```

### Continue no detecta modelo
```
Ctrl+Shift+P → Reload Window
```
Y verifica que `config.yaml` está en `C:\Users\TuUsuario\.continue\`

### WSL muy lento
```bash
# En PowerShell como admin
wsl --shutdown
# Luego reabrir Ubuntu
```

---

*Guía del taller "Tu propio ChatGPT en Linux" — Hernán López*
