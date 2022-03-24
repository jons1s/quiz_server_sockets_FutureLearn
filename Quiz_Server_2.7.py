# The socket server library is a more powerful module for handling sockets,
# it will help you set up and manage multiple clients in the next step
import socketserver
from collections import namedtuple
from fl_networking_tools import get_binary, send_binary
from random import choice
from time import sleep, time
#Allow threading
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
from threading import Event

'''
Commands:by client
PLACE YOUR COMMANDS HERE
************************
JOIN - request to join + team name
STAT - request server status
QUES - request question
ANSR - answer, team response
'''

# Named tuples are extensions of the tuple structure, with contents you
# can refer to by name. In this case, the question will be held in a variable
# named quest and the answer in answer.
# This is just the set up of the question - it will be sent to the client
# using the send_binary function when a request is made.
Question = namedtuple('Question', ['quest', 'answer'])

quiz_questions = [
    Question("Expand the acronym ALU", "Arithmetic Logic Unit"),
    Question("Expand the acronym RAM", "Random Access Memory"),
    Question("What does ROM stand for?", "Read Only Memory"),
    Question("What does GIGO mean?", "Garbage In Garbage Out"),
    Question("What does UDP stand for?","User Datagram Protocol"),
    Question("Is TCP a reliable communication protocol? (Y/N)","Y")
]

tie_breaker_question = ["Is UDP a reliable communication protocol? (Y/N)","N"]

