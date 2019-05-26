

# builds synonyms dict for quick lookup use later
synonyms_dict = {}
synonyms = [
    ["try", "do"],
    ["go","scroll", "jump", "show", "find"],
    ["to", "at", "2"],
    ["top", "begin", "beginning", "start", "upper", "start"],
    ["bottom", "floor", "end", "final"],
    ["title", "logo", "header", "beginning"],
    ["color", "shade"],
    ["next", "after"],
    ["above", "top", "before"],
    ["below", "underneath", "under"],
    ["same", "match", "identical", "equal", "similar"],
    ["gradient", "shade", "colorshift", "transition"],
    ["like", "similar", "around"],
    ["and", "also", "then"],
    ["set", "reset", "change", "alter", "modify", "switch", "turn"],
    ["make", "force", "turn", "makes"],
    ["say", "list", "read", "show"],
    ["reload", "refresh"],
    ["please", "welcome", "thanks", "thank"],
    ["clear", "restart", "reset", "undo"],
    ["changes", "modifications", "edits"],
    ["change", "modification", "edit"],
    ["everything", "all", "every"],
    ["left", "lefthand"],
    ["right", "righthand"],
    ["on", "enable", "bring", "restore", "reset"],
    ["off", "disable", "remove", "close", "erase", "delete", "clear", "rid"],
    ["text", "label", "string", "title"],
    ["background", "behind", "bg", "wallpaper", "wall"],
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
    ["add", "append", "create", "new"],
    ["it", "that", "previous", "last", "em", "him", "er", "her", "its"],
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
    ["footer", "credits", "acknowledgements", "copyright", "disclaimer"],
    ["section"],
]
for synonyms_list in synonyms:
    for synonym in synonyms_list:
        if synonym in synonyms_dict:
            synonyms_dict[synonym] = synonyms_dict[synonym] + synonyms_list
        else:
            synonyms_dict[synonym] = synonyms_list

