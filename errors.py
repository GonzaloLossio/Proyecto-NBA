from flask import jsonify

def register_error_handlers(app):
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error" : "NOT_FOUND",
            "message" : "El recurso que buscas no existe",
            "status" : 404
        }),404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "error" : "BAD_REQUEST",
            "message" : "La solicitud tiene parámetros inválidos",
            "status" : 400
        }),400

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "error" : "INTERNAL_SERVER_ERROR",
            "message" : "Algo salió mal en el servidor",
            "status" : 500
        }),500