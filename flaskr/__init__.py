import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template,send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
import os

#template_folder='C:\\Users\\Shavkat\\flask-login-darlar\\1\\templates\\',static_url_path='C:\\Users\\Shavkat\\flask-login-darlar\\1\\static\\'
app=Flask(__name__,template_folder='C:\\Users\\Shavkat\\flask-login-darlar\\1\\templates',static_folder='C:\\Users\\Shavkat\\flask-login-darlar\\1')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config["SECRET_KEY"]=os.urandom(32)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
UPLOAD_FOLDER = 'C:\\Users\\Shavkat\\flask-login-darlar\\1\\static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db=SQLAlchemy(app)
Bootstrap(app)
login_manager=LoginManager(app)

class User(UserMixin,db.Model):
  id=db.Column(db.Integer,primary_key=True)
  full_name=db.Column(db.String,nullable=False)
  email=db.Column(db.String,nullable=False)
  username=db.Column(db.String,nullable=False,unique=True)
  password=db.Column(db.String,nullable=False)
  def __repr__(self):
    return "User %s" % self.id
  def insert(self):
    db.session.add(self)
    db.session.commit()
  def delete(self):
    db.session.delete(self)
    db.session.commit()

class Video(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  video=db.Column(db.String,nullable=False)
  user_id=db.Column(db.ForeignKey(User.id))
  def __repr__(self):
    return "Video %s" % self.id
  def insert(self):
    db.session.add(self)
    db.session.commit()
  def delete(self):
    db.session.delete(self)
    db.session.commit()

db.create_all()

@login_manager.user_loader
def load_user(user_id):
  return User.query.filter_by(id=user_id).first()

@app.route('/')
def index():
  try:
    id=current_user.id
    return redirect("/home")
  except:
    videos=Video.query.all()
    return render_template('dashboard.html',videos=videos)
@app.route('/videos/<video>',methods=["POST"])
@login_required
def delete_video(video):
  found_video=Video.query.filter_by(user_id=current_user.id,video=video).first()
  if not found_video:
    flash("Video topilmadi")
    return redirect("/home")
  found_video.delete()
  flash("Video o'chirildi")
  return redirect("/videos")
  flash("Video muallifi emassiz")
  return redirect("/videos")
@app.route('/login',methods=["POST","GET"])
def login():
  if request.method=="POST":
    body=request.get_json()
    print(body)
    user= User.query.filter_by(username=request.form["username"],password=request.form["password"]).first()
    if not user:
      flash("Foydalanuvchi topilmadi")
      return render_template('login.html')
    login_user(user)
    return redirect("/")
  else:
    return render_template('login.html')
@app.route('/logout',methods=["POST","GET"])
@login_required
def logout():
  if request.method=="POST":
    logout_user()
    return redirect("/")
  else:
    return render_template('logout.html')

@app.route('/signup',methods=["POST","GET"])
def signup():
  if request.method == "POST":
    user= User(full_name=request.form["full_name"],username=request.form["username"],email=request.form["email"],password=request.form["password"])
    try:
      user.insert()
      return redirect('/login')
    except Exception as e:
      flash("Xatolik yuz berdi")
      return render_template('signup.html',message=message)
  else:
    return render_template('signup.html')

@app.route('/videos')
def videos():
  videos=Video.query.all()
  return render_template('videos.html',videos=videos)
      
@app.route('/videos/new')
@login_required
def upload_file_view():
   return render_template('upload.html')
	
@app.route('/videos/new', methods = ['POST'])
@login_required
def upload_file():
  f = request.files['file']
  filename=secure_filename(f.filename)
  f.save(filename)
  newVideo=Video(video=filename,user_id=request.form["user_id"])
  newVideo.insert()
  return redirect("/display/"+str(newVideo.video))

@app.route('/display/<video>')
def display_video(video):
  video=Video.query.filter_by(video=video).first()
  if not video:
    flash('Video topilmadi')
    return redirect('/')
  return redirect(url_for('static',filename=''+video.video))

@app.route('/home')
@login_required
def home():
  try:
    videos=Video.query.all()
    return render_template("dashboard.html",videos=videos)
  except Exception as e:
    return "Unauthorized\n"+str(e)
@app.errorhandler(401)
def auth_error(e):
  return render_template('error_pages/401.html')
@app.errorhandler(404)
def page_not_found_error(e):
  return render_template('error_pages/404.html')