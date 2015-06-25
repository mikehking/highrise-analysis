# Using https://github.com/seibert-media/Highton to integrate with Highrise CRM
# Change to Python 3.3 with this command:  source py3env/bin/activate
# Purpose:  Count activity by Highrise CRM user in the last 365 days
from highton import Highton
from datetime import date, datetime, timedelta

#initialize Highrise instance
high = Highton(
    api_key = 'THIS_IS_A_SECRET',
    user = 'SECRET_USERNAME'
)

users = high.get_users()

people = high.get_people()

notes = []
tmp_notes = []
for person in people:
  #print('Person: ', person.first_name, person.last_name)
  #person_highrise_id = person.highrise_id
  #print(person.last_name)
  tmp_notes = high.get_person_notes(person.highrise_id)
  if (type(tmp_notes) is list):
    notes.extend(high.get_person_notes(person.highrise_id)) # No quotes for person_highrise_id in ()'s

  #print('Notes is type ', type(notes), ' for ', person.first_name, ' ', person.last_name)

#print('total number of notes is ', len(notes))
  
for user in users:
  #print(user.name, ' has ', notes.author_id.count(user.highrise_id), ' activities')
  counter = 0
  for note in notes:
    if (note.author_id == user.highrise_id) and (note.created_at > datetime.utcnow() + timedelta(days = -365)):
      counter += 1
  print(user.name, ' has performed ', counter, ' activities')
