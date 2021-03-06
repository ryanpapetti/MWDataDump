# Modern Warfare Periodic Data Dump with AWS
## Ryan Papetti
## V 0.01

This repository contains a script that is meant to be packaged and delivered to AWS Lambda to periodically collect Call of Duty Modern Warfare data via their RapidAPI interface. 


`lambda_function.py` is the only script required and contains code to contact RAPIDAPI endpoint, gather data, and dump it to an appropriate S3 bucket and DynamoDB table. 

### To deploy to AWS successfully:

1. Get your `API-KEY` from RapidAPI by making an account. As of this writing, the Call of Duty Modern Warfare API is *free* to use. 

2. Create an AWS Lambda function with *at least* Python 3.6. Set any relevant tags or descriptions for you. Upload the `lambda_function.py` script to the function.

3. Create a DynamoDB table to store match data. Ensure the table is ***in the same region as your Lambda function.*** Save the table name.

4. Create an S3 Bucket ***in the same region as your Lambda function.*** Save the Bucket ARN.

5. Create a Rule on Amazon EventBridge ***in the same region as your Lambda function.*** The recommended event schedule is `rate(6 hours)` for running every, you guessed it, six hours. Add the rule as a trigger to the function.

6. Set the following Environment Variables in the Lambda function: 

    - `API_KEY`: set to the RapidAPI key you receive
    - `MWDynamoTable`: set to the name of a DynamoDB table you created
    - `MWBucketARN`: set to the ARN of the bucket where you'd like to dump data


7. Configure a blank test event (literally `"{}"`) to be able to test the script. The reason the test event can be blank here is that the function does not perform any actions with data from the event. 

8. If you see `"Execution result: succeeded"`, then the function sucessfully ran and dumped data. Congrats!



### Common API Issues

- `{'message': 'You are not subscribed to this API.'}` - got this multiple times when using an invalid API key. Check the key that is stored in your Environment Variables

- `{'error': True, 'message': '404 - Not found. Incorrect username or platform? Misconfigured privacy settings?'}` - more often than not, this is due to using an *incorrect* gamertag for the associated platform. I personally resolved this using my Activision ID.

