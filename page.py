from elements import *

page_title = "SwiftPage Demo"

# modify the 'page' object below to design your own SwiftPage
page = Page([
    Row("logo", {
        "text": "My Projects SwiftPage",
        "rounded": "true",
        "background-colors": ["#f06d55", "#1a32d5"],
    }),
    NavBar({
        "facebook": {"address": "#"},
        "soundcloud": {"address": "#"},
        "linkedin": {"address": "#", "color": "#0a4767"},
        "archipelago": {"address": "#archipelago", "color": "#684bb7"}
    }),
    Section("Archipelago", "An app project I made once", "archipelago", [
        {
            "name": "Test Links:",
            "type": "links",
            "links": [
                { "name": "External Link", "address": "http://www.magmhj.com/" },
                { "name": "Internal Link", "address": "#archipelago" }
            ]
        },
        {
            "name": "Images:",
            "type": "img_gallery",
        },
        {
            "name": "Trailer:",
            "type": "video-youtube",
            "address": "https://www.youtube.com/embed/NKnghW8DiI8"
        },
        {
            "name": "Downloads:",
            "type": "files",
            "links": [
                {"name": "Test Valid Download", "filename": "LaVieEnRose.tps"},
                {"name": "Test Invalid Download"}
            ]
        }
    ]),
    Row("footer", {}),
], "index.html", page_title)