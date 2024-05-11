# Architecural Structure
As this is a very complex undertaking, some structures need to be considered to properly interpret and design this incoherent mess that is Facebook

--------------
## Usage Goals
- should be as frictionless as possible (require as little pip modules as possible)
--------------
## Server Side
### Toolings
- Hosted using a very lightweight server (http.server should be fine, no need to go overkill with django/flask)

### Purpose
- host the webserver on localhost:6969
- grab the directory of the file from client
- interpret wtf is going on sa json
- return parsed shit to client

------------
## Client Side
### Toolings
- Using React for the rendering shits

### Purpose
- beautifully display shits that server sends to you
- send the path of the folder to server
