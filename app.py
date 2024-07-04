#importar o flask
from flask import Flask, request, jsonify 
from models.user import User
from database import db

from flask_login import LoginManager, login_user, current_user, logout_user, login_required #autenticação usuário

#criar a aplicação
app = Flask(__name__)

#configurar o secret-key e a uri
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager() #instancia da classe
db.init_app(app)
login_manager.init_app(app)

#view utilizada para o login -
# para que tudo funcione, colocar o login_manager com a nossa view.
#vamos usar a rota de login. Setar o login_view como 'login' => ele vai pegar a rota de login que criamos
login_manager.login_view = 'login'
# Session => conexão ativa

#carregando a sessão do usuário, e retorna o id do usuario. usa esta função quando precisar recuperar a informação do usuario em outras etapas do sistema.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) #faz a busca do usuário no banco de dados  #requisição com o id_user, busca as informações no BD


#construir a rota de login
@app.route("/login", methods=["POST"])
def login(): #criar a função login e recuperar o que o usuario enviou
    data = request.json #recupera as informações do usuário
    username = data.get("username") #recupera as informações do usuário
    password = data.get("password") #recupera as informações do usuário
    
    if username and password:
        #buscar o username na base de dados e depois comparar as senhas
        #recuperar o User que está dentro da pasta models; #vai chamar o atributo query e o atributo terá um método chamado filter_by e passar nele o username, verificando se é igual o do usuario digitado. #o retorno será uma lista, vamos buscar o primeiro registro (first()), pois o campo de usuário é uma chave única
        user = User.query.filter_by(username=username).first()  #requisição com o id_user, busca as informações no BD
        
        #se encontrar o user, verificar se as senhas são iguais
        if user and user.password == password:
            
            #usar o método login_user() passando o usuário recuperado no banco de dados. # é a autenticação do usuário,o usuario estará autenticado e conseguiremos recuperá-lo em qualquer lugar.
            login_user(user) 
             
            # #método current_user - recupera as informações do usuário autenticado
            print(current_user.is_authenticated)
            
            return jsonify({"message": "Autenticação realizada com sucesso"})
    
    return jsonify({"message":"Credenciais inválidas"}), 400

#rota logout - importar o método logout_user do flask_login
@app.route("/logout", methods=["GET"])
@login_required #importar o login_required (decorador) => protege a rota. #impede que usuários não atenticados acessem a rota
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso."})

#CADASTRO DE USUÁRIO
@app.route("/user", methods=["POST"])
def create_user(): #@login_required => se ele existir aqui, somente usuário logado vai conseguir cadastrar um novo user
    data = request.json     #recebe as informações do corpo da requisição => request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        #cadastrar no banco de dados
        user = User(username=username, password=password)
        db.session.add(user) #adiciona no BD
        db.session.commit() #salva no BD
        return jsonify({"message": "Usuário cadastrado com sucesso!"})
    return jsonify({"message":"Dados inválidos"}), 400  


#recuperar dados
@app.route("/user/<int:id_user>", methods=["GET"])
def read_user(id_user):
    user = User.query.get(id_user) #requisição com o id_user, busca as informações no BD
    if user:
        return {"username": user.username}
    return jsonify({"message": "Usuário não encontrado"}), 404    


#Update
@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json #recupera a informação no corpo da requisição
    user = User.query.get(id_user) #busca as informações no banco de dados #requisição com o id_user 

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit() #salva no banco de dados
        return jsonify({"message": f"Usuário {id_user} - {user.username} atualizado com sucesso."})
    
    return jsonify({"message": "Usuário não encontrado"}), 404

#Delete
@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user) #busca as informações do id informado no banco de dados
   
    #verificar se o usuário que está logado está tentando excluir a si mesmo, pois isso causaria um conflito no sistema de autenticação
    if id_user == current_user.id:
        return jsonify({"message": "Não é permitido excluir este usuário."}, 403)
    
    if user:
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Usuário {id_user} excluído com sucesso."})
    return jsonify({"message": "Usuário não encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)