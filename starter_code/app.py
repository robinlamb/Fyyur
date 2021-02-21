#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(), unique=True)
    facebook_link = db.Column(db.String(), unique=True)
    website_link = db.Column(db.String(), unique=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(), unique=True)
    facebook_link = db.Column(db.String(), unique=True)
    website_link = db.Column(db.String(), unique=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime())

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  #list to hold data
  data = []

  #Get each distinct city in the database
  cities = Venue.query.distinct('city', 'state').all()
  print("Cities")
  print(cities)


  for each_city in cities:

      #Get all venues in the city in the database
      venues = Venue.query.filter(Venue.city == each_city.city, Venue.state == each_city.state).all()
      print("Venues")
      print(venues)

      #List to store venue records for each city
      city_venue_records = []

      #Inner for loop to record data for each venue in each city
      for each_venue in venues:
          #Find number of upcoming shows by querying shows and finding which ones happen after current time
          future_shows = Show.query.filter(Show.venue_id == each_venue.id, Show.start_time > datetime.now()).count()
          print(future_shows)

          venue_record = {
            "id": each_venue.id,
            "name": each_venue.name,
            "num_upcoming_shows": future_shows
          }

          city_venue_records.append(venue_record)

      city_record = {
        "city": each_city.city,
        "state": each_city.state,
        "venues": city_venue_records
      }

      data.append(city_record)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  data = []
  #Get search item from form
  search_item = request.form.get('search_term')

  #Queries to get data and count of records
  matches = Venue.query.filter(Venue.name.ilike(f'%{search_item}%')).all()
  num_matches = Venue.query.filter(Venue.name.ilike(f'%{search_item}%')).count()

  #Loop to collect record for each match to return
  for match in matches:
      future_shows = Show.query.filter(Show.venue_id == match.id, Show.start_time > datetime.now()).count()
      record = {
        "id": match.id,
        "name": match.name,
        "num_upcoming_shows": future_shows
      }

      data.append(record)

  #Build response to send back
  response={
    "count": num_matches,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #Get venue selected from the database
  selected_venue = Venue.query.get(venue_id)

  #Get past shows and their count
  shows_past = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Venue.id == venue_id, Show.start_time < datetime.now()).all()
  shows_past_count = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Venue.id == venue_id, Show.start_time < datetime.now()).count()

  #Get upcoming shows and their count
  future_shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Venue.id == venue_id, Show.start_time > datetime.now()).all()
  future_shows_count = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Venue.id == venue_id, Show.start_time > datetime.now()).count()

  #Lists to store records of past and future shows to build output
  past_shows_records = []
  future_shows_records = []

  #Loop through past and future shows and store them in respective Lists
  for each_show in shows_past:
      record = {
        "artist_id": each_show.artist_id,
        "artist_name": each_show.artist.name,
        "artist_image_link": each_show.artist.image_link,
        "start_time": each_show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      past_shows_records.append(record)

  for each_show in future_shows:
       record = {
         "artist_id": each_show.artist_id,
         "artist_name": each_show.artist.name,
         "artist_image_link": each_show.artist.image_link,
         "start_time": each_show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
       future_shows_records.append(record)

  data = {
        "id": selected_venue.id,
        "name": selected_venue.name,
        "genres": selected_venue.genres,
        "address": selected_venue.address,
        "city": selected_venue.city,
        "state": selected_venue.state,
        "phone": selected_venue.phone,
        "website": selected_venue.website_link,
        "facebook_link": selected_venue.facebook_link,
        "seeking_talent": selected_venue.seeking_talent,
        "seeking_description": selected_venue.seeking_description,
        "image_link": selected_venue.image_link,
        "past_shows": past_shows_records,
        "upcoming_shows": future_shows_records,
        "past_shows_count": shows_past_count,
        "upcoming_shows_count": future_shows_count
   }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form, meta={"csrf": False})

  #Check if data on form is valid
  if form.validate():
      #Create new venue object
      newVenue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
        )
  #Try to insert venue into database and commit change, send message when done
      try:
          db.session.add(newVenue)
          db.session.commit()
          flash('Venue ' + form.name.data + ' was successfully listed!')

  #On unsuccessful db insert, flash an error instead
      except ValueError as e:
          print(e)
          db.session.rollback()
          flash('An error occurred. Venue ' + form.name.data + ' could not be listed. ')

      finally:
          db.session.close()
  else:
        #Whow errors if there was a problem with invalid data to help with debugging
        flash(form.errors)

  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  print(venue_id)
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash("Venue deleted.")
  except:
      db.session.rollback()
      flash('An error occurred. Venue could not be deleted')
  finally:
      db.session.close()


  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  #Get artists from db
  all_artists = Artist.query.all()

  #List to store data
  data = []

  #Build records for list
  for each_artist in all_artists:
      artist_data = {
      "id": each_artist.id,
      "name": each_artist.name
      }
      data.append(artist_data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
   data = []
   #Get search item from form
   search_item = request.form.get('search_term')

   #Queries to get data and count of records
   matches = Artist.query.filter(Artist.name.ilike(f'%{search_item}%')).all()
   num_matches = Artist.query.filter(Artist.name.ilike(f'%{search_item}%')).count()

   for match in matches:
       future_shows = Show.query.filter(Show.artist_id == match.id, Show.start_time > datetime.now()).count()
       record = {
         "id": match.id,
         "name": match.name,
         "num_upcoming_shows": future_shows
       }

       data.append(record)


   response={
     "count": num_matches,
     "data": data
   }

   return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  selected_artist = Artist.query.get(artist_id)

  #Get past shows and their count
  shows_past = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Artist.id == artist_id, Show.start_time < datetime.now()).all()
  shows_past_count = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Artist.id == artist_id, Show.start_time < datetime.now()).count()

  #Get upcoming shows and their count
  future_shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Artist.id == artist_id, Show.start_time > datetime.now()).all()
  future_shows_count = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).filter(Artist.id == artist_id, Show.start_time > datetime.now()).count()

  #Lists to store records of past and future shows to build output
  past_shows_records = []
  future_shows_records = []

  for each_show in future_shows:
      record = {
      "venue_id": each_show.venue_id,
      "venue_name": each_show.venue.name,
      "venue_image_link": each_show.venue.image_link,
      "start_time": str(each_show.start_time)
      }

  for each_show in shows_past:
    record = {
    "venue_id": each_show.venue_id,
    "venue_name": each_show.venue.name,
    "venue_image_link": each_show.venue.image_link,
    "start_time": str(each_show.start_time)
    }


  data={
    "id": selected_artist.id,
    "name": selected_artist.name,
    "genres": selected_artist.genres,
    "city": selected_artist.city,
    "state": selected_artist.state,
    "phone": selected_artist.phone,
    "website": selected_artist.website_link,
    "facebook_link": selected_artist.facebook_link,
    "seeking_venue": selected_artist.seeking_venue,
    "seeking_description": selected_artist.seeking_description,
    "image_link": selected_artist.image_link,
    "past_shows": past_shows_records,
    "upcoming_shows": future_shows_records,
    "past_shows_count": shows_past_count,
    "upcoming_shows_count": future_shows_count,
   }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form, meta={"csrf": False})

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form, meta={"csrf": False})

   #First check to see if the form is valid
  if form.validate():
         #Get selected artist from database and edit it
         selected_artist = Artist.query.get(artist_id)

         selected_artist.name = form.name.data
         selected_artist.city = form.city.data
         selected_artist.state = form.state.data
         selected_artist.phone = form.phone.data
         selected_artist.genres = form.genres.data
         selected_artist.image_link = form.image_link.data
         selected_artist.facebook_link = form.facebook_link.data
         selected_artist.website_link = form.website_link.data
         selected_artist.seeking_venue = form.seeking_venue.data
         selected_artist.seeking_description = form.seeking_description.data

         try:
             db.session.commit()

     # On unsuccessful db insert, flash an error instead and rollback session
         except ValueError as e:
             print(e)
             db.session.rollback()
             flash('An error occurred. Artist could not be updated. ')

         finally:
             db.session.close()
  else:
           #Show errors if form is not valid to help with debugging
           flash(form.errors)


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm(request.form, meta={"csrf": False})
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form, meta={"csrf": False})

  if form.validate():
      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.address = form.address.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.website_link = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data
      try:
             db.session.commit()

     # On unsuccessful db insert, flash an error instead and rollback session
      except ValueError as e:
             print(e)
             db.session.rollback()
             flash('An error occurred. Venue could not be updated. ')

      finally:
             db.session.close()
  else:
           #Show errors if form is not valid to help with debugging
           flash(form.errors)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form, meta={"csrf": False})
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  #First check to see if the form is valid
  if form.validate():
        #Create new artist object with form data
        newArtist = Artist(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          phone = form.phone.data,
          genres = form.genres.data,
          image_link = form.image_link.data,
          facebook_link = form.facebook_link.data,
          website_link = form.website_link.data,
          seeking_venue = form.seeking_venue.data,
          seeking_description = form.seeking_description.data
          )

        try:
            #Try to add new artist object to the database and commit the session, flash message if successful
            db.session.add(newArtist)
            db.session.commit()
            flash('Artist ' + form.name.data + ' was successfully listed!')

    # On unsuccessful db insert, flash an error instead and rollback session
        except ValueError as e:
            print(e)
            db.session.rollback()
            flash('An error occurred. Artist ' + form.name.data + ' could not be listed. ')

        finally:
            db.session.close()
  else:
          #Show errors if form is not valid to help with debugging
          flash(form.errors)

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []

  #Query to get all shows
  all_shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()

  for each_show in all_shows:
      record = {
        "venue_id": each_show.venue_id,
        "venue_name": each_show.venue.name,
        "artist_id": each_show.artist_id,
        "artist_name": each_show.artist.name,
        "artist_image_link": each_show.artist.image_link,
        "start_time": each_show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      data.append(record)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form, meta={"csrf": False})

  #Check if form is valid
  if form.validate():

      #Create new show object
      newShow = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )

      try:
          #Try to add new show object to database and commit change, show message when done.
          db.session.add(newShow)
          db.session.commit()
          flash('Show was successfully listed!')

        # On unsuccessful db insert, flash an error instead and rollback session
      except ValueError as e:
          print(e)
          db.session.rollback()
          flash('An error occurred.  Show could not be listed. ')

      finally:
          db.session.close()

  else:
      #Show why form is not valid to help with debugging
      flash(form.errors)


  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
