import boto3

def get_dynamodb_resource():
    """
    Returns a boto3 DynamoDB resource connected to the Mumbai region.
    """
    return boto3.resource(
        "dynamodb",
        region_name="ap-south-1"
    )


def get_table(table_name):
    """Returns a specific DynamoDB table by name."""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)