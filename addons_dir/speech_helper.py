import colorsys as cs
from math import *

import colorsys as cs
from math import *

# builds synonyms dict for quick lookup use later
synonyms_dict = {}
synonyms = [
    ["try", "do"],
    ["go","scroll", "jump", "show"],
    ["to", "at", "2"],
    ["top", "begin", "beginning", "start", "upper", "start"],
    ["bottom", "floor", "end", "final"],
    ["title", "logo", "header", "beginning"],
    ["color", "shade"],
    ["next", "after"],
    ["gradient", "shade", "colorshift", "transition"],
    ["like", "similar", "around"],
    ["and", "also"],
    ["set", "reset", "change", "alter", "modify", "switch", "turn"],
    ["make", "force", "turn"],
    ["say", "list", "read", "show"],
    ["reload", "refresh"],
    ["please", "welcome", "thanks", "thank"],
    ["clear", "restart", "reset", "undo"],
    ["changes", "modifications", "edits"],
    ["everything", "all", "every"],
    ["left", "lefthand"],
    ["right", "righthand"],
    ["on", "enable", "bring", "restore", "reset"],
    ["off", "disable", "remove", "close", "erase", "delete", "clear", "rid"],
    ["text", "label", "string", "title"],
    ["background", "behind", "bg", "wallpaper", "wall"],
    ["and", "then"],
    ["maybe", "possibly", "kindof", "sortof", "perhaps", "actually", "definitely", "yeah"],
    ["number", "letter"],
    ["navigation", "nav", "navbar"],
    ["one", "first"],
    ["two", "second", "to"],
    ["three", "third"],
    ["four", "fourth", "for"],
    ["five", "fifth"],
    ["six", "sixth"],
    ["seven", "seventh"],
    ["eight", "eighth", "ate"],
    ["nine", "ninth"],
    ["ten", "tenth"],
    ["last", "final", "ending", "end"],
    ["point", "dot", "decimal"],
    ["add", "append", "create", "make", "new"],
    ["it", "that", "previous", "last"],
    ["more", "greater", "larger", "grander", "louder"],
    ["less", "fewer", "smaller", "softer"],
    ["button", "link"],
    ["move", "put", "take"],
    ["red", "cherry", "crimson"],
    ["orange", "sunset", "apricot"],
    ["yellow", "lemon", "sunny"],
    ["green", "lime"],
    ["blue", "ocean"],
    ["purple", "violet"],
    ["black", "dark"],
    ["white", "bright", "light"],
    ["grey", "gray", "ash"],
    ["teal", "turquoise"],
    ["rose", "rosy"],
    ["brown", "cinnamon", "burnt", "burned"],
    ["bright", "brighter", "light", "lighter", "lighten"],
    ["darker", "dark", "dim", "dimmer", "darken"],
    ["hashtag", "pound"],
    ["again", "over"],
    ["round", "rounded", "curved"],
]
for synonyms_list in synonyms:
    for synonym in synonyms_list:
        if synonym in synonyms_dict:
            synonyms_dict[synonym] = synonyms_dict[synonym] + synonyms_list
        else:
            synonyms_dict[synonym] = synonyms_list

numbers_dict = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

colors_dict = {
    "red": "#ff2600",
    "orange": "#ff9300",
    "yellow": "#fefb00",
    "green": "#00ea00",
    "blue": "#0432ff",
    "purple": "#9437ff",
    "black": "#000000",
    "white": "#ffffff",
    "gray": "#7a7a7a",
    "pink": "#eb65ff",
    "teal": "#00fdcc",
    "rose": "#f5006b",
    "brown": "#844c00",
}

def hex_2_rgb(hex_color):
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def rgb_2_hsv(rgb):
    h, s, v = cs.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    return (h, s, v)

def hsv_2_rgb(hsv):
    r, g, b = cs.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return (r*255.0, g*255.0, b*255.0)

def rgb_2_hex(rgb):
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def merge_colors(rgb_a, rgb_b, ratio_a_b=0.5):
    return ( (rgb_a[0]*ratio_a_b)+(rgb_b[0]*(1-ratio_a_b)), (rgb_a[1]*ratio_a_b)+(rgb_b[1]*(1-ratio_a_b)), (rgb_a[2]*ratio_a_b)+(rgb_b[2]*(1-ratio_a_b)) )

