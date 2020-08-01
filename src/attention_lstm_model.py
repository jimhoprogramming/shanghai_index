# -*- coding: utf-8 -*-
import mxnet as mx

'''
### for keras code using class fuction ###
repeator = RepeatVector(Tx)
concatenator = Concatenate(axis=-1)
densor1 = Dense(10, activation = "tanh")
densor2 = Dense(1, activation = "relu")
activator = Activation(softmax, name='attention_weights') # We are using a custom softmax(axis = 1) loaded in this notebook
dotor = Dot(axes = 1)
'''
T_x = 10

def one_step_attention(attention_model_obj, a, s_prev, Tx):

    # Use repeator to repeat s_prev to be of shape (m, Tx, n_s) so that you can concatenate it with all hidden states "a" (≈ 1 line)
    s_prev = mx.ndarray.expand_dims(data = s_prev, axis = 1)
    #print(s_prev.shape)
    s_prev = mx.ndarray.broadcast_axis(data = s_prev, axis = 1, size = Tx)
    #print(s_prev.shape) 
    concat = mx.ndarray.concat(a, s_prev, dim = -1)
    print('concat shape = {}'.format(concat.shape))
    # Use densor1 to propagate concat through a small fully-connected neural network to compute the "intermediate energies" variable e. (≈1 lines)
    energies = attention_model_obj(concat)
    alphas = mx.ndarray.softmax(energies)
    # Use dotor together with "alphas" and "a" to compute the context vector to be given to the next (post-attention) LSTM-cell (≈ 1 line
    print('a.shape = {}'.format(a.shape))
    print('alpha.shape = {}'.format(alphas.shape))
    #context = mx.ndarray.dot(alphas, a, transpose_a = True)
    context = (alphas * a).sum(axis = 1)
    return context

def attention_model(attention_size, n_c):
    model = mx.gluon.nn.Sequential()
    model.add(mx.gluon.nn.Dense(attention_size, activation='tanh', use_bias=False, flatten=False))
    model.add(mx.gluon.nn.Dense(n_c, use_bias=False, flatten=False))
    return model
   
##n_a = 32
##n_s = 64
##post_activation_LSTM_cell = LSTM(n_s, return_state = True)
##output_layer = Dense(len(machine_vocab), activation=softmax)

def model(X, m_size, attention_size, Tx, Ty, n_a, n_s, human_vocab_size, machine_vocab_size):
    """
    Arguments:
    Tx -- length of the input sequence
    Ty -- length of the output sequence
    n_a -- hidden state size of the Bi-LSTM
    n_s -- hidden state size of the post-attention LSTM
    human_vocab_size -- size of the python dictionary "human_vocab"
    machine_vocab_size -- size of the python dictionary "machine_vocab"

    Returns:
    model -- Keras model instance
    """
    # define model
    model = nn.HybridSequential()
    
    # init attention model
    attention_model_obj = attention_model(attention_size = attention_size, n_c = n_a)
    attention_model_obj.initialize()    
    
    # Define the inputs of your model with a shape (Tx,)
    # Define s0 and c0, initial hidden state for the decoder LSTM of shape (n_s,)
    # X = Input(shape=(Tx, human_vocab_size))
    #s0 = Input(shape=(n_s,), name='s0')
    #c0 = Input(shape=(n_s,), name='c0')
    c0 = mx.ndarray.zeros((m_size, Tx, n_a))
    s0 = mx.ndarray.zeros((m_size, n_a))
    s = s0
    c = c0
    
    # Initialize empty list of outputs
    outputs = []
    
    # Step 1: Define your pre-attention Bi-LSTM. Remember to use return_sequences=True. (≈ 1 line)
##    a = Bidirectional(LSTM(n_a, return_sequences=True))(X)
    model.add(mx.gluon.rnn.LSTM(hidden_size = n_a, layout = 'NTC', bidirectional = True))
    
    
    # Step 2: Iterate for Ty steps
    for t in range(Ty):
    
        # Step 2.A: Perform one step of the attention mechanism to get back the context vector at step t (≈ 1 line)
        #context = one_step_attention(a, s)
        context = one_step_attention(attention_model_obj = attention_model_obj, a = a, s_prev = s, Tx = Tx)
        
        # Step 2.B: Apply the post-attention LSTM cell to the "context" vector.
        # Don't forget to pass: initial_state = [hidden state, cell state] (≈ 1 line)
        # s, _, c = post_activation_LSTM_cell(context, initial_state = [s,c])
        s, _, c = LSTM(n_s, return_state = True)(context, initial_state = [s,c])
        
        # Step 2.C: Apply Dense layer to the hidden state output of the post-attention LSTM (≈ 1 line)
        #out = output_layer(s)
        out = Dense(len(machine_vocab), activation=softmax)(s)
        # Step 2.D: Append "out" to the "outputs" list (≈ 1 line)
        outputs.append(out)
    
    # Step 3: Create model instance taking three inputs and returning the list of outputs. (≈ 1 line)
    #model = Model(inputs=[X, s0, c0], outputs=outputs)
    
    return outputs


def test_attention():
    seq_len, batch_size, num_hiddens = 10, 4, 8
    model = attention_model(attention_size = 10, n_c = 8)
    model.initialize()
    a0 = mx.ndarray.zeros((batch_size, seq_len, num_hiddens))
    s0 = mx.ndarray.zeros((batch_size, num_hiddens))
    c = one_step_attention(model, a = a0, s_prev = s0, Tx = seq_len)
    print(c.shape)

def test_model():
    seq_len, batch_size, num_hiddens = 10, 4, 8
    X = mx.ndarray.zeros((batch_size , seq_len, num_hiddens))    
    model_obj = model(X = X, m_size = 10, attention_size = 10, Tx = 4, Ty = 4, n_a = 8, n_s = 8, human_vocab_size = 100, machine_vocab_size = 200)

if __name__ == '__main__':
    # test_attention()
    test_model()
