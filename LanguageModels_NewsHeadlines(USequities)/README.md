##### Benefits of Charac2vec:
- Having the character embedding, every single word’s vector can be formed even it is out-of-vocabulary words (optional). On the other hand, word embedding can only handle those seen words.
- Good fits for misspelling words
- handles infrequent words better than word2vec embedding as later one suffers from lack of enough training opportunity for those rare words
- Reduces model complexity and improving the performance (in terms of speed)

##### Byte Level:
- When ASCII encoding is used, there is no difference between reading characters or bytes. The ASCII-way of encoding characters allows for 256 characters to be encoded and (surprise…) these 256 possible characters are stored as bytes.
4. Train Language Model and save embeddings representation and weights of the model.
5. Use weights and embeddings representation of language model to intialize new model that predict price direction movement, ultimaetly.
- Direction prediction correctness(DPC) will be used as final metric to evaluate on test data.