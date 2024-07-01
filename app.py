#importar o flask
from flask import Flask 
from models.user import User
from database import db

#criar a aplicação
app = Flask(__name__)
#configurar o secret-key e a uri
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"


db.init_app(app)

#criar a rota, qual o método e a função que vai retornar um texto
@app.route("/hello-world", methods=["GET"])
def hello_world():
    return 'hello_world'



if __name__ == '__main__':
    app.run(debug=True)


