#/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. 
#You will need to modify it to connect to your Part 2 database in order to use the data.

# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = "postgresql://zw2364:6005@w4111vm.eastus.cloudapp.azure.com/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. 
#This is only an example showing you how to run queries in your database using SQLAlchemy.
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/rank')
def rank():
  cursor = g.conn.execute("SELECT t.name,r.win,r.draw,r.lose,r.standing from rank r join team t on r.tid=t.tid order by r.standing desc")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("rank.html", **context)

@app.route('/topscorer', methods=['GET'])
def topscorer():
  cursor = g.conn.execute("SELECT tmp.name,tt.name,tmp.goal,tmp.penalty FROM (topscorer t join player p on t.pkey=p.pkey) tmp join team tt on tmp.tid=tt.tid")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("topscorer.html", **context)
   
@app.route('/match', methods=['GET'])
def match():
  return render_template("match.html")

@app.route('/search_match', methods=['POST'])
def search_match():
  home = request.form['Home']
  away = request.form['Away']
  rounds = request.form['Rounds']
  if rounds.isdigit() != True and rounds != '': 
    return render_template("match.html")
  if rounds != '' and home == '' and away == '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and m.numberofgames = %s" % (rounds))
  elif rounds == '' and home != '' and away == '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and  m.home = '%s' order by m.numberofgames" % (home))
  elif rounds == '' and home == '' and away != '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and m.away = '%s' order by m.numberofgames" % (away))
  elif rounds != '' and home != '' and away == '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and m.numberofgames = %s and m.home = '%s' order by m.numberofgames" % (rounds, home))
  elif rounds != '' and home == '' and away != '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and m.numberofgames = %s and m.away = '%s' order by m.numberofgames" % (rounds, away))
  elif rounds == '' and home != '' and away != '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and m.home='%s' and m.away = '%s' order by m.numberofgames" % (home, away))
  elif rounds != '' and home != '' and away != '':
    cursor = g.conn.execute("SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name FROM match m, team h,team a WHERE m.home=h.tid and m.away=a.tid and m.home='%s' and m.away = '%s' and m.numberofgames=%s order by m.numberofgames" % (home, away, rounds))
  else:
    return render_template("match.html")
  results = []
  title = [u'Rounds', u'Home', u'Home score', u'Away score', u'Away']
  results.append(title)
  for result in cursor:
    results.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = results)
  return render_template("match.html", **context)

@app.route('/team', methods=['GET'])
def team():
  return render_template("team.html")

@app.route('/search_team', methods=['POST'])
def search_team():
  team = request.form['Team']
  if team == '':
    return render_template("team.html")
  results = []
  cursor = g.conn.execute("SELECT t.tid,t.name,t.stadium FROM team t WHERE t.tid = '%s'" % (team))
  title = [u'Team', u'Name', u'Stadium']
  results.append(title)
  for result in cursor:
    results.append(result)
  cursor.close()
  
  cursor = g.conn.execute("SELECT m.name,m.ismaincoach FROM manager m WHERE m.tid = '%s'" % (team))
  title = [u'Caoch', u'isMainCoach']
  results.append(title)
  for result in cursor:
    results.append(result)
  cursor.close()  

  cursor = g.conn.execute("SELECT p.pid,p.name,p.position,p.nationality FROM player p WHERE p.tid = '%s'" % (team))
  title = [u'Number', u'Name', u'Position', u'Nationnality']
  results.append(title)
  for result in cursor:
    results.append(result)
  cursor.close()
  context = dict(data = results)  
  return render_template("team.html", **context)

@app.route('/player', methods=['GET'])
def player():
  return render_template("player.html")