def merge_colors_hex(hex_a, hex_b):
    hex_a_rgb = hex_2_rgb(hex_a)
    hex_b_rgb = hex_2_rgb(hex_b)

    hex_a_hsv = rgb_2_hsv(hex_a_rgb)
    hex_b_hsv = rgb_2_hsv(hex_b_rgb)

    merged_rgb = merge_colors(hex_a_rgb, hex_b_rgb)
    merged_hsv = merge_colors(hex_a_hsv, hex_b_hsv)
    merged_hsv_rgb = hsv_2_rgb(merged_hsv)

    merged_overall = merge_colors(merged_rgb, merged_hsv_rgb, 0.6)
    return rgb_2_hex(merged_overall)

def inverse_color(hex_color):
    rgb = hex_2_rgb(hex_color)
    rgb_magnitude = sqrt( pow(rgb[0], 2.0) + pow(rgb[1], 2.0) + pow(rgb[2], 2.0) )+1.0
    inverse_rgb = ( (255-rgb[0]), (255-rgb[1]), (255-rgb[2]) )
    inverse_magnitude = sqrt( pow(inverse_rgb[0], 2.0) + pow(inverse_rgb[1], 2.0) + pow(inverse_rgb[2], 2.0) )+1.0

    final_color = ( inverse_rgb[0]*rgb_magnitude/inverse_magnitude, inverse_rgb[1]*rgb_magnitude/inverse_magnitude, inverse_rgb[2]*rgb_magnitude/inverse_magnitude )

    return rgb_2_hex(final_color)

def extract_colors(variables, relative_color="#787878"):
    colors = []
    modifier_color = None

    # checks for color modifier
    more_or_less_found = None
    for variable in variables:
        for uncased_word in variable.split(' '):
            word = uncased_word.lower()
            if word in synonyms_dict["darker"]:
                modifier_color = colors_dict["black"]
            elif word in synonyms_dict["lighter"]:
                modifier_color = colors_dict["white"]
            elif word in synonyms_dict["more"]:
                more_or_less_found = "more"
            elif word in synonyms_dict["less"]:
                more_or_less_found = "less"
            elif len(word) >= 4 and (word[:-1] in synonyms_dict and word[-1:] == 'r' and synonyms_dict[word[:-1]][0] in colors_dict):
                more_or_less_found = "more"
                modifier_color = colors_dict[synonyms_dict[word[:-1]][0]]
            elif len(word) >= 4 and (word[:-2] in synonyms_dict and word[-2:] == 'er' and synonyms_dict[word[:-2]][0] in colors_dict):
                more_or_less_found = "more"
                modifier_color = colors_dict[synonyms_dict[word[:-2]][0]]

    if modifier_color != None:
        colors.append( merge_colors_hex(relative_color, modifier_color) )

    # extracts colors
    for variable in variables:
        for uncased_word in variable.split(' '):
            word = uncased_word.lower()
            if word in synonyms_dict and synonyms_dict[word][0] in colors_dict:
                if more_or_less_found != None:
                    if more_or_less_found == "more":
                        extracted_color = colors_dict[synonyms_dict[word][0]]
                        colors.append( merge_colors_hex(relative_color, extracted_color) )
                    else:
                        extracted_color = inverse_color(colors_dict[synonyms_dict[word][0]])
                        colors.append( merge_colors_hex(relative_color, extracted_color) )
                else:
                    colors.append( colors_dict[synonyms_dict[word][0]] )

    return colors

def remove_nonsense_words(words):
    filtered_words = []
    for uncased_word in words:
        word = uncased_word.lower()
        if word not in synonyms_dict["maybe"] and word not in synonyms_dict["number"] and word not in synonyms_dict["hashtag"]:
            filtered_words.append(word)
    return filtered_words

def concatenate(words):
    concatenation = ""
    for i in range(len(words)):
        word = words[i]
        concatenation += word
        if i != len(words)-1:
            concatenation += " "

    return concatenation

def break_into_words(word_segment):
    words = []

    if word_segment[0] == "(" and word_segment[-1] == ")": # indicates collection of possible words
        segment_components = word_segment[1:-1].split(',')
        words.extend(segment_components)
    else:
        words.append(word_segment)

    return words

def match_any_expression(expressions_to_match, speech):
    for expr in expressions_to_match:
        match = match_expression(expr, speech)
        if match != None:
            return match
    return None

