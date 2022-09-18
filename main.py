from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import os
import dotenv

dotenv.load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)
URL = os.getenv("REACT_API_URL")
parameters = {
    "api_key": os.getenv("REACT_API_KEY"),
    "query": "The Matrix",
}
movies_list = {}


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'{self.title}'


# db.create_all()


class EditMovie(FlaskForm):
    rating = FloatField(label="Your Rating out of 10. e.g:7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField()


class AddMovie(FlaskForm):
    movie = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


@app.route("/")
def home():
    movies = db.session.query(Movie).all()
    movies = db.session.query(Movie).order_by(Movie.rating)
    count = db.session.query(Movie).count()
    return render_template("index.html", movies=movies, count=count)


@app.route("/add", methods=['GET', 'POST'])
def add():
    global movies_list
    if request.method == "POST":
        name = request.form["movie"]
        parameters["query"] = name
        response = requests.get(url=URL, params=parameters)
        movies_list = response.json()['results']
        return render_template("select.html", movies_list=movies_list)
    else:
        form = AddMovie()
        return render_template("add.html", form=form)


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    movie = Movie.query.get(id)
    if request.method == "POST":
        movie.rating = request.form["rating"]
        movie.review = request.form["review"]
        db.session.commit()
        return redirect(url_for('home'))
    else:
        form = EditMovie()
        return render_template("edit.html", form=form, title=movie.title)


@app.route("/delete/<int:id>")
def delete(id):
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/selected/<string:title>/<string:date>/<string:review>", methods=['GET', 'POST'])
def selected(title, date, review):
    global movies_list
    if request.method == "POST":
        for movie in movies_list:
            if movie["title"] == title and movie["release_date"] == date and movie["overview"] == review:
                new_movie = Movie(
                    title=title,
                    year=date[:4],
                    description=review,
                    rating=request.form["rating"],
                    ranking="None",
                    review=request.form["review"],
                    img_url="https://image.tmdb.org/t/p/w500"+movie["poster_path"]
                )
                db.session.add(new_movie)
                db.session.commit()
                return redirect(url_for('home'))
    else:
        form = EditMovie()
        return render_template("edit.html", form=form, title=title)


if __name__ == '__main__':
    app.run(debug=True)