@app.route('/player_information', methods=['POST'])
def player_information():
  nationality = request.form['Nationality']
  team = request.form['Team']
  number = request.form['Number']
  position = request.form['Position']
  if number.isdigit() != True and number != '':
    return render_template("player.html") 
  if nationality != '' and team == '' and number == '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s'" % (nationality))
  elif nationality == '' and team != '' and number == '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.tid  = '%s'" % (team))
  elif nationality == '' and team == '' and number != '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.pid  = %s" % (number))
  elif nationality == '' and team == '' and number == '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.position  = '%s'" % (position))
  elif nationality != '' and team != '' and number == '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.tid  = '%s'" % (nationality,team))
  elif nationality != '' and team == '' and number != '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.pid  = %s" % (nationality,number))
  elif nationality != '' and team == '' and number == '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.position  = '%s'" % (nationality,position))
  elif nationality == '' and team != '' and number != '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.tid  = '%s' and p.pid  = %s" % (team,number))
  elif nationality == '' and team != '' and number == '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.tid  = '%s' and p.position  = '%s'" % (team,position))
  elif nationality == '' and team == '' and number != '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.pid  = '%s' and p.position  = '%s'" % (number,position))
  elif nationality != '' and team != '' and number != '' and position == '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.tid  = '%s' and p.pid  = %s" % (nationality,team,number))
  elif nationality != '' and team != '' and number == '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.tid  = '%s' and p.position  = '%s'" % (nationality,team,position))
  elif nationality != '' and team == '' and number != '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.pid  = %s and p.position  = '%s'" % (nationality,number,position))
  elif nationality == '' and team != '' and number != '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.tid  = '%s' and p.pid  = %s and p.position  = '%s'" % (team,number,position))
  elif nationality != '' and team != '' and number != '' and position != '':
    cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.nationality  = '%s' and p.tid  = '%s' and p.pid  = %s and p.position  = '%s'" % (nationality,team,number,position))
  else:
    return render_template("player.html")
  
  results = []
  title = [u'Name', u'Number', u'Team', u'Position', u'Nationality']
  results.append(title)
  for result in cursor:
    results.append(result)
  cursor.close()
  context = dict(data = results)  
  return render_template("player.html", **context)

@app.route('/player_name', methods=['POST'])
def player_name():
  name = request.form['Name']
  if name == '':
    return render_template("player.html")
  cursor = g.conn.execute("SELECT p.name,p.pid,p.tid,p.position,p.nationality FROM player p WHERE p.name  = '%s'" % (name))
  results = []
  title = [u'Name', u'Number', u'Team', u'Position', u'Nationality']
  results.append(title)
  for result in cursor:
    results.append(result)
  cursor.close()
  context = dict(data = results)  
  return render_template("player.html", **context)

@app.route('/goal', methods=['POST'])
def goal():
  rounds = request.form['Rounds']
  team = request.form['Team']
  name = request.form['Name']
  if rounds.isdigit() != True and rounds != '': 
    return render_template("player.html")
  if rounds != '' and team == '' and name == '':
    cursor = g.conn.execute("SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid WHERE m.numberofgames = %s " % (rounds))
  elif rounds != '' and team != '' and name == '':
    cursor = g.conn.execute("SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid WHERE tmp.tid = '%s' and m.numberofgames = %s and (m.home = '%s' or m.away = '%s') " % (team,rounds,team,team))
  elif rounds =='' and team !='' and name == '':
    cursor = g.conn.execute("SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid WHERE tmp.tid = '%s' and (m.home = '%s' or m.away = '%s') " % (team,team,team))
  elif rounds != '' and team == '' and name != '':
    cursor = g.conn.execute("SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid WHERE tmp.name = '%s' and m.numberofgames = %s" % (name,rounds))
  elif rounds != '' and team != '' and name != '':
    cursor = g.conn.execute("SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid WHERE tmp.name = '%s' and tmp.tid = '%s' and m.numberofgames = %s and (m.home = '%s' or m.away = '%s') " % (name,team,rounds,team,team))
  elif rounds == '' and team == '' and name != '':
    cursor = g.conn.execute("SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid WHERE tmp.name = '%s'" % (name))
  else:
    return render_template("player.html")
  results = []
  title = [u'Rounds', u'Team', u'Name', u'Time', u'OwnGoal', u'Penalty']
  results.append(title)
  for result in cursor:
    results.append(result)
  cursor.close()
  context = dict(data = results)  
  return render_template("player.html", **context)

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

