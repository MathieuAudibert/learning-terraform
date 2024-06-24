<<<<<<< HEAD
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
=======
#!/usr/bin/env python

import json
import boto3
import pandas as pd
from pathlib import Path

def get_caller_identity():
    sts_client = boto3.client('sts')
    try:
        res = sts_client.get_caller_identity()
        acc_id = res['Account']
        return acc_id
    except Exception as e:
        print(str(e))
        return None

def get_route_table_id(tgw_id):
    ec2_client = boto3.client('ec2')

    try:
        res = ec2_client.describe_transit_gateway_route_tables(
            Filters=[
                {
                    'Name': 'transit-gateway-id',
                    'Values': [tgw_id]
                }
            ]
        )

        if res['TransitGatewayRouteTables']:
            rte_id = res['TransitGatewayRouteTables'][0]['TransitGatewayRouteTableId']
            return rte_id
        else:
            print('No route table found for the TGW')
            return None
    except Exception as e:
        print(str(e))
        return None

def get_route_tables(tgw_id):
    ec2_client = boto3.client('ec2')

    try:
        rte_id = get_route_table_id(tgw_id)
        if not rte_id:
            return []

        res = ec2_client.search_transit_gateway_routes(
            TransitGatewayRouteTableId=rte_id,
            Filters=[
                {
                    'Name': 'state',
                    'Values': ['active']
                }
            ]
        )

        routes = []
        for route in res.get('Routes', []):
            routes.append({
                'DestinationCidrBlock': route.get('DestinationCidrBlock', ''),
                'TargetType': route.get('TargetType', ''),
                'PrefixList': route.get('PrefixListId', ''),
            })
        return routes

    except Exception as e:
        print(str(e))
        return []

def get_transit_gateways():
    ec2_client = boto3.client('ec2')

    try:
        res = ec2_client.describe_transit_gateways()
        transit_gateways = {}

        for tgw in res.get('TransitGateways', []):
            tgw_id = tgw['TransitGatewayId']
            tgw_details = {
                'Owner': tgw['OwnerId'],
                'State': tgw['State']
            }

            attachments = ec2_client.describe_transit_gateway_attachments(
                Filters=[
                    {
                        'Name': 'transit-gateway-id',
                        'Values': [tgw_id]
                    }
                ]
            )

            attachment_data = []
            for attachment in attachments.get('TransitGatewayAttachments', []):
                attachment_data.append({
                    'AttachmentId': attachment['TransitGatewayAttachmentId'],
                    'ResourceType': attachment['ResourceType'],
                    'Owner': attachment['ResourceOwnerId'],
                    'Routes': get_route_tables(tgw_id)
                })
            tgw_details['Attachments'] = attachment_data
            transit_gateways[tgw_id] = tgw_details

        return transit_gateways

    except Exception as e:
        print(str(e))
        return None

def to_json(data, acc_name):
    folderpath = Path(f'output/{acc_name}')
    folderpath.mkdir(parents=True, exist_ok=True)
    filename = folderpath / f'tgw_output-{acc_name}.json'

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def to_csv(data, acc_name):
    try:
        rows = []

        for tgw_id, tgw_details in data.items():
            for attachment in tgw_details['Attachments']:
                for route in attachment['Routes']:
                    rows.append({
                        'TGW ID': tgw_id,
                        'Owner': tgw_details['Owner'],
                        'State': tgw_details['State'],
                        'Attachment ID': attachment['AttachmentId'],
                        'Resource Type': attachment['ResourceType'],
                        'Attachment Owner': attachment['Owner'],
                        'Destination CIDR': route['DestinationCidrBlock'],
                        'Target Type': route['TargetType'],
                        'Prefix List': route['PrefixList']
                    })

        df = pd.DataFrame(rows)
        folderpath = Path(f'output/{acc_name}')
        folderpath.mkdir(parents=True, exist_ok=True)

        filename = folderpath / f'tgw_output-{acc_name}.csv'
        try:
            df.to_csv(filename, index=False)
        except Exception as e:
            print(str(e))

    except Exception as e:
        print(str(e))
        return None

#--------------------------------------------------------------------------
# Generate doc and outputs

def read_json_file(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def generate_markdown(json_data, output_md_path):
    md_content = f"""
# Reporting blablabla

# Routing
"""
    for tgw_id, tgw_details in json_data.items():
        md_content += f"\n ## TGW ID: {tgw_id}\n"
        md_content += f"**Owner:** {tgw_details['Owner']} | **State:** {tgw_details['State']}\n \n"
        for attachment in tgw_details['Attachments']:
            md_content += f"### Attachment ID: {attachment['AttachmentId']} | Resource Type: {attachment['ResourceType']} | Owner: {attachment['Owner']}\n"
            md_content += f"| Destination CIDR | Target Type | Prefix List |\n"
            md_content += f"| --- | --- | --- |\n"
            for route in attachment.get('Routes', []):
                md_content += f"| {route['DestinationCidrBlock']} | {route['TargetType']} | {route['PrefixList']} |\n"
            md_content += "\n"

    with open(output_md_path, 'w') as f:
        f.write(md_content)

def main():
    try:
        botoSession = boto3.Session()
        region = botoSession.region_name
        acc_id = get_caller_identity()
        print(acc_id, region)
        transit_gateways = get_transit_gateways()

        tgw_res = True
        to_json_res = True
        to_csv_res = True

        if transit_gateways:
            acc_name = botoSession.profile_name
            print("\n TGW OK \n")

            try:
                to_json(transit_gateways, acc_name)
                print("\n TO JSON OK \n")
            except Exception as e:
                print("TO JSON KO")
                to_json_res = False

            try:
                to_csv(transit_gateways, acc_name)
                print("\n TO CSV OK \n")
            except Exception as e:
                print("TO CSV KO")
                to_csv_res = False

            script_dir = Path(__file__).parent.resolve()
            output_dir = script_dir / 'output'

            json_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.json'
            csv_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.csv'
            output_md_path = output_dir / f'{acc_name}/tgw_output-{acc_name}.md'

            if not json_path.exists():
                print(f"No JSON file: {json_path}")
                return

            if not csv_path.exists():
                print(f"No CSV file: {csv_path}")
                return

            json_data = read_json_file(json_path)
            generate_markdown(json_data, output_md_path)

        else:
            print("TGW KO")
            tgw_res = False

        if tgw_res and to_json_res and to_csv_res:
            print("\n Reporting OK \n")

    except Exception as e:
        print("Reporting KO", " ", str(e))

if __name__ == '__main__':
    main()
>>>>>>> b3d4dac1347ea166ba7d251f4954ab6d289f7831
