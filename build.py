import os
import json
import subprocess
from pathlib import Path

# Metadata
overallVersion = '1.0.0'
clientVersion = '1.0.0'
serverVersion = '1.0.0'

# building clientside
cwd = os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd + '\\client')
buildCall = subprocess.call(["npm", "run", "build"], shell=True) 
if buildCall != 0: # something failed during build
    print('ERROR: Something went wrong with npm run build, please try to build it manually.')
    quit()
os.chdir('../client/build')
npmOutput = {}
for root, subdir, files in os.walk('./'):
    root = Path(root)
    for file in files:
        file = root / Path(file)
        with file.open() as f:
            npmOutput['/'+ file.as_posix()] = f.read()

# parsing serverside

with open(cwd + '\\server\\main.py') as f:

    serverOutput = ''
    isReading = False
    for i in f:
        if i.find('#!!!build-start-parse\n') != -1:
            isReading = True
        elif i.find('#!!!build-end-parse\n') != -1:
            isReading = False
        if isReading:
            serverOutput += i

# full structure of built main.py
mainOutput = f'''#!/usr/bin/python3

# FacebookJSONInterpreter - v{overallVersion}
# Made by: bonaktan
# Source Code on: https://github.com/bonaktan/FacebookJSONInterpreter


# Client Side - v{clientVersion}
def clientSide():
    from bottle import Bottle, run, response

    files = {(json.dumps(npmOutput, sort_keys=True, indent=4))}

    clientSide = Bottle()
    @clientSide.route('/', method='GET')
    def index(): return files['/index.html']
    @clientSide.route('/<filename:path>', method='GET')
    def fileRequest(filename):
        fileExt = filename.split('.')[-1]
        match fileExt:
            case 'css': response.content_type='text/css'
            case 'js': response.content_type='text/javascript'
        return files['/' + filename]
    run(clientSide, host='localhost', port=3000)

# Server Side - v{serverVersion}
{serverOutput}


if __name__ == '__main__':
    import multiprocessing 
    api = multiprocessing.Process(target=apiSide, args=()) 
    client = multiprocessing.Process(target=clientSide, args=()) 
    api.start()
    client.start()
    api.join()
    client.join()
'''

with open('../../main.py', 'w') as f:
    f.write(mainOutput)

print(f'FacebookJSONInterpreter v{overallVersion} fully built.\nBuilt with: Server v{serverVersion} and Client v{clientVersion}\nRun with "python main.py" and go to http://localhost:3000')