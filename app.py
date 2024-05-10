from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'

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
		user = User(username=username, password=password, role='user')
		# não precisaria colocar o role='user', porque isso já foi definido no user.py
		# porém é bom colocar, para que o próximo programador saiba que o valor padrão é o user
		db.session.add(user)
		db.session.commit()
		return jsonify({'message':'Usuario cadastrado com sucesso'})
	
	return jsonify({'message': 'Dados inválidos'}), 400

@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
	user = User.query.get(id_user)
	if user:
		return {'username': user.username}
	return jsonify({'message': 'Usuário não encontrado'}), 404


# para atualizar senha, ou tem q ser o próprio usuário, ou tem que ser um usuário administrador
@app.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
	data = request.json
	password = data.get('password')
	user = User.query.get(id_user)

	# para atualizar senha, ou tem q ser o próprio usuário, ou tem que ser um usuário administrador
	if id_user != current_user.id and current_user.role == 'user':
		return jsonify({'message': 'operação não permitida'}), 403
	
	if user and password:
		user.password = password        
		db.session.commit()
		return jsonify({'message': f'Usuario {id_user} atualizado com sucesso'})
	return jsonify({'message': 'Usuário não encontrado'}), 404

# Alterado para que apenas usuarios adm consigam fazer delete
@app.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
	user = User.query.get(id_user)
	
	print(current_user.role)
	if current_user.role != 'admin':
		# se não for admin não pode apagar
		return jsonify({'message': 'Operação não permitida'}), 403
	print(id_user)
	print(current_user.id)
	if id_user == current_user.id:
		# um usuário não pode apagar ele mesmo
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