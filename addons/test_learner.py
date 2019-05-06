from learner import *

samples = [
    [Datapoint({"text": "set the title to my website"}), Datapoint({"text": "s l my website"})],
    [Datapoint({"text": "set the title to apples"}), Datapoint({"text": "s l apples"})],
    [Datapoint({"text": "set the title to zunebuggy"}), Datapoint({"text": "s l zunebuggy"})],
    [Datapoint({"text": "set the title to suffix"}), Datapoint({"text": "s l suffix"})],
    [Datapoint({"text": "set the title to arbitrarium"}), Datapoint({"text": "s l arbitrarium"})],
    [Datapoint({"text": "set the title to microsoft.com"}), Datapoint({"text": "s l microsoft.com"})],
    [Datapoint({"text": "set the title to the best thing ever"}), Datapoint({"text": "s l the best thing ever"})],
    [Datapoint({"text": "set the title to the worst thing ever"}), Datapoint({"text": "s l the worst thing ever"})],
    [Datapoint({"text": "set the title color to red"}), Datapoint({"text": "s l c red"})],
    [Datapoint({"text": "set the title color to white"}), Datapoint({"text": "s l c white"})],
    [Datapoint({"text": "set the title color to blue"}), Datapoint({"text": "s l c blue"})],
    [Datapoint({"text": "set the title background color to blue"}), Datapoint({"text": "s l b c blue"})],
    [Datapoint({"text": "set the title background color to green"}), Datapoint({"text": "s l b c green"})],
    [Datapoint({"text": "set the title to awesomeness"}), Datapoint({"text": "s l awesomeness"})],
    [Datapoint({"text": "set the title to www.magmhj.com"}), Datapoint({"text": "s l www.magmhj.com"})],
    [Datapoint({"text": "reload the page"}), Datapoint({"text": "r"})],
    [Datapoint({"text": "refresh please"}), Datapoint({"text": "r"})],
    [Datapoint({"text": "refresh the browser please"}), Datapoint({"text": "r"})],
    [Datapoint({"text": "refresh the browser"}), Datapoint({"text": "r"})],
    [Datapoint({"text": "please just reload the page"}), Datapoint({"text": "r"})],
]

learning_rate = 4e-9
interpreter = Learner(60, 50, learning_rate, samples)

interpreter.train_network(10000)
Datapoint({}, [], [interpreter.test_network( Datapoint({"text": "set the title to my website"}).reduce() )]).print()
Datapoint({}, [], [interpreter.test_network( Datapoint({"text": "set the title to nickelodeon.com"}).reduce() )]).print()
Datapoint({}, [], [interpreter.test_network( Datapoint({"text": "refresh please"}).reduce() )]).print()
Datapoint({}, [], [interpreter.test_network( Datapoint({"text": "reload the page please"}).reduce() )]).print()
Datapoint({}, [], [interpreter.test_network( Datapoint({"text": "reload"}).reduce() )]).print()
Datapoint({}, [], [interpreter.test_network( Datapoint({"text": "set the title color to blue"}).reduce() )]).print()