# FineTuning an LLM vs LM (Bi-LSTM 10 million params)

OpenAI Released the following tool, whoch I previously have worked around a year ago in this sub directory. Feel free to check the steps
and then compare to a lesser low code implementation.

### How to Evaluate a Sentiment Analysis Model in OpenAI Evals
OpenAI provides tools to run evaluations on test datasets to ensure accurate model outputs. This tool helps you identify issues early, ensuring the model is reliable and performs consistently in real-world use.

Here’s how to evaluate a sentiment analysis model using the IMDB test dataset:


Step 1
Sign in to the OpenAI dashboard.

Step 2
In the dashboard, click “Create Evaluations” and select “Data Source.” Import your dataset from a JSONL or CSV file.

Step 3

Next, copy and paste the following text to add System Prompt and User response. 

System Message 
You are an expert in analyzing the sentiment of movie reviews. 
- If the moview review id positive, you will output a 1
- If the movie review is negative, you will output a 0
-Only output 1 or 0 as a response - do not output any other text

User 
Analyze this review: 


Step 4
Create evaluation criteria. Click “Add” and select “String Check” to verify if the model's output matches the label. Set "Check if" to and "Equals". Set the reference output .

Step 5
Click “Test Evaluation” to run the evaluation on the first row of the dataset.

Step 6
Click “Run” to execute the evaluation.

Step 7
Click “Report” to view results.

Step 8
Click “Add Run” to change the model or prompt if needed.
