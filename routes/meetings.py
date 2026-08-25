from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from pymongo import MongoClient

meetings_bp = Blueprint('meetings', __name__, template_folder = 'templates')

client = MongoClient('localhost', 27017)
db = client.dibs

@meetings_bp.route('/')
def get_meetings():
  meetings = list(db.meetings.find({}, {'id': False}))
  print(meetings)
  return render_template('meetings.html', meetings=meetings)

#@meetings_bp.route('/', methods=['POST'])
#def post_meeting():
