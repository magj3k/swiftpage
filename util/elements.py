import os
import colorsys as cs
from math import *
from PIL import Image
from shutil import copyfile
from util.manip import *

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

def pick_representative_color(image_address, size="large"):
    im = get_img_and_resize(image_address, size).convert('HSV')

    # tracks median color along border of hsv image
    width = im.size[0]
    height = im.size[1]
    border_colors = []
    strip_width = int(max(width*0.05, 2))
    for x in range(width):
        for y in range(height):
            if (x > strip_width*1.5 and x <= strip_width*2.5) or (x < width-1-(strip_width*1.5) and x >= width-1-(strip_width*2.5)):
                if (y > strip_width*1.5 and y <= strip_width*2.5) or (y < height-1-(strip_width*1.5) and y >= height-1-(strip_width*2.5)):
                    h, s, v = im.getpixel( (x, y) )
                    border_colors.append( [h, s, v] )

    border_colors.sort()
    mid_ind = len(border_colors)//2
    median_color = [0, 0, 0]
    median_count = 0
    for i in range(-min(mid_ind, 5), min(mid_ind, 5+1)):
        median_color[0] += border_colors[mid_ind+i][0]
        median_color[1] += border_colors[mid_ind+i][1]
        median_color[2] += border_colors[mid_ind+i][2]
        median_count += 1
    avg_median_color = [median_color[0]/median_count, median_color[1]/median_count, median_color[2]/median_count]

    # desaturates and lowers brightness
    avg_median_color[1] = max(0.0, avg_median_color[1]*0.9)
    avg_median_color[2] = max(0.0, avg_median_color[2]*0.65)

    # converts color back to rgb
    r, g, b = cs.hsv_to_rgb(avg_median_color[0]/255.0, avg_median_color[1]/255.0, avg_median_color[2]/255.0)
    hex_string = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

    return hex_string

def dim_hex(hex_color):
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    # converts rgb to hsv & dims color
    h, s, v = cs.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    hsv = [h, max(s*0.9, 0.0), max(v*0.7, 0.0)]

    # converts hsv to rgb hex
    r, g, b = cs.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    hex_string = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

    return hex_string

