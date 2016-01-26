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
    def __init__(self, input_size, output_size, output=False):
        """
        Initialize the layer.

        param input_size: number of nodes in previous layer
        param output_size: number of nodes in current layer
        param output: whether the layer is an output layer
        """
        self.input_size = input_size
        self.output_size = output_size
        self.generate_random_weights()
        self.output = output

        ####define and compile theano functions for internal use####
        inp = tensor.fmatrix('inputs')
        out = tensor.fmatrix('outputs')
        err = theano.tensor.fmatrix('errors')
        wei = tensor.fmatrix('weights')
        eta = theano.tensor.fscalar('eta')

        ##Compute outputs given inputs
        new_out = tensor.nnet.sigmoid(tensor.dot(inp, wei))
        self.get_output = theano.function([inp, wei], new_out,
                                          name='get_output')

        ##Compute error values given errors of previous layer
        prod = out * (1 - out) * tensor.dot(err, wei.T)
        self.find_errors = theano.function([err, wei, out], prod,
                                           name='find_errors')

        ##Compute new weight vector
        val = wei + theano.tensor.dot(inp.T, (eta * err))
        self.adjust = theano.function([inp, eta, err, wei], val,
                                     name='adjustment')

        
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
                4 * numpy.sqrt(6. / (self.input_size + self.output_size))
            ).astype('float32'))
        self.weights = weightfunc()
        
    def compute(self, inputs):
        """
        Pass a set of inputs through the layer's perceptrons, and store
        internally the inputs and outputs for use in training.
        """
        self.inputs = inputs
        self.outputs = self.get_output(inputs, self.weights)
        return self.outputs

    def get_errors(self, errors, weights=None):
        """
        Compute the error vector given the weight and error vectors
        for the next layer. If this is an output layer, simply store
        and return the given errors.
        """
        if self.output:
            self.errors = errors
        else:
            self.errors = self.find_errors(errors, weights, self.outputs)
        return self.errors

    def train(self, rate):
        self.weights = self.adjust(self.inputs, rate, self.errors, self.weights)

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
            self.layers.append(Layer(inputs, n, n == layers[-1]))
            inputs = n

    def run(self, inputs):
        '''Compute the MLP's output on a given set of inputs'''
        return reduce(lambda i, l: l.compute(i), self.layers, inputs)

    def train(self, data, epochs=5000, rate=2**-8, show_status=False):
        """
        Train the mlp using backpropegation.

        param data: training data, tuples of form (input, expected)
        param epochs: number of iterations through the training data
        param rate: rate of learing
        """
        a = tensor.fmatrix('a')
        b = tensor.fmatrix('b')
        c = a - b
        sub = theano.function([a, b], c)
        if show_status:
            print("Training MLP on sample data with {0} epochs:".format(epochs))
        for i in xrange(epochs):
            if show_status:
                print("\tEpoch {0} of {1}".format(i, epochs))
            for x, t in data:
                self.run(x)
                errors = self.layers[-1].get_errors(sub(t, self.run(x)))
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
    print(map(round, mlp.run([[1, 0, 0, 0, 1, 1, 0, 1]])[0]))
    print(map(round, mlp.run([[1, 0, 1, 0, 1, 1, 0, 0]])[0]))
    print(map(round, mlp.run([[0, 0, 0, 0, 0, 0, 0, 0]])[0]))
    print(map(round, mlp.run([[1, 1, 1, 1, 1, 1, 1, 1]])[0]))
    
    ##train on example data from book
    samples = [[[1, 0, 0, 0, 0, 0, 0, 0]],
               [[0, 1, 0, 0, 0, 0, 0, 0]],
               [[0, 0, 1, 0, 0, 0, 0, 0]],
               [[0, 0, 0, 1, 0, 0, 0, 0]],
               [[0, 0, 0, 0, 1, 0, 0, 0]],
               [[0, 0, 0, 0, 0, 1, 0, 0]],
               [[0, 0, 0, 0, 0, 0, 1, 0]],
               [[0, 0, 0, 0, 0, 0, 0, 1]],
##               [[0, 1, 1, 1, 1, 1, 1, 1]],
##               [[1, 0, 1, 1, 1, 1, 1, 1]],
##               [[1, 1, 0, 1, 1, 1, 1, 1]],
##               [[1, 1, 1, 0, 1, 1, 1, 1]],
##               [[1, 1, 1, 1, 0, 1, 1, 1]],
##               [[1, 1, 1, 1, 1, 0, 1, 1]],
##               [[1, 1, 1, 1, 1, 1, 0, 1]],
##               [[1, 1, 1, 1, 1, 1, 1, 0]]
               ]
    data = zip(samples, samples)
    mlp.train(data, show_status=True)

    ##run same inputs as before
    test1 = mlp.run([[1, 0, 0, 0, 1, 1, 0, 1]])[0]
    test2 = mlp.run([[1, 0, 1, 0, 1, 1, 0, 0]])[0]
    test3 = mlp.run([[0, 0, 0, 0, 0, 0, 0, 0]])[0]
    test4 = mlp.run([[1, 1, 1, 1, 1, 1, 1, 1]])[0]
    
    print([1, 0, 0, 0, 1, 1, 0, 1])
    print(test1)
    print(map(round, test1))
    print('')
    print([1, 0, 1, 0, 1, 1, 0, 0])
    print(test2)
    print(map(round, test2))
    print('')
    print([0, 0, 0, 0, 0, 0, 0, 0])
    print(test3)
    print(map(round, test3))
    print('')
    print([1, 1, 1, 1, 1, 1, 1, 1])
    print(test4)
    print(map(round, test4))
    print('')
    
    
    
