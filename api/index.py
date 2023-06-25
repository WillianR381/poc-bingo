from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

app = Flask(__name__)
api = Api(app)


# api.add_resource(Bingo, '/todos/<todo_id>')

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
    bingo_id = db.Column(db.Integer, db.ForeignKey('bingo.id'), nullable=False)

    def __init__(self, drawn_numbers):
        self.drawn_numbers = drawn_numbers


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

from  utils.generateNumberCards import randomNumberNotInserted 
@app.route('/bingo/insere-numero-aleatorio', methods=['PUT'])
def put2():
    try:
        bingo = BingoModel.query.order_by(BingoModel.created_at.desc()).first()

        if not bingo :
            raise ValueError('Nenhum bingo encontrado !')

        numbers = bingo.drawn_numbers.split(",") if bingo.drawn_numbers else list()

        drawn_number = randomNumberNotInserted(numbers)

        if drawn_number is None:
            raise ValueError('Cartela Completa !')

        numbers.insert(0, str(drawn_number))

        updated_drawn_numbers = ",".join(numbers)

        bingo.drawn_numbers = updated_drawn_numbers

        db.session.commit()

        return {'message': bingo.drawn_numbers}
    except ValueError as e:
        return {'message': str(e)}

## End Controller ##
if __name__ == '__main__':
    app.run(debug=True)
