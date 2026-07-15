import os
import json
import urllib3
import boto3
from datetime import datetime, timedelta

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # =========================================================================
    # SECURE CONFIGURATION (Loaded from Lambda Environment Variables)
    # =========================================================================
    # Fetch environment variables or fall back to generic safe placeholders
    api_base_url = os.environ.get('API_BASE_URL', 'https://api.example.com/v1')
    auth_header = os.environ.get('API_AUTH_TOKEN', 'Basic BASE64_ENCODED_CREDENTIALS')
    bucket_name = os.environ.get('S3_BUCKET_NAME', 'my-generic-iot-ingest-bucket')
    s3_prefix = os.environ.get('S3_PREFIX', 'iot-telemetry-data/')
    
    # 1. READ PARAMETERS DYNAMICALLY FROM THE EVENT
    # Fallback to a generic mock MAC ID if no payload is provided
    mac_id = event.get('device_mac', '00-11-22-33-44-55')
    
    # Fetch both standard telemetry and AI anomaly events
    datatypes = ["Signature_Anomaly", "Signature"]
    
    http = urllib3.PoolManager()
    execution_summary = []
    
    # Dynamic time calculation (Today - 30 Days)
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    to_time = int(now.timestamp() * 1000)
    from_time = int(thirty_days_ago.timestamp() * 1000)
    file_timestamp = now.strftime("%Y%m%d-%H%M%S")
    
    # =========================================================================
    # FLEET CONFIGURATION LOADER (Keep commented for portfolio reference)
    # =========================================================================
    """
    try:
        config_object = s3_client.get_object(Bucket=bucket_name, Key="config/devices.json")
        config_data = json.loads(config_object['Body'].read().decode('utf-8'))
        target_macs = config_data.get('devices', [])
    except Exception as e:
        return {'statusCode': 500, 'body': f"Failed reading fleet config: {str(e)}"}
    """
    target_macs = [mac_id]  # Processes the single event MAC by default
    
    # =========================================================================
    # CORE API INGESTION LOOP
    # =========================================================================
    for current_mac in target_macs:
        for datatype in datatypes:
            # Construct the clean API URL using dynamic parameters
            url = f"{api_base_url}/?datatype={datatype}&device_mac={current_mac}&from={from_time}&to={to_time}"
            
            headers = {
                "Authorization": auth_header,
                "Accept": "application/json"
            }
            
            try:
                response = http.request("GET", url, headers=headers)
                
                if response.status != 200:
                    execution_summary.append(f"Failed {datatype} for {current_mac}: Status {response.status}")
                    continue
                    
                response_data = json.loads(response.data.decode('utf-8'))
                
                # Output filename dynamically matches configuration parameters
                s3_key = f"{s3_prefix}{datatype.lower()}_{current_mac}_{file_timestamp}.json"
                
                # Upload directly to S3
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=json.dumps(response_data, indent=4),
                    ContentType='application/json'
                )
                
                execution_summary.append(f"Successfully saved {datatype} for {current_mac}")
                
            except Exception as e:
                execution_summary.append(f"Error processing {datatype} for {current_mac}: {str(e)}")
                
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Completed ingestion for {len(target_macs)} device(s)',
            'time_range_query': f"From {from_time} to {to_time}",
            'results': execution_summary
        })
    }
