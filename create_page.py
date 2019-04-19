from elements import *

output_file = "index.html"
page_title = "SwiftPage Test Website"

page = Page([
    Row("logo", {
        "text": "Rocky Road",
    }),
    NavBar({
        "soundcloud": {"address": "#"},
        "facebook": {"address": "#"},
        "linkedin": {"address": "#"}
    }),
    Section("Rocky Road 2", "An app project I made once", "rockyroad2", [
        {
            "name": "Test Links:",
            "type": "links",
            "links": [
                { "name": "Link A", "address": "top" },
                { "name": "Link B", "address": "#top" }
            ]
        },
        {
            "name": "Images:",
            "type": "img_gallery",
        },
        {
            "name": "Downloads:",
            "type": "files",
            "links": [
                {"name": "Beyond The Sea", "filename": "BeyondTheSea.tps"},
                {"name": "Invalid Download"}
            ]
        },
        {
            "name": "Team:",
            "type": "people",
            "people": [
                {"name": "Magnus Johnson", "filename": "magnus.png"},
                {"name": "Rando Calrissian"}
            ]
        },
        {
            "name": "About Us:",
            "type": "text",
            "text": "Bacon ipsum dolor amet frankfurter boudin jowl ribeye hamburger ball tip strip steak ground round tail doner ham hock. Pig chicken sausage cow. Strip steak meatball beef ribs pork belly kielbasa picanha cow leberkas pancetta bresaola ball tip pastrami meatloaf. Capicola ham alcatra pastrami kevin tongue turkey leberkas beef ribs ham hock spare ribs flank pork belly kielbasa. Short loin meatloaf buffalo tenderloin, drumstick beef prosciutto jerky spare ribs.<br><br>Ball tip frankfurter beef spare ribs, pastrami meatloaf cupim. Tenderloin meatball sirloin, filet mignon ham sausage pancetta tongue tail ball tip landjaeger pork chop. Cupim pancetta frankfurter pork loin, buffalo jowl turducken beef ribs burgdoggen cow boudin beef spare ribs venison corned beef. Turkey t-bone spare ribs biltong turducken bacon cow chuck boudin salami ham hock rump tri-tip sirloin meatloaf. Tri-tip beef ribs tail, bacon ribeye ball tip pig short loin bresaola t-bone porchetta sirloin kevin pork belly. Jerky pancetta ribeye pork loin, pig corned beef ground round porchetta strip steak salami meatball."
        }
    ]),
    Section("Chromavera 2", "An app project I made once", "chromavera2"),
    Section("Rocky Road", "An app project I made once", "rockyroad"),
    Row("footer", {}),
], output_file, page_title)

page.check()
page.write()