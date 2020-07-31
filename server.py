import os
import time
import webbrowser
import threading
from addons.addons_server import *
from page import *

import http.server
import socketserver

last_modified_time = 0

dev_page_prefix = '''
<html>

<title>SwiftPage Development Server</title>

<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script>
    var lastRefreshToken = "none";

    function loadCommands(filename) {
        $.get(filename, function(data, textStatus) {
            if (textStatus == 'success') {
                var lines = data.match(/^.*(('''
dev_page_middle = '\\'+'r'+'\\'+'n'+'|'+'\\'+'n'+'|'+'\\'+'r'
dev_page_suffix = ''')|$)/gm)
                for (var i = 0; i < lines.length; i++) {
                    //console.log(lines[i]); // TODO: remove
                    if (lines[i] !== '' && lines[i] !== ' ') {
                        if (lastRefreshToken !== lines[i]) {
                            lastRefreshToken = lines[i];

                            var iframe = document.getElementsByName('content_window')[0];
                            iframe.src = iframe.src
                            iframe.contentWindow.location.reload(true);
                            //iframe.location.reload(true);
                        }
                    }
                }
            } else {
                console.log('Commands file does not exist.');
            }
        });
    }

    function checkForCommands() {
        var filename = '.swiftpage_commands';
        loadCommands(filename);
    }

    setInterval(checkForCommands, 30);
</script>

<body style='padding: 0px; margin: 0px;'>
<iframe src='./site/index.html' name='content_window' style='width: 100%; height: 100%; outline: none;' frameborder='0'></iframe>
</body>

</html>
'''
dev_page = dev_page_prefix+dev_page_middle+dev_page_suffix
addons_server = AddonsServer(page)

def main_loop():
    while True:
        global last_modified_time

        # checks to see if files have been updated
        modified_time = os.path.getmtime("page.py")

        # if necessary, saves new copy of swiftpage
        if last_modified_time != modified_time:
            last_modified_time = modified_time

            os.system('python create_page.py')
            print("Page modified, new SwiftPage generated: "+str(last_modified_time))

            # refreshes web browser and writes other commands
            commands = open(".swiftpage_commands","w") 
            commands.write(str(last_modified_time))
            commands.close() 
        else:
            # empties commands
            commands = open(".swiftpage_commands","w")
            commands.write("")
            commands.close() 

        time.sleep(0.6)

def addons_loop():
    global addons_server
    addons_server.on_update()

# removes existing commands file
os.remove(".swiftpage_commands")

# creates dev_server.html
dev_server_page = open("dev_server.html","w") 
dev_server_page.write(dev_page)
dev_server_page.close() 

# defines custom HTTP handler
class customHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

# starts web server
port = 8080
handler = customHandler # http.server.SimpleHTTPRequestHandler
t1 = threading.Thread(target=main_loop)
t2 = threading.Thread(target=addons_loop)
with socketserver.TCPServer(("", port), handler) as httpd:

    # opens web browser of local server
    webbrowser.open('http://127.0.0.1:8080/dev_server.html', new=0, autoraise=True)
    print("SwiftPage server running, your site will now be automatically regenerated when changes are made")
 
    # starts loops
    t1.start()
    t2.start()

    # serves html server
    httpd.serve_forever()

