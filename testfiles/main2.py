import unittest
from unittest.mock import patch, MagicMock
from your_script import get_caller_identity, get_route_table_id, get_route_tables, get_transit_gateways, to_json, to_csv
import json
import pandas as pd
from pathlib import Path

class TestTGWScripts(unittest.TestCase):

    @patch('boto3.client')
    def test_get_caller_identity(self, mock_boto_client):
        mock_sts_client = MagicMock()
        mock_boto_client.return_value = mock_sts_client
        mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}

        account_id = get_caller_identity()
        self.assertEqual(account_id, '123456789012')
        mock_sts_client.get_caller_identity.assert_called_once()

    @patch('boto3.client')
    def test_get_route_table_id(self, mock_boto_client):
        mock_ec2_client = MagicMock()
        mock_boto_client.return_value = mock_ec2_client
        mock_ec2_client.describe_transit_gateway_route_tables.return_value = {
            'TransitGatewayRouteTables': [{'TransitGatewayRouteTableId': 'tgw-rtb-0123456789abcdef0'}]
        }

        route_table_id = get_route_table_id('tgw-0123456789abcdef0')
        self.assertEqual(route_table_id, 'tgw-rtb-0123456789abcdef0')
        mock_ec2_client.describe_transit_gateway_route_tables.assert_called_once()

    @patch('boto3.client')
    def test_get_route_tables(self, mock_boto_client):
        mock_ec2_client = MagicMock()
        mock_boto_client.return_value = mock_ec2_client
        mock_ec2_client.search_transit_gateway_routes.return_value = {
            'Routes': [
                {'DestinationCidrBlock': '10.0.0.0/16', 'TargetType': 'vpc', 'PrefixListId': 'pl-0123456789abcdef0'}
            ]
        }

        routes = get_route_tables('tgw-rtb-0123456789abcdef0')
        expected_routes = [{
            'DestinationCidrBlock': '10.0.0.0/16',
            'TargetType': 'vpc',
            'PrefixList': 'pl-0123456789abcdef0'
        }]
        self.assertEqual(routes, expected_routes)
        mock_ec2_client.search_transit_gateway_routes.assert_called_once()

    @patch('boto3.client')
    def test_get_transit_gateways(self, mock_boto_client):
        mock_ec2_client = MagicMock()
        mock_boto_client.return_value = mock_ec2_client
        mock_ec2_client.describe_transit_gateways.return_value = {
            'TransitGateways': [{'TransitGatewayId': 'tgw-0123456789abcdef0', 'OwnerId': '123456789012', 'State': 'available'}]
        }
        mock_ec2_client.describe_transit_gateway_attachments.return_value = {
            'TransitGatewayAttachments': [{'TransitGatewayAttachmentId': 'tgw-attach-0123456789abcdef0', 'ResourceType': 'vpc', 'ResourceOwnerId': '123456789012'}]
        }
        mock_ec2_client.describe_transit_gateway_route_tables.return_value = {
            'TransitGatewayRouteTables': [{'TransitGatewayRouteTableId': 'tgw-rtb-0123456789abcdef0'}]
        }
        mock_ec2_client.search_transit_gateway_routes.return_value = {
            'Routes': [
                {'DestinationCidrBlock': '10.0.0.0/16', 'TargetType': 'vpc', 'PrefixListId': 'pl-0123456789abcdef0'}
            ]
        }

        transit_gateways = get_transit_gateways()
        expected_transit_gateways = {
            'tgw-0123456789abcdef0': {
                'Owner': '123456789012',
                'State': 'available',
                'Attachments': [{
                    'AttachmentId': 'tgw-attach-0123456789abcdef0',
                    'ResourceType': 'vpc',
                    'Owner': '123456789012',
                    'Routes': [{
                        'DestinationCidrBlock': '10.0.0.0/16',
                        'TargetType': 'vpc',
                        'PrefixList': 'pl-0123456789abcdef0'
                    }]
                }]
            }
        }
        self.assertEqual(transit_gateways, expected_transit_gateways)

    def test_to_json(self):
        data = {'key': 'value'}
        acc_name = 'test_account'
        to_json(data, acc_name)
        expected_path = Path(f'output/{acc_name}/tgw_output-{acc_name}.json')
        self.assertTrue(expected_path.exists())

        with open(expected_path, 'r') as f:
            content = json.load(f)
        self.assertEqual(content, data)

    def test_to_csv(self):
        data = {
            'tgw-0123456789abcdef0': {
                'Owner': '123456789012',
                'State': 'available',
                'Attachments': [{
                    'AttachmentId': 'tgw-attach-0123456789abcdef0',
                    'ResourceType': 'vpc',
                    'Owner': '123456789012',
                    'Routes': [{
                        'DestinationCidrBlock': '10.0.0.0/16',
                        'TargetType': 'vpc',
                        'PrefixList': 'pl-0123456789abcdef0'
                    }]
                }]
            }
        }
        acc_name = 'test_account'
        to_csv(data, acc_name)
        expected_path = Path(f'output/{acc_name}/tgw_output-{acc_name}.csv')
        self.assertTrue(expected_path.exists())

        df = pd.read_csv(expected_path)
        self.assertEqual(df.shape[0], 1)  # Check that one row is present in the CSV
        self.assertEqual(df.iloc[0]['Destination CIDR'], '10.0.0.0/16')

if __name__ == '__main__':
    unittest.main()
