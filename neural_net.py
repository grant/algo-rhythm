import theano, numpy, os
import theano.tensor as tensor
import readxml, midi_to_statematrix

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
        self.random = tensor.shared_randomstreams.RandomStreams()
        self.generate_random_weights()
        self.errors = theano.shared(numpy.zeros([1, output_size], 'float32'))
        self.inputs = theano.shared(numpy.zeros([1, input_size], 'float32'))
        self.outputs = theano.shared(numpy.zeros([1, output_size], 'float32'))
        self.output = next_layer == None
        self.generate_theano_functions(next_layer)
        
    def generate_theano_functions(self, next_layer):
        '''Compile necessary theano functions'''
        exp = tensor.fmatrix('expected')
        rate = tensor.fscalar('rate')
        momentum = tensor.fscalar('momentum')

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
                                               name='find_errors',
                                               allow_input_downcast=True)
        else:
            self.find_errors = theano.function([],
                                               updates = [(self.errors,
                                                          self.outputs *
                                                          (1 - self.outputs) *
                                             tensor.dot(next_layer.errors,
                                                        next_layer.weights.T))],
                                           name='find_errors')

        ##Compute the change to the weight vector using stochastic gradient
        ##descent with momentum
        self.train_compute = theano.function([rate, momentum],
                                      updates = [(self.delta_weights,
                                                  self.delta_weights *
                                                  momentum +
                                            theano.tensor.dot(self.inputs.T,
                                                        (rate * self.errors)))],
                                     name='train_compute',
                                     allow_input_downcast=True)

        ##Adjust weights using the delta_w computed in train_compute
        self.adjust = theano.function([], updates=[(self.weights, self.weights +
                                                    self.delta_weights)],
                                      name='adjust')

        ##Drop a number of nodes roughly equal to rate/output_size
        self.dropout = theano.function([rate], updates = [(self.outputs,
                                            tensor.switch(
                                                self.random.binomial(size=(1,
                                                    self.output_size),
                                                    p=rate), self.outputs /
                                                             rate, 0))],
                                       name='dropout',
                                       allow_input_downcast=True)

        
    def generate_random_weights(self):
        """
        Generates a random set of weights by uniformly distributing on
        an interval described at:
        http://deeplearning.net/tutorial/mlp.html#mlp
        """
        weightfunc = theano.function([], self.random.uniform(
                (self.input_size, self.output_size),
                -4 * numpy.sqrt(6. / (self.input_size + self.output_size)),
                4 * numpy.sqrt(6. / (self.input_size + self.output_size))
            ).astype('float32'))
        self.weights = theano.shared(weightfunc())
        self.delta_weights = theano.shared(numpy.zeros([self.input_size,
                                                         self.output_size],
                                                        'float32'))
        
    def compute(self, inputs, dropout=0):
        """
        Pass a set of inputs through the layer's perceptrons, and store
        internally the inputs and outputs for use in training.

        param dropout: percentage of nodes to drop
        """
        self.inputs.set_value(inputs)
        self.get_output()
        if dropout != 0:
            self.dropout(dropout)
        return self.outputs.get_value()

    def train(self, rate, momentum):
        self.train_compute(rate, momentum)
        self.adjust()

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


