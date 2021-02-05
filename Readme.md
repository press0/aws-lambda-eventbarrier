


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#Introduction">Introduction</a></li>
     <li><a href="#prerequisites">Prerequisites</a></li>
     <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



## Introduction


Barriers and Latches are synchronisation mechanisms that enable 
a dependent thread to wait upon independent events. 


* C++: std::barrier, std::latch
* Java: [CyclicBarrier](https://docs.oracle.com/en/java/javase/15/docs/api/java.base/java/util/concurrent/CyclicBarrier.html), [CountDownLatch](https://docs.oracle.com/en/java/javase/15/docs/api/java.base/java/util/concurrent/CountDownLatch.html)

Lambda functions depend on independent events too.

This project implements a generic Event Barrier as an AWS Lambda function.
The Lambda function waits until all independent events have arrived.
AWS S3 is used for state management.


These AWS services are configured and deployed from the command line 

* [AWS Lambda](https://aws.amazon.com/lambda/)
* [AWS S3](https://aws.amazon.com/s3/)
* [AWS IAM](https://aws.amazon.com/iam/)
* [AWS CloudWatch](https://aws.amazon.com/cloudwatch/)


## Prerequisites

Python, an AWS account, and the AWS CLI are needed to run this project.

## Installation

1. Clone the repo
   ```sh
   git clone https://github.com/press0/aws-eventbarrier.git
   ```

2. create a virtual environment
   ```sh
   python -m venv venv
   ```
2. install requirements
   ```sh
   python -m pip install -r requirements.txt
   ```
3. define event barriers in a configuration file.  
   ```json
   {
        "event-barrier-0": [
            "0/0",
            "0/1"
        ],
        "event-barrier-1": [
            "1/0",
            "1/1"
        ],
        "event-barrier-2": [
            "2/0",
            "2/1",
            "2/2"
        ]
   }

4. Unit tests. Verify the lambda function logic and validate your event barrier configuration 
   ```sh
   python -m pip pytest
   ```
5. build the lambda function zip file
   ```sh
   zip function.zip eventbarrier.py eventbarrier.json 
   ```

6. create the lambda function.  Replace the 12 hash characters with your AWS account number.

   ```sh
   aws lambda create-function --function-name eventbarrier \
         --runtime python3.8 \
         --zip-file fileb://function.zip \
         --handler eventbarrier.lambda_handler \
         --role arn:aws:iam::############:role/eventbarrier 
   ```
7. update lambda function code as needed
   ```sh
   aws lambda update-function-code \
         --function-name eventbarrier \
         --zip-file fileb://function.zip
   ```

8. create an S3 bucket and a prefix
   ```sh
   aws s3 rb s3://eventbarrier
   

   ```
9. create an IAM policy with minimum required permissions
   ```json

   {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:s3:::eventbarrier/*",
                "arn:aws:logs:*:*:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::eventbarrier"
        }
    ]
   }
   ```

10. create an IAM role
   ```sh
   aws iam create-role --role-name eventbarrier --assume-role-policy-document file://eventbarrier-policy.json

   ```
11. create an event notification binding S3 create events to the lambda function
    the notification can be creates 2 ways:
    - manually: s3 console > bucket properties tab > create event event notification
    - aws cli
```sh
    aws s3api put-bucket-notification-configuration \
        --bucket eventbarrier 
        --notification-configuration file://notification.json
   ```
   with notification.json like:

   ```json
       {
         "TopicConfigurations": [
            {
               "TopicArn": "arn:aws:sns:us-west-2:123456789012:s3-notification-topic",
               "Events": [
                  "s3:ObjectCreated:*"
               ]
            }
         ]
      }

   ```


12. AWS Lambda event barrier integration testing. 
    The following commands upload test files to the respective prefixes of each event barrier.
    The log file verifies the Event Barrier condition. 
   ```sh


   ```

#### Usage



#### Roadmap

See the [open issues](https://github.com/press0/aws-lambda-eventbarrier/issues) for a list of proposed features (and known issues).


#### Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
#### License

Distributed under the MIT License. See `LICENSE` for more information.




<!-- ACKNOWLEDGEMENTS -->
#### Acknowledgements

