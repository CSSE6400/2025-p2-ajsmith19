from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    query = Todo.query

    completed = request.args.get('completed')
    if completed is not None:
        query = query.filter_by(completed=True)

    window = request.args.get('window')
    if window is not None:
        try:
            days = int(window)
            # timedelta To get the difference between now and x amount of days
            cutoff = datetime.utcnow() + timedelta(days=days)
            query = query.filter(Todo.deadline_at <= cutoff)
        except ValueError:
            return jsonify({'error': 'Invalid.'}), 400

    """Return the list of todo items"""
    todos = query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    #Ensure request is JSON
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    # Set a request.json variable for redundance
    data = request.json

    # Permitted fields
    permitted_fields = {'title', 'description', 'completed', 'deadline_at'}

    # Extract keys from the JSON request
    if not set(data.keys()).issubset(permitted_fields):
        return jsonify({'error': 'Invalid fields in request'}), 400
    
    # Ensure the 'title' variable is present
    if 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    """Create a new todo item and return the created item"""
    todo = Todo(
        title=data.get('title'),
        description=data.get('description'),
        completed=data.get('completed', False),
    )

    if 'deadline_at' in data:
        todo.deadline_at = datetime.fromisoformat(data.get('deadline_at'))

    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)

    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    todo = Todo.query.get(todo_id)

    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    # Permitted fields
    permitted_fields = {'title', 'description', 'completed', 'deadline_at'}

    # Extract keys from the JSON request
    if not set(request.json.keys()).issubset(permitted_fields):
        return jsonify({'error': 'Invalid fields in request'}), 400
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)

    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    todo = Todo.query.get(todo_id)

    if todo is None:
        return jsonify({}), 200
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
 
