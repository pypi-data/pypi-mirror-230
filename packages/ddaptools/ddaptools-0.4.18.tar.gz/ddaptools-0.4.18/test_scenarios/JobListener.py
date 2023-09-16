import boto3
from ddaptools.aws_classes.class_enhancement import *
from ddaptools.dda_constants import *

sqs = boto3.client('sqs')

# Define the URL of your SQS queue
queue_url = 'https://sqs.us-east-1.amazonaws.com/796522278827/MockQueue.fifo'



def processFromJobParameter(job_parameters):
    
    organizationDBProvider = MockOrganizationQuerier

    
    credentials = {
        'USERNAME': "postgres",
        'PASSWORD': "dDueller123araM=!",
        "HOST": "test-ddanalytics-rds-v2.cpcwi20k2qgg.us-east-1.rds.amazonaws.com",
        "DB": "v1_2"
    }

    settings = {
        "GET_TABLENAME": "staging_events",
        "TABLENAME_EVENTS": "event",
        "COLUMN_NAMES_EVENTS": Event.get_attribute_keys(),
        "TABLENAME_TIMESLOTS": "timeslot",
        "COLUMN_NAMES_TIMESLOTS": Timeslot.get_attribute_keys()
    }
    publishingDBProvider = PostgreSQLProviderTimeSlotPlusEventsPublishing(credentials=credentials, settings=settings)

    processor = ConnecToGUIDHarcodedDictBasedCommonProcessor(
        job_parameters=job_parameters,
        organization_provider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider
    ) 
    processor.runJobs() # Should also post at the Mock Database


# Receive and process SQS messages
def process_messages():
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,  # Maximum number of messages to retrieve
            WaitTimeSeconds=5  # Wait time for new messages in the queue
        )
        
        if 'Messages' in response:
            for message in response['Messages']:
                # And here you should start calling it => Making sure that the received message is a valid job => Having the received message as a dict.
                # Then what you want to to do is that once you receive the message, then you want to have the max number of messages here.

                job_parameter =  {"guid": message['Body'] }
                # print("Job parameter created: ", job_parameter, " from message: ", job_parameter[EVENT_GUID])
                processFromJobParameter(job_parameter)

                # Delete then the message from the queue.     
                # Delete the message from the queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
        else:
            print('No messages in the queue.')


# Call the function to start processing messages
process_messages()