class RecurrentLayer(Layer):
    """
    A simple LTSM layer of a recurrent neural network.

    A layer takes a certain number of inputs and outputs a certain number of
    outputs, just like a typical feedforward layer, but the most recent outputs
    are stored and used in addition to new inputs when calculating subsequent
    outputs.

    A RecurrentLayer cannot currently be chained with a normal Layer.
    """
    
    def __init__(self, input_size, output_size, next_layer=None):
        Layer.__init__(self, input_size, output_size, next_layer)

    def generate_theano_functions(self, next_layer):
        exp = tensor.fmatrix('expected')
        rate = tensor.fscalar('rate')
        momentum = tensor.fscalar('momentum')
        self.combined_inputs = tensor.concatenate([self.inputs, self.outputs],
                                                  1)
                                             
        ##Compute outputs given inputs
        self.get_output = theano.function([],
                                        updates = [(self.outputs,
                                                    tensor.nnet.sigmoid(
                                                      tensor.dot(
                                                        self.combined_inputs,
                                                        self.weights)))],
                                          name='get_output')


        ##Compute error values given errors of previous layer
        if self.output:
            self.find_errors = theano.function([exp],
                                               updates = [(self.errors,
                                                           self.outputs *
                                                           (1 - self.outputs)
                                                           * exp)],
                                               name='find_errors',
                                               allow_input_downcast=True)
        else:
            self.find_errors = theano.function([],
                updates = [(self.errors,
                            self.outputs * (1 - self.outputs) *
                            tensor.dot(next_layer.errors,
                                    next_layer.weights[:self.output_size].T))],
                            name='find_errors')

        ##Compute the change to the weight vector using stochastic gradient
        ##descent with momentum
        self.train_compute = theano.function([rate, momentum],
                    updates = [(self.delta_weights,
                                self.delta_weights * momentum +
                                    theano.tensor.dot(self.combined_inputs.T,
                                                (rate * self.errors)))],
                                     name='train_compute',
                                     allow_input_downcast=True)

        ##Adjust weights using the delta_w computed in train_compute
        self.adjust = theano.function([], updates=[(self.weights, self.weights +
                                                    self.delta_weights)],
                                      name='adjust')

        ##Drop a number of nodes roughly equal to rate/output_size
        self.dropout = theano.function([rate], updates = [(self.outputs,
                                            tensor.switch(
                                                self.random.binomial(size=(1,
                                                    self.output_size),
                                                    p=rate), self.outputs /
                                                             rate, 0))],
                                       name='dropout',
                                       allow_input_downcast=True)
        

    def generate_random_weights(self):
        """
        Generates a random set of weights by uniformly distributing on
        an interval described at:
        http://deeplearning.net/tutorial/mlp.html#mlp
        """
        weightfunc = theano.function([], self.random.uniform(
                (self.input_size + self.output_size, self.output_size),
                -4 * numpy.sqrt(6. / (self.input_size + self.output_size * 2)),
                4 * numpy.sqrt(6. / (self.input_size + self.output_size * 2))
            ).astype('float32'))
        self.weights = theano.shared(weightfunc())
        self.delta_weights = theano.shared(numpy.zeros([self.input_size +
                                                         self.output_size,
                                                         self.output_size],
                                                        'float32'))
        
    def reset(self):
        """
        Resets the stored output values to zeroes.
        """
        self.outputs.set_value(numpy.zeros([1, self.output_size], 'float32'))
                                          

class MLP:
    '''A simple multi-layered perceprtron'''
    
    def __init__(self, inputs, outputs, layers, recurrent=False):
        """
        Initialize the MLP with random weights.

        param inputs: number of inputs to the first layer
        param layers: list of layer sizes (in nodes), final value is
                      number of outputs
        """
        self.recurrent = recurrent
        if recurrent:
            self.layers = []
            next_layer = RecurrentLayer(layers[-1], outputs)
            self.layers.append(next_layer)
            outputs = layers[-1]
            for n in layers[-2::-1]:
                next_layer = RecurrentLayer(n, outputs, next_layer)
                self.layers.append(next_layer)
                outputs = n
            self.layers.append(RecurrentLayer(inputs, outputs, next_layer))
            self.layers = self.layers[::-1]
        else:
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

    def run(self, inputs, dropout=0):
        '''Compute the MLP's output on a given set of inputs'''
        return reduce(lambda i, l: l.compute(i, dropout), self.layers, inputs)

    def train(self, data, epochs=5000, rate=2**-3, dropout=0, momentum=0,
              show_status=False):
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
                self.layers[-1].get_errors(sub(t, self.run(x,dropout)))
                self.layers[-1].train(rate, momentum)
                for layer in self.layers[-2::-1]:
                    layer.get_errors()
                    layer.train(rate, momentum)

    def save(self, path):
        """
        Save the weights of a network to a folder of npy files
        'RNN' is appended to the path if network is recurrent, but internal
        state is not preserved.
        """
        path = path + 'RNN/' if self.recurrent else path + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        for i in range(len(self.layers)):
            numpy.save(path + str(i),
                        self.layers[i].weights.get_value())

    def reset(self):
        if self.recurrent:
            for l in self.layers:
                l.reset()
        
