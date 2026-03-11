"""
DynamoDB Table Setup Script
Run this ONCE to create all required DynamoDB tables for HomeMade Pickles & Snacks.

Usage:
    python aws/dynamodb_setup.py

Prerequisites:
    - AWS credentials set in environment variables or ~/.aws/credentials
    - boto3 installed: pip install boto3
"""

import boto3
import os
import time
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.client(
    "dynamodb",
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)


def create_table(name, key_schema, attribute_definitions):
    """Helper to create a DynamoDB table with PAY_PER_REQUEST billing."""
    try:
        print(f"  Creating table: {name} ...")
        dynamodb.create_table(
            TableName=name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode="PAY_PER_REQUEST",  # No capacity planning needed for academic project
        )
        # Wait until table is active
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=name)
        print(f"  ✅ Table '{name}' is ACTIVE.\n")
    except dynamodb.exceptions.ResourceInExistsException:
        print(f"  ⚠️  Table '{name}' already exists. Skipping.\n")
    except Exception as e:
        print(f"  ❌ Failed to create '{name}': {e}\n")


def setup_all_tables():
    print("\n=== HomeMade Pickles & Snacks – DynamoDB Table Setup ===\n")

    # --- Users Table ---
    create_table(
        name="Users",
        key_schema=[{"AttributeName": "UserID", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "UserID", "AttributeType": "S"}],
    )

    # --- Products Table ---
    create_table(
        name="Products",
        key_schema=[{"AttributeName": "ProductID", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "ProductID", "AttributeType": "S"}],
    )

    # --- Orders Table ---
    create_table(
        name="Orders",
        key_schema=[{"AttributeName": "OrderID", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "OrderID", "AttributeType": "S"}],
    )

    # --- Inventory Table ---
    create_table(
        name="Inventory",
        key_schema=[{"AttributeName": "ProductID", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "ProductID", "AttributeType": "S"}],
    )

    # --- Subscriptions Table ---
    create_table(
        name="Subscriptions",
        key_schema=[{"AttributeName": "SubscriptionID", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "SubscriptionID", "AttributeType": "S"}],
    )

    print("=== All tables created successfully! ===\n")
    print("Next step: Run 'python aws/seed_products.py' to load sample products.\n")


if __name__ == "__main__":
    setup_all_tables()
