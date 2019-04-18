import os
import time

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

print("SwiftPage server running, your site will now be automatically regenerated when changes are made")

while True:
    main_loop()
    time.sleep(0.25)