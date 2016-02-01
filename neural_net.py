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
    def __init__(self, input_size, output_size, next_layer=None):
        """
        Initialize the layer.

        param input_size: number of nodes in previous layer
        param output_size: number of nodes in current layer
        param output: whether the layer is an output layer
        """
        self.input_size = input_size
        self.output_size = output_size
        self.generate_random_weights()
        self.errors = theano.shared(numpy.zeros([1, output_size], 'float32'))
        self.inputs = theano.shared(numpy.zeros([1, input_size], 'float32'))
        self.outputs = theano.shared(numpy.zeros([1, output_size], 'float32'))
        self.output = next_layer == None

        ####define and compile theano functions for internal use####
        exp = tensor.fmatrix('expected')
        eta = tensor.fscalar('eta')

        ##Compute outputs given inputs
        self.get_output = theano.function([],
                                          updates = [(self.outputs,
                                                        tensor.nnet.sigmoid(
                                                            tensor.dot(
                                                               self.inputs,
                                                               self.weights)))],
                                          name='get_output')

        ##Compute error values given errors of previous layer
        if self.output:
            self.find_errors = theano.function([exp],
                                               updates = [(self.errors,
                                                           self.outputs *
                                                           (1 - self.outputs)
                                                           * exp)],
                                           name='find_errors')
        else:
            self.find_errors = theano.function([],
                                               updates = [(self.errors,
                                                          self.outputs *
                                                          (1 - self.outputs) *
                                             tensor.dot(next_layer.errors,
                                                        next_layer.weights.T))],
                                           name='find_errors')

        ##Compute new weight vector
        self.train = theano.function([eta],
                                      updates = [(self.weights,
                                                  self.weights +
                                            theano.tensor.dot(self.inputs.T,
                                                        (eta * self.errors)))],
                                     name='train')

        
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
        self.weights = theano.shared(weightfunc())
        
    def compute(self, inputs):
        """
        Pass a set of inputs through the layer's perceptrons, and store
        internally the inputs and outputs for use in training.
        """
        self.inputs.set_value(inputs)
        self.get_output()
        return self.outputs.get_value()

    def get_errors(self, errors=None):
        """
        Compute the error vector given the weight and error vectors
        for the next layer. If the layer is an output layer, the function
        is passed some external computation of error values for the whole
        network.
        """
        if self.output:
            self.find_errors(errors)
        else:
            self.find_errors()


##class RecurrentLayer(Layer):
    


class MLP:
    '''A simple multi-layered perceprtron'''
    
    def __init__(self, inputs, outputs, layers):
        """
        Initialize the MLP with random weights.

        param inputs: number of inputs to the first layer
        param layers: list of layer sizes (in nodes), final value is
                      number of outputs
        """
        self.layers = []
        next_layer = Layer(layers[-1], outputs)
        self.layers.append(next_layer)
        outputs = layers[-1]
        for n in layers[-2::-1]:
            next_layer = Layer(n, outputs, next_layer)
            self.layers.append(next_layer)
            outputs = n
        self.layers.append(Layer(inputs, outputs, next_layer))
        self.layers = self.layers[::-1]

    def run(self, inputs):
        '''Compute the MLP's output on a given set of inputs'''
        return reduce(lambda i, l: l.compute(i), self.layers, inputs)

    def train(self, data, epochs=5000, rate=2**-3, show_status=False):
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
                    errors = layer.get_errors()
                    weights = layer.weights
                    layer.train(rate)
                

if __name__ == '__main__':
    ##Example
    ##initialize MLP with eight inputs, a 3-node hidden layer, and eight outputs
    ##like the binary identity example
    mlp = MLP(8, 8, [5])
    
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
    mlp.train(data, show_status=False, rate=.25)

    ##run test inputs
    for s in samples:
        test = mlp.run(s)[0]
        print(s)
        print(test)
        print mlp.layers[0].outputs.get_value()
        print(map(round, test))
        print('')
    
