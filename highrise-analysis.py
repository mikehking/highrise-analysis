# Using https://github.com/seibert-media/Highton to integrate with Highrise CRM
# Written for Python 3.3 -- change to v3.3 with this cmd:  source py3env/bin/activate

# Purpose:  Count activity by Highrise CRM user in the last 365 days
# Created by @mikehking in early July 2015

from highton import Highton
from datetime import date, datetime, timedelta
import time
import pickle
from config import *

# ===================================================================
def Create_Notes_Backup(highrise_key, highrise_user, notesfile, userfile, peoplefile, casesfile, trailing_days = 365):
  # Function to create new Notes backup file of Highrise instance (this can take a while)
  print('Entered Create_Notes_Backup function')
  high = Highton(api_key = highrise_key, user = highrise_user) # Connect to API
  print('Connected to Highrise')
  users = high.get_users()
  print('Pulled ', len(users), ' users')
  people = high.get_people()
  print('Pulled ', len(people), ' people')
  cases = high.get_cases()
  deals = high.get_deals()
  companies = high.get_companies()
  
  notes = []
  tmp_notes = []
  print('Started creating notes array')
  
  # Collect Notes data by person
  for person in people:
    tmp_notes = high.get_person_notes(person.highrise_id)
    time.sleep(.4) # Pause per API limits https://github.com/basecamp/highrise-api
    if (type(tmp_notes) is list):
      print('Pulled ', len(tmp_notes), ' notes for ', person.first_name, ' ', person.last_name)
      #if tmp_notes[0].created_at > datetime.utcnow() + timedelta(days = -trailing_days):
      #  notes.extend(high.get_person_notes(person.highrise_id))
      notes.extend(tmp_notes) # Removed redundant data call by reusing tmp_notes
  
  # Collect Notes by case
  if cases: # Watch out for Highrise environments with no cases
    for case in cases:
      tmp_notes = high.get_case_notes(case.highrise_id)
      time.sleep(.3) # Pause per API limits https://github.com/basecamp/highrise-api
      if (type(tmp_notes) is list):
        print('Pulled ', len(tmp_notes), ' notes from ', case.name)
        #if tmp_notes[0].created_at > datetime.utcnow() + timedelta(days = -trailing_days):
        #  notes.extend(high.get_person_notes(person.highrise_id))
        notes.extend(tmp_notes) # Removed redundant data call by reusing tmp_notes

  # Collect Notes by deal
  if deals: # Watch out for Highrise environments with no cases
    for deal in deals:
      tmp_notes = high.get_deal_notes(deal.highrise_id)
      time.sleep(.3) # Pause per API limits https://github.com/basecamp/highrise-api
      if (type(tmp_notes) is list):
        print('Pulled ', len(tmp_notes), ' notes from ', deal.name)
        notes.extend(tmp_notes) 
  
  # Collect Notes by company
  if companies: # Watch out for Highrise environments with no cases
    for company in companies:
      tmp_notes = high.get_company_notes(company.highrise_id)
      time.sleep(.3) # Pause per API limits https://github.com/basecamp/highrise-api
      if (type(tmp_notes) is list):
        print('Pulled ', len(tmp_notes), ' notes from ', company.name)
        #if tmp_notes[0].created_at > datetime.utcnow() + timedelta(days = -trailing_days):
        #  notes.extend(high.get_person_notes(person.highrise_id))
        notes.extend(tmp_notes) # Removed redundant data call by reusing tmp_notes        
        
  # Note:  Notes associated with deals and companies are not counted
  print('Finished creating notes array')
  
  # Final Step:  Export lists into pickle files
  with open(notesfile, 'wb') as f:
    pickle.dump(notes, f)
  with open(userfile, 'wb') as g:
    pickle.dump(users, g)
  with open(peoplefile, 'wb') as h:
    pickle.dump(people, h)
  print('Exported lists to *.bak files')
  
# ===================================================================  
  
def Update_Notes_Backup(api_key, highrise_user, notesfile, userfile, peoplefile, trailing_days = 365):
  # Function to update a Notes backup file with any recently-added notes
  # STUB - NOT CREATED YET
  print('Entered Update_Notes_Backup function')
  notes = []
  # Load current list from notesfile
  with open(notesfile, 'rb') as f:
    notes = pickle.load(f)
  
  # STUB - connect to Highrise and update with recent notes
  
  # STUB - save updated notes list to notesfile
  
# ===================================================================

def Analyze_Notes_Backup(notesfile, userfile, peoplefile, trailing_days = 365):
  # Function to analyze notes backup:
  #   1. Count number of activities in last trailing_days days
  #   2. Identify date of last note update
  print('Entered Analyze_Notes_Backup function')
  notes = []
  users = []
  people = []
  
  # Load the lists
  with open(notesfile, 'rb') as a:
    notes = pickle.load(a)
  with open(userfile, 'rb') as b:
    users = pickle.load(b)
  with open(peoplefile, 'rb') as c:
    people = pickle.load(c)
 
  # Start counting
  user_activity_count = {}
  last_user_update = {}
  for user in users:
    user_activity_count[user.highrise_id] = 0
    last_user_update[user.highrise_id] = date(1901, 1, 1)

  print('Started counting user activity by note')
  for note in notes:
    if note.created_at > (datetime.utcnow() - timedelta(days = trailing_days)):
      #print('Note created ', note.created_at, ' by ', note.author_id, ' regarding ', note.body)
      try:      
        user_activity_count[note.author_id] += 1
      except KeyError:
        print('User no longer exists')
    try:
      if (note.created_at.date() > last_user_update[note.author_id]):
        last_user_update[note.author_id] = note.created_at.date()
    except KeyError:
      print('...')
  print('Finished counting user activity by note')
  print('=======================================')

  f = open('highrise-analysis-output.txt', 'w')
  f.write('Report run on ')
  f.write(str(date.today()))
  f.write('\n Highrise People Count: ')
  f.write(str(len(people)))
  f.write('\n ============================ \n')

  for user in users:
    print(user.name, ' has performed ', user_activity_count[user.highrise_id], ' activities')
    f.write(str.join(' ', (user.name, ', ', str(user_activity_count[user.highrise_id]))))
    if last_user_update[user.highrise_id] == date(1901, 1, 1):
      print(user.name, ' has not updated Highrise in the last 365 days')
      f.write(str.join(' ', (', NO_UPDATES\n')))
    else:
      print(user.name, ' last updated Highrise ', last_user_update[user.highrise_id])
      f.write(str.join(' ', (', ', str(last_user_update[user.highrise_id]), '\n')))
  all_done = time.time()

  f.close
     
# ===================================================================
if __name__ == "__main__":
  # Test Environment Analysis
  Create_Notes_Backup(TEST_API_KEY, TEST_API_USR, 'highrise-test-notes.bak', 'highrise-test-users.bak', 'highrise-test-people.bak', 'highrise-test-cases.bak', trailing_days = 365000) 
  Analyze_Notes_Backup('highrise-test-notes.bak', 'highrise-test-users.bak', 'highrise-test-people.bak', trailing_days = 365000)
  
  # Production Environment Analysis
  #Create_Notes_Backup(PROD_API_KEY, PROD_API_USR, 'highrise-production-notes.bak', 'highrise-production-users.bak', 'highrise-production-people.bak', 'highrise-production-cases.bak', trailing_days = 365) # Production Environment
  #Analyze_Notes_Backup('highrise-production-notes.bak', 'highrise-production-users.bak', 'highrise-production-people.bak', trailing_days = 365)
