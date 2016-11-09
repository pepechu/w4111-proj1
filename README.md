# w4111-proj1
Project of Columbia COMS w4111 Introduction to Database Course
COMS4111 Database Project 1.3


1. The URL of your web application. http://40.121.160.219:8111

2. Description
On the hello site (home page), there are some option to choose, which would direct to another
page. Rank of LaLiga: This gives the rank of the Spanish league of the first 7 rounds. Top scorer of LaLiga: This gives the rank of top scorer in the Spanish league of the first 7 rounds. Search for matches: Input information into the boxes to get the match information. If you leave
everything blank, there is no result. You can input information in either box or 2, or 3 together
to search for the information. Note in the “Home” and “Away”, you should type the
abbreviation of the teams. What’s more, we only have data of the first 7 rounds. Search for team: In this page, you input the abbreviation of any LaLiga team. The page would
show the team’s information to you including the coach information and player information. Player: In this page, you have multiple choices to search. You can type name of the player to
search for his information. You can also type nationality or team or number or position to
search specific players in the LaLiga. What’s more, you can input the rounds or name or team in
order to search for the goals.

3. Interesting operations
(1).
In the player page(http://40.121.160.219:8111/player), you can do searches within the all
player data of the La Liga. For example, if you want to search for all Spanish goal keepers in the
league, just type as shown in the picture below:
By clicking search at the end of the second row, the information would be displayed, and this is
identical to the sql:
SELECT p.name,p.pid,p.tid,p.position,p.nationality
FROM player p
WHERE p.nationality = 'Spain' and p.position = 'GK' And we get the result on the web shown in the following picture:
Also you can filter the information by adding their number (number appears in the player’s suit)
and/or the team: for example, all the Midfielder wearing number 10:
This is equal to the sql query:
SELECT p.name,p.pid,p.tid,p.position,p.nationality
FROM player p
WHERE p.pid =10 and p.position = 'MF'
Users can also search for goals scored by a player or a team or just a round, or any combination, but here we don’t have data to show all goals happen in the first 7 rounds, only some of
selected matches: for example, to search Pique’s goal in the 7
th round with the following input:
This is identical to the query:
SELECT m.numberofgames, tmp.tid, tmp.name, tmp.time, tmp.isowngoal, tmp.ispenalty
FROM (goal g join player p on g.pkey=p.pkey) tmp join match m on tmp.matchid=m.matchid
WHERE tmp.name = 'Gerard Pique' and m.numberofgames =7
And the result is :
(2).
In the match page, you can search for any match happened in the first 7 round, by entering
information of the teams and/or the round number. For instance, if you want to know the
match statistics in the first round, you should input 1 in the round box and then search for the
result:
The corresponding sql is :
SELECT m.numberofgames,h.name,m.hscore,m.ascore,a.name
FROM match m, team h,team a
WHERE m.home=h.tid and m.away=a.tid and m.numberofgames = 1
And in this way we can get all matches happen in the first round with the corresponding scores
and teams against their rivalries. Also, we can filter the information by team, like searching for team Barcelona’s performance as
an away team:
Why interesting: For a user of these websites, he can acquire different aspect of information
that the league has presented like what was the score of the match he really cares about but
too busy to watch it, and catch up with the statistics given. Also, the information of his favorite
teams and players. In there websites we provide different ways of querying data, so it would be
fun and easy to search.