class Page(object):
    def __init__(self, sections, filename, title, separator_color="#bbbbbb"):
        self.sections = sections
        self.filename = filename
        self.title = title
        self.separator_color = separator_color

    def check(self):
        print("\nChecking page to issue warnings if necessary...")

        # prints warnings if page design fails certain standards
        issues = []
        if self.filename == "":
            issues.append("No filename has been specified.")
        elif self.filename[-4:] != "html":
            issues.append("Specified filename should have a '.html' file extension suffix.")
        if self.title == "":
            issues.append("No webpage title has been specified.")
        if len(self.sections) == 0:
            issues.append("More than one Component needs to be specified.")
        elif len(self.sections) == 1:
            issues.append("SwiftPages should ideally have at least one Component.")
        if len(self.sections) >= 2:
            if not isinstance(self.sections[0], Row) or (isinstance(self.sections[0], Row) and self.sections[0].type != "logo"):
                issues.append("The page's first Component should be a 'logo' Row.")
            if not isinstance(self.sections[-1], Row) or (isinstance(self.sections[-1], Row) and self.sections[-1].type != "footer"):
                issues.append("The page's last Component should be a 'footer' Row.")

            navbar_exists = False
            filesrow_exists = False
            peoplerow_exists = False
            empty_link_exists = False
            for section in self.sections:
                if isinstance(section, NavBar):
                    navbar_exists = True
                elif isinstance(section, Section):
                    for row in section.rows:
                        if row.type == "files":
                            filesrow_exists = True
                        elif row.type == "people":
                            peoplerow_exists = True
                        elif row.type == "links":
                            if "links" in row.metadata:
                                links = row.metadata["links"]
                                for link in links:
                                    if "address" not in link or link["address"] == "":
                                        empty_link_exists = True

            if navbar_exists == False:
                issues.append("Consider adding a 'NavBar' to make navigation easier for viewers.")
            if empty_link_exists == True:
                issues.append("Make sure all links have a specified 'address'.  Empty links may cause rendering abnormalities.")
            if filesrow_exists == True and not os.path.isfile("site/images/document_icon.png"):
                issues.append("To use 'files' Rows, you need to have a square image named 'document_icon.png' in 'site/images'.")
            if peoplerow_exists == True and not os.path.isfile("site/images/unknown.png"):
                issues.append("To use 'people' Rows, you need to have a square image named 'unknown.png' in 'site/images'.")

        if len(issues) == 0:
            print("No issues found, SwiftPage design is complete")
        else:
            for issue in issues:
                print("WARNING: "+issue)

    def render(self):
        html_prefix = "<!DOCTYPE html>\n<html>\n<head>\n<link rel='shortcut icon' href='images/favicon.ico'>\n<link type='text/css' rel='stylesheet' href='main.css' media='screen'>\n<meta charset='utf-8'>\n<meta name='viewport' content='width=device-width'>\n<title>"+self.title+"</title>\n</head>\n<body>\n"
        html_suffix = "</body>\n</html>\n"

        separator_row = Row("", { "color": self.separator_color })

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

    def calculate_link_color(self, image_address):
        im = get_img_and_resize(image_address, 'small').convert('HSV')

        # calculates average color along border of hsv image
        width = im.size[0]
        height = im.size[1]
        color_sum = [0.0, 0.0, 0.0]
        pixel_count = 0
        for x in range(width):
            for y in range(height):
                if x <= 1 or x >= width-2:
                    if y <= 1 or y >= height-2:
                        h, s, v = im.getpixel( (x, y) )
                        color_sum[0] += h
                        color_sum[1] += s
                        color_sum[2] += v
                        pixel_count += 1
        color_avg = [color_sum[0]/pixel_count, color_sum[1]/pixel_count, color_sum[2]/pixel_count]

        # saturates and raises brightness
        color_avg[1] = min(255.0, color_avg[1]*1.1)
        color_avg[2] = min(255.0, color_avg[2]*1.5)

        # converts color back to rgb
        r, g, b = cs.hsv_to_rgb(color_avg[0]/255.0, color_avg[1]/255.0, color_avg[2]/255.0)
        hex_string = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

        return hex_string

    def render(self):
        prefix = "<div class='row' id='halfrow'><!-- main navigation bar -->\n"
        suffix = "</div>\n"

        rendered_bar = prefix

        for link_name in self.links.keys():
            link_address = self.links[link_name]["address"]
            link_color = ""
            if "color" in self.links[link_name]:
                link_color = self.links[link_name]["color"]

            if link_address != None and link_address != "":
                if link_address[0] == "#":
                    rendered_bar += "<a href='"+link_address+"'><div class='link'>\n"
                else:
                    rendered_bar += "<a href='"+link_address+"' target='_blank'><div class='link'>\n"

            if os.path.isfile("site/images/nav_"+link_name+".png"):
                if link_color == "":
                    link_color = self.calculate_link_color("site/images/nav_"+link_name+".png")
                else:
                    get_img_and_resize("site/images/nav_"+link_name+".png", size='small')
                rendered_bar += "<div class='column' style='background-color: "+link_color+"'><div class='vertical-center'><div class='icon'><img src='images/nav_"+link_name+".png' width='100%'></div></div></div>\n"
            elif os.path.isfile("site/images/"+link_name+"_icon.png"):
                if link_color == "":
                    link_color = self.calculate_link_color("site/images/"+link_name+"_icon.png")
                else:
                    get_img_and_resize("site/images/"+link_name+"_icon.png", size='small')
                rendered_bar += "<div class='column' style='background-color: "+link_color+"'><div class='vertical-center'><div class='icon'><img src='images/"+link_name+"_icon.png' width='100%'></div></div></div>\n"

            if link_address != None and link_address != "":
                rendered_bar += "</div></a>\n"

        rendered_bar += suffix

        return rendered_bar

