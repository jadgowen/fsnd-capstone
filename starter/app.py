import os
from datetime import datetime
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movies, Actors
from auth import AuthError, requires_auth

def create_app(test_config=None):

    app = Flask(__name__)
    CORS(app)
    setup_db(app)


    @app.route('/', methods=['GET'])
    def index():
        return jsonify("Healthy")


    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        movie_list = Movies.query.all()
        movies = []
        for movie in movie_list:
            movies.append(movie.format())
        return jsonify({
            'success': True,
            'movies': [movies]
        }), 200


    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        actor_list = Actors.query.all()
        actors = []
        for actor in actor_list:
            actors.append(actor.format())
        return jsonify({
            'success': True,
            'actors': [actors]
        }), 200


    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def add_movies(payload):
        try:
            new_movie = request.get_json()
            movie = Movies(**new_movie)
            movie.title = new_movie['title']
            movie.release_date = datetime.strptime(new_movie['release_date'],'%Y-%m-%d')
            movie.insert()
            return jsonify({
                'success': True,
                'movie': movie.format()
            }), 200
        except Exception:
            abort(400)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def add_actors(payload):
        try:
            new_actor = request.get_json()
            actor = Actors(**new_actor)
            actor.name = new_actor['name']
            actor.age = new_actor['age']
            actor.gender = new_actor['gender']
            actor.insert()
            return jsonify({
                'success': True,
                'movie': actor.format()
            }), 200
        except Exception:
            abort(400)

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movies(payload, id):
        movie = Movies.query.filter(Movies.id == id).one_or_none()
        if not movie:
            abort(404)
        else:
            try:
                movie.delete()
                return jsonify({
                    'success': True,
                    'deleted': movie.id
                }), 200
            except Exception:
                abort(400)

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actors(payload, id):
        actor = Actors.query.filter(Actors.id == id).one_or_none()
        if not actor:
            abort(404)
        else:
            try:
                actor.delete()
                return jsonify({
                    'success': True,
                    'deleted': actor.id
                }), 200
            except Exception:
                abort(400)

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def edit_movies(payload, id):
        edit_movies = request.get_json()
        movie = Movies.query.filter(Movies.id == id).one_or_none()
        if not movie:
            abort(404)
        else:
            try:
                if edit_movies.get('title'):
                    movie.title = edit_movies['title']
                if edit_movies.get('release_date'):
                    movie.release_date = datetime.strptime(edit_movies['release_date'],'%Y-%m-%d')
                movie.update()
                return jsonify({
                    'success': True,
                    'updated': movie.format()
                }), 200
            except Exception:
                abort(400)

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def edit_actors(payload, id):
        edit_actors = request.get_json()
        actor = Actors.query.filter(Actors.id == id).one_or_none()
        if not actor:
            abort(404)
        else:
            try:
                if edit_actors.get('name'):
                    actor.name = edit_actors['name']
                if edit_actors.get('age'):
                    actor.age = edit_actors['age']
                if edit_actors.get('gender'):
                    actor.gender = edit_actors['gender']
                actor.update()
                return jsonify({
                    'success': True,
                    'updated': actor.format()
                }), 200
            except Exception:
                abort(400)

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False,
                        "error": 422,
                        "message": "Unprocessable entity"
                        }), 42


    # Handler for 404 errors for missing resources
    @app.errorhandler(404)
    def missing_resource(error):
        return jsonify({
                        "success": False,
                        "error": 404,
                        "message": "Resource not found"
                        }), 404


    # Handler for 403 errors for invalid methods
    @app.errorhandler(403)
    def wrong_method(error):
        return jsonify({
                        "success": False,
                        "error": 403,
                        "message": "Incorrect method for endpoint"
                        }), 403


    # Handler for 401 errors for authorization failures
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
                        "success": False,
                        "error": 401,
                        "message": "Unathorized"
                        }), 401


    # Handler for 400 errors for inaccurately formatted requests
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
                        "success": False,
                        "error": 400,
                        "message": "Request data is unprocessable"
                        }), 400

    # Utilizes class AuthError from auth.py
    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
                        "success": False,
                        "error": error.status_code,
                        "message": error.error['description']
                        }), error.status_code

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
