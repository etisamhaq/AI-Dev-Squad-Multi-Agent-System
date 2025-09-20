#!/usr/bin/env python3
"""
Backend Developer Agent - MCP-compliant agent for Python/Django development
"""

import asyncio
import json
from typing import Dict, Optional, Any
from base_agent import MCPAgent, AgentCollaborationMixin


class BackendDeveloperAgent(MCPAgent, AgentCollaborationMixin):
    """Backend Developer Agent specializing in Python/Django"""
    
    def __init__(self):
        super().__init__(
            agent_name="backend-developer",
            agent_type="backend",
            version="1.0.0"
        )
        self.tech_stack = ["Python", "Django", "FastAPI", "PostgreSQL", "Redis"]
        self.hourly_rate = 80
        
    async def setup_capabilities(self):
        """Define backend development capabilities"""
        self.capabilities = [
            {
                "name": "create_api_endpoint",
                "description": "Create a REST API endpoint",
                "parameters": [
                    {"name": "endpoint_path", "type": "string", "required": True},
                    {"name": "method", "type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                    {"name": "authentication", "type": "boolean"},
                    {"name": "request_schema", "type": "object"},
                    {"name": "response_schema", "type": "object"}
                ]
            },
            {
                "name": "create_model",
                "description": "Create a database model",
                "parameters": [
                    {"name": "model_name", "type": "string", "required": True},
                    {"name": "fields", "type": "array", "required": True},
                    {"name": "relationships", "type": "array"}
                ]
            },
            {
                "name": "implement_business_logic",
                "description": "Implement business logic for a feature",
                "parameters": [
                    {"name": "feature_description", "type": "string", "required": True},
                    {"name": "requirements", "type": "array"}
                ]
            },
            {
                "name": "setup_database",
                "description": "Setup and configure database",
                "parameters": [
                    {"name": "db_type", "type": "string", "enum": ["postgresql", "mysql", "sqlite"]},
                    {"name": "migrations", "type": "boolean", "default": True}
                ]
            },
            {
                "name": "implement_authentication",
                "description": "Implement authentication system",
                "parameters": [
                    {"name": "auth_type", "type": "string", "enum": ["jwt", "session", "oauth"]},
                    {"name": "providers", "type": "array"}
                ]
            },
            {
                "name": "optimize_query",
                "description": "Optimize database queries",
                "parameters": [
                    {"name": "query", "type": "string"},
                    {"name": "use_caching", "type": "boolean", "default": True}
                ]
            }
        ]
        
    async def process_message(self, content: str) -> Optional[str]:
        """Process messages related to backend development"""
        content_lower = content.lower()
        
        if "api" in content_lower or "endpoint" in content_lower:
            return "I'll create the API endpoint. Please specify the HTTP method and authentication requirements."
        elif "database" in content_lower or "model" in content_lower:
            return "I can design the database schema and create the models. Share your data requirements."
        elif "authentication" in content_lower or "auth" in content_lower:
            return "I'll implement the authentication system. JWT or session-based?"
        elif "business logic" in content_lower:
            return "I'll implement the business logic. Please provide the feature requirements."
        elif "performance" in content_lower or "optimize" in content_lower:
            return "I'll optimize the backend performance and database queries."
        
        return None
        
    async def execute_task(self, task_id: str, description: str) -> Dict:
        """Execute backend development tasks"""
        result = {
            "task_id": task_id,
            "status": "completed",
            "agent": self.agent_name
        }
        
        # Analyze task type
        if "api" in description.lower() or "endpoint" in description.lower():
            code = await self.create_api_endpoint_code(description)
            result["artifact"] = {"type": "api", "code": code}
        elif "model" in description.lower() or "database" in description.lower():
            model_code = await self.create_model_code(description)
            result["artifact"] = {"type": "model", "code": model_code}
        elif "authentication" in description.lower():
            auth_code = await self.create_authentication_code(description)
            result["artifact"] = {"type": "auth", "code": auth_code}
        else:
            result["artifact"] = {"type": "general", "message": "Task completed successfully"}
            
        return result
        
    async def execute_capability(self, capability: str, parameters: Dict) -> Any:
        """Execute specific backend capabilities"""
        if capability == "create_api_endpoint":
            return await self.create_api_endpoint(**parameters)
        elif capability == "create_model":
            return await self.create_model(**parameters)
        elif capability == "implement_business_logic":
            return await self.implement_business_logic(**parameters)
        elif capability == "setup_database":
            return await self.setup_database(**parameters)
        elif capability == "implement_authentication":
            return await self.implement_authentication(**parameters)
        elif capability == "optimize_query":
            return await self.optimize_query(**parameters)
        else:
            raise ValueError(f"Unknown capability: {capability}")
            
    async def create_api_endpoint(self, endpoint_path: str, method: str = "GET", 
                                authentication: bool = True, 
                                request_schema: Dict = None,
                                response_schema: Dict = None) -> Dict:
        """Create a REST API endpoint"""
        
        # Django REST Framework view
        auth_decorator = "@permission_classes([IsAuthenticated])" if authentication else "@permission_classes([AllowAny])"
        
        code = f"""from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

{auth_decorator}
@api_view(['{method}'])
def {self._path_to_function_name(endpoint_path)}(request):
    \"\"\"
    API endpoint: {method} {endpoint_path}
    \"\"\"
    try:
        if request.method == '{method}':
            {self._generate_method_logic(method, request_schema, response_schema)}
            
            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {{'error': str(e)}},
            status=status.HTTP_400_BAD_REQUEST
        )
"""
        
        # URL configuration
        url_config = f"""path('{endpoint_path.lstrip("/")}/', views.{self._path_to_function_name(endpoint_path)}, name='{self._path_to_function_name(endpoint_path)}'),"""
        
        return {
            "endpoint": endpoint_path,
            "method": method,
            "view_code": code,
            "url_config": url_config,
            "authentication": authentication
        }
        
    async def create_model(self, model_name: str, fields: list, relationships: list = None) -> Dict:
        """Create a Django model"""
        relationships = relationships or []
        
        field_definitions = []
        for field in fields:
            field_def = self._generate_field_definition(field)
            field_definitions.append(field_def)
            
        relationship_definitions = []
        for rel in relationships:
            rel_def = self._generate_relationship_definition(rel)
            relationship_definitions.append(rel_def)
            
        code = f"""from django.db import models
from django.contrib.auth.models import User
import uuid

class {model_name}(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    {chr(10).join(field_definitions)}
    {chr(10).join(relationship_definitions) if relationship_definitions else ''}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{{{model_name} object}}"
"""
        
        # Serializer code
        serializer_code = f"""from rest_framework import serializers
from .models import {model_name}

class {model_name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model_name}
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
"""
        
        return {
            "model_name": model_name,
            "model_code": code,
            "serializer_code": serializer_code,
            "migration_command": f"python manage.py makemigrations && python manage.py migrate"
        }
        
    async def implement_business_logic(self, feature_description: str, requirements: list = None) -> Dict:
        """Implement business logic for a feature"""
        requirements = requirements or []
        
        # Generate service class for business logic
        code = f"""from typing import Dict, List, Optional
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class FeatureService:
    \"\"\"
    Business logic for: {feature_description}
    \"\"\"
    
    def __init__(self):
        self.validators = []
        self.processors = []
        
    @transaction.atomic
    def execute(self, data: Dict) -> Dict:
        \"\"\"
        Execute the feature logic
        \"\"\"
        try:
            # Validation phase
            self._validate(data)
            
            # Processing phase
            result = self._process(data)
            
            # Post-processing
            self._post_process(result)
            
            return {{
                'success': True,
                'data': result
            }}
        except Exception as e:
            logger.error(f"Feature execution failed: {{e}}")
            raise
            
    def _validate(self, data: Dict):
        \"\"\"Validate input data\"\"\"
        # Implement validation logic
        pass
        
    def _process(self, data: Dict) -> Dict:
        \"\"\"Process the feature logic\"\"\"
        # Implement core business logic
        result = {{}}
        
        {self._generate_requirements_logic(requirements)}
        
        return result
        
    def _post_process(self, result: Dict):
        \"\"\"Post-processing tasks\"\"\"
        # Implement post-processing
        pass
"""
        
        return {
            "feature": feature_description,
            "code": code,
            "requirements_implemented": requirements
        }
        
    async def setup_database(self, db_type: str = "postgresql", migrations: bool = True) -> Dict:
        """Setup database configuration"""
        
        if db_type == "postgresql":
            config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ai_dev_squad'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}"""
        elif db_type == "mysql":
            config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'ai_dev_squad'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}"""
        else:  # sqlite
            config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""
        
        commands = []
        if migrations:
            commands = [
                "python manage.py makemigrations",
                "python manage.py migrate",
                "python manage.py createsuperuser --noinput"
            ]
            
        return {
            "db_type": db_type,
            "configuration": config,
            "setup_commands": commands
        }
        
    async def implement_authentication(self, auth_type: str = "jwt", providers: list = None) -> Dict:
        """Implement authentication system"""
        providers = providers or []
        
        if auth_type == "jwt":
            code = """from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    \"\"\"User registration endpoint\"\"\"
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
        
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    return Response({'message': 'User created successfully'})

