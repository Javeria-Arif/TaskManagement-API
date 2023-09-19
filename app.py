from flask import Flask, request, make_response, jsonify, Response
from datetime import datetime
from auth_middleware import auth_required
from database import db
from helpers import check_password, hash_password, sign_jwt
from models import Todo, User
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.db_uri

db.init_app(app)
limiter = Limiter(
    get_remote_address,
    app= app,
    default_limits=["200 per day", "50 per hour"]
)

@app.errorhandler(HTTPException)
def handle_rate_limit_exceeded(error):
    if error.code == 429:
        response = jsonify({"error": "Rate limit exceeded", "message": str(error)})
        response.status_code = 429  # HTTP 429 Too Many Requests
        return response


@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    
    body = request.get_json()
    found_user = User.query.filter_by(email=body['email']).first()

    if found_user is None:
        return make_response(jsonify({"success": False, "error": "User not found"}), 404)

    if check_password(body['password'], found_user.password):
        return make_response(sign_jwt(str(found_user.id)), 200)

    return make_response(jsonify({"success": False, "error": "incorrect password"}), 400)

    
    

@app.route("/signup", methods=["POST"])
@limiter.exempt
def signup():
    body = request.get_json()
    user_with_email = User.query.filter_by(email=body['email']).first()

    if user_with_email is not None:
        return make_response(jsonify({"success": False, "error": "User with this email already exists"}), 409
                             )

    hashed_password = hash_password(body['password'])
    new_user = User(email=body['email'], password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({"success": True, 
                                      "message": "New user successfully added to the database"}), 201)

    except Exception as e:
        print(e)
        return make_response(jsonify({"success": False, "error": "unable to create user"}), 500)



@app.route('/', methods=['GET'])
@auth_required
def get_all(current_user: User):
    tasks = Todo.query.all()

    return make_response(jsonify({
        "success": True,
        "data": [task.to_json() for task in tasks]
    }), 200)


@app.route('/<int:id>')
@auth_required
def get_by_id(current_user: User, id: int):
    task = Todo.query.filter_by(id = id).all()
    if task == []:
        return make_response(jsonify({
        "success": False,
        "message":"No Data Found",
        "data" : [task.to_json()]
    }), 404)
        
    else:
        return make_response(jsonify({
            "success": True,
            "data": task
        }), 200)


@app.route('/', methods=['POST'])
@limiter.limit("2 per minute")
@auth_required
def create(current_user: User):
    body = request.get_json()

    if "status" not in body or not body['status']:
        status = "IN_PROGRESS"
    else:
        status = body['status']
        if body['status'] not in ["IN_PROGRESS", "COMPLETED"]:
                return make_response(jsonify({
                "success" : False,
                "error" : 'Status can only be "IN_PROGRESS or "COMPLETED"'
            }) , 400)
    if "title" not in body or "due_date" not in body or not body['title'] or not body['due_date']:
        return make_response(jsonify({
            "success" : False,
            "error" : "Title or due date missing"
        }) , 400)
    if "description" not in body:
        description =  ""
        
    title = body['title']
    description = body['description']
    due_date = datetime.strptime(body['due_date'], "%Y-%m-%d")
    
    try:
        new_task = Todo(
            title= title,
            description= description,
            due_date=due_date,status = status
            )
        db.session.add(new_task)
        db.session.commit()
        return make_response(jsonify({
            "success": True,
            "data": new_task.to_json()
        }), 201)
    except Exception as e:
        print(e)
        return make_response(jsonify({
            "success": False,
            "error": "error while creating todo"
        }), 400)


@app.route('/<int:id>', methods=['DELETE'])
@auth_required
def delete(current_user: User, id: int):
    task_to_delete = Todo.query.get_or_404(id, "Task not found")
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return make_response(jsonify({
            "success": True ,
            "message": "Task successfully deleted",
            "data": task_to_delete.to_json()
        }), 200)
    except Exception as e:
        return make_response(jsonify({
            "success": False,
            "error": e
        }), 400)


@app.route('/<int:id>', methods=['PUT'])
@limiter.limit("2 per minute")
@auth_required
def update(current_user: User, id: int):
    task = Todo.query.get_or_404(id, "todo not found")
    body = request.get_json()

    if "status" not in body or not body['status']:
        status = "IN_PROGRESS"
    else:
        
        if body['status'] not in ["IN_PROGRESS", "COMPLETED"]:
                return make_response(jsonify({
                "success" : False,
                "error" : 'Status can only be "IN_PROGRESS or "COMPLETED"'
            }) , 400)
        
        task.status = body['status']
    if "title" in body:
        task.title = body['title']
   
    if "description" in body:
        task.description = body['description']
    if "due_date" in body:
        task.due_date = datetime.strptime(body['due_date'], "%Y-%m-%d")
    try:
        db.session.commit()
        return make_response(jsonify({
            "success": True,
            "message": "Task successfully updated",
            "data": task.to_json()
        }), 200)
    except Exception as e:
        print(e)
        return make_response(jsonify({
            "success": False,
            "error": "unable to update todo"
        }), 400)


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
    main()
