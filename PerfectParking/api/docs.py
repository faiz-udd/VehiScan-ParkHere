from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="PerfectParking API",
        default_version='v1',
        description="""
        The PerfectParking API provides a comprehensive interface for managing parking operations.
        
        ## Authentication
        All API endpoints require authentication using JWT tokens. To obtain a token:
        ```
        POST /api/token/
        {
            "username": "your_username",
            "password": "your_password"
        }
        ```
        
        ## Rate Limiting
        API requests are limited to:
        - 100 requests per minute for authenticated users
        - 20 requests per minute for anonymous users
        
        ## Error Handling
        The API uses standard HTTP status codes and returns error responses in the format:
        ```
        {
            "error": {
                "code": "ERROR_CODE",
                "message": "Error description",
                "details": {}
            }
        }
        ```
        """,
        terms_of_service="https://www.perfectparking.com/terms/",
        contact=openapi.Contact(email="api@perfectparking.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API Endpoint documentation
parking_lot_list_docs = {
    'get': {
        'operation_description': "List all parking lots with optional filtering",
        'parameters': [
            openapi.Parameter(
                'latitude',
                openapi.IN_QUERY,
                description="Latitude for location-based search",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
            openapi.Parameter(
                'longitude',
                openapi.IN_QUERY,
                description="Longitude for location-based search",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
            openapi.Parameter(
                'radius',
                openapi.IN_QUERY,
                description="Search radius in kilometers",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
        ],
        'responses': {
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'address': openapi.Schema(type=openapi.TYPE_STRING),
                                    'available_spaces': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'hourly_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                                }
                            )
                        )
                    }
                )
            )
        }
    }
}

booking_create_docs = {
    'post': {
        'operation_description': "Create a new parking booking",
        'request_body': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['parking_lot_id', 'start_time', 'duration'],
            properties={
                'parking_lot_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'start_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                'duration': openapi.Schema(type=openapi.TYPE_INTEGER, description='Duration in hours'),
            }
        ),
        'responses': {
            201: openapi.Response(
                description="Booking created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'message': openapi.Schema(type=openapi.TYPE_STRING),
                                'details': openapi.Schema(type=openapi.TYPE_OBJECT),
                            }
                        )
                    }
                )
            )
        }
    }
} 