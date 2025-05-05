import pandas as pd
from fastapi import FastAPI, HTTPException,Path
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import HTTPException
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import io
from fastapi.responses import Response








app = FastAPI()

MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')  
MYSQL_USER = os.getenv('MYSQL_USER', 'user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password') 
MYSQL_DB = os.getenv('MYSQL_DB', 'video_games')

engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}')
FIELD_QUERIES = {
"platform_name": "SELECT DISTINCT platform_name FROM platform",
"release_year": "SELECT DISTINCT release_year FROM game_platform ORDER BY release_year",
"publisher_name": "SELECT DISTINCT publisher_name FROM publisher",
"genre_name": "SELECT DISTINCT genre_name FROM genre",
"region_name": "SELECT DISTINCT region_name FROM region"
}
tablas = ['genre', 'game','game_platform','game_publisher','platform','publisher','region','region_sales']
carpeta_destino = '/app/data'

#Exportacion de archivos
def extraer_tablas():
    os.makedirs(carpeta_destino, exist_ok=True)

    for tabla in tablas:
        df = pd.read_sql(f"SELECT * FROM {tabla}", con=engine)
        archivo_salida = os.path.join(carpeta_destino, f"{tabla}.csv")
        df.to_csv(archivo_salida, index=False)
        print(f"Tabla {tabla} exportada a {archivo_salida}")

extraer_tablas()

df = {}
#Verificar la existencia de loa archivos exportados
for archivo in tablas:
    ruta_archivo = os.path.join(carpeta_destino, f"{archivo}.csv")
    
    if os.path.exists(ruta_archivo):
        print(f"El archivo {archivo} se ha descargado correctamente.")
        d = pd.read_csv(ruta_archivo)        
        df[archivo] = d 
    else:
        print(f"El archivo {archivo} no se encuentra en la ruta {ruta_archivo}.")

#Consultas




@app.get("/games/publisher/{formato}")
def get_publisher_games(
    formato: str,  # "json" o "tabla"
    publisher: str,
    limit: int = 20
):
    try:
        # 1. Unir game con game_publisher y publisher
        merged = df["game"].merge(
            df["game_publisher"],
            left_on="id",
            right_on="game_id"
        ).merge(
            df["publisher"],
            left_on="publisher_id",
            right_on="id"
        )
        
        # 2. Filtrar por publisher (búsqueda exacta)
        merged = merged[merged["publisher_name"] == publisher]
        
        # 3. Limitar resultados y seleccionar columnas
        result = merged[["game_name", "publisher_name"]].head(limit)
        
        # 4. Formatear respuesta según parámetro
        if formato.lower() == "json":
            return JSONResponse(content=result.to_dict(orient="records"))
        elif formato.lower() == "tabla":
            return HTMLResponse(content=result.to_html(index=False))
        else:
            raise HTTPException(status_code=400, detail="Formato no válido. Use 'json' o 'tabla'")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    






