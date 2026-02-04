"""
Lambda function to shutdown ECS tasks when CloudWatch alarm triggers.
This function is invoked by SNS when the backend has been inactive for too long.
"""
import json
import os
import boto3
from datetime import datetime

ecs_client = boto3.client('ecs')

# Environment variables
CLUSTER_NAME = os.environ['ECS_CLUSTER_NAME']
TASK_DEFINITION = os.environ['TASK_DEFINITION_FAMILY']
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'storyarchitect')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')

def lambda_handler(event, context):
    """
    Main handler - stops all running ECS tasks due to inactivity.
    Triggered by CloudWatch alarm via SNS.
    """
    print(f"=== Task Shutdown Lambda Invocation ===")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Event: {json.dumps(event, indent=2)}")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Cluster: {CLUSTER_NAME}")

    try:
        # Parse SNS message
        if 'Records' in event:
            for record in event['Records']:
                if record.get('EventSource') == 'aws:sns':
                    message = json.loads(record['Sns']['Message'])
                    print(f"CloudWatch Alarm Message: {json.dumps(message, indent=2)}")
                    alarm_name = message.get('AlarmName', 'Unknown')
                    print(f"Triggered by alarm: {alarm_name}")

        # Get all running tasks
        running_tasks = list_running_tasks()

        if not running_tasks:
            print("No running tasks found. Nothing to shutdown.")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No running tasks to shutdown',
                    'timestamp': datetime.utcnow().isoformat()
                })
            }

        # Stop all running tasks
        stopped_tasks = []
        for task_arn in running_tasks:
            print(f"Stopping task due to inactivity: {task_arn}")
            try:
                stop_task(task_arn)
                stopped_tasks.append(task_arn)
            except Exception as e:
                print(f"Error stopping task {task_arn}: {e}")

        print(f"Successfully stopped {len(stopped_tasks)} task(s)")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Stopped {len(stopped_tasks)} task(s) due to inactivity',
                'stopped_tasks': stopped_tasks,
                'timestamp': datetime.utcnow().isoformat()
            })
        }

    except Exception as e:
        print(f"!!! ERROR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def list_running_tasks():
    """
    List all running tasks for the task definition.
    Returns a list of task ARNs.
    """
    print(f"Querying ECS for running tasks...")

    try:
        list_response = ecs_client.list_tasks(
            cluster=CLUSTER_NAME,
            family=TASK_DEFINITION,
            desiredStatus='RUNNING'
        )

        task_arns = list_response.get('taskArns', [])
        print(f"Found {len(task_arns)} running task(s)")

        return task_arns

    except Exception as e:
        print(f"Error listing tasks: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

def stop_task(task_arn):
    """
    Stop an ECS task gracefully.
    """
    print(f"Stopping task: {task_arn}")

    try:
        response = ecs_client.stop_task(
            cluster=CLUSTER_NAME,
            task=task_arn,
            reason='Stopped due to inactivity (CloudWatch alarm)'
        )

        print(f"Task stopped successfully: {response.get('task', {}).get('stoppedReason', 'No reason provided')}")
        return response

    except Exception as e:
        print(f"Error stopping task {task_arn}: {e}")
        raise
