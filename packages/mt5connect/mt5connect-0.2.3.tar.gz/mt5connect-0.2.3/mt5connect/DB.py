import boto3
from boto3.dynamodb.types import TypeDeserializer


class DB:
    def __init__(self, table_name, region_name):
        self.dynamodb = boto3.client("dynamodb", region_name=region_name)
        self.table_name = table_name

    # ==================================================================================== #
    #                                DB Functions                                      #
    # ==================================================================================== #
    def get_DB_settings_for_user(self, user_id):
        # Define the key of the item you want to retrieve
        key = {"user": {"S": user_id}}

        # Retrieve the item from the DynamoDB table
        response = self.dynamodb.get_item(TableName=self.table_name, Key=key)

        # Check if the item exists in the response
        if "Item" in response:
            item = response["Item"]
            json_item = {
                key: TypeDeserializer().deserialize(value)
                for key, value in item.items()
            }
            return json_item["conf"]
        else:
            print(f"User with ID {user_id} not found.")

    def update_db_status(self):
        # Define the new status dictionary
        status_data = {
            "initialized": {"BOOL": self.status["initialized"]},
            "logged_in": {"BOOL": self.status["logged_in"]},
            "ea_trade_allowed": {"BOOL": self.status["ea_trade_allowed"]},
            "account_info": {"S": str(self.status["account_info"]["login"])},
            "dwx_attached": {"BOOL": self.status["dwx_attached"]},
        }

        # Update the item in DynamoDB
        response = self.dynamodb.update_item(
            TableName=self.table_name,
            Key={"user": {"S": self.conf["user"]}},
            UpdateExpression="SET #mt5_status = :mt5_status",
            ExpressionAttributeNames={"#mt5_status": "mt5_status"},
            ExpressionAttributeValues={":mt5_status": {"M": status_data}},
        )
