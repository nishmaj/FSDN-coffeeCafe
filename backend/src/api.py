import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, true'
    header['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE,PATCH,OPTIONS'
    return response

db_drop_and_create_all()

## ROUTES
'''
GET /drinks
    Public route for getting all drinks
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['GET'])
def get_drinks():
    
    drinks = Drink.query.all()
    drinks_short = [drink.short() for drink in drinks]
    
    result = {
        "success": True,
        "drinks": drinks_short
    }
    return jsonify(result)

'''
GET /drinks-detail
    Route handler for getting detailed representation of all drinks.
    Requires 'get:drinks-detail' permission.
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
        drinks = [drink.long() for drink in Drink.query.all()]

        result = {
            'success': True,
            'drinks': drinks
        }
        return jsonify(result)

'''
POST /drinks
    Route handler for adding new drink.
    Requires 'post:drinks' permission.
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    print(request)
    if request.data:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink(title=title, recipe=json.dumps(recipe))
        try:
            # add drink to the database
            Drink.insert(drink)
            new_drink = Drink.query.filter_by(id=drink.id).first()

            return jsonify({
                'success': True,
                'drinks': [new_drink.long()]
             })

        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)        
    else:
        abort(422)

'''
PATCH /drinks/<id>
    Route handler for editing existing drink.
    Requires 'patch:drinks' permission.
returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(token, drink_id):
    print(request)
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)
    
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()

        if drink is None:
            abort(404)

        if title is None:
            abort(400)
        
        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        updated_drink = Drink.query.filter_by(id=drink_id).first()
        print(updated_drink)

        return jsonify({
            'success': True,
            'drinks': [updated_drink.long()]
        })
    except Exception as e:
        # catch exceptions
        print('EXCEPTION: ', str(e))
        abort(422)


'''
DELETE /drinks/<id>
    Route handler for deleting drink.
    Requires 'delete:drinks' permission.
returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        print(drink)
        if drink is None:
            abort(404)
        drink.delete()
        print('deleted')
        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except:
        abort(422)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"+error
                    }), 422

'''
Error handling for resource not found

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    
    }), 404

'''
Error handling for bad request
'''
@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

'''
Error handling for unauthorized
'''

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "unauthorized"
                    }), 401

'''
Error handling for method_not_allowed
'''

def method_not_allowed(error):
    return jsonify({
                    "success": False, 
                    "error": 405,
                    "message": "method_not_allowed"
                    }), 405

'''
Error handling for Internal Server Error
'''
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }, 500)


'''
Error handling for AuthError
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

if __name__ == '__main__':
    app.run(port=8080, debug=True)                    