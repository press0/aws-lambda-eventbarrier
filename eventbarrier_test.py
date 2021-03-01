import unittest.mock

import botocore.session
from botocore.stub import Stubber

import eventbarrier as lambda_function


def s3_client_stubs(s3bucket_name, object_keys: list):
    get_head_response = {}

    s3_client = botocore.session.get_session().create_client('s3')
    stubber = Stubber(s3_client)

    for object_key in object_keys:
        expected_params = {
            "Bucket": s3bucket_name,
            "Key": object_key
        }
        stubber.add_response('head_object', get_head_response, expected_params)

    stubber.add_client_error('head_object',
                             service_error_code='NoSuchObject',
                             service_message='The specified object does not exist.',
                             http_status_code=400,
                             service_error_meta=None,
                             expected_params=None,
                             response_meta=None)
    stubber.activate()
    return s3_client


def s3_client_stub(s3bucket_name, object_key):
    get_head_response = {}
    expected_params = {
        "Bucket": s3bucket_name,
        "Key": object_key
    }
    s3_client = botocore.session.get_session().create_client('s3')
    stubber = Stubber(s3_client)
    stubber.add_response('head_object', get_head_response, expected_params)
    stubber.add_client_error('head_object',
                             service_error_code='NoSuchObject',
                             service_message='The specified object does not exist.',
                             http_status_code=400,
                             service_error_meta=None,
                             expected_params=None,
                             response_meta=None)
    stubber.activate()
    return s3_client


def get_object_key_from_event():
    return event['Records'][0]['s3']['object']['key']


s3bucket_name = 'eventbarrier'
context = {'requestid': '1234'}
event = \
    {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "example-bucket"
                    },
                    "object": {
                        "key": "2/0/file1.txt",
                    }
                }
            }
        ]
    }


class Test(unittest.TestCase):

    def test_s3_stub(self):
        # assemble
        object_key = get_object_key_from_event()
        expected_params = {
            "Bucket": s3bucket_name,
            "Key": object_key
        }
        s3_client = s3_client_stub(s3bucket_name, object_key)

        # act
        response = s3_client.head_object(Bucket=s3bucket_name, Key=object_key)

        # assert
        assert response == {}
        try:
            response = s3_client.head_object(Bucket=s3bucket_name, Key=object_key)
        except Exception as e:
            print(e)
        print(response)

    def test_eventbarrier_when_all_files_exist(self):
        # assemble
        s3_target_object_keys = ["2/0/file1.txt", "2/1/file1.txt", "2/2/file1.txt"]
        s3_client = s3_client_stubs(s3bucket_name, s3_target_object_keys)

        # act
        lambda_function.set_s3_client(s3_client)
        result = lambda_function.lambda_handler(event, context)

        # assert
        assert result

    def test_eventbarrier_when_last_file_does_not_exist(self):
        # assemble
        s3_target_object_keys = ["2/0/file1.txt", "2/1/file1.txt", "2/2/file1.txt"]
        s3_target_object_keys.pop()
        s3_client = s3_client_stubs(s3bucket_name, s3_target_object_keys)

        # act
        lambda_function.set_s3_client(s3_client)
        result = lambda_function.lambda_handler(event, context)

        # assert
        assert not result


if __name__ == '__main__':
    unittest.main()
