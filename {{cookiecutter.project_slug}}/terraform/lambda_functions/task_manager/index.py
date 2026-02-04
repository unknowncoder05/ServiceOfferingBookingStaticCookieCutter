"""
Lambda function to manage ECS task lifecycle and API Gateway integration.
Ensures backend task is running and updates API Gateway to proxy to it.
"""
import json
import os
import time
import boto3
from datetime import datetime

ecs_client = boto3.client('ecs')
ec2_client = boto3.client('ec2')
apigw_client = boto3.client('apigatewayv2')
cloudwatch_client = boto3.client('cloudwatch')

# Environment variables
CLUSTER_NAME = os.environ['ECS_CLUSTER_NAME']
TASK_DEFINITION = os.environ['TASK_DEFINITION_FAMILY']
SUBNET_IDS = os.environ['SUBNET_IDS'].split(',')
SECURITY_GROUP_ID = os.environ['SECURITY_GROUP_ID']
API_GATEWAY_ID = os.environ.get('API_GATEWAY_ID', '')
API_INTEGRATION_ID = os.environ.get('API_INTEGRATION_ID', '')
TASK_LIFETIME_SECONDS = int(os.environ.get('TASK_LIFETIME_SECONDS', '300'))
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'storyarchitect')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')
BACKEND_PORT = os.environ.get('BACKEND_PORT', '8000')
CLOUDWATCH_NAMESPACE = os.environ.get('CLOUDWATCH_NAMESPACE', 'StoryArchitect/Backend')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def get_cors_headers():
    """
    Get standardized CORS headers for all responses.
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://storyarchitect.yerson.co',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD',
        'Access-Control-Allow-Headers': 'content-type,authorization,x-requested-with,x-csrftoken,accept,origin,user-agent,cache-control,pragma',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '300'
    }

def push_activity_metric():
    """
    Push CloudWatch metric to track backend activity.
    This starts/resets the inactivity alarm timer.
    """
    try:
        print(f"Pushing CloudWatch activity metric to {CLOUDWATCH_NAMESPACE}")

        cloudwatch_client.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    'MetricName': 'BackendActivity',
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': ENVIRONMENT
                        },
                        {
                            'Name': 'Project',
                            'Value': PROJECT_NAME
                        }
                    ],
                    'Value': 1.0,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )

        print(f"CloudWatch metric pushed successfully")

    except Exception as e:
        print(f"Warning: Failed to push CloudWatch metric: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Don't raise - metric push failure shouldn't block startup

def lambda_handler(event, context):
    """
    Main handler - ensures backend is running and API Gateway points to it.
    """
    print(f"=== Lambda Invocation Start ===")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Event: {json.dumps(event, indent=2)}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Cluster: {CLUSTER_NAME}")
    print(f"API Gateway ID: {API_GATEWAY_ID}")
    print(f"Integration ID: {API_INTEGRATION_ID}")

    # Parse request
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    raw_path = event.get('rawPath', '/')
    query_params = event.get('queryStringParameters', {}) or {}
    action = query_params.get('action', '')

    print(f"Method: {http_method}, Path: {raw_path}, Action: {action}")

    try:
        # Handle OPTIONS (CORS preflight) requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({'message': 'OK'})
            }

        # Handle explicit stop request
        if action == 'stop':
            return handle_stop()

        # For any other request, ensure backend is running
        return ensure_backend_running()

    except Exception as e:
        print(f"!!! ERROR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def ensure_backend_running():
    """
    Ensure backend task is running and API Gateway integration points to it.
    """
    print(f"--- Ensuring backend is running ---")

    # Check for existing running task
    running_task = get_running_task()

    if running_task:
        task_arn = running_task['taskArn']
        print(f"Found running task: {task_arn}")

        # Get public IP
        public_ip = get_task_public_ip(running_task)

        if public_ip:
            print(f"Task public IP: {public_ip}")

            # Update API Gateway integration
            update_api_gateway_integration(public_ip)

            # Push CloudWatch metric to start inactivity alarm timer
            push_activity_metric()

            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'status': 'ready',
                    'message': 'Backend is running and API Gateway is configured',
                    'backend_url': f'http://{public_ip}:{BACKEND_PORT}',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        else:
            print("!!! Task running but no public IP yet")
            return {
                'statusCode': 202,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'status': 'starting',
                    'message': 'Backend is starting, IP not yet assigned. Retry in 5 seconds.',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
    else:
        print("No running task found. Starting new task...")

        # Clean up any stopped tasks first
        cleanup_stopped_tasks()

        # Start new task
        task_arn, public_ip = start_new_task()

        if public_ip:
            # Update API Gateway integration
            update_api_gateway_integration(public_ip)

            # Push CloudWatch metric to start inactivity alarm timer
            push_activity_metric()

            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'status': 'started',
                    'message': 'New backend started and API Gateway configured. Please wait 30-60 seconds for full startup.',
                    'backend_url': f'http://{public_ip}:{BACKEND_PORT}',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        else:
            return {
                'statusCode': 202,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'status': 'starting',
                    'message': 'Backend task started but IP not yet assigned. Retry in 10 seconds.',
                    'task_arn': task_arn,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }

def update_api_gateway_integration(backend_ip):
    """
    Update API Gateway HTTP integration to point to backend task.
    """
    if not API_GATEWAY_ID or not API_INTEGRATION_ID:
        print("WARN: API Gateway ID or Integration ID not set. Skipping integration update.")
        return

    integration_uri = f'http://{backend_ip}:{BACKEND_PORT}/{{proxy}}'

    print(f"Updating API Gateway integration to: {integration_uri}")

    try:
        response = apigw_client.update_integration(
            ApiId=API_GATEWAY_ID,
            IntegrationId=API_INTEGRATION_ID,
            IntegrationUri=integration_uri
        )

        print(f"API Gateway integration updated successfully")
        print(f"Response: {json.dumps(response, default=str)}")

    except Exception as e:
        print(f"!!! Error updating API Gateway integration: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

def handle_stop():
    """
    Handle stop request - stop any running tasks.
    """
    print(f"--- Handling STOP request ---")

    running_task = get_running_task()

    if not running_task:
        print("No running task found to stop")
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'No task is currently running',
                'timestamp': datetime.utcnow().isoformat()
            })
        }

    task_arn = running_task['taskArn']
    print(f"Stopping task: {task_arn}")

    stop_task(task_arn)

    return {
        'statusCode': 200,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'message': 'Task stopped successfully',
            'task_arn': task_arn,
            'timestamp': datetime.utcnow().isoformat()
        })
    }

def get_running_task():
    """
    Get the currently running task from ECS (if any).
    Returns the task dict or None.
    """
    print(f"Querying ECS for running tasks...")

    try:
        list_response = ecs_client.list_tasks(
            cluster=CLUSTER_NAME,
            family=TASK_DEFINITION,
            desiredStatus='RUNNING'
        )

        task_arns = list_response.get('taskArns', [])
        print(f"Found {len(task_arns)} task(s) in RUNNING state")

        if not task_arns:
            return None

        describe_response = ecs_client.describe_tasks(
            cluster=CLUSTER_NAME,
            tasks=task_arns
        )

        tasks = describe_response.get('tasks', [])
        print(f"Described {len(tasks)} task(s)")

        if not tasks:
            return None

        for task in tasks:
            last_status = task.get('lastStatus', '')
            print(f"Task {task['taskArn']}: lastStatus={last_status}")

            if last_status == 'RUNNING':
                return task

        return None

    except Exception as e:
        print(f"Error querying ECS tasks: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def cleanup_stopped_tasks():
    """
    Stop any tasks in weird states (PENDING, STOPPING, etc).
    """
    print(f"Cleaning up stopped/stopping tasks...")

    try:
        list_response = ecs_client.list_tasks(
            cluster=CLUSTER_NAME,
            family=TASK_DEFINITION
        )

        task_arns = list_response.get('taskArns', [])

        if not task_arns:
            print("No tasks to clean up")
            return

        describe_response = ecs_client.describe_tasks(
            cluster=CLUSTER_NAME,
            tasks=task_arns
        )

        tasks = describe_response.get('tasks', [])

        for task in tasks:
            task_arn = task['taskArn']
            last_status = task.get('lastStatus', '')

            if last_status != 'RUNNING' and last_status != 'STOPPED':
                print(f"Stopping task in state {last_status}: {task_arn}")
                try:
                    stop_task(task_arn)
                except Exception as e:
                    print(f"Error stopping task {task_arn}: {e}")

    except Exception as e:
        print(f"Error during cleanup: {e}")

def start_new_task():
    """
    Start a new ECS task and return its ARN and public IP.
    """
    print(f"Starting new ECS task...")
    print(f"  Cluster: {CLUSTER_NAME}")
    print(f"  Task Definition: {TASK_DEFINITION}")
    print(f"  Subnets: {SUBNET_IDS}")
    print(f"  Security Group: {SECURITY_GROUP_ID}")

    try:
        response = ecs_client.run_task(
            cluster=CLUSTER_NAME,
            taskDefinition=TASK_DEFINITION,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': SUBNET_IDS,
                    'securityGroups': [SECURITY_GROUP_ID],
                    'assignPublicIp': 'ENABLED'
                }
            },
            count=1
        )

        print(f"RunTask response: {json.dumps(response, default=str, indent=2)}")

        if not response.get('tasks'):
            failures = response.get('failures', [])
            print(f"!!! Failed to start task. Failures: {json.dumps(failures, indent=2)}")
            raise Exception(f"Failed to start task: {failures}")

        task = response['tasks'][0]
        task_arn = task['taskArn']

        print(f"Task started successfully: {task_arn}")
        print(f"Task status: {task.get('lastStatus')}")

        # Wait for network interface
        print("Waiting 10 seconds for network interface assignment...")
        time.sleep(10)

        # Get task details again to get public IP
        describe_response = ecs_client.describe_tasks(
            cluster=CLUSTER_NAME,
            tasks=[task_arn]
        )

        if describe_response.get('tasks'):
            task = describe_response['tasks'][0]
            public_ip = get_task_public_ip(task)
            print(f"Task public IP: {public_ip}")
        else:
            public_ip = None
            print("Warning: Could not retrieve task details after starting")

        return task_arn, public_ip

    except Exception as e:
        print(f"!!! Error starting task: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

def stop_task(task_arn):
    """
    Stop an ECS task gracefully.
    """
    print(f"Stopping task: {task_arn}")

    try:
        response = ecs_client.stop_task(
            cluster=CLUSTER_NAME,
            task=task_arn,
            reason='Stopped by Lambda task manager'
        )

        print(f"Task stopped successfully: {response.get('task', {}).get('stoppedReason', 'No reason provided')}")
        return response

    except Exception as e:
        print(f"Error stopping task {task_arn}: {e}")
        raise

def get_task_public_ip(task):
    """
    Get the public IP address of a task from its details.
    """
    print(f"Extracting public IP from task...")

    try:
        for attachment in task.get('attachments', []):
            if attachment['type'] == 'ElasticNetworkInterface':
                print(f"Found ENI attachment")

                for detail in attachment['details']:
                    if detail['name'] == 'networkInterfaceId':
                        eni_id = detail['value']
                        print(f"ENI ID: {eni_id}")

                        eni_response = ec2_client.describe_network_interfaces(
                            NetworkInterfaceIds=[eni_id]
                        )

                        if eni_response['NetworkInterfaces']:
                            association = eni_response['NetworkInterfaces'][0].get('Association', {})
                            public_ip = association.get('PublicIp')

                            if public_ip:
                                print(f"Found public IP: {public_ip}")
                                return public_ip
                            else:
                                print("No public IP in association")

        print("Could not find public IP in task attachments")
        return None

    except Exception as e:
        print(f"Error getting public IP: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None