class Section(object):
    def __init__(self, name, subtitle, filename, row_info=[], primary_color="", secondary_color=""):
        self.name = name
        self.subtitle = subtitle
        self.filename = filename
        self.primary_color = primary_color
        if primary_color == "": self.primary_color = pick_representative_color("site/images/"+str(filename)+"_icon.png", "large")
        self.secondary_color = secondary_color
        if secondary_color == "": self.secondary_color = dim_hex(self.primary_color)

        # constructs row objects for section
        self.rows = [
            Row("header", {
                "name": name,
                "subtitle": subtitle,
                "icon_path": "images/"+str(filename)+"_icon.png",
                "filename": filename,
                "color": self.primary_color
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
            metadata["color"] = color

            # adds title row if name is provided
            if metadata["name"] != None and metadata["name"] != "":
                metadata_copy = metadata.copy()
                metadata_copy["color"] = self.secondary_color
                self.rows.append(
                    Row("title", metadata_copy)
                )

            self.rows.append( Row(row_type, metadata) )

    def render(self):
        rendered_section = ""
        for row in self.rows:
            rendered_section += row.render()
        return rendered_section

class Row(object):
    def __init__(self, row_type, metadata={}):
        self.type = row_type
        self.metadata = metadata
        self.color = "#ffffff"
        if "color" in metadata and metadata["color"] != None:
            self.color = metadata["color"]

    def ordered_filelist(self, input_list):
        return sorted(input_list)

    def height_for_image(self, filepath, multiplier):
        im = Image.open(filepath)
        height_ratio = sizing_function(im.size[1]/im.size[0])
        render_height = max(min(375, 300*height_ratio*multiplier), 120)

        return render_height

    def render(self):
        if self.type == "header":
            div_style = "background-color: "+self.color+"; text-align: left"
            return "<a name='"+self.metadata["filename"]+"'><div class='row' style='"+div_style+"'><!-- content row -->\n<div class='rowicon'><img src='"+self.metadata["icon_path"]+"' height='100%'></div>\n<div class='rowheader'>"+self.metadata["name"]+"</div>\n<div class='rowsubtitle'>"+self.metadata["subtitle"]+"</div>\n</div></a>\n"
        elif self.type == "title":
            return "<div class='row' id='thinrow' style='background-color: "+self.color+"'><div class='vertical-center'>\n"+self.metadata["name"]+"\n</div></div>\n"
        elif self.type == "logo":
            style = "background-color: "+self.color+";"

            # background color
            if "background-colors" in self.metadata:
                colors = self.metadata["background-colors"]
                if len(colors) == 1: # new background color
                    style = "background-color: "+colors[0]+";"
                elif len(colors) > 1: # background gradient
                    style = "background-image: linear-gradient(to right, "+colors[0]+", "+colors[-1]+");"

            if "background-filename" in self.metadata: # background image
                if os.path.isfile("site/images/"+self.metadata["background-filename"]):
                    style = "background-color: "+self.color+"; background-image: url('images/"+self.metadata["background-filename"]+"');"

            prefix = "<div class='row' id='logorow' style='"+style+"'><!-- logo -->\n<div class='vertical-center'>"
            suffix = "</div>\n</div>\n"

            rendered_row = prefix

            if "filename" in self.metadata and self.metadata["filename"] != "" and "text" in self.metadata and self.metadata["text"] != "":
                height = 250
                gap_height = (330-height)//2
                if "height" in self.metadata and self.metadata["height"] != "":
                    height = int(self.metadata["height"])
                text_color = '#000000'
                if "text-color" in self.metadata and self.metadata["text-color"] != "":
                    text_color = self.metadata["text-color"]

                rendered_row += "<div style='position: absolute; left: "+str(gap_height+7)+"px; top: calc(50% - "+str(height//2)+"px);'>"
                rendered_row += "<img src='images/"+self.metadata["filename"]+"' height='"+str(height)+"' width='"+str(height)+"'>"
                rendered_row += "</div><div style='position: absolute; left: "+str(gap_height+306)+"px; height: 60px; top: calc(50% - 36px);'>"
                rendered_row += "<font color='"+text_color+"'><b>"+self.metadata["text"]+"</b></font>"
                rendered_row += "</div>"
            elif "filename" in self.metadata and self.metadata["filename"] != "":
                height = 280
                if "height" in self.metadata and self.metadata["height"] != "":
                    height = int(self.metadata["height"])
                rendered_row += "<img src='images/"+self.metadata["filename"]+"' height='"+str(height)+"'>"
            elif "text" in self.metadata and self.metadata["text"] != "":
                text_color = '#000000'
                if "text-color" in self.metadata and self.metadata["text-color"] != "":
                    text_color = self.metadata["text-color"]

                # rounds logo text if specified
                if "rounded" in self.metadata and self.metadata["rounded"] == "true":
                    rounded_color = "#ffffff"
                    rounded_border_color = ""
                    if "rounded-color" in self.metadata and self.metadata["rounded-color"] != "":
                        rounded_color = self.metadata["rounded-color"]
                    if "rounded-border-color" in self.metadata and self.metadata["rounded-border-color"] != "":
                        rounded_border_color = self.metadata["rounded-border-color"]
                        rendered_row += "<div id='borderedlogo' style='background-color: "+rounded_color+"; border-width: 5px; border-color: "+rounded_border_color+";'>"
                    else:
                        rendered_row += "<div id='borderedlogo' style='background-color: "+rounded_color+";'>"

                rendered_row += "<font color='"+text_color+"'><b>"+self.metadata["text"]+"</b></font>"
                if "rounded" in self.metadata and self.metadata["rounded"] == "true": rendered_row += "</div>"
            elif "snippet" in self.metadata and self.metadata["snippet"] != "":
                rendered_row += self.metadata["snippet"]

            rendered_row += suffix

            return rendered_row
        elif self.type == "footer":
            footer_content = ""
            text_color = '#969696'
            if "text-color" in self.metadata and self.metadata["text-color"] != "":
                    text_color = self.metadata["text-color"]

            if "snippet" in self.metadata and self.metadata["snippet"] != "":
                footer_content = self.metadata["snippet"]
            elif "text" in self.metadata and self.metadata["text"] != "":
                rendered_row += "<font color='"+text_color+"'>"+self.metadata["text"]+"</font>"

            # default footer content
            if footer_content == "":
                footer_content = "<font color='"+text_color+"'>Website created with <a href='https://github.com/magj3k/swiftpage' target='_blank' style='color: "+text_color+"; display: auto; width: auto; height: auto;'>SwiftPage</a> (available on GitHub).<br>SwiftPage is an open-source project created and maintained by <a href='http://www.magmhj.com' target='_blank' style='color: "+text_color+"; display: auto; width: auto; height: auto;'>MagMHJ, LLC</a>.</font>"

            # background color
            style = "background-color: "+self.color+";"
            if "background-colors" in self.metadata:
                colors = self.metadata["background-colors"]
                if len(colors) == 1: # new background color
                    style = "background-color: "+colors[0]+";"
                elif len(colors) > 1: # background gradient
                    style = "background-image: linear-gradient(to right, "+colors[0]+", "+colors[-1]+");"

            return "<div class='row' id='footer' style='"+style+"'><!-- footer -->\n<div class='vertical-center'>"+footer_content+"</div>\n</div>\n"
        elif self.type == "img_gallery":
            prefix = "<div class='row' id='bigbigrow' style='background-color: "+self.color+"'><div class='slideshow'>\n<table border='0' height='420'><tr>\n"
            suffix = "</tr></table>\n</div></div>\n"

            rendered_row = prefix

            # gets list of all images from image directory
            filepath_prefix = "site/images/"+str(self.metadata["filename"])+"/"
            if "extension" in self.metadata and self.metadata["extension"] != None:
                ext_string = self.metadata["extension"]
                if ext_string[-1] == "/": ext_string = ext_string[:-1]
                filepath_prefix = "site/images/"+str(self.metadata["filename"])+"/"+ext_string+"/"

            filelist = self.ordered_filelist(os.listdir(filepath_prefix)[:])
            j = 0
            for i in range(len(filelist)):
                filename = filelist[i]

                if filename[-3:].lower() in supported_img_extensions:
                    filepath = filepath_prefix+filename
                    multiplier = 1.0
                    if "multipliers" in self.metadata and self.metadata["multipliers"] != None:
                        if j < len(self.metadata["multipliers"]): multiplier = self.metadata["multipliers"][j]
                    render_height = self.height_for_image(filepath, multiplier)

                    rendered_row += "<td>&nbsp;</td>\n"
                    rendered_row += "<td valign='middle'>\n<img src='"+filepath[5:]+"' height='"+str(int(render_height))+"' style='border-radius: 0px'>\n</td>\n"
                    j += 1

            rendered_row += "<td>&nbsp;</td>\n"
            rendered_row += suffix

            return rendered_row
        elif self.type == "links":
            prefix = "<div class='row' id='halfrow' style='background-color: "+self.color+"; color: white'>\n"
            suffix = "</div>\n"

            rendered_row = prefix

            if "links" in self.metadata:
                links = self.metadata["links"]
                for link in links:
                    if "address" in link and link["address"] != "":
                        if link["address"][0] == "#":
                            rendered_row += "<a href='"+link["address"]+"'><div class='link'>"
                        else:
                            rendered_row += "<a href='"+link["address"]+"' target='_blank'><div class='link'>"
                    rendered_row += "<div class='column'>"
                    rendered_row += "<div class='vertical-center'><div id='borderedlabel'>"+link["name"]+"</div></div>"
                    rendered_row += "</div>"
                    if "address" in link and link["address"] != "": rendered_row += "</div></a>"
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

            if "links" in self.metadata:
                links = self.metadata["links"]
                for link in links:
                    name = link["name"]
                    link_address = "files/"+str(self.metadata["filename"])+"/"
                    if "filename" in link:
                        link_address += link["filename"]
                        if link["filename"] == "":
                            link_address = "#"    
                    elif "address" in link:
                        link_address += link["address"]
                        if link["address"] == "":
                            link_address = "#"    
                    else:
                        link_address = "#"

                    if not os.path.isfile("site/"+link_address):
                        link_address = "#"

                    link_target = ""
                    if link_address[0] != "#":
                        link_target = " target='_blank'"

                    rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"
                    rendered_row += "<td valign='middle' align='center'>\n<a href='"+link_address+"'"+link_target+"><div class='link'>\n<div style='width: 150px; height: 150px; border-radius: 50%; border-width: 5px; border-color: white; border-style: solid;'><table width='100%'><tr><td valign='middle' align='center' height='150'><img src='images/document_icon.png' height='85' style='border-radius: 0px'></td></tr></table></div>\n</div></a>\n<br><div id='borderedlabel'>"+name+"</div>\n</td>\n"
                rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"

            rendered_row += suffix

            return rendered_row
        elif self.type == "people":
            prefix = "<div class='row' id='bigrow' style='background-color: "+self.color+"'><div class='slideshow' style='font-size: 22px'>\n<table border='0' height='330'><tr>\n"
            suffix = "</tr></table>\n</div></div>\n"

            rendered_row = prefix

            if "people" in self.metadata:
                people = self.metadata["people"]
                for person in people:
                    name = person["name"]
                    filename = "unknown.png"
                    if "filename" in person:
                        filename = str(self.metadata["filename"])+"/people/"+person["filename"]

                        # checks that filename exists, else replaces with unknown symbol
                        file_exists = os.path.isfile("site/images/"+filename)
                        if not file_exists:
                            filename = str(self.metadata["filename"])+"/"+person["filename"]
                            file_exists = os.path.isfile("site/images/"+filename)

                            if not file_exists: 
                                filename = "unknown.png"

                    # resizes image if necessary
                    get_img_and_resize("site/images/"+filename)

                    rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"
                    rendered_row += "<td valign='middle' align='center'>\n<div style='width: 150px; height: 150px; border-radius: 50%; border-width: 5px; border-color: white; border-style: solid; overflow: hidden;'><img src='images/"+filename+"' width='150' height='150' style='border-radius: 0px'></div>\n<br><div id='borderedlabel'>"+name+"</div>\n</td>\n"
                rendered_row += "<td>&nbsp;&nbsp;&nbsp;</td>\n"

            rendered_row += suffix

            return rendered_row
        elif self.type == "text":
            prefix = "<div class='row' id='bigrow' style='background-color: "+self.color+"; text-align: center; overflow-y: scroll; font-size: 29px; -webkit-overflow-scrolling: touch;'>"
            if "height" in self.metadata:
                prefix = "<div class='row' id='bigrow' style='background-color: "+self.color+"; height: "+str(max(self.metadata["height"], 200))+"px; text-align: center; overflow-y: scroll; font-size: 29px; -webkit-overflow-scrolling: touch;'>"
            rendered_row = prefix+"<table width='100%'><tr><td width='7%'></td><td valign='top'>\n<br>"+self.metadata["text"]+"\n"+"<br><br></td><td width='7%'></td></tr></table></div>\n"
            return rendered_row
        elif self.type == "custom":
            row_type = "bigrow"
            if "size" in self.metadata and (self.metadata["size"] == "big" or self.metadata["size"] == "large"):
                row_type = "bigbigrow"
            prefix = "<div class='row' id='"+row_type+"'"

            style = " style='background-color: "+self.color+"'"
            if "height" in self.metadata:
                style = " style='background-color: "+self.color+"; height: "+max(self.metadata["height"], 120)+"px;'"

            rendered_row = prefix+style+"><div class='vertical-center'>\n"+self.metadata["snippet"]+"\n"+"</div></div>\n"
        return "<div class='row' id='separator' style='background-color: "+self.color+"'></div>\n"