def load_MLP(path):
    """
    Loads an MLP from a previously saved folder.
    """
    layers = []
    i = 0
    while os.path.exists(path + '/' + str(i) + '.npy'):
        layers.append(numpy.load(path + '/' + str(i) + '.npy'))
        i+=1
    inputs = layers[0].shape[0]
    recurrent = False
    if path[-3:] == 'RNN':
        recurrent = True
        inputs -= layers[0].shape[1]
    outputs = layers[0].shape[1]
    sizes = []
    for l in layers[1:]:
        sizes.append(outputs)
        outputs = l.shape[1]
    mlp = MLP(inputs, outputs, sizes, recurrent)
    for l, w in zip(mlp.layers, layers):
        l.weights.set_value(w)
    return mlp
        
def train_statematrix_net(net, batch_size=100, dropout=.5, output_rate = 100,
                          output_length=100, total_epochs=5000,
                          path = 'net_output/'):
    """
    Trains a neural network, taking time steps from state matrices as input
    and output.
    """
    statematrices = readxml.createStateMatrices()
    batches = []
    for song in statematrices.values():
        matrix = song[1]
        while len(matrix) > 0:
            batch = []
            for i in xrange(batch_size):
                if len(matrix) == 0:
                    break
                batch.append([[n for l in matrix.pop() for n in l]])
            batches.append(zip(batch[:-1], batch[1:]))

    if not os.path.exists(path):
            os.makedirs(path)

    print('\nTraining network:')
    for i in xrange(0, total_epochs, output_rate):
        last = [[0] * 156]
        statematrix = []
        for j in xrange(output_length):
            last = net.run(last)
            statematrix.append(estimate_statematrix_from_output(last[0]))
        midi_to_statematrix.noteStateMatrixToMidi(statematrix,
                                    name=(path + 'example{0}'.format(i)))
        print('\tfile example{0}.mid created'.format(i))
        
        for j in xrange(output_rate):
            print('\t\t' + str(i + j))
            for batch in batches:
                net.reset()
                net.train(batch, 1, .1, dropout, .5)
                
def estimate_statematrix_from_output(output):
    """Given output from the neural net, construct a statematrix"""
    matrix = []
    for i in range(0, 156, 2):
        pair = [round(output[i]), round(output[i+1])]
        if pair in [[1, 1], [1, 0]]:
            matrix.append(pair)
        else:
            matrix.append([0, 0])
    return matrix
    

def binary_example():
    ##Example
    ##initialize MLP with eight inputs, a 3-node hidden layer, and eight outputs
    ##like the binary identity example
    mlp = MLP(8, 8, [4], recurrent=True)
    
    ##train on example data from book
##    samples = [[[.5, -.5, -.5, -.5, -.5, -.5, -.5, -.5]],
##               [[-.5, .5, -.5, -.5, -.5, -.5, -.5, -.5]],
##               [[-.5, -.5, .5, -.5, -.5, -.5, -.5, -.5]],
##               [[-.5, -.5, -.5, .5, -.5, -.5, -.5, -.5]],
##               [[-.5, -.5, -.5, -.5, .5, -.5, -.5, -.5]],
##               [[-.5, -.5, -.5, -.5, -.5, .5, -.5, -.5]],
##               [[-.5, -.5, -.5, -.5, -.5, -.5, .5, -.5]],
##               [[-.5, -.5, -.5, -.5, -.5, -.5, -.5, .5]]]
    samples = [[[1, 0, 0, 0, 0, 0, 0, 0]],
               [[0, 1, 0, 0, 0, 0, 0, 0]],
               [[0, 0, 1, 0, 0, 0, 0, 0]],
               [[0, 0, 0, 1, 0, 0, 0, 0]],
               [[0, 0, 0, 0, 1, 0, 0, 0]],
               [[0, 0, 0, 0, 0, 1, 0, 0]],
               [[0, 0, 0, 0, 0, 0, 1, 0]],
               [[0, 0, 0, 0, 0, 0, 0, 1]]]
    data = zip(samples, samples)
    mlp.train(data, epochs=200, show_status=True)

    ##run test inputs
    for s in samples:
        test = mlp.run(s)[0]
        print(s)
        print(test)
        print mlp.layers[0].outputs.get_value()
        print('')
    mlp.save('testsave')
    mlp2 = load_MLP('testsaveRNN')
    print(mlp.layers[0].weights.get_value())
    print(mlp2.layers[0].weights.get_value())

if __name__ == '__main__':
    net = MLP(156, 156, [512, 512], True)
    train_statematrix_net(net)
    mlp.save('trained_statematrix_net')