@app.get("/games/genre-platform")
def get_games_by_genre_and_platform(
    genre: str, 
    platform: str, 
    limit: int = 20, 
    formato: str = "tabla"
):
    try:
        query = """
        SELECT 
            g.game_name,
            gen.genre_name,
            p.platform_name,
            gp.release_year
        FROM game g
        JOIN genre gen ON g.genre_id = gen.id
        JOIN game_publisher gpubl ON g.id = gpubl.game_id
        JOIN game_platform gp ON gpubl.id = gp.game_publisher_id
        JOIN platform p ON gp.platform_id = p.id
        WHERE gen.genre_name LIKE %s AND p.platform_name LIKE %s
        LIMIT %s
        """
        params = (f"%{genre}%", f"%{platform}%", limit)
        result = pd.read_sql(query, con=engine, params=params)

        if formato.lower() == "json":
            return JSONResponse(content=result.to_dict(orient="records"))
        elif formato.lower() == "tabla":
            return HTMLResponse(content=result.to_html(index=False))
        else:
            raise HTTPException(status_code=400, detail="Formato no válido. Usa 'json' o 'tabla'.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    
    
    
    
    
    
    
    
    
    
    
    
   
@app.get("/games/search")
def search_game(
    name: str,
    limit: int = 10,
    formato: str = "json"
):
    try:
        query = """
        SELECT 
            g.game_name,
            gen.genre_name,
            p.platform_name,
            pub.publisher_name,
            gp.release_year
        FROM game g
        JOIN genre gen ON g.genre_id = gen.id
        JOIN game_publisher gpubl ON g.id = gpubl.game_id
        JOIN publisher pub ON gpubl.publisher_id = pub.id
        JOIN game_platform gp ON gpubl.id = gp.game_publisher_id
        JOIN platform p ON gp.platform_id = p.id
        WHERE LOWER(g.game_name) LIKE LOWER(%s)
        LIMIT %s
        """
        params = (f"%{name}%", limit)
        result = pd.read_sql(query, con=engine, params=params)

        if result.empty:
            raise HTTPException(status_code=404, detail="No se encontraron juegos con ese nombre.")

        if formato.lower() == "json":
            return JSONResponse(content=result.to_dict(orient="records"))
        elif formato.lower() == "tabla":
            return HTMLResponse(content=result.to_html(index=False))
        else:
            raise HTTPException(status_code=400, detail="Formato no válido. Usa 'json' o 'tabla'.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
    
    
    
    
    
    
    
    
    
    
    









@app.get("/games/top-sales-by-year")
def top_sales_by_year(
    year: int,
    formato: str = "json",  # "json" o "grafica"
    limit: int = 10
):
    try:
        # Validar existencia de DataFrames
        required_dfs = ["region_sales", "game_platform", "game_publisher", "game"]
        for name in required_dfs:
            if name not in df:
                raise HTTPException(status_code=500, detail=f"DataFrame '{name}' no disponible.")

        # 1. Unir tablas necesarias
        merged = df["region_sales"].merge(
            df["game_platform"], left_on="game_platform_id", right_on="id"
        ).merge(
            df["game_publisher"], left_on="game_publisher_id", right_on="id"
        ).merge(
            df["game"], left_on="game_id", right_on="id"
        )

        # 2. Filtrar por año
        result = merged[merged["release_year"] == year]

        if result.empty:
            raise HTTPException(status_code=404, detail=f"No hay ventas registradas para el año {year}.")

        # 3. Agrupar por juego y sumar ventas
        grouped = result.groupby("game_name")["num_sales"].sum().reset_index()

        # 4. Obtener top N
        top_games = grouped.sort_values("num_sales", ascending=False).head(limit)

        # 5. Devolver según formato
        if formato.lower() == "grafica":
            plt.switch_backend('Agg')
            plt.figure(figsize=(12, 8))
            top_games.sort_values("num_sales").plot(
                kind="barh",
                x="game_name",
                y="num_sales",
                legend=False,
                color="mediumseagreen"
            )
            plt.title(f"Top {limit} juegos más vendidos en {year}")
            plt.xlabel("Ventas (millones)")
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            plt.close()
            buf.seek(0)

            return Response(content=buf.read(), media_type="image/png")
        else:
            return JSONResponse(content=top_games.to_dict(orient="records"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    
    
    

















@app.get("/platforms/top5-games-by-year")
def get_top5_platforms_by_year(
    year: int, 
    formato: str = "json"
):
    try:
        # Consulta SQL para obtener el top 5 de plataformas con más juegos lanzados
        query = """
        SELECT 
            p.platform_name, 
            COUNT(gp.game_publisher_id) AS num_games
        FROM game_platform gp
        JOIN platform p ON gp.platform_id = p.id
        WHERE gp.release_year = %s
        GROUP BY p.platform_name
        ORDER BY num_games DESC
        LIMIT 5;
        """
        
        # Ejecutar la consulta y obtener los resultados
        result = pd.read_sql(query, con=engine, params=(year,))

        if result.empty:
            raise HTTPException(status_code=404, detail="No se encontraron resultados.")

        # Formatear la respuesta según el formato deseado
        if formato.lower() == "json":
            return JSONResponse(content=result.to_dict(orient="records"))
        elif formato.lower() == "grafica":
            # Si el formato es gráfico, generar un gráfico
            plt.switch_backend('Agg')  # Usado en servidores
            plt.figure(figsize=(10, 5))
            result.sort_values("num_games", ascending=True).plot(
                kind="barh",
                x="platform_name",
                y="num_games",
                color="skyblue",
                legend=False
            )
            plt.title(f"Top 5 plataformas con más juegos en {year}")
            plt.xlabel("Número de juegos")
            plt.ylabel("Plataforma")
            plt.tight_layout()

            # Guardar el gráfico en un buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            buf.seek(0)

            return Response(content=buf.read(), media_type="image/png")
        else:
            raise HTTPException(status_code=400, detail="Formato no válido. Usa 'json' o 'grafica'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
    
    
    
@app.get("/publishers/top-by-year")
def top_publishers_by_year(
    year: int,
    formato: str = "json",  # "json" o "grafica"
    limit: int = 10
):
    try:
        # Consulta SQL para obtener el top publishers con más juegos lanzados
        query = """
        SELECT 
            pub.publisher_name, 
            COUNT(g.id) AS num_games
        FROM game g
        JOIN game_publisher gpubl ON g.id = gpubl.game_id
        JOIN publisher pub ON gpubl.publisher_id = pub.id
        JOIN game_platform gp ON gpubl.id = gp.game_publisher_id
        WHERE gp.release_year = %s
        GROUP BY pub.publisher_name
        ORDER BY num_games DESC
        LIMIT %s;
        """
        
        # Ejecutar la consulta y obtener los resultados
        result = pd.read_sql(query, con=engine, params=(year, limit))

        if result.empty:
            raise HTTPException(status_code=404, detail="No se encontraron resultados para este año.")

        # Formatear la respuesta según el formato deseado
        if formato.lower() == "json":
            return JSONResponse(content=result.to_dict(orient="records"))
        elif formato.lower() == "grafica":
            # Si el formato es gráfico, generar un gráfico
            plt.switch_backend('Agg')  # Usado en servidores
            plt.figure(figsize=(10, 6))
            result.sort_values("num_games", ascending=True).plot(
                kind="barh",
                x="publisher_name",
                y="num_games",
                color="orange",
                legend=False
            )
            plt.title(f"Top {limit} publishers con más juegos en {year}")
            plt.xlabel("Número de juegos")
            plt.ylabel("Publisher")
            plt.tight_layout()

            # Guardar el gráfico en un buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100)
            buf.seek(0)

            return Response(content=buf.read(), media_type="image/png")
        else:
            raise HTTPException(status_code=400, detail="Formato no válido. Usa 'json' o 'grafica'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


























