import theano
import theano.tensor as tensor
import numpy

##function to convert python list to matrix

class Layer:
    """
    A single layer of an MLP.

    Calling compute on a theano matrix (1 x n_inputs) prudces array
    of node outputs.
    """
    def __init__(self, input_size, output_size):
        """
        Initialize the layer.

        param input_size: number of nodes in previous layer
        param output_size: number of nodes in current layer
        """
        self.input_size = input_size
        self.output_size = output_size
        self.generate_random_weights()
        ##inputs, outputs, and error values are stored for use in training
        self.inputs = numpy.ndarray((0, 0))
        self.outputs = numpy.ndarray((0, 0))
        self.errors = numpy.ndarray((0, 0))        

        
    def generate_random_weights(self):
        """
        Generates a random set of weights by uniformly distributing on
        an interval described at:
        http://deeplearning.net/tutorial/mlp.html#mlp
        """
        random = tensor.shared_randomstreams.RandomStreams()
        weightfunc = theano.function([], random.uniform(
            (self.input_size, self.output_size),
            -4 * numpy.sqrt(6. / (self.input_size + self.output_size)),
            4 * numpy.sqrt(6. / (self.input_size + self.output_size))))
        self.weights = weightfunc()
        
    def compute(self, inputs):
        """
        Pass a set of inputs through the layer's perceptrons, and store
        internally the inputs and outputs for use in training.
        """
        inp = tensor.dmatrix('inp') ##to be passed in and stored as inputs
        self.inputs = inputs
        set_output = theano.function([], tensor.nnet.sigmoid(tensor.dot(
                                                               self.inputs,          
                                                               self.weights)))
        self.outputs = set_output()
        return self.outputs

    def get_errors(self, errors, weights):
        """
        Compute the error vector given the weight and error vectors
        for the next layer.
        """
        next_e = theano.tensor.dmatrix('next_e') ##next layer's errors
        next_w = theano.tensor.dmatrix('next_w') ##next layer's weights
        prod = tensor.dot(next_e, next_w.T) #their product
        find_errors = theano.function([next_e, next_w], (self.outputs *
                                                    (1 - self.outputs) *
                                                        prod))
        self.errors = find_errors(errors, weights)
        return self.errors

    def train(self, rate):
        eta = theano.tensor.dscalar('eta')
        inp = theano.tensor.dmatrix('inp')
        err = theano.tensor.dmatrix('err')
        val = theano.tensor.dot(inp.T, (eta * err))
        adjustment = theano.function([inp, eta, err], val)
        self.weights += adjustment(self.inputs, rate, self.errors)


class MLP:
    '''A simple multi-layered perceprtron'''
    
    def __init__(self, inputs, layers):
        """
        Initialize the MLP with random weights.

        param inputs: number of inputs to the first layer
        param layers: list of layer sizes (in nodes), final value is
                      number of outputs
        """
        self.layers = []
        for n in layers:
            self.layers.append(Layer(inputs, n))
            inputs = n

    def run(self, inputs):
        '''Compute the MLP's output on a given set of inputs'''
        return reduce(lambda i, l: l.compute(i), self.layers, inputs)

    def train(self, data, epochs=5000, rate=.001, show_status=False):
        """
        Train the mlp using backpropegation.

        param data: training data, tuples of form (input, expected)
        param epochs: number of iterations through the training data
        """
        if show_status:
            print("Training MLP on sample data with {0} epochs:".format(epochs))
        for i in xrange(epochs):
            print("\tEpoch {0} of {1}".format(i, epochs))
            for x, t in data:
                self.run(x)
                errors = self.layers[-1].get_errors((t - self.run(x)),
                             numpy.identity(self.layers[-1].output_size))
                weights = self.layers[-1].weights
                self.layers[-1].train(rate)
                for layer in self.layers[-2::-1]:
                    errors = layer.get_errors(errors, weights)
                    weights = layer.weights
                    layer.train(rate)
                

if __name__ == '__main__':
    ##Example
    ##initialize MLP with eight inputs, a 3-node hidden layer, and eight outputs
    ##like the binary identity example
    mlp = MLP(8, [3, 8])
    
    ##feed it some arbitrary inputs and print results
    ##note that training hasn't taken place yet, so weights are all random, and
    ##these outputs don't mean anything
    print(mlp.run([[1, 0, 0, 0, 1, 1, 0, 1]]))
    print(mlp.run([[1, 0, 1, 0, 1, 1, 0, 0]]))
    print(mlp.run([[0, 0, 0, 0, 0, 0, 0, 0]]))
    print(mlp.run([[1, 1, 1, 1, 1, 1, 1, 1]]))
    
    ##train on example data from book
    samples = [[[1, 0, 0, 0, 0, 0, 0, 0]],
               [[0, 1, 0, 0, 0, 0, 0, 0]],
               [[0, 0, 1, 0, 0, 0, 0, 0]],
               [[0, 0, 0, 1, 0, 0, 0, 0]],
               [[0, 0, 0, 0, 1, 0, 0, 0]],
               [[0, 0, 0, 0, 0, 1, 0, 0]],
               [[0, 0, 0, 0, 0, 0, 1, 0]],
               [[0, 0, 0, 0, 0, 0, 0, 1]]]
    data = zip(samples, samples)
    mlp.train(data, show_status=True)

    ##run same inputs as before
    print(mlp.run([[1, 0, 0, 0, 1, 1, 0, 1]]))
    print(mlp.run([[1, 0, 1, 0, 1, 1, 0, 0]]))
    print(mlp.run([[0, 0, 0, 0, 0, 0, 0, 0]]))
    print(mlp.run([[1, 1, 1, 1, 1, 1, 1, 1]]))
    
    
    
