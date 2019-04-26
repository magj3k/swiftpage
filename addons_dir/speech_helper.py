
# builds synonyms dict for quick lookup use later
synonyms_dict = {}
synonyms = [
    ["try", "do"],
    ["go","scroll", "jump", "show"],
    ["to", "at", "2"],
    ["top", "begin", "beginning", "start", "upper"],
    ["bottom", "floor", "end", "final"],
    ["title", "logo", "header", "beginning"],
    ["color", "shade"],
    ["brightness", "shine", "white"],
    ["next", "after"],
    ["gradient", "shade", "colorshift", "transition"],
    ["like", "similar", "around"],
    ["and", "also"],
    ["set", "reset", "change", "alter", "modify", "switch", "turn"],
    ["make", "force"],
    ["say", "list", "read", "show"],
    ["reload", "refresh"],
    ["please", "welcome", "thanks", "thank"],
    ["clear", "restart", "reset", "undo"],
    ["changes", "modifications", "edits"],
    ["everything", "all", "every"],
    ["left", "lefthand"],
    ["righthand", "right"],
    ["on", "enable", "bring", "restore", "add", "reset"],
    ["off", "disable", "remove", "close", "erase", "delete", "clear", "rid"],
    ["text", "label", "string", "title"],
    ["background", "behind", "bg", "wallpaper", "wall"],
    ["and", "then"],
    ["maybe", "possibly", "kindof", "sortof", "perhaps", "actually", "definitely"],
    ["navigation", "nav", "navbar"],
]
for synonyms_list in synonyms:
    for synonym in synonyms_list:
        if synonym in synonyms_dict:
            synonyms_dict[synonym] = synonyms_dict[synonym] + synonyms_list
        else:
            synonyms_dict[synonym] = synonyms_list

def remove_nonsense_words(words):
    filtered_words = []
    for word in words:
        if word not in synonyms_dict["maybe"]:
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

def match_expression(expression_to_match, speech): # returns tuple of prefix and variables
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
                variables = [ concatenate(words_in_speech[speech_pointer+1:next_expression_start]) ]
                next_phrase = concatenate(words_in_speech[next_expression_start:])
                    
            break

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
