# 🎮 Proyecto FastAPI + MySQL + Docker

Este es un proyecto de API REST construida con **FastAPI**, que se conecta a una base de datos **MySQL**, todo gestionado mediante **Docker**. Proporciona endpoints para consultar datos de videojuegos como géneros, plataformas, publishers y ventas por región.

## 🚀 Tecnologías usadas

- Python 3
- FastAPI
- SQLAlchemy
- MySQL
- Docker y Docker Compose
- Uvicorn

## 📁 Estructura del proyecto

├── app/
│ ├── main.py # Código principal de la API
│ └── requirements.txt # Dependencias de Python
├── data/ # Archivos CSV para poblar la base de datos
├── database_game/ # Scripts SQL para crear tablas y cargar datos
├── docker-compose.yml # Orquestación de los servicios
└── .gitignore


## 🛠️ Ejecución del Proyecto

Para ejecutar este proyecto, sigue los siguientes pasos:

### 1. Clonar el Repositorio

Clona el repositorio en tu máquina local con el siguiente comando:

```bash
git clone https://github.com/tu_usuario/nombre_del_repositorio.git
```
### 2. Construir y Ejecutar con Docker
Este proyecto usa Docker para gestionar las dependencias y ejecutar el servidor FastAPI con MySQL. Asegúrate de tener Docker instalado en tu máquina.

1.Navega a la carpeta del proyecto:

```bash
cd nombre_del_repositorio
```
2.Construye los contenedores de Docker:

```bash
docker-compose build
```
3.Inicia los contenedores de Docker:

```bash
docker-compose up
```
Esto iniciará los contenedores de MySQL y FastAPI. Una vez que se haya iniciado el proyecto, podrás acceder a la API en:
```bash
FastAPI: http://localhost:8000
```

## 🖥️ Endpoints de la API

La API proporciona los siguientes endpoints para consultar y visualizar datos sobre videojuegos. Cada uno de ellos puede responder en formato **JSON** o **HTML (tabla)**. 

### 1. `/games/publisher/{formato}`

**Descripción**: Obtiene los juegos de un **publisher** específico.

- **Parámetros**:
  - `formato`: `json` o `tabla` (formato de respuesta).
  - `publisher`: Nombre del publisher.
  - `limit`: Limita la cantidad de resultados (opcional, valor predeterminado: 20).

- **Respuesta**: Lista de juegos con el nombre del juego y el publisher.

### 2. `/games/genre-platform`

**Descripción**: Consulta juegos filtrados por **género** y **plataforma**.

- **Parámetros**:
  - `genre`: Género del juego.
  - `platform`: Plataforma en la que está disponible el juego.
  - `limit`: Limita la cantidad de resultados (opcional, valor predeterminado: 20).
  - `formato`: `json` o `tabla` (formato de respuesta).

- **Respuesta**: Lista de juegos con nombre, género, plataforma y año de lanzamiento.

### 3. `/games/search`

**Descripción**: Busca juegos por nombre.

- **Parámetros**:
  - `name`: Nombre del juego (búsqueda parcial).
  - `limit`: Limita la cantidad de resultados (opcional, valor predeterminado: 10).
  - `formato`: `json` o `tabla` (formato de respuesta).

- **Respuesta**: Lista de juegos con nombre, género, plataforma, publisher y año de lanzamiento.

### 4. `/games/top-sales-by-year`

**Descripción**: Obtiene los juegos más vendidos de un año específico.

- **Parámetros**:
  - `year`: Año para filtrar las ventas.
  - `formato`: `json` o `grafica` (formato de respuesta).
  - `limit`: Limita la cantidad de resultados (opcional, valor predeterminado: 10).

- **Respuesta**: Los juegos más vendidos por año en formato JSON o una gráfica de barras.

### 5. `/platforms/top5-games-by-year`

**Descripción**: Obtiene las 5 plataformas con más juegos lanzados en un año.

- **Parámetros**:
  - `year`: Año de lanzamiento.
  - `formato`: `json` o `grafica` (formato de respuesta).

- **Respuesta**: Las 5 plataformas con más juegos lanzados, ya sea en formato JSON o una gráfica de barras.

### 6. `/publishers/top-by-year`

**Descripción**: Obtiene los **top publishers** con más juegos lanzados en un año específico.

- **Parámetros**:
  - `year`: Año de lanzamiento.
  - `formato`: `json` o `grafica` (formato de respuesta).
  - `limit`: Limita la cantidad de resultados (opcional, valor predeterminado: 10).

- **Respuesta**: Los publishers con más juegos lanzados en el año, en formato JSON o gráfico de barras.

