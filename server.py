import os
import time
import webbrowser
import threading
from addons import *
from page import *

import http.server
import socketserver

last_modified_time = 0

dev_page_prefix = '''
<html>

<title>SwiftPage Development Server</title>

<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script>
    function loadCommands(filename) {
        $.get(filename, function(data, textStatus) {
            if (textStatus == 'success') {
                var lines = data.match(/^.*(('''
dev_page_middle = '\\'+'r'+'\\'+'n'+'|'+'\\'+'n'+'|'+'\\'+'r'
dev_page_suffix = ''')|$)/gm)
                for (var i = 0; i < lines.length; i++) {
                    if (lines[i] === 'refresh') {
                        // location.reload(false);
                        var iframe = document.getElementsByName('content_window')[0];
                        iframe.contentWindow.location.reload(true);
                    } else if (lines[i] === 'scroll_to_bottom') {
                        console.log('scrolling to bottom');
                        var iframe = document.getElementsByName('content_window')[0];
                        iframe.contentWindow.scrollTo(0, 999999);
                    } else if (lines[i] === 'scroll_to_top') {
                        console.log('scrolling to top');
                        var iframe = document.getElementsByName('content_window')[0];
                        iframe.contentWindow.scrollTo(0, 0);
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

    setInterval(checkForCommands, 250);
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
        global addons_server

        # checks to see if files have been updated
        modified_time = os.path.getmtime("page.py")

        # checks if addons have generated any server commands
        addons_server.on_update()
        addon_commands = addons_server.get_server_commands()

        # if necessary, saves new copy of swiftpage
        if last_modified_time != modified_time or len(addon_commands) >= 1:
            command = ""
            if last_modified_time != modified_time:
                last_modified_time = modified_time
                command = "refresh"

            for cmd in addon_commands:
                command += "\n" + cmd

            os.system('python create_page.py')
            print("Page modified, new SwiftPage generated: "+str(last_modified_time))

            # refreshes web browser and writes other commands
            commands = open(".swiftpage_commands","w") 
            commands.write(command)
            commands.close() 
        else:
            # empties commands
            commands = open(".swiftpage_commands","w") 
            commands.write("")
            commands.close() 

        time.sleep(0.25)

# creates dev_server.html
dev_server_page = open("dev_server.html","w") 
dev_server_page.write(dev_page)
dev_server_page.close() 

# defines custon HTTP handler
class customHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

# starts web server
port = 8080
handler = customHandler # http.server.SimpleHTTPRequestHandler
t1 = threading.Thread(target=main_loop)
with socketserver.TCPServer(("", port), handler) as httpd:

    # opens web browser of local server
    webbrowser.open('http://127.0.0.1:8080/dev_server.html', new=0, autoraise=True)
    print("SwiftPage server running, your site will now be automatically regenerated when changes are made")
 
    # starts loops
    t1.start()

    # serves html server
    httpd.serve_forever()

