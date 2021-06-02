from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from typing import Callable
import random
import os

app = Flask(__name__)

# # Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1", "sqlite:///quotes.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable


db = MySQLAlchemy(app)


# # Quote TABLE Configuration
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        # # Method 1.
        # dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     print(getattr(self, column.name))
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# # HTTP GET - Read Record

@app.route("/random", methods=["GET"])
def get_random_quote():
    quotes = db.session.query(Quote).all()
    random_quote = random.choice(quotes)
    return jsonify(quote=random_quote.to_dict())


@app.route("/all", methods=["GET"])
def get_all_quotes():
    quotes = db.session.query(Quote).all()
    return jsonify(quotes=[quote.to_dict() for quote in quotes])


@app.route("/search-by-author")
def get_quote_by_author():
    query_author = request.args.get("author")
    quotes = db.session.query(Quote).filter_by(author=query_author).all()
    if quotes:
        return jsonify(quotes=[quote.to_dict() for quote in quotes])
    else:
        return jsonify(error={"Not Found": "Sorry, this author does not exist in this database."})


@app.route("/search")
def get_quote():
    query_quote = request.args.get("quote")
    quotes = db.session.query(Quote).filter_by(quote=query_quote)
    if quotes:
        return jsonify(quotes=[quote.to_dict() for quote in quotes])
    else:
        return jsonify(error={"Not Found": "Sorry, this author does not exist in this database."})


# # HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_quote():
    new_quote = Quote(
        quote=request.form.get("quote"),
        author=request.form.get("author"),
    )
    db.session.add(new_quote)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new quote."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-quote/<int:quote_id>", methods=["PATCH"])
def patch_quote(quote_id):
    new_quote = request.args.get("new_quote")
    quote = db.session.query(Quote).get(quote_id)
    if quote:
        quote.quote = new_quote
        db.session.commit()
        # Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the quote."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a quote with that id was not found in the database."}), 404


@app.route("/update-quote-author/<int:quote_id>", methods=["PATCH"])
def patch_quote_author(quote_id):
    new_author = request.args.get("new_author")
    quote = db.session.query(Quote).get(quote_id)
    if quote:
        quote.author = new_author
        db.session.commit()
        # Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the author of the quote."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a quote with that id was not found in the database."}), 404


# # HTTP DELETE - Delete Record
@app.route("/delete-quote/<quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        quote = db.session.query(Quote).get(quote_id)
        if quote:
            db.session.delete(quote)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the quote from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a quote with that id was not found in the database."}), 404

    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