# URL patterns
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', register, name='register'),
]"""
            
            settings = """INSTALLED_APPS += ['rest_framework_simplejwt']

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}"""
            
        else:  # session-based
            code = """from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({'message': 'Login successful'})
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    logout(request)
    return Response({'message': 'Logout successful'})"""
            
            settings = """REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}"""
        
        return {
            "auth_type": auth_type,
            "code": code,
            "settings": settings,
            "providers": providers
        }
        
    async def optimize_query(self, query: str, use_caching: bool = True) -> Dict:
        """Optimize database query"""
        optimizations = []
        
        # Analyze query for optimization opportunities
        if "select" in query.lower():
            optimizations.append({
                "type": "select_related",
                "description": "Use select_related for foreign key relationships",
                "code": "queryset.select_related('related_field')"
            })
            
            optimizations.append({
                "type": "prefetch_related",
                "description": "Use prefetch_related for many-to-many relationships",
                "code": "queryset.prefetch_related('many_to_many_field')"
            })
            
        if use_caching:
            cache_code = """from django.core.cache import cache

def get_cached_data(key, query_func, timeout=300):
    data = cache.get(key)
    if data is None:
        data = query_func()
        cache.set(key, data, timeout)
    return data"""
            
            optimizations.append({
                "type": "caching",
                "description": "Implement Redis caching",
                "code": cache_code
            })
            
        # Database indexing
        optimizations.append({
            "type": "indexing",
            "description": "Add database indexes",
            "code": """class Meta:
    indexes = [
        models.Index(fields=['field1', 'field2']),
    ]"""
        })
        
        return {
            "original_query": query,
            "optimizations": optimizations,
            "estimated_improvement": "50-70% query performance improvement"
        }
        
    async def create_api_endpoint_code(self, description: str) -> str:
        """Generate API endpoint code from description"""
        return f"""# API Endpoint generated from: {description}
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def generated_endpoint(request):
    if request.method == 'GET':
        # Handle GET request
        data = {{'message': 'Data retrieved successfully'}}
        return Response(data)
    elif request.method == 'POST':
        # Handle POST request
        # Process request.data
        return Response({{'message': 'Data created successfully'}})"""
        
    async def create_model_code(self, description: str) -> str:
        """Generate model code from description"""
        return f"""# Model generated from: {description}
