# Alarm-Based Task Monitoring

## Overview

The StoryArchitect backend uses **CloudWatch Alarms** to monitor task activity and trigger shutdowns only when necessary, rather than polling every minute with a scheduled Lambda.

## How It Works

### 1. Task Activity Tracking

When the Task Manager Lambda handles requests:

- **Start Request**: Starts task + publishes initial `TaskPing` metric
- **Ping Request**: Extends lifetime + publishes `TaskPing` metric

The metric is published to CloudWatch:
```python
cloudwatch.put_metric_data(
    Namespace='storyarchitect/ECS',
    MetricData=[{
        'MetricName': 'TaskPing',
        'Value': 1,
        'Unit': 'Count',
        'Timestamp': datetime.utcnow(),
        'Dimensions': [{'Name': 'Environment', 'Value': 'prod'}]
    }]
)
```

### 2. CloudWatch Alarm Monitoring

The alarm is configured to:
- **Monitor**: `TaskPing` metric in `storyarchitect/ECS` namespace
- **Evaluation Period**: 5 minutes (configurable via `task_lifetime_seconds`)
- **Threshold**: Sum < 1 (i.e., no pings received)
- **Missing Data**: Treat as breaching (alarm state)

```hcl
resource "aws_cloudwatch_metric_alarm" "task_inactivity" {
  alarm_name          = "storyarchitect-task-inactivity-prod"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "TaskPing"
  period              = 300  # 5 minutes
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "breaching"
}
```

### 3. Alarm State Transitions

**OK → ALARM**:
- No pings received in last 5 minutes
- Alarm goes into ALARM state
- SNS notification sent to topic
- Task Monitor Lambda triggered

**ALARM → OK**:
- Ping received (task started or extended)
- Alarm returns to OK state
- No action taken

### 4. Task Monitor Lambda

Triggered only when alarm enters ALARM state:

```python
def lambda_handler(event, context):
    # Parse SNS message from alarm
    for record in event.get('Records', []):
        message = json.loads(record['Sns']['Message'])
        new_state = message.get('NewStateValue')

        # Only act on ALARM state
        if new_state == 'ALARM':
            # Stop the idle task
            stop_task(task_arn)
```

## Architecture Flow

```
┌─────────────────┐
│  /start request │
└────────┬────────┘
         │
         v
┌────────────────────┐
│ Task Manager Lambda│
└────────┬───────────┘
         │
         ├──> Start/Extend Task
         │
         └──> Publish TaskPing metric
                      │
                      v
              ┌───────────────────┐
              │ CloudWatch Metrics│
              └────────┬──────────┘
                       │
                       v
              ┌───────────────────┐
              │ CloudWatch Alarm  │
              │ (Evaluates every  │
              │  5 minutes)       │
              └────────┬──────────┘
                       │
         No pings?     │ Yes, pings
         │             │ received
         v             v
    ALARM state    OK state
         │             │
         v             └──> (No action)
    ┌─────────┐
    │   SNS   │
    │  Topic  │
    └────┬────┘
         │
         v
┌────────────────────┐
│ Task Monitor Lambda│
│ (Stops idle task)  │
└────────────────────┘
```

## Benefits Over Scheduled Polling

### 1. Cost Efficiency
**Before** (Scheduled every minute):
- 43,200 Lambda invocations/month
- Most invocations do nothing (task is active)

**After** (Alarm-triggered):
- ~30-50 invocations/month (only when tasks go idle)
- 99.9% reduction in unnecessary executions

### 2. Faster Response Time
- Alarm evaluates at exact timeout (5 minutes)
- No delay waiting for next scheduled check
- Immediate action when threshold breached

### 3. Better Observability
- CloudWatch Alarms visible in console
- Alarm history tracks all state changes
- SNS topic can route to multiple destinations (email, Slack, etc.)

### 4. Simplified Logic
- Task Monitor doesn't need to calculate expiration times
- Just acts on alarm notifications
- Single source of truth (CloudWatch Metrics)

## Configuration

