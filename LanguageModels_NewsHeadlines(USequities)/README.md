# RNN-NLP Applications
- Motivation: Character Level language model ( 2 methods of encoding) to regenerate/reproduce news headlines to learn embeddings and LSTM weights 
              in order to transfer its learning to classification models that aim to predict stock price direction from news headlines.
- Models, model training notebooks, dbs and certain files are not provided. Only proof of concept from idea formulation and data fetching to deployment and mean of use.

 
## Benefits of Charac2vec:
- Having the character embedding, every single word’s vector can be formed even it is out-of-vocabulary words (optional). On the other hand, word embedding can only handle those seen words.
- Good fits for misspelling words
- handles infrequent words better than word2vec embedding as later one suffers from lack of enough training opportunity for those rare words
- Reduces model complexity and improving the performance (in terms of speed)

## Byte Level:
- When ASCII encoding is used, there is no difference between reading characters or bytes. The ASCII-way of encoding characters allows for 256 characters to be encoded and (surprise…) these 256 possible characters are stored as bytes.
4. Train Language Model and save embeddings representation and weights of the model.
5. Use weights and embeddings representation of language model to intialize new model that predict price direction movement, ultimaetly.
- Direction prediction correctness(DPC) will be used as final metric to evaluate on test data.

## Tips for LSTM Inputs
- The LSTM input layer must be 3D.
- The meaning of the 3 input dimensions are: samples, time steps, and features (sequences, sequence_length, characters).
- The LSTM input layer is defined by the input_shape argument on the first hidden layer.
- The input_shape argument takes a tuple of two values that define the number of time steps and features.
- The number of samples is assumed to be 1 or more.
- The reshape() function on NumPy arrays can be used to reshape your 1D or 2D data to be 3D.
- The reshape() function takes a tuple as an argument that defines the new shape
- The LSTM return the entire sequence of outputs for each sample (one vector per timestep per sample), if you set return_sequences=True.
- Stateful RNN only makes sense if each input sequence in a batch starts exactly where the corresponding sequence in the previous batch left off. Our RNN model is stateless since each sample is different from the other and they dont form a text corpus but are separate headlines.

## Tips for Embedding Layer
- Gives relationship between characters.
- Dense vector representation (n-Dimensional) of float point values. Map(char/byte) to a dense vector.
- Embeddings are trainable weights/paramaeters by the model equivalent to weights learned by dense layer.
- In our case each unique character/byte is represented with an N-Dimensional vector of floating point values, where the learned embedding forms a lookup table by "looking up" each characters dense vector in the table to encode it.
- A simple integer encoding of our characters is not efficient for the model to interpret since a linear classifier only learns the weights for a single feature but not the relationship (probability distribution) between each feature(characters) or there encodings.
- A higher dimensional embedding can capture fine-grained relationships between characters, but takes more data to learn.(256-Dimensions our case)

## Logits Predicting Log-Likelihood from Ouput Layer:
For each character/byte the model looks up the embedding, runs the LSTM one timestep with the embedding as input, and applies the dense layer to generate logits predicting the log-likelihood of the next character/Byte. This distribution, for each predicted character/byte, is defined by the logits over the characters(i.e 1-127 Decimal Points bytes). Second way is to just encode all characters to UTF-8 covering greater variety of language and character symbols up too 4 bytes per character.
