# The socket server library is a more powerful module for handling sockets,
# it will help you set up and manage multiple clients in the next step
import socketserver
from collections import namedtuple
from fl_networking_tools import get_binary, send_binary
from random import choice

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
# named q and the answer in answer.
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

# The socketserver module uses 'Handlers' to interact with connections.
# When a client connects a version of this class is made to handle it.
class QuizGame(socketserver.BaseRequestHandler):
    # The handle method is what actually handles the connection
    
    def handle(self):
        #Retrieve Command
        questions_asked = 1
        for command in get_binary(self.request):
            global players, answers_so_far, current_question, scores, number_of_questions
            
            if questions_asked <= number_of_questions or command[0] == "ANSR": 
                if command[0] == "JOIN":
                    #Client sends tuple JOIN,'team name'
                    team_name = command[1]
                    #add team name to players list
                    players.append(team_name)
                    #store score with team name
                    scores[team_name] = 0
                    #Check if all players have joined
                    #send acknowledgement of connection
                    #wait until all players have joined when ready_to_start is set
                    if len(players) == number_of_players:
                        ready_to_start.set()
                    send_binary(self.request,(1,""))
                    ready_to_start.wait()
            
                elif command[0] == "QUES":
                    #Send question if None choose question
                    #if already chosen send it
                    if current_question == None:
                        current_question = choice(quiz_questions)
                        wait_for_answer.clear()
                    send_binary(self.request, (2, current_question.quest))
                    print(current_question.quest + "\n" + current_question.answer)
                    questions_asked += 1
                    print(questions_asked)
                
                elif command[0] == "STAT":
                    if ready_to_start.isSet() and not wait_for_answer.isSet():
                        starting = "\nQuiz is starting with " + str(number_of_players) + " teams and " + str(number_of_questions) + " Questions\nQuestion 1\n"
                        send_binary(self.request,[4,starting])
                    elif ready_to_start.isSet() and wait_for_answer.isSet():
                        scores_so_far = {}
                        for k,v in scores.items():
                            scores_so_far[k] = v
                        continuing = "\nQuiz is continuing      " + str(scores_so_far) + "\nQuestion number " + str(questions_asked) + "\n"
                        send_binary(self.request,[4,continuing])                

                
                elif command[0] == "ANSR":
                    answers_so_far +=1
                    #check if answer correct and save in reply
                    if command[1].lower() == current_question.answer.lower():
                        scores[team_name] += 1
                        reply = " correct\n" + "\nCorrect answer is " + current_question.answer + "\nScore = " + str(scores[team_name])
                    
                    else:
                        reply = " wrong\n" + "\nCorrect answer is " + current_question.answer + "\nScore = " + str(scores[team_name])
                    #Check how many answers recieved
                    #reset current question when everyone answered
                    #set wait for answer
                    if answers_so_far == len(players):
                        quiz_questions.remove(current_question)
                        current_question = None
                        wait_for_answer.set()
                    wait_for_answer.wait()
                    #Once all answers in, send reply update answers so far
                    send_binary(self.request, (3, reply))
                    answers_so_far = 0
            else:
                best_score = 0
                for key,value in scores.items():
                    if int(value) > best_score:
                        best_score = int(value)
                        best_team = key
                        
                check_for_tie = best_score
                #check at least one team scored
                if check_for_tie == 0:
                    reply = 'No winners this time'
                    send_binary(self.request, (8, reply))
                else:
                    #teams with best_score in dictionary scores
                    #added to new dictionary tied_teams
                    tied=0
                    tied_teams = {}
                    for k,v in scores.items():
                        if int(v) == check_for_tie:
                            tied += 1
                            tied_teams[k] = v
                    #Check to see if more than one winner and print out accordingly        
                    if tied > 1:
                        reply =str(tied) + " teams got a score of, " + str(check_for_tie) + "\n" + 'The joint winners are' + str(tied_teams)
                        send_binary(self.request, (8, reply))
                    else:
                        reply = 'The winners are' + str(tied_teams)
                        send_binary(self.request, (8, reply))
                break
                

            
#Your server code goes here
server_address = "127.0.0.1"
number_of_players = 2


players = []
answers_so_far = 0
ready_to_start = Event()
wait_for_answer = Event()
current_question = None
scores = {}
number_of_questions = len(quiz_questions)
print("Number of Questions is, ",number_of_questions)


# Open the quiz server and bind it to a port - creating a socket
# This works similarly to the sockets you used before,
# but you have to give it both an address pair (IP and port) and a handler
# "QuizGame" for the server.
quiz_server = ThreadedTCPServer((server_address, 2065), QuizGame)
print("Server started")
quiz_server.serve_forever()

print("***************************\nEnd\n*********************")
