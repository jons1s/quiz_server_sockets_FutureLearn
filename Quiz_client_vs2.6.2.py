import socket
# Import the functions from the networking tools module
from fl_networking_tools import get_binary, send_binary

'''
Responses
LIST YOUR RESPONSE CODES HERE
1 - Team Name
2 - Question
3 - Answer
4 - Question available
5 - Join request accepted
6 - Status
8 - final Score
9 - tiebreak
10 - close
'''
#Ask for team name and ip address of the Quiz server
#for examople local host is 127.0.0.1
team_name = input("What is your team name?\n>")
quiz_server_ip_address = input("What is the IP address of the Quiz Server?\n>")
print("Quiz server IP address is "+ quiz_server_ip_address + "\n")

# A flag used to control the quiz loop.
playing = True

quiz_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

quiz_server.connect((quiz_server_ip_address, 2065))

#print("Welcome " + team_ name + " Good Luck\n")
send_binary(quiz_server,["JOIN",team_name])
# Sending a command to the server.
#send_binary(quiz_server, ["QUES", ""])

while playing:
    # The get_binary function returns a list of messages - loop over them
    for response in get_binary(quiz_server):
        # response is the command/response tuple - response[0] is the code
        # response[1] is the message from the server

                    
        if response[0] == 1:# Initial acknowledgement from Quiz server and welcome to game
            print("Welcome " + team_name + " Good Luck\n")
            #Ask quiz server for status regarding next Question
            send_binary(quiz_server,["STAT",""])
            
        elif response[0] == 2: # The question response from the Quiz server
            # Display it to the user & wait for user to input answer
            print("Question.........\n" + response[1])
            team_answer =input(">")
            send_binary(quiz_server,["ANSR",team_answer])
            
        elif response[0] == 3:# The Answer response from the Quiz server
            #print the answer and whether Quiz server thinks user got it correct
            print("\nAnswer is......... "+ response[1])
            #Ask quiz server for status regarding next Question
            send_binary(quiz_server,["STAT",""])

            
        elif response[0] == 4:# Quiz server saying Question available
            # client then prints server message that question is available
            # and then asks for the question
            print(response[1])
            send_binary(quiz_server, ["QUES",""])

        elif response[0] == 8: #server sending final score
            print("***************************\nTHAT'S ALL FOLKS\nTHANKS FOR PLAYING\n***************************")
            print(response[1])

        elif response[0] == 9:#Tie break required
            print(response[1])
            print("***************************\nTIE BREAKER\n***************************")
            print("First correct answer wins...")

        elif response[0] == 10:#Server closing
            quiz_server.close()
            print("socket closed")
    
            
        
            
            
        