# The socketserver module uses 'Handlers' to interact with connections.
# When a client connects a version of this class is made to handle it.
class QuizGame(socketserver.BaseRequestHandler):
    # The handle method is what actually handles the connection
    
    def handle(self):
        #Retrieve Command
        questions_asked = 1
        for command in get_binary(self.request):
            global players, answers_so_far, current_question, scores, number_of_questions, team_time
            
            if questions_asked <= number_of_questions or command[0] == "ANSR":#checks if all questions have been asked
                if command[0] == "JOIN":
                    #Client sends tuple JOIN,'team name'
                    team_name = command[1]
                    #add team name to players list
                    players.append(team_name)
                    #store score with team name and initialise with 0
                    scores[team_name] = 0
                    #store time with team_time and initialise with 0
                    team_time[team_name] = 0
                    #Check if all players have joined
                    if len(players) == number_of_players:
                        ready_to_start.set()
                    #send acknowledgement of connection
                    reply = "\nWelcome " + team_name + " Good Luck\n"
                    send_binary(self.request,(1,reply))
                    print(reply)# Keeps track of what server sending, can #'d out later
                    #wait until all players have joined when ready_to_start is set
                    ready_to_start.wait()
            
                elif command[0] == "QUES":
                    #Send question if == None randomly choose question and set wait for answer
                    if current_question == None:
                        current_question = choice(quiz_questions)
                        wait_for_answer.clear()
                    #send current_question
                    send_binary(self.request, (2, current_question.quest))
                    #These print lines letting you see what server is doing and can be #'d out later
                    print(current_question.quest + "\n" + current_question.answer+"\n")
                    #increment number of questions asked
                    questions_asked += 1
                    print(questions_asked)
                
                elif command[0] == "STAT":
                    #Checks when all players logged in to start game an first question
                    if ready_to_start.isSet() and not wait_for_answer.isSet():
                        starting = "\nQuiz is starting with " + str(number_of_players) + " teams and " + str(number_of_questions) + " Questions\nQuestion 1\n"
                        send_binary(self.request,[4,starting])
                    #Updates teams with their scores so far and asks next question
                    elif ready_to_start.isSet() and wait_for_answer.isSet():
                        scores_so_far = {}
                        for k,v in scores.items():
                            scores_so_far[k] = v
                        continuing = "\nQuiz is continuing      " + str(scores_so_far) + "\nQuestion number " + str(questions_asked) + "\n"
                        send_binary(self.request,[4,continuing])                

                
                elif command[0] == "ANSR":
                    answers_so_far +=1
                    #check if answer correct (using .lower to change to lower case, ignoring capitalisation) increment score and reply string
                    if command[1].lower() == current_question.answer.lower():
                        scores[team_name] += 1
                        reply = " correct\n" + "\nCorrect answer is " + current_question.answer + "\nYour Score = " + str(scores[team_name])
                    
                    else:
                        reply = " wrong\n" + "\nCorrect answer is " + current_question.answer + "\nYour Score = " + str(scores[team_name])
                    #check how many answers recieved
                    #when everyone answered send reply and reset current question
                    #set wait for answer
                    if answers_so_far == len(players):
                        quiz_questions.remove(current_question)
                        current_question = None
                        wait_for_answer.set()
                    wait_for_answer.wait()
                    #Once all answers in, send reply, reset answers so far for next question
                    send_binary(self.request, (3, reply))
                    answers_so_far = 0
            else:#as all questions now asked and answered, need to determine winner
                #find best team with best score
                best_score = 0
                for key,value in scores.items():
                    if int(value) > best_score:
                        best_score = int(value)
                        best_team = key
                        
                check_for_tie = best_score
                #check at least one team scored if all teams 0 no winners
                if check_for_tie == 0:
                    reply = 'No winners this time'
                    send_binary(self.request, (8, reply))
                    sleep(1)
                    #end game
                    send_binary(self.request, (0, "*****Game Over*****")) 
                    quiz_server.shutdown()
                    
                else:
                    #teams with best_score in dictionary scores
                    #added to new dictionary tied_teams, tied is a simple counter
                    tied=0
                    tied_teams = {}
                    for k,v in scores.items():
                        if int(v) == check_for_tie:
                            tied += 1
                            tied_teams[k] = v
                    #Check to see if more than one winner and print out accordingly        
                    if tied == 1:#Only 1 winning team
                        reply = 'The winners are' + str(tied_teams)
                        send_binary(self.request, (8, reply))
                        sleep(1)
                        #end game
                        send_binary(self.request, (0, "*****Game Over*****"))
                        quiz_server.shutdown()
                        
                    else:#tied for 1st place
                        reply =str(tied) + " teams got a score of, " + str(check_for_tie) + "\n" + "Time for the tie break question!"+"\nFirst correct answer wins.."
                        send_binary(self.request, (9, reply))
                        reply = "\n****This tie breaker for teams " +str(tied_teams) + " only*****"
                        send_binary(self.request, (9, reply))
                        sleep(2)
                        
                        #Tie breaker question with first correct answer winning 
                        reply = tie_breaker_question[0]
                        send_binary(self.request, (2,reply))
                        sent_time = time()#set start time when sent to each client
                        #reset answers so far to zero and wait for answer
                        answers_so_far = 0
                        wait_for_answer.clear()
                        
                        for command in get_binary(self.request):
                            #Check if correct answer increment score and calculate time
                            if command[0] == "ANSR":
                                answers_so_far += 1
                                #check how many answers recieved
                                #set wait for answer
                                if answers_so_far == tied:
                                    wait_for_answer.set()
                                if command[1].lower() == tie_breaker_question[1].lower():
                                    answer_time = round((time() - sent_time),2) #find time to answer question
                                    scores[team_name] += 1
                                    team_time[team_name] = answer_time
                                    wait_for_answer.wait()
                                    reply = " correct\n" + "\nCorrect answer is " + tie_breaker_question[1] + "\nScore = " + str(scores[team_name])
                                    send_binary(self.request, (3, reply))
                                    shortest_time = time() #sets shortest time to large value
                                    #find shortest time and set best_team to key value
                                    for k,v in team_time.items():
                                        if float(v) < shortest_time:
                                            shortest_time = float(v)
                                            best_team = k
                                        
                                    print("correct", str(answer_time))
                                    reply = "Winners are " + best_team + " in a time of " + str(shortest_time) + "secs"
                                    print(reply)
                                    send_binary(self.request, (8, reply))
                                    sleep(1)
                                    #end game
                                    send_binary(self.request, (0, "*****Game Over*****")) 
                                    quiz_server.shutdown()
                                else:#if wrong answer set team time to large number
                                    answer_time = round(time(),2)
                                    team_time[team_name] = answer_time
                                    wait_for_answer.wait()
                                    reply = " wrong\n" + "\nCorrect answer is " + str(tie_breaker_question[1]) + "\nScore = " + str(scores[team_name])
                                    send_binary(self.request, (8, reply))
                                    print("wrong" + str(answer_time))
                                    sleep(1)
                                    #end game
                                    send_binary(self.request, (0, "*****Game Over*****")) 
                                    quiz_server.shutdown()
                                
            
#Your server code goes here
server_address = "127.0.0.1"
number_of_players = 2


players = [] #stores team names in a list
answers_so_far = 0
ready_to_start = Event()
wait_for_answer = Event()
current_question = None
scores = {} #stores scores in a dictionary, key = team_name, value = score
team_time = {} # stores time reply recieved in a dictionary, key = team_name, value = time
number_of_questions = len(quiz_questions)
print("Number of Questions: ",number_of_questions)
print("Number of players required: ",number_of_players)
print("Server address: "+server_address)


# Open the quiz server and bind it to a port - creating a socket
# This works similarly to the sockets you used before,
# but you have to give it both an address pair (IP and port) and a handler
# "QuizGame" for the server.
quiz_server = ThreadedTCPServer((server_address, 2065), QuizGame)
print("Server starting")
# Activate the server; this will keep running until you
# interrupt the program with Ctrl-C
quiz_server.serve_forever()
quiz_server.shutdown()
#shutting down connection and cleaning up, on mac
print("***************************\nEnd\n*********************\nQuit with Ctrl-C then Ctrl -fn 6")