def extract_numbers(prefix, variables):
    numbers = []

    words_in_prefix = remove_nonsense_words(prefix.split(' '))
    consideration_threshold = 0
    for word in words_in_prefix:
        if word in synonyms_dict and consideration_threshold == 0:
            syns = synonyms_dict[word]
            if syns[0] in numbers_dict:
                consideration_threshold = 2
                numbers.append(numbers_dict[syns[0]])
        consideration_threshold = max(consideration_threshold-1, 0)

    for variable in variables:
        words_in_variable = remove_nonsense_words(variable.split(' '))
        consideration_threshold = 0
        for word in words_in_variable:
            if word in synonyms_dict and consideration_threshold == 0:
                syns = synonyms_dict[word]
                if syns[0] in numbers_dict:
                    consideration_threshold = 2
                    numbers.append(numbers_dict[syns[0]])
            consideration_threshold = max(consideration_threshold-1, 0)

    return numbers

def match_expression(expression_to_match, speech, context=None): # returns tuple of prefix and variables
    variables = []
    prefix = speech
    next_phrase = None

    # checks that similar words in expression occur similarly in speech
    words_in_expression = expression_to_match.split(' ')
    words_in_speech = remove_nonsense_words(speech.split(' '))
    speech_pointer = -1

    # safety check
    if len(words_in_speech) < 1 or len(words_in_expression) < 1:
        return None

    for i in range(len(words_in_expression)):

        # finds similar words for expression
        dual_words = break_into_words(words_in_expression[i])
        syns = []
        for word in dual_words:
            if word in synonyms_dict: syns += synonyms_dict[word][:]

        # tracks where similar word occurs in speech
        match_found = False
        max_bound = speech_pointer+5
        if speech_pointer == -1: max_bound = len(words_in_speech)
        if speech_pointer <= len(words_in_speech)-1:
            for j in range(min(speech_pointer+1, len(words_in_speech)-1), min(max_bound, len(words_in_speech))):
                speech_word = words_in_speech[j]
                if speech_word != None and syns != None and speech_word in syns:
                    speech_pointer = j
                    match_found = True
                    break

        # if no match has been found
        if match_found == False:
            return None

        # if last word in expression has been matched
        if i == len(words_in_expression)-1:
            
            # parses out variable(s)
            next_expression_start = -1
            prefix_length = 0
            for j in range(len(words_in_speech)):
                if words_in_speech[j] in synonyms_dict["and"]:
                    next_expression_start = j+1
                    break
                elif j <= speech_pointer:
                    prefix_length += len(words_in_speech[j])+1
            prefix = speech[:prefix_length]
            
            if next_expression_start == -1:
                variables = [ concatenate(words_in_speech[speech_pointer+1:]) ]
            else:
                variables = [ concatenate(words_in_speech[speech_pointer+1:next_expression_start-1]) ]
                next_phrase = concatenate(words_in_speech[next_expression_start:])
                    
            break

    # extracts numbers
    numbers = extract_numbers(prefix, variables)
    variables += numbers

    # extracts colors
    colors = extract_colors(variables)
    variables += colors

    return [prefix, variables, next_phrase]

# tests
# print("\n")
# print(match_expression("set title to", "change the top title bar to the Avengers"))
# print(match_expression("set title to", "change the top header thing to the coolest website ever"))
# print(match_expression("make title say", "make the logo title bar say Hello World"))
# print(match_expression("refresh", "reload the page please"))
# print(match_expression("scroll to bottom", "please just scroll down to the bottom of the page"))
# print(match_expression("reset changes", "please clear all of my changes"))
# print(match_expression("reset changes","please reset all of my changes and scroll back up to the top"))
# print(match_expression("set title to","change the title to archipelago game"))
# print(match_expression("set (title,background) to","change the background to red"))
# print(match_expression("delete second navbar","please remove the second navbar from the page"))
# print(match_expression("add navbar","add a new navbar above the second one"))
# print(match_expression("set title to","change the title of my page to project page and delete the logo text background"))
# print(match_expression("(make,set) title","turn the title green please"))
# print(match_expression("(make,set) title","please make the title even oranger"))
# print( rgb_2_hex(hex_2_rgb("#ff0000")) )
# print( hsv_2_rgb(rgb_2_hsv( (255, 0, 0) )) )
# print( rgb_2_hex(hsv_2_rgb(rgb_2_hsv(hex_2_rgb("#ff0000")))) )
# print( rgb_2_hex(hsv_2_rgb( merge_colors(rgb_2_hsv(hex_2_rgb("#ff0000")), rgb_2_hsv(hex_2_rgb("#0000ff"))) )) )
# print( merge_colors_hex("#ffffff", "#0000ff") )
# print( merge_colors_hex("#e7db74", "#282923") )
# print(match_expression("(make,set) title","change the title color to white"))
# print(match_expression("(make,set) title","change the title color to blue"))
# print(match_expression("(make,set) (logo,title) background", "make the title background red"))
