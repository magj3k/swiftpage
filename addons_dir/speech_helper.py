
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

}

def remove_nonsense_words(words):
    filtered_words = []
    for word in words:
        if word not in synonyms_dict["maybe"] and word not in synonyms_dict["number"]:
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
                variables = [ concatenate(words_in_speech[speech_pointer+1:next_expression_start-1]) ]
                next_phrase = concatenate(words_in_speech[next_expression_start:])
                    
            break

    # extracts numbers
    numbers = extract_numbers(prefix, variables)
    variables += numbers

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