### Changing Task Lifetime

Edit `terraform.tfvars`:
```hcl
task_lifetime_seconds = 600  # 10 minutes instead of 5
```

The alarm period automatically adjusts to match.

### Adding Email Notifications

Subscribe your email to the SNS topic:
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT:storyarchitect-task-inactivity-prod \
  --protocol email \
  --notification-endpoint your-email@example.com
```

Now you'll receive emails when tasks shut down.

### Testing the Alarm

Manually trigger the alarm:
```bash
aws cloudwatch set-alarm-state \
  --alarm-name storyarchitect-task-inactivity-prod \
  --state-value ALARM \
  --state-reason "Manual test"
```

Check Task Monitor Lambda logs to verify it was triggered.

## Monitoring

### Check Alarm Status
```bash
aws cloudwatch describe-alarms \
  --alarm-names storyarchitect-task-inactivity-prod
```

Output:
```json
{
  "MetricAlarms": [{
    "AlarmName": "storyarchitect-task-inactivity-prod",
    "StateValue": "OK",
    "StateReason": "Threshold Crossed: 1 datapoint [1.0 (20/01/25 10:30:00)] was not less than the threshold (1.0)",
    "ActionsEnabled": true,
    "AlarmActions": ["arn:aws:sns:..."]
  }]
}
```

### View Ping Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace storyarchitect/ECS \
  --metric-name TaskPing \
  --dimensions Name=Environment,Value=prod \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Alarm History
```bash
aws cloudwatch describe-alarm-history \
  --alarm-name storyarchitect-task-inactivity-prod \
  --max-records 10
```

Shows all state transitions with timestamps.

## Troubleshooting

### Alarm Not Triggering

1. **Check metric is being published**:
   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace storyarchitect/ECS \
     --metric-name TaskPing \
     --dimensions Name=Environment,Value=prod \
     --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Sum
   ```

2. **Verify Lambda has CloudWatch permissions**:
   - Check IAM policy includes `cloudwatch:PutMetricData`

3. **Check alarm configuration**:
   ```bash
   aws cloudwatch describe-alarms \
     --alarm-names storyarchitect-task-inactivity-prod
   ```

### Task Not Stopping

1. **Check SNS subscription is active**:
   ```bash
   aws sns list-subscriptions-by-topic \
     --topic-arn <sns-topic-arn>
   ```

2. **View Task Monitor Lambda logs**:
   ```bash
   aws logs tail /aws/lambda/storyarchitect-task-monitor-prod --follow
   ```

3. **Verify Lambda has ECS permissions**:
   - Check IAM policy includes `ecs:StopTask`

### False Alarms

If alarm triggers too frequently:

1. **Increase evaluation period**:
   ```hcl
   task_lifetime_seconds = 600  # 10 minutes
   ```

2. **Change to multiple evaluation periods**:
   ```hcl
   evaluation_periods = 2  # Require 2 consecutive breaches
   ```

## Cost Analysis

### CloudWatch Costs

- **Alarms**: $0.10/alarm/month = $0.10
- **Metrics**: First 10,000 free, $0.30/1000 after
  - ~8,640 metrics/month (1 per ping) = Free
- **API Requests**: $0.01/1000 PutMetricData requests = negligible

### Lambda Costs (Alarm-Triggered)

Assuming 30 task shutdowns/month:
- **Invocations**: 30/month = Free (1M free tier)
- **Duration**: 30 × 1 second × 256 MB = negligible

**Total additional cost**: ~$0.10/month

Compare to scheduled (every minute):
- 43,200 invocations/month
- Still free tier, but wastes compute

## Summary

The alarm-based approach:
- ✅ Reduces Lambda invocations by 99.9%
- ✅ Provides exact timing (no polling delay)
- ✅ Better observability via CloudWatch console
- ✅ Extensible (add email, Slack, etc. via SNS)
- ✅ Only $0.10/month additional cost
- ✅ Cleaner architecture (event-driven vs polling)

The alarm only fires when needed, making the system more efficient and easier to monitor.
