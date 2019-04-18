import os
from math import *
from PIL import Image
from shutil import copyfile

supported_img_extensions = ["png", "jpg"]

def sizing_function(x):
    val = 0.6
    var_triplets= [
        [0.8, 1.77777, 0.09],
        [0.2, 0.625, 0.07,],
        [0.2, 0.5622, 0.07],
        [0.1, 0.5634, 0.07],
        [0.4, 0.75, 0.07],
        [0.8, 1.5, 0.12]
    ]

    for triplet in var_triplets:
        val += triplet[0]*pow(e, -pow(x-triplet[1], 2.0)/(2*pow(triplet[2], 2.0)))

    return val

class Page(object):
    def __init__(self, sections, filename, title):
        self.sections = sections
        self.filename = filename
        self.title = title

    def render(self):
        html_prefix = "<!DOCTYPE html>\n<html>\n<head>\n<link rel='shortcut icon' href='images/favicon.ico'>\n<link type='text/css' rel='stylesheet' href='main.css' media='screen'>\n<meta charset='utf-8'>\n<meta name='viewport' content='width=device-width, initial-scale=0.75'>\n<title>"+self.title+"</title>\n</head>\n<body>\n"
        html_suffix = "</body>\n</html>\n"

        separator_row = Row("")

        rendered_page = html_prefix
        for i in range(len(self.sections)):
            section = self.sections[i]
            rendered_page += section.render()

            if i < len(self.sections)-1:
                rendered_page += separator_row.render()

        rendered_page += html_suffix

        return rendered_page

    def write(self):
        # creates necessary directories
        if not os.path.exists("site"):
            os.makedirs("site")
        if not os.path.exists("site/fonts"):
            os.makedirs("site/fonts")
        if not os.path.exists("site/files"):
            os.makedirs("site/files")
        if not os.path.exists("site/images"):
            os.makedirs("site/images")

        f = open("site/"+self.filename, "w")
        f.write(self.render())
        f.close()

class NavBar(object):
    def __init__(self, links={}):
        self.links = links

    def render(self):
        prefix = "<div class='row' id='halfrow'><!-- main navigation bar -->\n"
        suffix = "</div>\n"

        rendered_bar = prefix

        for social_name in self.links.keys():
            link_address = self.links[social_name]["address"]
            link_color = self.links[social_name]["color"]

            if link_address != None and link_address != "":
                if link_address[0] == "#":
                    rendered_bar += "<a href='"+link_address+"'><div class='link'>\n"
                else:
                    rendered_bar += "<a href='"+link_address+"' target='_blank'><div class='link'>\n"

            if os.path.isfile("images/"+social_name+"_icon.png"):
                rendered_bar += "<div class='column' style='background-color: "+link_color+"'><div class='vertical-center'><div class='icon'><img src='images/"+social_name+"_icon.png' width='100%'></div></div></div>\n"
            else:
                rendered_bar += "<div class='column' style='background-color: "+link_color+"'><div class='vertical-center'><div class='icon'><img src='images/sc_"+social_name+".png' width='100%'></div></div></div>\n"

            if link_address != None and link_address != "":
                rendered_bar += "</div></a>\n"

        rendered_bar += suffix

        return rendered_bar

class Section(object):
    def __init__(self, name, subtitle, filename, primary_color, secondary_color, row_info=[]):
        self.name = name
        self.subtitle = subtitle
        self.filename = filename
        self.primary_color = primary_color
        self.secondary_color = secondary_color

        # constructs row objects for section
        self.rows = [
            Row("header", self.primary_color, {
                "name": name,
                "subtitle": subtitle,
                "icon_path": "images/"+str(filename)+"_icon.png",
                "filename": filename
            })
        ]
        if name == "" or filename == "":
            self.rows = []
        for i in range(len(row_info)):
            row_type = row_info[i]["type"]
            metadata = row_info[i]
            metadata["filename"] = filename

            color = self.primary_color
            if row_type == "title":
                color = self.secondary_color

            # adds title row is name is provided
            if metadata["name"] != None and metadata["name"] != "":
                self.rows.append(
                    Row("title", self.secondary_color, metadata)
                )

            self.rows.append( Row(row_type, color, metadata) )

    def render(self):
        rendered_section = ""
        for row in self.rows:
            rendered_section += row.render()
        return rendered_section

