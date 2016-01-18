import theano
import numpy

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

        inputs = theano.tensor.dmatrix('inputs')
        outputs = theano.tensor.nnet.sigmoid(theano.tensor.dot(inputs,
                                                               self.weights))
        self.compute = theano.function([inputs], outputs)
        
    def generate_random_weights(self):
        """
        Generates a random set of weights by uniformly distributing on
        an interval described at:
        http://deeplearning.net/tutorial/mlp.html#mlp
        """
        random = theano.tensor.shared_randomstreams.RandomStreams()
        weightfunc = theano.function([], random.uniform(
            (self.input_size, self.output_size),
            -4 * numpy.sqrt(6. / (self.input_size + self.output_size)),
            4 * numpy.sqrt(6. / (self.input_size + self.output_size))))
        self.weights = theano.shared(weightfunc(), name='weights', borrow=True)

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

if __name__ == '__main__':
    ##Example
    ##initialize MLP with eight inputs, a 3-node hidden layer, and eight outputs
    ##like the binary identity example
    mlp = MLP(8, [3, 8])
    ##feed it some arbitrary inputs and print results
    ##note that learning isn't implemented yet, so weights are all random, and
    ##these outputs don't mean anything
    print(mlp.run([[1, 0, 0, 0, 1, 1, 0, 1]]))
    print(mlp.run([[1, 0, 1, 0, 1, 1, 0, 0]]))
    print(mlp.run([[0, 0, 0, 0, 0, 0, 0, 0]]))
    print(mlp.run([[1, 1, 1, 1, 1, 1, 1, 1]]))
    
