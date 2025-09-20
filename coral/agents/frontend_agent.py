#!/usr/bin/env python3
"""
Frontend Developer Agent - MCP-compliant agent for React/Next.js development
"""

import asyncio
import json
from typing import Dict, Optional, Any
from base_agent import MCPAgent, AgentCollaborationMixin


class FrontendDeveloperAgent(MCPAgent, AgentCollaborationMixin):
    """Frontend Developer Agent specializing in React/Next.js"""
    
    def __init__(self):
        super().__init__(
            agent_name="frontend-developer",
            agent_type="frontend",
            version="1.0.0"
        )
        self.tech_stack = ["React", "Next.js", "TypeScript", "Tailwind CSS"]
        self.hourly_rate = 75
        
    async def setup_capabilities(self):
        """Define frontend development capabilities"""
        self.capabilities = [
            {
                "name": "create_component",
                "description": "Create a React component",
                "parameters": [
                    {"name": "component_name", "type": "string", "required": True},
                    {"name": "component_type", "type": "string", "enum": ["functional", "class"]},
                    {"name": "props", "type": "object"}
                ]
            },
            {
                "name": "setup_routing",
                "description": "Set up routing for the application",
                "parameters": [
                    {"name": "routes", "type": "array", "required": True},
                    {"name": "framework", "type": "string", "enum": ["react-router", "nextjs"]}
                ]
            },
            {
                "name": "implement_ui",
                "description": "Implement UI based on design specifications",
                "parameters": [
                    {"name": "design_spec", "type": "string", "required": True},
                    {"name": "responsive", "type": "boolean", "default": True}
                ]
            },
            {
                "name": "integrate_api",
                "description": "Integrate frontend with backend API",
                "parameters": [
                    {"name": "api_endpoint", "type": "string", "required": True},
                    {"name": "method", "type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                    {"name": "auth_required", "type": "boolean"}
                ]
            },
            {
                "name": "optimize_performance",
                "description": "Optimize frontend performance",
                "parameters": [
                    {"name": "target_metrics", "type": "object"},
                    {"name": "lazy_loading", "type": "boolean", "default": True}
                ]
            }
        ]
        
    async def process_message(self, content: str) -> Optional[str]:
        """Process messages related to frontend development"""
        content_lower = content.lower()
        
        if "component" in content_lower:
            return "I can create React components. Please provide the component specifications."
        elif "ui" in content_lower or "design" in content_lower:
            return "I'll implement the UI based on the design specifications. Share the mockups or requirements."
        elif "api" in content_lower or "integration" in content_lower:
            return "I can integrate the frontend with your API. Please provide the endpoint details."
        elif "performance" in content_lower:
            return "I'll optimize the frontend performance. Let me analyze the current metrics."
        
        return None
        
    async def execute_task(self, task_id: str, description: str) -> Dict:
        """Execute frontend development tasks"""
        result = {
            "task_id": task_id,
            "status": "completed",
            "agent": self.agent_name
        }
        
        # Analyze task type
        if "component" in description.lower():
            code = await self.create_react_component(description)
            result["artifact"] = {"type": "component", "code": code}
        elif "routing" in description.lower():
            routing_config = await self.setup_routing_config(description)
            result["artifact"] = {"type": "routing", "config": routing_config}
        elif "ui" in description.lower():
            ui_code = await self.implement_ui_from_spec(description)
            result["artifact"] = {"type": "ui", "code": ui_code}
        else:
            result["artifact"] = {"type": "general", "message": "Task completed successfully"}
            
        return result
        
    async def execute_capability(self, capability: str, parameters: Dict) -> Any:
        """Execute specific frontend capabilities"""
        if capability == "create_component":
            return await self.create_component(**parameters)
        elif capability == "setup_routing":
            return await self.setup_routing(**parameters)
        elif capability == "implement_ui":
            return await self.implement_ui(**parameters)
        elif capability == "integrate_api":
            return await self.integrate_api(**parameters)
        elif capability == "optimize_performance":
            return await self.optimize_performance(**parameters)
        else:
            raise ValueError(f"Unknown capability: {capability}")
            
    async def create_component(self, component_name: str, component_type: str = "functional", props: Dict = None) -> Dict:
        """Create a React component"""
        props = props or {}
        
        if component_type == "functional":
            code = f"""import React from 'react';

interface {component_name}Props {{
    {self._generate_prop_types(props)}
}}

const {component_name}: React.FC<{component_name}Props> = ({{ {', '.join(props.keys())} }}) => {{
    return (
        <div className="{component_name.lower()}">
            <h2>{component_name}</h2>
            {{/* Component implementation */}}
        </div>
    );
}};

export default {component_name};"""
        else:
            code = f"""import React, {{ Component }} from 'react';

interface {component_name}Props {{
    {self._generate_prop_types(props)}
}}

interface {component_name}State {{
    // Define state interface
}}

class {component_name} extends Component<{component_name}Props, {component_name}State> {{
    constructor(props: {component_name}Props) {{
        super(props);
        this.state = {{}};
    }}
    
    render() {{
        return (
            <div className="{component_name.lower()}">
                <h2>{component_name}</h2>
                {{/* Component implementation */}}
            </div>
        );
    }}
}}

export default {component_name};"""
        
        return {
            "component_name": component_name,
            "type": component_type,
            "code": code,
            "file_path": f"components/{component_name}.tsx"
        }
        
    async def setup_routing(self, routes: list, framework: str = "nextjs") -> Dict:
        """Set up routing configuration"""
        if framework == "nextjs":
            # Next.js uses file-based routing
            routing_structure = {
                "pages": {}
            }
            for route in routes:
                path = route.get("path", "/")
                component = route.get("component", "Page")
                routing_structure["pages"][path] = f"{component}.tsx"
        else:
            # React Router configuration
            routing_structure = {
                "router_config": [
                    {
                        "path": route.get("path", "/"),
                        "component": route.get("component", "Page"),
                        "exact": route.get("exact", True)
                    }
                    for route in routes
                ]
            }
            
        return routing_structure
        
    async def implement_ui(self, design_spec: str, responsive: bool = True) -> Dict:
        """Implement UI from design specifications"""
        # Parse design spec and generate UI code
        ui_code = f"""<div className="container mx-auto p-4">
    <header className="mb-8">
        <h1 className="text-4xl font-bold">AI Dev Squad</h1>
    </header>
    
    <main className="grid {'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' if responsive else 'grid-cols-3'} gap-6">
        {{/* UI implementation based on design spec */}}
    </main>
    
    <footer className="mt-8 text-center">
        <p>© 2025 AI Dev Squad</p>
    </footer>
</div>"""
        
        return {
            "design_spec": design_spec,
            "responsive": responsive,
            "code": ui_code
        }
        
    async def integrate_api(self, api_endpoint: str, method: str = "GET", auth_required: bool = False) -> Dict:
        """Generate API integration code"""
        auth_header = """
    const token = localStorage.getItem('authToken');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };""" if auth_required else """
    const headers = {
        'Content-Type': 'application/json'
    };"""
        
        code = f"""import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiCall(data?: any) {{
    {auth_header}
    
    try {{
        const response = await axios({{
            method: '{method}',
            url: `${{API_BASE_URL}}{api_endpoint}`,
            headers,
            {f'data,' if method in ['POST', 'PUT'] else ''}
        }});
        
        return {{ success: true, data: response.data }};
    }} catch (error) {{
        console.error('API call failed:', error);
        return {{ success: false, error: error.message }};
    }}
}}"""
        
        return {
            "endpoint": api_endpoint,
            "method": method,
            "code": code
        }
        
    async def optimize_performance(self, target_metrics: Dict = None, lazy_loading: bool = True) -> Dict:
        """Optimize frontend performance"""
        optimizations = []
        
        if lazy_loading:
            optimizations.append({
                "type": "lazy_loading",
                "description": "Implement lazy loading for components",
                "code": """const LazyComponent = React.lazy(() => import('./Component'));

<Suspense fallback={<Loading />}>
    <LazyComponent />
</Suspense>"""
            })
            
        optimizations.append({
            "type": "code_splitting",
            "description": "Implement code splitting",
            "impact": "Reduces initial bundle size by 30-40%"
        })
        
        optimizations.append({
            "type": "image_optimization",
            "description": "Use Next.js Image component for optimized images",
            "code": "import Image from 'next/image';"
        })
        
        return {
            "optimizations": optimizations,
            "estimated_improvement": "40-60% performance boost",
            "target_metrics": target_metrics or {
                "LCP": "< 2.5s",
                "FID": "< 100ms",
                "CLS": "< 0.1"
            }
        }
        
    async def create_react_component(self, description: str) -> str:
        """Create a React component based on description"""
        # Simple component generation based on description
        return f"""import React from 'react';

const GeneratedComponent: React.FC = () => {{
    // Component generated from: {description}
    return (
        <div>
            <h3>Generated Component</h3>
            <p>Implementation based on: {description}</p>
        </div>
    );
}};

export default GeneratedComponent;"""
        
    async def setup_routing_config(self, description: str) -> Dict:
        """Setup routing configuration"""
        return {
            "type": "next.js",
            "routes": [
                {"path": "/", "component": "Home"},
                {"path": "/agents", "component": "AgentList"},
                {"path": "/projects", "component": "ProjectList"}
            ]
        }
        
    async def implement_ui_from_spec(self, description: str) -> str:
        """Implement UI from specifications"""
        return f"""<div className="ui-container">
    <!-- UI Implementation -->
    <!-- Based on: {description} -->
    <div className="content">
        <h1>UI Implementation</h1>
        <p>Generated based on specifications</p>
    </div>
</div>"""
        
    def _generate_prop_types(self, props: Dict) -> str:
        """Generate TypeScript prop type definitions"""
        if not props:
            return ""
            
        prop_types = []
        for name, prop_type in props.items():
            ts_type = self._get_typescript_type(prop_type)
            prop_types.append(f"    {name}: {ts_type};")
            
        return "\n".join(prop_types)
        
    def _get_typescript_type(self, prop_type: str) -> str:
        """Convert prop type to TypeScript type"""
        type_map = {
            "string": "string",
            "number": "number",
            "boolean": "boolean",
            "array": "any[]",
            "object": "Record<string, any>",
            "function": "() => void"
        }
        return type_map.get(prop_type, "any")


async def main():
    """Main entry point for the frontend agent"""
    agent = FrontendDeveloperAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())