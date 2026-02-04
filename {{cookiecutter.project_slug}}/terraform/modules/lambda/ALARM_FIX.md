# Fix for Idle Alarm Triggers

## Problem
When no task is running, the alarm triggers every 5 minutes because:
- No metrics published (no task exists)
- `treat_missing_data = "breaching"` treats this as alarm state
- Wastes Lambda invocations (though still free tier)

## Solution: Dynamic Alarm State

Update Task Manager Lambda to enable/disable alarm based on task state.

### Changes to task_manager/index.py

```python
import boto3
cloudwatch = boto3.client('cloudwatch')

ALARM_NAME = os.environ.get('ALARM_NAME', '')

def start_new_task():
    # ... existing code to start task ...

    # Enable alarm when task starts
    enable_alarm()

    # Publish initial ping metric
    publish_ping_metric()

    return task_arn, public_ip

def stop_task_via_api():
    """Called when manually stopping task"""
    task_state = get_current_task_state()

    if task_state:
        stop_task(task_state['task_arn'])
        table.delete_item(Key={'task_id': 'main'})

        # Disable alarm when no tasks remain
        disable_alarm()

def enable_alarm():
    """Enable the CloudWatch alarm"""
    if not ALARM_NAME:
        return

    try:
        cloudwatch.enable_alarm_actions(
            AlarmNames=[ALARM_NAME]
        )
        print(f"Enabled alarm: {ALARM_NAME}")
    except Exception as e:
        print(f"Error enabling alarm: {e}")

def disable_alarm():
    """Disable the CloudWatch alarm"""
    if not ALARM_NAME:
        return

    try:
        cloudwatch.disable_alarm_actions(
            AlarmNames=[ALARM_NAME]
        )
        print(f"Disabled alarm: {ALARM_NAME}")
    except Exception as e:
        print(f"Error disabling alarm: {e}")
```

### Changes to task_monitor/index.py

```python
def stop_task(task_arn):
    """Stop an ECS task and disable alarm"""
    try:
        response = ecs_client.stop_task(
            cluster=CLUSTER_NAME,
            task=task_arn,
            reason='Task exceeded idle timeout'
        )
        print(f"Task {task_arn} stopped successfully")

        # Disable alarm when task stops
        disable_alarm()

        return response
    except Exception as e:
        print(f"Error stopping task {task_arn}: {e}")
        raise e

def disable_alarm():
    """Disable the CloudWatch alarm"""
    alarm_name = os.environ.get('ALARM_NAME', '')
    if not alarm_name:
        return

    try:
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.disable_alarm_actions(
            AlarmNames=[alarm_name]
        )
        print(f"Disabled alarm: {alarm_name}")
    except Exception as e:
        print(f"Error disabling alarm: {e}")
```

### Changes to terraform/modules/lambda/main.tf

Add alarm name to environment variables:

```hcl
environment {
  variables = {
    # ... existing vars ...
    ALARM_NAME = aws_cloudwatch_metric_alarm.task_inactivity.alarm_name
  }
}
```

Add CloudWatch permissions:

```hcl
{
  Effect = "Allow"
  Action = [
    "cloudwatch:EnableAlarmActions",
    "cloudwatch:DisableAlarmActions"
  ]
  Resource = aws_cloudwatch_metric_alarm.task_inactivity.arn
}
```

## Result

When idle:
- ✅ Alarm is disabled
- ✅ No SNS notifications
- ✅ No Lambda invocations
- ✅ **Zero compute cost when idle**

When active:
- Task starts → Enable alarm
- Task receives pings → Alarm stays OK
- No pings for 5 min → Alarm triggers → Stop task → Disable alarm
