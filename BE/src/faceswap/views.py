# Add these imports at the top
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

# Add this view to the file
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ws_token(request):
    """Generate a token for WebSocket authentication"""
    token = AccessToken.for_user(request.user)
    return Response({
        'token': str(token)
    })
