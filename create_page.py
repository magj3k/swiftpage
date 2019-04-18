from elements import *

output_file = "index.html"
page_title = "Mark Zuckerberg"

page = Page([
    Row("logo", "#ffffff", {
        "text": "Test4"
    }),
    NavBar({
        "soundcloud": {"address": "https://soundcloud.com/mitanimationgroup", "color": "#FE4800"},
        "facebook": {"address": "http://www.facebook.com/mitanimationgroup", "color": "#3B579D"},
        "email": {"address": "mailto: mitag_exec@mit.edu", "color": "#CEB182"}
    }),
    Row("footer", "#ffffff", {
        "text": ""
    }),
], output_file, page_title)

page.write()