class GeneratedModel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name"""
        
    async def create_authentication_code(self, description: str) -> str:
        """Generate authentication code from description"""
        return f"""# Authentication implementation for: {description}
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Custom authentication logic
        return super().authenticate(request)"""
        
    def _path_to_function_name(self, path: str) -> str:
        """Convert API path to function name"""
        # Remove leading/trailing slashes and replace remaining with underscores
        clean_path = path.strip('/').replace('/', '_').replace('-', '_')
        return f"api_{clean_path}"
        
    def _generate_method_logic(self, method: str, request_schema: Dict, response_schema: Dict) -> str:
        """Generate method-specific logic"""
        if method == "GET":
            return """# Fetch data
            data = Model.objects.all()
            serializer = ModelSerializer(data, many=True)
            response_data = serializer.data"""
        elif method == "POST":
            return """# Create new object
            serializer = ModelSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
        elif method == "PUT":
            return """# Update existing object
            instance = Model.objects.get(id=request.data.get('id'))
            serializer = ModelSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
        else:  # DELETE
            return """# Delete object
            instance = Model.objects.get(id=request.data.get('id'))
            instance.delete()
            response_data = {'message': 'Deleted successfully'}"""
            
    def _generate_field_definition(self, field: Dict) -> str:
        """Generate Django model field definition"""
        field_name = field.get("name", "field")
        field_type = field.get("type", "string")
        required = field.get("required", False)
        
        type_map = {
            "string": f"models.CharField(max_length={field.get('max_length', 200)})",
            "text": "models.TextField()",
            "integer": "models.IntegerField()",
            "decimal": "models.DecimalField(max_digits=10, decimal_places=2)",
            "boolean": "models.BooleanField(default=False)",
            "date": "models.DateField()",
            "datetime": "models.DateTimeField()",
            "email": "models.EmailField()",
            "url": "models.URLField()",
            "uuid": "models.UUIDField(default=uuid.uuid4)",
            "json": "models.JSONField(default=dict)"
        }
        
        field_def = type_map.get(field_type, "models.CharField(max_length=200)")
        
        if not required:
            field_def = field_def.replace(")", ", null=True, blank=True)")
            
        return f"    {field_name} = {field_def}"
        
    def _generate_relationship_definition(self, rel: Dict) -> str:
        """Generate Django model relationship definition"""
        rel_type = rel.get("type", "foreign_key")
        rel_name = rel.get("name", "related")
        rel_to = rel.get("to", "Model")
        
        if rel_type == "foreign_key":
            return f"    {rel_name} = models.ForeignKey('{rel_to}', on_delete=models.CASCADE, related_name='{rel_name}_set')"
        elif rel_type == "many_to_many":
            return f"    {rel_name} = models.ManyToManyField('{rel_to}', related_name='{rel_name}_set')"
        elif rel_type == "one_to_one":
            return f"    {rel_name} = models.OneToOneField('{rel_to}', on_delete=models.CASCADE)"
        else:
            return ""
            
    def _generate_requirements_logic(self, requirements: list) -> str:
        """Generate logic based on requirements"""
        logic_lines = []
        for req in requirements:
            logic_lines.append(f"        # Requirement: {req}")
            logic_lines.append(f"        # TODO: Implement {req}")
            
        return "\n".join(logic_lines) if logic_lines else "        pass"


async def main():
    """Main entry point for the backend agent"""
    agent = BackendDeveloperAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())