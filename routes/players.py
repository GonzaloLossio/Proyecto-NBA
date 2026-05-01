from flask import Blueprint,request,jsonify
from services.players_api_client import fetch_players,fetch_players_stats,fetch_player_trends,fetch_compare_players
from extensions import cache,limiter

players_bp = Blueprint("players",__name__)

@players_bp.route("/search")
@limiter.limit("20 per minute")
def search_player():
    """
    Busca jugadores por nombre en la base de datos de la NBA.
    ---
    parameters:
      - name: name
        in: query
        type: string
        required: true
        description: El nombre o apellido del jugador (mínimo 3 letras). Ej. curry
    responses:
      200:
        description: Lista de jugadores encontrados exitosamente.
      400:
        description: Error de validación por falta de caracteres.
    """

    name = request.args.get("name")

    if not name or len (name)<3:
        return jsonify({"Error": "Ingrese al menos 3 letras para poder buscar un jugador"}), 400
    
    raw_data = fetch_players(name)

    if not raw_data:
        return jsonify({"RESULTADOS" : [] , "Mensaje" : "Jugador No encotrado"}),404
    
    clean_data = []
    clean_data = [{
        "id" : p["id"],
        "full_name" : p["full_name"],
        "is_active" : p["is_active"],
    }for p in raw_data]

    return jsonify({"Resultados" : clean_data})

@players_bp.route("/stats")
@limiter.limit("10 per minute")
@cache.cached(timeout=300, query_string=True)
def player_stat():
    """
    Obtiene el historial de partidos de un jugador con filtros y paginación.
    ---
    parameters:
      - name: id
        in: query
        type: string
        required: true
        description: ID único del jugador. Ej. 2544 (LeBron James)
      - name: season
        in: query
        type: string
        required: false
        default: "2023-24"
        description: Temporada a consultar. Ej. 2023-24
      - name: min_points
        in: query
        type: integer
        required: false
        description: Filtrar partidos donde anotó al menos esta cantidad de puntos.
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Número de página para los resultados.
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: Cantidad de partidos por página.
    responses:
      200:
        description: Partidos paginados y metadata de la consulta.
      400:
        description: Parámetros inválidos o faltantes.
    """
    player_id = request.args.get("id")
    season = request.args.get("season","2023-24")
    min_points = request.args.get("min_points")

    try: 
        page = int(request.args.get("page",1))
        per_page = int(request.args.get("per_page",10))
    except ValueError:
        return jsonify({
            "error": "BAD_REQUEST", 
            "message": "Los parámetros 'page' y 'per_page' deben ser números enteros."
        }),400
    
    if page <1 or per_page <1:
        return jsonify({
            "error": "BAD_REQUEST", 
            "message": "La pagina y la cantidad de paginas deben ser mayores a 0."
        })
    
    if min_points is not None:
        try : 
            min_points = int(min_points)
        except ValueError:
            return jsonify({
                "error": "BAD_REQUEST", 
                "message": "El parámetro 'min_points' debe ser un número entero."
            }),400   


    if not player_id:
        return jsonify({"Error" : "Se requiere el ID del jugador"}),400
    
    raw_data = fetch_players_stats(player_id = player_id, season =season)

    clean_data = [{
        "date": stat["GAME_DATE"],
        "points": stat["PTS"],
        "assists" : stat["AST"],
        "rebounds" : stat["REB"]
    } for stat in raw_data]

    if min_points:
        clean_data = [g for g in clean_data if g["points"] >= int(min_points)]

    total = len (clean_data)
    total_pages = -(-total // per_page)
    start = (page - 1) * per_page
    end = page * per_page

    return jsonify({
        "data": clean_data[start:end],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    })

@players_bp.route("/trends")
@cache.cached(timeout=300, query_string=True)
def player_trends():

    """
    Calcula las tendencias recientes de un jugador (Racha y promedios).
    ---
    parameters:
      - name: id
        in: query
        type: string
        required: true
        description: ID único del jugador. Ej. 201939 (Stephen Curry)
      - name: season
        in: query
        type: string
        required: false
        default: "2023-24"
        description: Temporada a evaluar.
    responses:
      200:
        description: Estadísticas recientes, promedios y estado de racha.
      400:
        description: Falta el ID del jugador.
      404:
        description: Datos no encontrados.
    """

    player_id = request.args.get("id")
    season = request.args.get("season","2023-24")

    if not player_id:
        return jsonify({"Error": "Se requiere el ID del jugador"}),400
    
    data = fetch_player_trends(player_id=player_id,season=season)

    if not data:
        return jsonify({"Error": "no se encontraron los datos para este jugador"}),404
    
    return data

@players_bp.route("/compare")
@limiter.limit("5 per minute")
@cache.cached(timeout=300, query_string=True)
def compare_players():

    """
    Compara las estadísticas de dos jugadores y decide un ganador.
    ---
    parameters:
      - name: id1
        in: query
        type: string
        required: true
        description: ID del primer jugador. Ej. 2544
      - name: id2
        in: query
        type: string
        required: true
        description: ID del segundo jugador. Ej. 201939
      - name: season
        in: query
        type: string
        required: false
        default: "2023-24"
        description: Temporada a evaluar.
    responses:
      200:
        description: Comparación detallada y ganadores por categoría.
      400:
        description: Faltan IDs.
      404:
        description: Datos no encontrados.
    """
    
    first_id = request.args.get("id1")
    second_id = request.args.get("id2")
    season = request.args.get("season","2023-24")

    if not first_id or not second_id:
        return jsonify({"Error" : "Se requiere los 2 IDS de los jugadores"}),400
    
    data = fetch_compare_players(first_id=first_id,second_id=second_id,season=season)

    if not data:
        return jsonify({"Error" : "no se encontraron los datos de los jugadores"}),404
    
    return data