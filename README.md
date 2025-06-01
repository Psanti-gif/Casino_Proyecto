# Proyecto de Casino 🎰

Este es un proyecto **fullstack** para la presentación del trabajo final. El proyecto está enfocado en un sistema de casino, desarrollando un **backend en Python (FastAPI)** y un **frontend en Next.js**.

---

## 📁 Estructura

- `backend/`: API REST construida en FastAPI.  
- `frontend/`: Interfaz visual desarrollada con Next.js.

---

## 🚀 Cómo iniciar

### ✅ Requisitos previos

- Python 3.10 o superior
- Node.js 18 o superior
- npm o yarn

---

### ⚙️ Backend - FastAPI + ReactPy

```bash
cd backend

# Recomendado: activar entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate    # Linux/macOS
venv\Scriptsctivate       # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
```
---

---
# 🎰 CUADRE CASINO

**CUADRE CASINO** es un sistema fullstack desarrollado como parte de un proyecto final académico. Su propósito es gestionar usuarios y generar reportes sobre el uso de máquinas de casino. El backend está construido con **FastAPI**, y el frontend con **Next.js**, con integración de **ReactPy** para componentes interactivos desde Python.

---

## 📁 Estructura del Proyecto

```
CUADRE-CASINO/
│
├── backend/               # Servidor FastAPI
│   ├── app/
│   │   ├── main.py        # Punto de entrada de la API
│   │   └── modules/
│   │       └── usuarios_configuracion.py
│   ├── usuarios.csv       # Base de datos simple (CSV)
│   ├── contador_id.txt    # Para IDs autoincrementales
│   └── requirements.txt
│
├── frontend/              # Frontend en Next.js (no incluido aquí)
│   └── ...
│
├── .gitignore             # Ignora entornos y archivos temporales
└── README.md              # Documentación del proyecto
```
---

## ⚙️ Backend (FastAPI + ReactPy)

### 🔧 Instalación y ejecución

```bash
cd backend

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload
```

Una vez iniciado, accede a:
- Documentación interactiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Página principal: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📌 Endpoints principales

- `GET /`: Mensaje de bienvenida
- `POST /usuarios/`: Agregar nuevo usuario
- `GET /usuarios/`: Listar usuarios registrados

---

## 🧠 Lógica adicional (CLI)

El proyecto también cuenta con un módulo CLI para generar reportes, con opciones como:

- Selección de casino
- Filtrado de máquinas disponibles por casino
- Rango de fechas para reportes
- Tipos de reporte:
  - Individual
  - Grupal
  - Consolidado

Funciones clave:
```python
SeleccionarCasino(nombre=None, zona=None)
SeleccionarMaquina(casino_id=None, estado=False)
SeleccionarRangoFechas()
GenerarReporte()
```

---

## 📦 Dependencias principales

`requirements.txt`:

```
fastapi==0.115.12
reactpy==1.1.0
uvicorn==0.29.0
pydantic==2.7.1
```

---

## 📄 .gitignore

El proyecto ignora:

- Archivos temporales de Python (`__pycache__/`, `*.pyc`)
- Entornos virtuales (`env/`, `venv/`)
- Módulos de Node.js (`node_modules/`)
- Archivos del sistema (`.DS_Store`)
- Variables de entorno (`.env`)
- Carpetas de compilación de Next.js (`.next/`, `out/`)

---

---

# 🎰 Módulo de Reportes - Sistema Casino

Este módulo permite **generar**, **exportar**, **visualizar** y **enviar reportes personalizados** sobre el comportamiento de las máquinas de juego en un casino. Integra directamente los datos reales de los contadores y cuadre de máquinas, ofreciendo una herramienta poderosa para análisis operativo, estratégico y auditoría.

---

## ✅ Funcionalidades Principales

### 🔎 Filtros Avanzados

- Por marca y modelo de máquina  
- Por casino o ciudad  
- Por rango de fechas

---

### 📊 Tipos de Reporte

| Tipo               | Descripción                                                              |
|--------------------|---------------------------------------------------------------------------|
| Individual          | Reporte de utilidad de una sola máquina entre dos fechas                 |
| Grupo de máquinas   | Reporte combinado de múltiples máquinas seleccionadas                    |
| Consolidado         | Reporte global por casino, agrupando todas sus máquinas                  |
| Por Participación   | Cálculo del valor de participación sobre una utilidad total (%)         |

---

## 🔁 Exportación y Envío

- **Exportar** reportes a: 📄 PDF y 📊 Excel (.xlsx)  
- **Enviar por correo** (manual o programado) usando Gmail  
- Carpeta de archivos generados: `exports/`

---

## 🚀 Endpoints Disponibles

### 🎯 Visualización y Generación

| Método | Endpoint                      | Descripción                                      |
|--------|-------------------------------|--------------------------------------------------|
| GET    | `/reportes/casinos`           | Lista de casinos filtrables por ciudad          |
| GET    | `/reportes/maquinas`          | Máquinas filtradas por marca, modelo y ciudad   |
| GET    | `/reportes/individual`        | Reporte individual por máquina                  |
| GET    | `/reportes/consolidado`       | Reporte consolidado por casino                  |
| POST   | `/reportes/grupo`             | Reporte por grupo de máquinas                   |
| POST   | `/reportes/participacion`     | Cálculo de participación por utilidad           |

---

### 📤 Exportación y Envío

| Método | Endpoint                          | Descripción                                      |
|--------|-----------------------------------|--------------------------------------------------|
| POST   | `/reportes/exportar`              | Exportar reporte como PDF o Excel               |
| POST   | `/reportes/enviar-email`          | Enviar reporte por correo (SMTP - Gmail)        |
| POST   | `/reportes/programar-envio`       | Programar envío automático a fecha y hora       |

---

## 📥 Ejemplo de Envío por Correo

```http
POST /reportes/enviar-email?formato=pdf&destinatario=usuario@gmail.com
```

```json
{
  "detalle_maquinas": [...],
  "totales_grupo": {
    "total_in": 1200,
    "total_out": 800,
    "utilidad_total": 400
  }
}
```

---

## 🛡️ Requisitos

- Python 3.10+  
- Librerías utilizadas:
  - `fastapi`  
  - `apscheduler`  
  - `fpdf`  
  - `pandas`  
  - `uvicorn`  

- Cuenta de Gmail con contraseña de aplicación para SMTP

---

## 🧠 Autor

> **Samuel Sánchez**  
> Backend Casino-Modulo de reportes
> 2025