class Row(object):
    def __init__(self, row_type, color="#ffffff", metadata=None):
        self.type = row_type
        self.metadata = metadata
        self.color = color

    def ordered_filelist(self, input_list):
        return sorted(input_list)

    def height_for_image(self, filepath, multiplier):
        im = Image.open(filepath)
        height_ratio = sizing_function(im.size[1]/im.size[0])
        render_height = max(min(375, 300*height_ratio*multiplier), 120)

        return render_height

    def render(self):
        if self.type == "header":
            return "<a name='"+self.metadata["filename"]+"'><div class='row' style='background-color: "+self.color+"; text-align: left'><!-- content row -->\n<div class='rowicon'><img src='"+self.metadata["icon_path"]+"' height='100%'></div>\n<div class='rowheader'>"+self.metadata["name"]+"</div>\n<div class='rowsubtitle'>"+self.metadata["subtitle"]+"</div>\n</div></a>\n"
        elif self.type == "title":
            return "<div class='row' id='thinrow' style='background-color: "+self.color+"'><div class='vertical-center'>\n"+self.metadata["name"]+"\n</div></div>\n"
        elif self.type == "logo":
            prefix = "<div class='row' id='logorow' style='background-color: "+self.color+"'><!-- logo -->\n<div class='vertical-center'>"
            suffix = "</div>\n</div>\n"

            rendered_row = prefix

            if "filename" in self.metadata and self.metadata["filename"] != "":
                height = 380
                if "height" in self.metadata and self.metadata["height"] != "":
                    height = int(self.metadata["height"])
                rendered_row += "<img src='images/"+self.metadata["filename"]+"' height='"+str(height)+"'>"
            elif "text" in self.metadata and self.metadata["text"] != "":
                text_color = '#000000'
                if "text-color" in self.metadata and self.metadata["text-color"] != "":
                    text_color = self.metadata["text-color"]
                rendered_row += "<font color='"+text_color+"'>"+self.metadata["text"]+"</font>"
            elif "snippet" in self.metadata and self.metadata["snippet"] != "":
                rendered_row += self.metadata["snippet"]

            rendered_row += suffix

            return rendered_row
        elif self.type == "footer":
            footer_content = ""
            text_color = '#969696'

            if "snippet" in self.metadata and self.metadata["snippet"] != "":
                footer_content = self.metadata["snippet"]
            elif "text" in self.metadata and self.metadata["text"] != "":
                if "text-color" in self.metadata and self.metadata["text-color"] != "":
                    text_color = self.metadata["text-color"]
                rendered_row += "<font color='"+text_color+"'>"+self.metadata["text"]+"</font>"

            # default footer content
            if footer_content == "":
                footer_content = "<font color='"+text_color+"'>Website created with <a href='https://github.com/magj3k/swiftpage' target='_blank' style='color: "+text_color+"; display: auto; width: auto; height: auto;'>SwiftPage</a> (available on GitHub).<br>SwiftPage is an open-source project created and maintained by <a href='http://www.magmhj.com' target='_blank' style='color: "+text_color+"; display: auto; width: auto; height: auto;'>MagMHJ, LLC</a>.</font>"

            return "<div class='row' id='footer' style='background-color: "+self.color+"'><!-- footer -->\n<div class='vertical-center'>"+footer_content+"</div>\n</div>\n"
        elif self.type == "img_gallery":
            prefix = "<div class='row' id='bigbigrow' style='background-color: "+self.color+"'><div class='slideshow'>\n<table border='0' height='420'><tr>\n"
            suffix = "</tr></table>\n</div></div>\n"

            rendered_row = prefix

            # gets list of all images from image directory
            filepath_prefix = "images/"+str(self.metadata["filename"])+"/"
            if "extension" in self.metadata and self.metadata["extension"] != None:
                filepath_prefix = "images/"+str(self.metadata["filename"])+"/"+self.metadata["extension"]+"/"

            filelist = self.ordered_filelist(os.listdir(filepath_prefix)[:])
            j = 0
            for i in range(len(filelist)):
                filename = filelist[i]

                if filename[-3:].lower() in supported_img_extensions:
                    filepath = filepath_prefix+filename
                    multiplier = 1.0
                    if self.metadata["multipliers"] != None:
                        if j < len(self.metadata["multipliers"]): multiplier = self.metadata["multipliers"][j]
                    render_height = self.height_for_image(filepath, multiplier)

                    rendered_row += "<td>&nbsp;</td>\n"
                    rendered_row += "<td valign='middle'>\n<img src='"+filepath+"' height='"+str(int(render_height))+"' style='border-radius: 0px'>\n</td>\n"
                    j += 1

            rendered_row += "<td>&nbsp;</td>\n"
            rendered_row += suffix

            return rendered_row
        elif self.type == "links":
            prefix = "<div class='row' id='halfrow' style='background-color: "+self.color+"; color: white'>\n"
            suffix = "</div>\n"

            rendered_row = prefix

            if self.metadata["links"] != None:
                links = self.metadata["links"]
                for link in links:
                    if link["address"] != None and link["address"] != "":
                        if link["address"][0] == "#":
                            rendered_row += "<a href='"+link["address"]+"'><div class='link'>"
                        else:
                            rendered_row += "<a href='"+link["address"]+"' target='_blank'><div class='link'>"
                    rendered_row += "<div class='column'>"
                    rendered_row += "<div class='vertical-center'><div id='borderedlabel'>"+link["name"]+"</div></div>"
                    rendered_row += "</div>"
                    if link["address"] != None and link["address"] != "": rendered_row += "</div></a>"
                    rendered_row += "\n"

            rendered_row += suffix

            return rendered_row
        elif self.type == "video-youtube":
            return "<div class='row' id='bigrow' style='background-color: "+self.color+"'><div class='vertical-center'>\n<iframe width='516' height='290' src='"+self.metadata["address"]+"' frameborder='0' allow='accelerometer; encrypted-media; gyroscope; picture-in-picture' allowfullscreen></iframe>\n</div></div>"
        elif self.type == "video-vimeo":
            return "<div class='row' id='bigrow' style='background-color: "+self.color+"'><div class='vertical-center'>\n<iframe src='"+self.metadata["address"]+"' width='516' height='290' frameborder='0' allow='fullscreen' allowfullscreen></iframe>\n</div></div>"
        elif self.type == "files":
            prefix = "<div class='row' id='bigrow' style='background-color: "+self.color+"'><div class='slideshow' style='font-size: 23px'>\n<table border='0' height='330'><tr>\n"
            suffix = "</tr></table>\n</div></div>\n"

            rendered_row = prefix

            if self.metadata["links"] != None:
                links = self.metadata["links"]
                for link in links:
                    name = link["name"]
                    link_address = "files/"+str(self.metadata["filename"])+"/"+link["filename"]
                    rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"
                    rendered_row += "<td valign='middle' align='center'>\n<a href='"+link_address+"' target='_blank'><div class='link'>\n<div style='width: 150px; height: 150px; border-radius: 50%; border-width: 5px; border-color: white; border-style: solid;'><table width='100%'><tr><td valign='middle' align='center' height='150'><img src='images/document_icon.png' height='85' style='border-radius: 0px'></td></tr></table></div>\n</div></a>\n<br><div id='borderedlabel'>"+name+"</div>\n</td>\n"
                rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"

            rendered_row += suffix

            return rendered_row
        elif self.type == "people":
            prefix = "<div class='row' id='bigrow' style='background-color: "+self.color+"'><div class='slideshow' style='font-size: 22px'>\n<table border='0' height='330'><tr>\n"
            suffix = "</tr></table>\n</div></div>\n"

            rendered_row = prefix

            if self.metadata["people"] != None:
                people = self.metadata["people"]
                for person in people:
                    name = person["name"]
                    filename = "people/"+person["filename"]

                    # checks that filename exists, else replaces with unknown symbol
                    file_exists = os.path.isfile("images/"+filename)
                    if not file_exists:
                        filename = person["filename"]
                        file_exists = os.path.isfile("images/"+filename)

                        if not file_exists: 
                            filename = "people/unknown.png"

                    rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"
                    rendered_row += "<td valign='middle' align='center'>\n<div style='width: 150px; height: 150px; border-radius: 50%; border-width: 5px; border-color: white; border-style: solid; overflow: hidden;'><img src='images/"+filename+"' width='150' height='150' style='border-radius: 0px'></div>\n<br><div id='borderedlabel'>"+name+"</div>\n</td>\n"
                rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"

            rendered_row += suffix

            return rendered_row
        elif self.type == "text":
            return "<div class='row' id='bigrow' style='background-color: "+self.color+"; text-align: center; overflow-y: scroll; font-size: 29px; -webkit-overflow-scrolling: touch;'><table width='100%'><tr><td width='7%'></td><td valign='top'>\n<br>"+self.metadata["text"]+"\n"+"<br><br></td><td width='7%'></td></tr></table></div>\n"
        elif self.type == "custom":
            row_type = "bigrow"
            if self.metadata["size"] != None and (self.metadata["size"] == "big" or self.metadata["size"] == "large"):
                row_type = "bigbigrow"
            return "<div class='row' id='"+row_type+"' style='background-color: "+self.color+"'><div class='vertical-center'>\n"+self.metadata["snippet"]+"\n"+"</div></div>\n"
        return "<div class='row' id='separator'></div>\n"

