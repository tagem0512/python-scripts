


import boto3
from prettytable import PrettyTable

def check_imdsv2_mode(instance_id, instance_name, region_name):
    ec2_client = boto3.client('ec2', region_name=region_name)

    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        # Check for IMDSv2 mode
        imdsv2_state = instance.get('MetadataOptions', {}).get('HttpTokens', 'unknown')

        return instance_name, imdsv2_state

    except Exception as e:
        print(f"Error checking IMDSv2 mode for instance {instance_id}: {e}")
        return instance_name, 'error'




def main():
    ec2 = boto3.client('ec2')
    all_regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    
    print("Available AWS regions:")
    for idx, region in enumerate(all_regions, start=1):
        print(f"{idx}. {region}")

    selected_region = None
    while selected_region is None:
        try:
            region_choice = input("Enter the number of the region (Press Enter for default 'us-east-1'): ")

            if region_choice.strip() == "":
                selected_region = 'us-east-1'
            else:
                region_choice = int(region_choice)
                if 1 <= region_choice <= len(all_regions):
                    selected_region = all_regions[region_choice - 1]
                else:
                    print("Invalid region number. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    table = PrettyTable()
    table.field_names = ["Region", "Instance Name", "Instance ID", "IMDSv2 Mode"]

    ec2_client = boto3.client('ec2', region_name=selected_region)
    try:
        # Retrieve all EC2 instances for the selected region
        response = ec2_client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_name = next((tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'), '')
                imdsv2_mode = check_imdsv2_mode(instance_id, instance_name, selected_region)

                imdsv2_display = {
                    'required': 'Required',
                    'optional': 'Optional',
                    'unknown': 'unknown',
                    'error': 'error'
                }

                table.add_row([selected_region, imdsv2_mode[0], instance_id, imdsv2_display.get(imdsv2_mode[1], imdsv2_mode[1])])

    except Exception as e:
        print(f"Error retrieving EC2 instances in {selected_region}: {e}")

    print(table)

if __name__ == "__main__":
    main()


