# Rest framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# AWS
import os
import boto3
from datetime import datetime
from django.conf import settings


class BaseViewSet:

    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()

        return context

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring backend availability.
    Used by the frontend to verify backend is ready after cold start.
    """
    return Response({
        'status': 'healthy',
        'message': 'Backend is running'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def keep_alive(request):
    """
    Keep-alive endpoint that pushes CloudWatch metric to track backend activity.

    This endpoint should be called periodically by the frontend to:
    1. Track backend activity via CloudWatch metrics
    2. Prevent automatic shutdown due to inactivity

    The CloudWatch alarm monitors these metrics and triggers shutdown
    after X minutes of inactivity.
    """
    try:
        # Get configuration from environment
        cloudwatch_namespace = os.environ.get('CLOUDWATCH_NAMESPACE', 'MyProject/Backend')
        project_name = os.environ.get('PROJECT_NAME', 'myproject')
        environment = os.environ.get('ENVIRONMENT', 'prod')
        ping_frequency = int(os.environ.get('PING_FREQUENCY_SECONDS', '300'))

        # Push CloudWatch metric to track activity
        push_cloudwatch_metric(cloudwatch_namespace, project_name, environment)

        return Response({
            'status': 'alive',
            'message': 'Activity recorded successfully',
            'ping_frequency_seconds': ping_frequency,
            'ping_frequency_ms': ping_frequency * 1000,
            'timestamp': datetime.utcnow().isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the error but don't fail the request
        print(f"Error in keep-alive: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

        # Still return success - metric push failure shouldn't break frontend
        return Response({
            'status': 'alive',
            'message': 'Keep-alive received (metric push failed)',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=status.HTTP_200_OK)


def push_cloudwatch_metric(namespace, project_name, environment):
    """
    Push a custom CloudWatch metric to track backend activity.
    This metric is monitored by CloudWatch alarms to detect inactivity.
    """
    try:
        cloudwatch_client = boto3.client('cloudwatch', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

        cloudwatch_client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    'MetricName': 'BackendActivity',
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': environment
                        },
                        {
                            'Name': 'Project',
                            'Value': project_name
                        }
                    ],
                    'Value': 1.0,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )

        print(f"CloudWatch metric pushed successfully to {namespace}")

    except Exception as e:
        print(f"Error pushing CloudWatch metric: {e}")
        raise
