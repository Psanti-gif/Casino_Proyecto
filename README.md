# Proyecto de Casino 🎰

Este es un proyecto fullstack para la presentación del trabajo final, proyecto enfocado en un Casino, realizando un backend en Python (FastAPI) y frontend en Next.js.

## Estructura
- `backend/`: API REST construida en FastAPI.
- `frontend/`: Interfaz visual en Next.js.

## Cómo iniciar

###Requisitos

- Python 3.10+
- Node.js 18+
- npm o yarn

---

### Backend - FastAPI + ReactPy

```bash
cd backend

# Recomendado: activar entorno virtual
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
# 🎰 Módulo de Reportes - Sistema Casino

Este módulo permite generar, exportar, visualizar y enviar reportes personalizados sobre el comportamiento de las máquinas de juego en un casino. Integra directamente los datos reales de los contadores y cuadre de máquinas, ofreciendo una herramienta poderosa para análisis operativo, estratégico y auditoría.

---

## ✅ Funcionalidades Principales

### 🔎 Filtros Avanzados
- Por marca y modelo de máquina
- Por casino o ciudad
- Por rango de fechas

### 📊 Tipos de Reporte
| Tipo              | Descripción                                                              |
|-------------------|---------------------------------------------------------------------------|
| Individual         | Reporte de utilidad de una sola máquina entre dos fechas                 |
| Grupo de máquinas  | Reporte combinado de múltiples máquinas seleccionadas                   |
| Consolidado        | Reporte global por casino, agrupando todas sus máquinas                 |
| Por Participación  | Cálculo del valor de participación sobre una utilidad total (%)         |

---

## 🔁 Exportación y Envío

- **Exportar** reportes a: 📄 PDF y 📊 Excel (.xlsx)
- **Enviar por correo** (manual o programado) usando Gmail
- Carpeta de archivos generados: `exports/`

---

## 🚀 Endpoints Disponibles

### 🎯 Visualización y Generación

| Método | Endpoint                      | Descripción                                   |
|--------|-------------------------------|-----------------------------------------------|
| GET    | `/reportes/casinos`           | Lista de casinos filtrables por ciudad        |
| GET    | `/reportes/maquinas`          | Máquinas filtradas por marca, modelo, ciudad  |
| GET    | `/reportes/individual`        | Reporte individual por máquina                |
| GET    | `/reportes/consolidado`       | Reporte consolidado por casino                |
| POST   | `/reportes/grupo`             | Reporte por grupo de máquinas                 |
| POST   | `/reportes/participacion`     | Cálculo de participación por utilidad         |

### 📤 Exportación y Envío

| Método | Endpoint                          | Descripción                                |
|--------|-----------------------------------|--------------------------------------------|
| POST   | `/reportes/exportar`              | Exportar reporte como PDF o Excel          |
| POST   | `/reportes/enviar-email`          | Enviar reporte por correo Gmail            |
| POST   | `/reportes/programar-envio`       | Programar envío automático a fecha y hora  |

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
- Librerías:
  - `fastapi`
  - `apscheduler`
  - `fpdf`
  - `pandas`
  - `uvicorn`
- Cuenta de Gmail con contraseña de aplicación para SMTP

---

## 🧠 Autor

> Samuel Sánchez  
> Proyecto Final - Backend Casino  
> 2025
