{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 Quiz program part of Future Learn / Raspberry Pi Foundation course on Python Sockets\
\
Uses two programs a server and a client\
\
Quiz_server is the server.\
Quiz_client is the client\
\
In this demo version the server is running on local host (127.0.0.1)\
This can be changed by changing server_address\
\
The server expects at least two clients to be running (held in variable number_of players) before starting the Quiz\
\
Questions are held in quiz_questions (six questions in the demo)\
 After all the questions have been asked the server will declare a winning team unless no-one scored any points.\
\
In the case of a draw, a tie breaker Question will be asked with the first correct answer being the winner.\
}