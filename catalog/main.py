from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base,GunsmodelsName,GunsName, GmailUser
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///guns.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Guns Hub"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
gbs_cat = session.query(GunsmodelsName).all()

#completed
# login
@app.route('/login')
def showLogin():
    
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    gbs_cat = session.query(GunsmodelsName).all()
    gbes = session.query(GunsName).all()
    return render_template('login.html',
                           STATE=state, gbs_cat=gbs_cat, gbes=gbes)
    # return render_template('myhome.html', STATE=state
    # gbs_cat=gbs_cat,gbes=gbes)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = GmailUser(name=login_session['username'], email=login_session[
                   'email'])
    session.add(User1)
    session.commit()
    user = session.query(GmailUser).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(GmailUser).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(GmailUser).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####completed
# Home
@app.route('/')
@app.route('/home')
def home():
    gbs_cat = session.query(GunsmodelsName).all()
    return render_template('myhome.html', gbs_cat=gbs_cat)

#####completed
# Guns models for admins
@app.route('/GunsHub')
def GunsHub():
    try:
        if login_session['username']:
            name = login_session['username']
            gbs_cat = session.query(GunsmodelsName).all()
            gbs = session.query(GunsmodelsName).all()
            gbes = session.query(GunsName).all()
            return render_template('myhome.html', gbs_cat=gbs_cat,
                                   gbs=gbs, gbes=gbes, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing Guns based on Guns models
@app.route('/GunsHub/<int:gbid>/showGunsmodels')
def showGunsmodels(gbid):
    gbs_cat = session.query(GunsmodelsName).all()
    gbs = session.query(GunsmodelsName).filter_by(id=gbid).one()
    gbes = session.query(GunsName).filter_by(gunsmodelsnameid=gbid).all()
    try:
        if login_session['username']:
            return render_template('showGunsmodelss.html', gbs_cat=gbs_cat,
                                   gbs=gbs, gbes=gbes,
                                   uname=login_session['username'])
    except:
        return render_template('showGunsmodels.html',
                               gbs_cat=gbs_cat, gbs=gbs, gbes=gbes)

#####
# Add New Guns models
@app.route('/GunsHub/addGunsmodels', methods=['POST', 'GET'])
def addGunsmodels():
    if request.method == 'POST':
        company = GunsmodelsName(name=request.form['name'],
                           user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('GunsHub'))
    else:
        return render_template('addGunsmodels.html', gbs_cat=gbs_cat)

########
# Edit Guns models
@app.route('/GunsHub/<int:gbid>/edit', methods=['POST', 'GET'])
def editGunsmodels(gbid):
    editGunsmodels = session.query(GunsmodelsName).filter_by(id=gbid).one()
    creator = getUserInfo(editGunsmodels.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Guns models."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GunsHub'))
    if request.method == "POST":
        if request.form['name']:
            editGunsmodels.name = request.form['name']
        session.add(editGunsmodels)
        session.commit()
        flash("Guns models Edited Successfully")
        return redirect(url_for('GunsHub'))
    else:
        # gbs_cat is global variable we can them in entire application
        return render_template('editGunsmodels.html',
                               gb=editGunsmodels, gbs_cat=gbs_cat)

######
# Delete Guns models
@app.route('/GunsHub/<int:gbid>/delete', methods=['POST', 'GET'])
def deleteGunsmodels (gbid):
    gb = session.query(GunsmodelsName).filter_by(id=gbid).one()
    creator = getUserInfo(gb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Guns models."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GunsHub'))
    if request.method == "POST":
        session.delete(gb)
        session.commit()
        flash("Guns models Deleted Successfully")
        return redirect(url_for('GunsHub'))
    else:
        return render_template('deleteGunsmodels.html', gb=gb, gbs_cat=gbs_cat)

######
# Add New Guns Name Details
@app.route('/GunsHub/addGunsmodels/addGunsDetails/<string:gbname>/add',
           methods=['GET', 'POST'])
def addGunsDetails(gbname):
    gbs = session.query(GunsmodelsName).filter_by(name=gbname).one()
    # See if the logged in user is not the owner of Guns
    creator = getUserInfo(gbs.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGunsmodels', gbid=gbs.id))
    if request.method == 'POST':
        gunsname = request.form['gunsname']
        launchyear = request.form['launchyear']
        killrating = request.form['killrating']
        price = request.form['price']
        gunstype = request.form['gunstype']
        gunsdetails = GunsName(gunsname=gunsname, launchyear=launchyear,
                              killrating=killrating,
                              price=price,
                              gunstype=gunstype,
                              date=datetime.datetime.now(),
                              gunsmodelsnameid=gbs.id,
                              gmailuser_id=login_session['user_id'])
        session.add(gunsdetails)
        session.commit()
        return redirect(url_for('showGunsmodels', gbid=gbs.id))
    else:
        return render_template('addGunsDetails.html',
                               gbname=gbs.name, gbs_cat=gbs_cat)

######
# Edit Guns details
@app.route('/GunsHub/<int:gbid>/<string:gbename>/edit',
           methods=['GET', 'POST'])
def editGuns(gbid, gbename):
    gb = session.query(GunsmodelsName).filter_by(id=gbid).one()
    gunsdetails = session.query(GunsName).filter_by(gunsname=gbename).one()
    # See if the logged in user is not the owner of Guns
    creator = getUserInfo(gb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGunsmodels', gbid=gb.id))
    # POST methods
    if request.method == 'POST':
        gunsdetails.gunsname = request.form['gunsname']
        gunsdetails.launchyear = request.form['launchyear']
        gunsdetails.killrating = request.form['killrating']
        gunsdetails.price = request.form['price']
        gunsdetails.gunstype = request.form['gunstype']
        gunsdetails.date = datetime.datetime.now()
        session.add(gunsdetails)
        session.commit()
        flash("Guns Edited Successfully")
        return redirect(url_for('showGunsmodels', gbid=gbid))
    else:
        return render_template('editGuns.html',
                               gbid=gbid, gunsdetails=gunsdetails, gbs_cat=gbs_cat)

#####
# Delte Guns Edit
@app.route('/GunsHub/<int:gbid>/<string:gbename>/delete',
           methods=['GET', 'POST'])
def deleteGuns(gbid, gbename):
    gb = session.query(GunsmodelsName).filter_by(id=gbid).one()
    gunsdetails = session.query(GunsName).filter_by(gunsname=gbename).one()
    # See if the logged in user is not the owner of Guns
    creator = getUserInfo(gb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGunsmodels', gbid=gb.id))
    if request.method == "POST":
        session.delete(gunsdetails)
        session.commit()
        flash("Deleted Guns Successfully")
        return redirect(url_for('showGunsmodels', gbid=gbid))
    else:
        return render_template('deleteGuns.html',
                               gbid=gbid, gunsdetails=gunsdetails, gbs_cat=gbs_cat)

####
# Logout from current user
@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json
@app.route('/GunsHub/JSON')
def allGunsJSON():
    gunsmodels = session.query(GunsmodelsName).all()
    category_dict = [c.serialize for c in gunsmodels]
    for c in range(len(category_dict)):
        Guns = [i.serialize for i in session.query(
                 GunsName).filter_by(gunsmodelsnameid=category_dict[c]["id"]).all()]
        if Guns:
            category_dict[c]["guns"] = Guns
    return jsonify(GunsmodelsName=category_dict)

####
@app.route('/GunsHub/gunsmodels/JSON')
def categoriesJSON():
    Guns = session.query(gunsmodelsName).all()
    return jsonify(gunsmodels=[c.serialize for c in Guns])

####
@app.route('/Gunshub/guns/JSON')
def itemsJSON():
    items = session.query(GunsName).all()
    return jsonify(guns=[i.serialize for i in items])

#####
@app.route('/GunsHub/<path:guns_name>/guns/JSON')
def categoryItemsJSON(Guns_name):
    models = session.query(GunsmodelsName).fgunsilter_by(name=Guns_name).one()
    guns = session.query(GunsName).filter_by(gunsname=GunsCategory).all()
    return jsonify(GunsEdtion=[i.serialize for i in Guns])

#####
@app.route('/GunsHub/<path:guns_name>/<path:edition_name>/JSON')
def ItemJSON(guns_name, edition_name):
    gunsmodels = session.query(GunsmodelsName).filter_by(name=guns_name).one()
    gunsEdition = session.query(GunsName).filter_by(
           gunsname=edition_name,gunsname1=gunsmodels).one()
    return jsonify(gunsEdition=[gunsEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
