import os
import json

from flask import Flask, request, jsonify, abort, url_for, redirect
from sqlalchemy import exc
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from models import setup_db, User, Account, Portfolio
from auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# ROUTES
@app.route('/', methods=['POST', 'GET'])
def go_home():
  return redirect(url_for('show_login_results'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    #return redirect('https://hqadir-demo.us.auth0.com/authorize?audience=drinks_fs_demo&response_type=token&client_id=3ppuJcwYqIUBt6caNpsR01NP2JlMkho7&redirect_uri=http://127.0.0.1:8080/login-token')
  return(jsonify({'status':'Not implemented'}))

@app.route('/logout', methods=['POST', 'GET'])
def logout():
  return jsonify({
      'msg': 'logout successful'
    })


@app.route('/login-token', methods=['POST', 'GET'])
def show_login_results():
  token = request.args.get('access_token')
  token_type = request.args.get('token_type')
  return jsonify({
      'token': token,
      'token_type': token_type
  })

@app.route('/drinks', methods=['GET'])
def read_drinks():
  try:
      drink_list = Drink.query.order_by('id').all()
  except:
      abort(404)

  if len(drink_list) == 0:
      return jsonify({
              'success': True,
              'num_records': len(drink_list),
              'drinks': []
          })
  else:
      return jsonify({
              'success': True,
              'num_records': len(drink_list),
              'drinks': [x.short() for x in drink_list]
          })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def read_drink_details(jwt_pl):
  try:
      drink_list = Drink.query.order_by('id').all()
  except:
      abort(404)

  return jsonify({
    'success': True,
    'drinks': [x.long() for x in drink_list]
  })


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def write_drink_details(jwt_pl):
  r = json.loads(request.data)
  given_recipe = json.dumps(r['recipe'])
  formatted_recipe = given_recipe if '[' in given_recipe else f'[{given_recipe}]'
  drink = Drink(title=r['title'], recipe=formatted_recipe)
  try:
      drink.insert()
      return jsonify({
          'success': True,
          'drinks': [drink.long()]
          }), 200
  except:
      abort(409)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def modify_drink(jwt_pl, id):
  try:
      response = {
              'success': False,
          }
      drink = Drink.query.get(id)
      if drink:
          patched_attributes_dict = json.loads(request.data)
          for k in patched_attributes_dict:
              drink.__dict__[k] = patched_attributes_dict[k]
          drink.update()
          response.update({'success': True, 'drinks': [drink.long()]})
          return jsonify(response)
      else:
          abort(404)
  except:
      abort(404)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(jwt_pl,  id):
  response = {
      'success': False,
      'delete': id
      }
  try:
      drink = Drink.query.get(id)
      if drink:
          drink.delete()
          response.update({'success': True, 'drinks': [drink.long()]})
          return jsonify(response)
      else:
          abort(404)
  except:
      abort(404)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
                  "success": False,
                  "error": 422,
                  "message": "unprocessable"
                  }), 422

@app.errorhandler(404)
def not_found(error):
  return jsonify({
      "success": False,
      "error": 404,
      "message": "Not found"
      }), 404


@app.errorhandler(405)
def wrong_method(error):
  return jsonify({
      "success": False,
      "error": 405,
      "message": "Method Not Allowed"
      }), 405

@app.errorhandler(AuthError)
def unauthorized(error):
  return jsonify({
      'error': error.error['code'],
      'description': error.error['description'],
      'status_code': error.status_code
  }), error.status_code


if __name__ == '__main__':
  app.run(debug=True, host='127.0.0.1', port=5000)
