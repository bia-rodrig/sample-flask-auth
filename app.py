from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql:///root:admin123@127.0.0.1:3306/flask-crud'
# root: usuario
# admin123: senha desse usuario
# 127.0.0.1: onde está rodando esse banco de dados
# 3306: a porta configurada
#flask-crud: nome dado ao banco de dados

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
	data = request.json
	username = data.get('username')
	password = data.get('password')

	if username and password:
		user = User.query.filter_by(username=username).first()
		if user and user.password == password:
				login_user(user)
				print(current_user.is_authenticated)
				return jsonify({'message': 'Autenticação OK'})
	
	return jsonify({'message': 'Credenciais inválidas'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
	logout_user()
	return jsonify({'message': 'logout realizado com sucesso.'})

@app.route('/user', methods=['POST'])
#@login_required -> se colocar essa linha, somente usuários cadastrados poderiam adicionar novos usuários
def create_user():
	data = request.json
	username = data.get('username')
	password = data.get('password')
	if username and password:
		user = User(username=username, password=password)
		db.session.add(user)
		db.session.commit()
		return jsonify({'message':'Usuario cadastrado com sucesso'})
	
	return jsonify({'message': 'Dados inválidos'}), 400 # Bad request - faltando informação

# buscar usuário
@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
	user = User.query.get(id_user)
	if user:
		return {'username': user.username}
	return jsonify({'message': 'Usuário não encontrado'}), 404

# atualizar usuário
@app.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
	data = request.json
	password = data.get('password')
	user = User.query.get(id_user)
	if user and password:
		# atualiza senha do usuario
		user.password = password        
		db.session.commit()
		return jsonify({'message': f'Usuario {id_user} atualizado com sucesso'})
	return jsonify({'message': 'Usuário não encontrado'}), 404

# Deletar usuário
@app.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
	user = User.query.get(id_user)
	if id_user != current_user.id: # para o usuário logado não apagar ele mesmo
		return jsonify({'message': 'Deleção não permitida'}), 403
    
	if user: 
		db.session.delete(user)
		db.session.commit()
		
		return jsonify({'message': f'Usuario {id_user} removido com sucesso'})
	return jsonify({'message': 'Usuário não encontrado'}), 404


@app.route('/hello-world', methods=['GET'])
def hello_world():
	return 'Hello world'

if __name__ == '__main__':
	app.run(debug=True)