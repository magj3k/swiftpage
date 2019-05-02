import pathlib
import torch
from torch.autograd import Variable

class Datapoint(object):
    def __init__(self, metadata = {}, numerical_data = [], tensor_data = []):
        self.metadata = metadata

        if len(numerical_data) > 0:
            string = ""
            for number in numerical_data:
                string += chr(number)
            self.metadata["text"] = string

        if len(tensor_data) > 0:
            string = ""
            for tens_item in tensor_data[0]:
                string += chr(int(round(max(0, tens_item.item()))))
            self.metadata["text"] = string                

    def reduce(self):
        numerical_output = []
        if "text" in self.metadata:
            for character in self.metadata["text"]:
                num = ord(character)
                numerical_output.append(num)

        return numerical_output

    def print(self):
        if "text" in self.metadata:
            print("Datapoint: "+str(self.metadata["text"]))
        else:
            print("No valid data in datapoint.")

class Dataset(object):
    def __init__(self, samples):
        self.samples = samples

    def getInputsTensor(self, D_in):
        inputs = []
        for sample in self.samples:
            if isinstance(sample[0], Datapoint):
                inputs.append(sample[0].reduce())
            else:
                inputs.append(sample[0])
            for i in range(max(D_in-len(inputs[-1]), 0)):
                inputs[-1].append(0)
            if len(inputs[-1]) > D_in:
                inputs[-1] = inputs[-1][:D_in]
        return torch.FloatTensor(inputs)

    def getOutputsTensor(self, D_out):
        outputs = []
        for sample in self.samples:
            if isinstance(sample[1], Datapoint):
                outputs.append(sample[1].reduce())
            else:
                outputs.append(sample[1])
            for i in range(max(D_out-len(outputs[-1]), 0)):
                outputs[-1].append(0)
            if len(outputs[-1]) > D_out:
                outputs[-1] = outputs[-1][:D_out]
        return torch.FloatTensor(outputs)

class Network(torch.nn.Module):
    def __init__(self, D_in, D_out):
        super(Network, self).__init__()
        self.layers = []

        # define internal neural network structure here

        self.layer_1 = torch.nn.Linear(D_in, 2*D_in)
        self.layers.append(self.layer_1)
        self.layer_2 = torch.nn.Linear(2*D_in, int(3*D_in)+int(3*D_out))
        self.layers.append(self.layer_2)
        self.layer_3 = torch.nn.Linear(int(3*D_in)+int(3*D_out), int(5*D_in)+int(5*D_out))
        self.layers.append(self.layer_3)
        self.layer_4 = torch.nn.Linear(int(5*D_in)+int(5*D_out), int(5*D_in)+int(5*D_out))
        self.layers.append(self.layer_4)
        self.layer_5 = torch.nn.Linear(int(5*D_in)+int(5*D_out), int(3*D_in)+int(3*D_out))
        self.layers.append(self.layer_5)
        self.layer_6 = torch.nn.Linear(int(3*D_in)+int(3*D_out), 2*D_out)
        self.layers.append(self.layer_6)
        self.layer_7 = torch.nn.Linear(2*D_out, D_out)
        self.layers.append(self.layer_7)

    def forward(self, x):
        layeroutput = x
        activation = torch.nn.LeakyReLU(0.05)

        for layer in self.layers:
            layeroutput = activation(layer(layeroutput))

        return layeroutput

class Learner(object):
    def __init__(self, D_in, D_out, learning_rate, initial_samples=[]):
        self.D_in = D_in
        self.D_out = D_out
        self.learning_rate = learning_rate
        self.model = Network(D_in, D_out)
        self.dataset = Dataset(initial_samples)

        modelfile = pathlib.Path("savedmodel.pt")
        if modelfile.is_file():
            self.model = torch.load("savedmodel.pt")

        self.criterion = torch.nn.MSELoss(size_average=False)
        self.optimizer = torch.optim.SGD(self.model.parameters(), self.learning_rate)

    def train_network(self, num_cycles):

        # gathers training data
        x = Variable(self.dataset.getInputsTensor(self.D_in))
        y = Variable(self.dataset.getOutputsTensor(self.D_out))

        # trains network
        for cycle in range(num_cycles):
            y_pred = self.model(x)
            loss = self.criterion(y_pred, y)

            print("Cycle "+str(cycle)+", Loss: "+str(loss.data[0]))

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        torch.save(self.model, "savedmodel.pt")

    def test_network(self, test_input_data):
        for i in range(max(self.D_in-len(test_input_data), 0)):
            test_input_data.append(0)

        # print("Testing network: "+str(test_input_data))
        x = Variable(torch.FloatTensor(test_input_data))
        y = self.model(x)
        # print("Test output: "+str(y))

        return y

