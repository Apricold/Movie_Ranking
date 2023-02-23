from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_movies.db'
Bootstrap(app)
db=SQLAlchemy(app)
API_KEY='f16de67094417f4d46a319ae42d71cc2'
API_MOVIES='https://api.themoviedb.org/3/search/movie'
#CREATING THE COLUMNS AND THE TABLE OF THE DATA BASE 
class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),unique=True,nullable=False)
    year=db.Column(db.Integer,unique=False,nullable=False)
    description=db.Column(db.String(250),unique=False,nullable=False)
    rating=db.Column(db.Float,nullable=True,unique=False)
    ranking=db.Column(db.Integer,unique=False,nullable=True)
    review=db.Column(db.String(50),unique=False,nullable=True)
    img_url=db.Column(db.String(150),unique=False,nullable=False)
app.app_context().push()   # It is necessary in order to create the data base 
db.create_all()

#CREATING A FORM TO CHANGE THE RATING OF THE MOVIE WITH WTF
class RateMovie(FlaskForm):
    rating = FloatField('New Rating', validators=[DataRequired()])
    review=StringField('Your Review',validators=[DataRequired()])
    submit=SubmitField('enviar')

#CREATING A FORM TO ADD A MOVIE
class NewMovie(FlaskForm):
    movie_title=StringField('New Movie',validators=[DataRequired()])
    Submit=SubmitField('enviar')



#----------------------HOME ROUTE-----------------#
@app.route("/")
def home():
    if type(request.args.get('id')) == str:
        id=request.args.get('id')
        print(id)
        parameters={
            'api_key':API_KEY
        }
        new_movie=requests.get(f'https://api.themoviedb.org/3/movie/{id}',params=parameters)
        new_movie=new_movie.json()
        row=Movie(title=new_movie['original_title'],year=new_movie['release_date'],description=new_movie['overview'],img_url=f"https://image.tmdb.org/t/p/w500{new_movie['poster_path']}",rating=None,review=None,ranking=None)
        db.session.add(row)
        db.session.commit()
        return redirect(url_for('update',id=row.id))
    
    mov=Movie.query.order_by('rating')
    count=Movie.query.count()
    rank=0
    for i in mov:
        i.ranking=count-rank
        rank+=1
    db.session.commit()
    return render_template("index.html",movies=mov)

#-------------------UPDATING MOVIES--------------------#
@app.route("/update",methods=['POST','GET'])
def update():
    form=RateMovie()
    id=request.args.get('id')
    row=Movie.query.filter_by(id=id).first()
    if form.validate_on_submit():
        row=Movie.query.filter_by(id=id).first()
        row.rating=form.rating.data
        row.review=form.review.data
        db.session.commit()
        return redirect(url_for('home'))
        
    return render_template('edit.html',form=form,movietitle=row.title)

#---------------------DELETE A MOVIE FROM THE DATA BASE--------------------#
@app.route('/delete')
def delete():
    id=request.args.get('id')
    row=Movie.query.filter_by(id=id).first()
    db.session.delete(row)
    db.session.commit()
    return redirect(url_for('home'))
@app.route('/add',methods=['post','get'])

#----------------------ADDING MOVIE TO THE DATABASE---------------------#
def add():
    list_movies=[]
    form=NewMovie()
    if form.validate_on_submit():
        print(form.movie_title.data)
        parameters={
            'api_key':API_KEY,
            'query':form.movie_title.data, 
            'page':1,    
        }
        movie_info=requests.get(API_MOVIES,params=parameters)
        print(movie_info.raise_for_status())
        results=movie_info.json()['results']
        for i in results:
            try:
                list_movies.append([i['original_title'],i['release_date'],i['id']])
               
            except KeyError:
                pass
        
        return render_template('select.html',info=list_movies)

        
    return render_template('add.html',form=form)
if __name__ == '__main__':
    app.run(debug=True)
