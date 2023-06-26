from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

## Model ##
class BingoModel(db.Model):
    __tablename__ = 'bingo'

    id = db.Column(db.Integer, primary_key=True)
    drawn_numbers = db.Column(db.String, default='', nullable=False)
    color = db.Column(db.String,  nullable=False)
    cards = db.relationship('CardModel', backref='bingo', lazy=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now) 

    def __init__(self, color):
        self.color = color


class CardModel(db.Model):
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    drawn_numbers = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bingo_id = db.Column(db.Integer, db.ForeignKey('bingo.id'), nullable=False)
    number_card = db.Column(db.Integer, nullable=False)
    
    def __init__(self, drawn_numbers, bingo_id, user_id, number_card):
        self.drawn_numbers = drawn_numbers
        self.bingo_id = bingo_id
        self.user_id = user_id
        self.number_card = number_card


class UserModel(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    cards = db.relationship('CardModel', backref='user', lazy=True)

    def __init__(self, name, password, email):
        self.name = name
        self.password = password
        self.email = email

with app.app_context():
    db.create_all()

## End Model ###


## Controller ##
from utils.colors import nextColor   

@app.route('/bingo/nova-rodada', methods=['POST'])
def post():
    last_bingo = BingoModel.query.order_by(BingoModel.created_at.desc()).first()
    color = nextColor(last_bingo.color if not  last_bingo is None else '' )

    bingo = BingoModel(color)

    db.session.add(bingo)
    db.session.commit()
    return {'message': bingo.color}


@app.route('/bingo/insere-numero', methods=['PUT'])
def put():
    try:
        req_body = request.json
        drawn_number = req_body['number']

        if not drawn_number:
            raise ValueError('Nenhum bingo criado !')
        
        bingo = BingoModel.query.order_by(BingoModel.created_at.desc()).first()

        if not bingo :
            raise ValueError('Nenhum bingo encontrado !')

        numbers = bingo.drawn_numbers.split(",") if bingo.drawn_numbers else list()

        if not drawn_number in numbers:
            numbers.insert(0, drawn_number)

        updated_drawn_numbers = ",".join(numbers)

        bingo.drawn_numbers = updated_drawn_numbers

        db.session.commit()

        return {'message': bingo.drawn_numbers}
    except ValueError as e:
        return {'message': str(e)}

from  utils.generateNumberCards import randomNumberNotInsertedBingo 
@app.route('/bingo/insere-numero-aleatorio', methods=['PUT'])
def put2():
    try:
        bingo = BingoModel.query.order_by(BingoModel.created_at.desc()).first()

        if not bingo :
            raise ValueError('Nenhum bingo encontrado !')

        numbers = bingo.drawn_numbers.split(",") if bingo.drawn_numbers else list()

        drawn_number = randomNumberNotInsertedBingo(numbers)

        if drawn_number is None:
            raise ValueError('Cartela Completa !')

        numbers.insert(0, str(drawn_number))

        updated_drawn_numbers = ",".join(numbers)

        bingo.drawn_numbers = updated_drawn_numbers

        db.session.commit()

        return {'message': bingo.drawn_numbers}
    except ValueError as e:
        return {'message': str(e)}
    

from utils.generateNumberCards import generateNumberCards, generateUniqueRandomNumbersCards, formatCardsResponse
@app.route('/cartela/cria-nova', methods=['POST'])
# Cria cartela com sequencia única de numeros aléatorio
def post2():
    try:
        req_body = request.json

        user_id = req_body['userId']

        if not user_id:
            raise ValueError('User id é obrigatório !')
        
        user = UserModel.query.get(user_id)

        if( not user):
            raise ValueError('Usuario não encontrado !')
        
        bingo = BingoModel.query.order_by(BingoModel.created_at.desc()).first()
        
        if not bingo:
            raise ValueError('Nenhum bingo encontrado !')
        
        user_has_card = CardModel.query.filter_by(bingo=bingo, user_id=user_id).first()

        if(user_has_card):
            raise ValueError('Cartela  já criada para o usuario!')
        
        # Pega todos os valores sorteados das catelas da atual rodada, e gera um cartela de valores únicos
        all_drawn_numbers_sorted = [set(drawn_numbers_sorted.drawn_numbers.split(',')) for drawn_numbers_sorted in bingo.cards]

        random_numbers_cards = generateUniqueRandomNumbersCards(all_drawn_numbers_sorted)

        updated_drawn_numbers = ",".join(random_numbers_cards)

        # Pega o ultimo valor de cartelas criada e soma + 1 para a atual
        number_card = len(bingo.cards) + 1

        card = CardModel(updated_drawn_numbers, bingo.id, user_id, number_card)

        db.session.add(card)
        db.session.commit()
        return  jsonify( {'message': 'Cartela criada', 'cards':{'id': card.id, 'number_card': number_card, 'numbers': formatCardsResponse(card.drawn_numbers) }}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

#https://medium.com/@hedgarbezerra35/api-rest-com-flask-autenticacao-25d99b8679b6
from sqlalchemy.exc import IntegrityError
@app.route('/usuario/criar', methods=['POST'])
def post3():
    try:
        req_body = request.json      

        name = req_body['name']
        password = req_body['password']
        email =  req_body['email']

        if(not (name and password and email)):
            raise ValueError('Nome, senha e email obrigatórios !')
        
        user = UserModel(name, password, email)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Usuario criado !'}), 200
    except ValueError  as e:
        return {'message': str(e)}
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'message':'Usuario já existe !'}), 400
    
## End Controller ##
if __name__ == '__main__':
    app.run(debug=True)
