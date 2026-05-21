"""
Swagger/OpenAPI Configuration
Interactive API documentation setup
"""

from flasgger import Swagger

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}

# OpenAPI 3.0 template
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Chemical Calculations API",
        "description": "Advanced REST API for absorption and desorption calculations",
        "contact": {
            "responsibleOrganization": "Chemical Engineering Solutions",
            "responsibleDeveloper": "Development Team",
            "email": "api@chemcalc.com",
            "url": "https://chemcalc.com",
        },
        "termsOfService": "https://chemcalc.com/terms",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:5000",
    "basePath": "/api/v1",
    "schemes": [
        "http",
        "https"
    ],
    "operationId": "get_my_endpoint",
    "produces": [
        "application/json",
    ],
    "securityDefinitions": {
        "JWT": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Format: 'Bearer {token}'"
        },
        "APIKey": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
            "description": "API Key for service-to-service authentication"
        }
    },
    "security": [
        {
            "JWT": []
        },
        {
            "APIKey": []
        }
    ],
    "tags": [
        {
            "name": "Authentication",
            "description": "User authentication and API key management"
        },
        {
            "name": "Calculations",
            "description": "Chemical absorption and desorption calculations"
        },
        {
            "name": "Exports",
            "description": "Multi-format data export functionality"
        },
        {
            "name": "Notifications",
            "description": "Real-time notification system"
        },
        {
            "name": "Administration",
            "description": "System administration and monitoring"
        }
    ]
}

def init_swagger(app):
    """Initialize Swagger documentation"""
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    return swagger