import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret123'

db = SQLAlchemy(app)

class City(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
  url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=e015ac40c1e51777f52433b0962155a4'
  r = requests.get(url).json()
  return r

def capitalize_full_string(string):
  if len(string) == 0:
    return string
    
  words = str.split(string)
  if len(words) == 0:
    return words[0]
  else:
    new_words = []
    for word in words:
      new_words.append(word[:1].upper() + word[1:].lower())
    return ' '.join(new_words)

@app.route('/')
def index_get():
  cities = City.query.all()

  weather_data = []

  for city in cities:
    r = get_weather_data(city.name)

    weather = {
      'city': city.name,
      'temperature': int(round(r['main']['temp'])),
      'description': r['weather'][0]['description'],
      'icon': r['weather'][0]['icon'],
    }

    weather_data.append(weather)

  return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
  err_msg = ''
  new_city = capitalize_full_string(request.form.get('city'))

  if new_city:
    is_existing_city = City.query.filter(City.name.ilike(new_city)).first()

    if not is_existing_city:
      new_city_data = get_weather_data(new_city)

      if new_city_data['cod'] == 200:
        new_city_obj = City(name=new_city)
      
        db.session.add(new_city_obj)
        db.session.commit()
      else:
        err_msg = 'City does not exist in the world!'
    else:
        err_msg = 'City already exists in the database!'

  if err_msg:
    flash(err_msg, 'error')
  else:
    flash('City added successfully')

  return redirect(url_for('index_get'))

@app.route('/delete/<name>')
def delete_city(name):
  city = City.query.filter(City.name.ilike(name)).first()
  db.session.delete(city)
  db.session.commit()

  flash(f'Successfully deleted { city.name }', 'success')
  return redirect(url_for('index_get'))
