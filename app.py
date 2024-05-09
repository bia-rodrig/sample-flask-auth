from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# view login -> a rota criada de login é a que vai ser utilizada para login
login_manager.login_view = 'login'

@login_manager.user_loader # carrega a sessão do usuário -> retorna o id do usuario
def load_user(user_id):
	# busca o usuário
	return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
	data = request.json
	username = data.get('username')
	password = data.get('password')

	if username and password:
		user = User.query.filter_by(username=username).first()
		if user and user.password == password:
				login_user(user) # chama a função importada passando o usuário encontrado
				#automaticamente o usuário estará autenticado - faz autenticada
				print(current_user.is_authenticated) # printa se o usuario ta autenticado ou não
				return jsonify({'message': 'Autenticação OK'})
	
	return jsonify({'message': 'Credenciais inválidas'}), 400



@app.route('/hello-world', methods=['GET'])
def hello_world():
	return 'Hello world'

if __name__ == '__main__':
	app.run(debug=True)