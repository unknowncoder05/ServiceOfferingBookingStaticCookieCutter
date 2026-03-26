"""
GitHub OAuth Views
"""
import secrets
import requests
from urllib.parse import urlencode

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.users.conf import users_settings


class GitHubOAuthViewSet(GenericViewSet):
    """
    ViewSet for GitHub OAuth operations
    """

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            name='auth-url', url_path='auth-url')
    def auth_url(self, request):
        """
        Generate GitHub OAuth authorization URL with proper scopes.
        Returns the URL that the frontend should redirect to.
        """
        if not users_settings.github_client_id:
            return Response(
                {'error': 'GitHub OAuth is not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Generate a state token for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state in session for validation during callback
        request.session['github_oauth_state'] = state
        request.session.modified = True

        # Build the authorization URL
        params = {
            'client_id': users_settings.github_client_id,
            'redirect_uri': users_settings.github_redirect_uri,
            'scope': ' '.join(users_settings.github_oauth_scopes),
            'state': state,
            'allow_signup': 'false',
        }

        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"

        return Response({
            'auth_url': auth_url,
            'state': state,
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated],
            name='callback', url_path='callback')
    def callback(self, request):
        """
        Handle the OAuth callback from GitHub.
        Exchange the authorization code for an access token.
        """
        code = request.data.get('code')
        state = request.data.get('state')

        if not code:
            return Response(
                {'error': 'Authorization code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate state to prevent CSRF attacks
        stored_state = request.session.get('github_oauth_state')
        if not stored_state or stored_state != state:
            return Response(
                {'error': 'Invalid state parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clear the state from session
        request.session.pop('github_oauth_state', None)

        # Exchange code for access token
        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': users_settings.github_client_id,
                'client_secret': users_settings.github_client_secret,
                'code': code,
                'redirect_uri': users_settings.github_redirect_uri,
            },
            headers={'Accept': 'application/json'},
            timeout=30
        )

        if token_response.status_code != 200:
            return Response(
                {'error': 'Failed to exchange code for token'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        token_data = token_response.json()

        if 'error' in token_data:
            return Response(
                {'error': token_data.get('error_description', token_data['error'])},
                status=status.HTTP_400_BAD_REQUEST
            )

        access_token = token_data.get('access_token')

        # Fetch GitHub user info
        user_response = requests.get(
            'https://api.github.com/user',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/vnd.github.v3+json',
            },
            timeout=30
        )

        if user_response.status_code != 200:
            return Response(
                {'error': 'Failed to fetch GitHub user info'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        github_user = user_response.json()

        # Update the current user with GitHub info
        user = request.user
        user.github_id = str(github_user['id'])
        user.github_username = github_user['login']
        user.github_access_token = access_token
        user.github_token_expires_at = None  # GitHub tokens don't expire unless revoked
        user.save()

        return Response({
            'success': True,
            'github_username': github_user['login'],
            'github_id': str(github_user['id']),
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated],
            name='disconnect', url_path='disconnect')
    def disconnect(self, request):
        """
        Disconnect GitHub account from user profile.
        """
        user = request.user

        if not user.github_id:
            return Response(
                {'error': 'No GitHub account linked'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clear GitHub fields
        user.github_id = None
        user.github_username = None
        user.github_access_token = None
        user.github_token_expires_at = None
        user.save()

        return Response({
            'success': True,
            'message': 'GitHub account disconnected successfully'
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            name='repos', url_path='repos')
    def repos(self, request):
        """
        List the authenticated user's GitHub repositories.
        Proxies to GitHub API using the user's stored access token.
        """
        user = request.user

        if not user.github_access_token:
            return Response(
                {'error': 'GitHub account not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch repos from GitHub API (paginated, up to 100)
            page = int(request.query_params.get('page', 1))
            per_page = min(int(request.query_params.get('per_page', 50)), 100)
            sort = request.query_params.get('sort', 'updated')

            gh_response = requests.get(
                'https://api.github.com/user/repos',
                headers={
                    'Authorization': f'Bearer {user.github_access_token}',
                    'Accept': 'application/vnd.github.v3+json',
                },
                params={
                    'sort': sort,
                    'direction': 'desc',
                    'per_page': per_page,
                    'page': page,
                    'type': 'all',
                },
                timeout=30,
            )

            if gh_response.status_code == 401:
                return Response(
                    {'error': 'GitHub token expired or revoked. Please reconnect.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if gh_response.status_code != 200:
                return Response(
                    {'error': f'GitHub API error: {gh_response.status_code}'},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            repos = gh_response.json()

            # Return simplified repo data
            result = [
                {
                    'id': repo['id'],
                    'full_name': repo['full_name'],
                    'name': repo['name'],
                    'html_url': repo['html_url'],
                    'clone_url': repo['clone_url'],
                    'default_branch': repo['default_branch'],
                    'private': repo['private'],
                    'description': repo.get('description', ''),
                    'language': repo.get('language', ''),
                    'updated_at': repo.get('updated_at', ''),
                }
                for repo in repos
            ]

            return Response({
                'repos': result,
                'page': page,
                'per_page': per_page,
            })

        except requests.Timeout:
            return Response(
                {'error': 'GitHub API request timed out'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch repositories: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            name='status', url_path='status')
    def connection_status(self, request):
        """
        Get the current GitHub connection status for the user.
        """
        user = request.user

        return Response({
            'connected': bool(user.github_id),
            'github_username': user.github_username,
            'github_id': user.github_id,
        })
