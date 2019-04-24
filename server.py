import os
import time
import webbrowser
import threading

import http.server
import socketserver

last_modified_time = 0

def main_loop():
    global last_modified_time

    # checks to see if files have been updated
    modified_time = os.path.getmtime("create_page.py")

    # if necessary, saves new copy of swiftpage
    if last_modified_time != modified_time:
        last_modified_time = modified_time

        os.system('python create_page.py')
        print("Page modified, new SwiftPage generated: "+str(last_modified_time))

        # refreshes web browser and writes other commands
        commands = open(".swiftpage_commands","w") 
        commands.write("refresh")
        commands.close() 
    else:
        # empties commands
        commands = open(".swiftpage_commands","w") 
        commands.write("")
        commands.close() 

    time.sleep(0.25)
    main_loop()

# starts web server
port = 8080
handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", port), handler) as httpd:

    # opens web browser of local server
    filename = "dev.html" # TODO: generate dev.html and point to saved file from create_page.py
    webbrowser.open('http://127.0.0.1:8080/'+filename, new=0, autoraise=True)
    print("SwiftPage server running, your site will now be automatically regenerated when changes are made")
 
    # starts main loop
    t1 = threading.Thread(target=main_loop)
    t1.start()

    # serves html server
    httpd.serve_forever()

