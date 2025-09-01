# No Vendor Lock-In Rule

**CRITICAL**: The AI Development Agent system must NEVER create vendor lock-in. All components must support multiple providers, be easily migratable, and maintain complete freedom of choice for users.

## Description
This rule ensures that the AI Development Agent system remains completely free from vendor lock-in by supporting multiple providers, using open standards, and maintaining portability across different services and platforms.

## Core Requirements

### 1. Multi-Provider Support
**MANDATORY**: All components must support multiple providers
```yaml
# REQUIRED: Support multiple providers for each service
llm_providers:
  primary: "Google Gemini (Free)"
  alternatives:
    - "OpenAI GPT-4 (Paid)"
    - "Anthropic Claude (Paid)"
    - "Local Models (Ollama, LM Studio)"
    - "Open Source Models (Llama, Mistral)"

workflow_frameworks:
  primary: "LangGraph"
  alternatives:
    - "LangChain"
    - "AutoGen"
    - "CrewAI"
    - "Custom Implementation"

monitoring_services:
  primary: "LangSmith (Free)"
  alternatives:
    - "Custom Logging"
    - "OpenTelemetry"
    - "Prometheus + Grafana"
    - "No Monitoring (Basic)"

storage_solutions:
  primary: "Local Files"
  alternatives:
    - "SQLite"
    - "PostgreSQL"
    - "MongoDB"
    - "Cloud Storage (AWS, GCP, Azure)"
```

### 2. Provider Abstraction Layer
**MANDATORY**: Implement provider abstraction for all services
```python
# REQUIRED: Abstract provider interfaces
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, config: Dict[str, Any]) -> str:
        """Generate response from any LLM provider."""
        pass
    
    @abstractmethod
    def get_usage_limits(self) -> Dict[str, Any]:
        """Get usage limits for the provider."""
        pass
    
    @abstractmethod
    def get_cost_per_request(self) -> float:
        """Get cost per request (0 for free providers)."""
        pass

class WorkflowFramework(ABC):
    """Abstract interface for workflow frameworks."""
    
    @abstractmethod
    async def create_workflow(self, definition: Dict[str, Any]) -> str:
        """Create workflow in any framework."""
        pass
    
    @abstractmethod
    async def execute_workflow(self, workflow_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow in any framework."""
        pass

class MonitoringService(ABC):
    """Abstract interface for monitoring services."""
    
    @abstractmethod
    async def log_execution(self, execution_id: str, data: Dict[str, Any]) -> None:
        """Log execution to any monitoring service."""
        pass
    
    @abstractmethod
    async def get_metrics(self, execution_id: str) -> Dict[str, Any]:
        """Get metrics from any monitoring service."""
        pass
```

### 3. Configuration-Driven Provider Selection
**MANDATORY**: Allow runtime provider selection via configuration
```python
# REQUIRED: Configuration-driven provider selection
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class ProviderConfig:
    """Configuration for provider selection."""
    
    # LLM Provider Configuration
    llm_provider: str = "gemini"  # gemini, openai, anthropic, local
    llm_api_key: Optional[str] = None
    llm_model: str = "gemini-2.5-flash-lite"
    
    # Workflow Framework Configuration
    workflow_framework: str = "langgraph"  # langgraph, langchain, autogen, custom
    workflow_config: Dict[str, Any] = field(default_factory=dict)
    
    # Monitoring Configuration
    monitoring_service: str = "langsmith"  # langsmith, custom, none
    monitoring_api_key: Optional[str] = None
    
    # Storage Configuration
    storage_provider: str = "local"  # local, sqlite, postgresql, cloud
    storage_config: Dict[str, Any] = field(default_factory=dict)

class ProviderManager:
    """Manages provider selection and abstraction."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.llm_provider = self._create_llm_provider()
        self.workflow_framework = self._create_workflow_framework()
        self.monitoring_service = self._create_monitoring_service()
        self.storage_provider = self._create_storage_provider()
    
    def _create_llm_provider(self) -> LLMProvider:
        """Create LLM provider based on configuration."""
        if self.config.llm_provider == "gemini":
            return GeminiProvider(self.config.llm_api_key, self.config.llm_model)
        elif self.config.llm_provider == "openai":
            return OpenAIProvider(self.config.llm_api_key, self.config.llm_model)
        elif self.config.llm_provider == "anthropic":
            return AnthropicProvider(self.config.llm_api_key, self.config.llm_model)
        elif self.config.llm_provider == "local":
            return LocalLLMProvider(self.config.llm_model)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
    
    def _create_workflow_framework(self) -> WorkflowFramework:
        """Create workflow framework based on configuration."""
        if self.config.workflow_framework == "langgraph":
            return LangGraphFramework(self.config.workflow_config)
        elif self.config.workflow_framework == "langchain":
            return LangChainFramework(self.config.workflow_config)
        elif self.config.workflow_framework == "autogen":
            return AutoGenFramework(self.config.workflow_config)
        elif self.config.workflow_framework == "custom":
            return CustomWorkflowFramework(self.config.workflow_config)
        else:
            raise ValueError(f"Unsupported workflow framework: {self.config.workflow_framework}")
```

### 4. Data Portability
**MANDATORY**: Ensure all data is portable between providers
```python
# REQUIRED: Data portability standards
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class MigrationPlan:
    """Plan for migrating data between providers."""
    from_provider: str
    to_provider: str
    steps: List[str]
    estimated_time: str
    risks: List[str]

@dataclass
class MigrationResult:
    """Result of a provider migration."""
    success: bool
    migration_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of provider configuration validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)

@dataclass
class TestResult:
    """Result of a migration test."""
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class CostComparison:
    """Comparison of costs between providers for a given usage pattern."""
    usage_pattern: UsagePattern
    provider_costs: Dict[str, float]
    recommendations: List[str]

@dataclass
class FreeTierComparison:
    """Comparison of free tier offerings between providers."""
    providers: Dict[str, Dict[str, Any]]

@dataclass
class HealthStatus:
    """Health status of a provider."""
    provider: str
    status: str
    error: Optional[str] = None

@dataclass
class ProviderRecommendation:
    """Recommendation for provider selection."""
    provider: str
    reason: str

@dataclass
class AvailabilityMetrics:
    """Metrics for real-time availability of providers."""
    providers: Dict[str, float] # Percentage of availability
    recommendations: List[ProviderRecommendation]

class DataPortabilityManager:
    """Manages data portability between providers."""
    
    def __init__(self):
        self.export_formats = ["json", "yaml", "sql", "csv"]
        self.import_formats = ["json", "yaml", "sql", "csv"]
    
    async def export_data(self, provider: str, format: str = "json") -> str:
        """Export data from any provider in standard format."""
        if provider == "langsmith":
            return await self._export_from_langsmith(format)
        elif provider == "local":
            return await self._export_from_local(format)
        elif provider == "custom":
            return await self._export_from_custom(format)
        else:
            raise ValueError(f"Unsupported provider for export: {provider}")
    
    async def import_data(self, provider: str, data: str, format: str = "json") -> bool:
        """Import data to any provider from standard format."""
        if provider == "langsmith":
            return await self._import_to_langsmith(data, format)
        elif provider == "local":
            return await self._import_to_local(data, format)
        elif provider == "custom":
            return await self._import_to_custom(data, format)
        else:
            raise ValueError(f"Unsupported provider for import: {provider}")
    
    def get_migration_plan(self, from_provider: str, to_provider: str) -> MigrationPlan:
        """Generate migration plan between providers."""
        return MigrationPlan(
            from_provider=from_provider,
            to_provider=to_provider,
            steps=self._generate_migration_steps(from_provider, to_provider),
            estimated_time=self._estimate_migration_time(from_provider, to_provider),
            risks=self._identify_migration_risks(from_provider, to_provider)
        )
```

### 5. Open Standards Compliance
**MANDATORY**: Use open standards and avoid proprietary formats
```yaml
# REQUIRED: Open standards for all data and APIs
open_standards:
  data_formats:
    - "JSON (RFC 7159)"
    - "YAML (YAML 1.2)"
    - "SQL (ANSI SQL)"
    - "OpenAPI 3.0"
    - "JSON Schema"
  
  communication_protocols:
    - "HTTP/HTTPS (RFC 7230)"
    - "WebSockets (RFC 6455)"
    - "REST (Fielding Dissertation)"
    - "GraphQL"
    - "gRPC"
  
  authentication:
    - "OAuth 2.0 (RFC 6749)"
    - "OpenID Connect"
    - "JWT (RFC 7519)"
    - "API Keys (Custom)"
  
  monitoring:
    - "OpenTelemetry"
    - "Prometheus"
    - "Jaeger"
    - "Zipkin"
```

### 6. Migration Tools and Documentation
**MANDATORY**: Provide tools and documentation for easy migration
```python
# REQUIRED: Migration tools and utilities
class MigrationToolkit:
    """Comprehensive toolkit for provider migration."""
    
    def __init__(self):
        self.migration_scripts = {}
        self.validation_tools = {}
        self.rollback_mechanisms = {}
    
    async def migrate_provider(self, from_config: ProviderConfig, 
                             to_config: ProviderConfig) -> MigrationResult:
        """Migrate from one provider configuration to another."""
        
        # Validate migration feasibility
        validation = await self._validate_migration(from_config, to_config)
        if not validation.is_feasible:
            return MigrationResult(
                success=False,
                error=f"Migration not feasible: {validation.reason}"
            )
        
        # Create migration plan
        plan = self._create_migration_plan(from_config, to_config)
        
        # Execute migration
        try:
            result = await self._execute_migration(plan)
            
            # Validate migration success
            validation = await self._validate_migration_result(result)
            
            return MigrationResult(
                success=validation.is_successful,
                migration_id=result.migration_id,
                details=result.details
            )
            
        except Exception as e:
            # Rollback on failure
            await self._rollback_migration(plan)
            return MigrationResult(
                success=False,
                error=f"Migration failed: {str(e)}"
            )
    
    async def generate_migration_guide(self, from_provider: str, 
                                     to_provider: str) -> str:
        """Generate step-by-step migration guide."""
        return f"""
# Migration Guide: {from_provider} to {to_provider}

## Prerequisites
- Backup all data from {from_provider}
- Install {to_provider} dependencies
- Configure {to_provider} API keys

## Migration Steps
1. Export data from {from_provider}
2. Transform data format if needed
3. Import data to {to_provider}
4. Validate migration success
5. Update configuration
6. Test functionality

## Rollback Plan
If migration fails, follow these steps:
1. Restore {from_provider} configuration
2. Import backup data
3. Verify system functionality

## Support
For migration assistance, refer to:
- Provider documentation
- Migration scripts in /tools/migration/
- Validation tools in /tools/validation/
"""
```

### 7. Cost Transparency and Comparison
**MANDATORY**: Provide transparent cost comparison between providers
```python
# REQUIRED: Cost comparison and transparency
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class UsagePattern:
    """Pattern of usage for cost comparison."""
    requests_per_minute: int
    requests_per_day: int
    model_size: str
    data_volume: int # in MB

@dataclass
class CostComparison:
    """Comparison of costs between providers for a given usage pattern."""
    usage_pattern: UsagePattern
    provider_costs: Dict[str, float]
    recommendations: List[str]

@dataclass
class FreeTierComparison:
    """Comparison of free tier offerings between providers."""
    providers: Dict[str, Dict[str, Any]]

class CostComparisonService:
    """Provides cost comparison between different providers."""
    
    def __init__(self):
        self.provider_costs = self._load_provider_costs()
    
    def compare_provider_costs(self, usage_pattern: UsagePattern) -> CostComparison:
        """Compare costs between providers for given usage pattern."""
        
        comparisons = {}
        for provider in self.provider_costs:
            cost = self._calculate_provider_cost(provider, usage_pattern)
            comparisons[provider] = cost
        
        return CostComparison(
            usage_pattern=usage_pattern,
            provider_costs=comparisons,
            recommendations=self._generate_cost_recommendations(comparisons)
        )
    
    def get_free_tier_comparison(self) -> FreeTierComparison:
        """Compare free tier offerings between providers."""
        return FreeTierComparison(
            providers={
                "gemini": {
                    "requests_per_minute": 60,
                    "requests_per_day": 1500,
                    "cost": 0.0,
                    "limitations": ["No advanced features", "Rate limited"]
                },
                "openai": {
                    "requests_per_minute": 0,
                    "requests_per_day": 0,
                    "cost": 0.0,
                    "limitations": ["No free tier", "Credit card required"]
                },
                "anthropic": {
                    "requests_per_minute": 0,
                    "requests_per_day": 0,
                    "cost": 0.0,
                    "limitations": ["No free tier", "Credit card required"]
                },
                "local": {
                    "requests_per_minute": "unlimited",
                    "requests_per_day": "unlimited",
                    "cost": 0.0,
                    "limitations": ["Hardware requirements", "Setup complexity"]
                }
            }
        )
```

### 8. Provider Health Monitoring
**MANDATORY**: Monitor provider health and availability
```python
# REQUIRED: Provider health monitoring
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class HealthStatus:
    """Health status of a provider."""
    provider: str
    status: str
    error: Optional[str] = None

@dataclass
class ProviderRecommendation:
    """Recommendation for provider selection."""
    provider: str
    reason: str

@dataclass
class AvailabilityMetrics:
    """Metrics for real-time availability of providers."""
    providers: Dict[str, float] # Percentage of availability
    recommendations: List[ProviderRecommendation]

class ProviderHealthMonitor:
    """Monitors health and availability of all providers."""
    
    def __init__(self):
        self.health_checks = {}
        self.availability_metrics = {}
    
    async def check_provider_health(self, provider: str) -> HealthStatus:
        """Check health status of a specific provider."""
        
        if provider == "gemini":
            return await self._check_gemini_health()
        elif provider == "openai":
            return await self._check_openai_health()
        elif provider == "anthropic":
            return await self._check_anthropic_health()
        elif provider == "local":
            return await self._check_local_health()
        else:
            return HealthStatus(
                provider=provider,
                status="unknown",
                error="Unsupported provider"
            )
    
    async def get_provider_recommendations(self) -> List[ProviderRecommendation]:
        """Get recommendations for provider selection based on health and cost."""
        
        health_statuses = {}
        for provider in ["gemini", "openai", "anthropic", "local"]:
            health_statuses[provider] = await self.check_provider_health(provider)
        
        return self._generate_recommendations(health_statuses)
    
    async def monitor_provider_availability(self) -> AvailabilityMetrics:
        """Monitor real-time availability of all providers."""
        
        metrics = {}
        for provider in ["gemini", "openai", "anthropic", "local"]:
            metrics[provider] = await self._measure_availability(provider)
        
        return AvailabilityMetrics(
            providers=metrics,
            recommendations=self._generate_availability_recommendations(metrics)
        )
```

## Implementation Guidelines

### 1. Provider Factory Pattern
```python
# REQUIRED: Use factory pattern for provider creation
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ProviderFactory:
    """Factory for creating provider instances."""
    
    @staticmethod
    def create_llm_provider(provider_type: str, config: Dict[str, Any]) -> LLMProvider:
        """Create LLM provider instance."""
        providers = {
            "gemini": GeminiProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "local": LocalLLMProvider
        }
        
        if provider_type not in providers:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        return providers[provider_type](config)
    
    @staticmethod
    def create_workflow_framework(framework_type: str, config: Dict[str, Any]) -> WorkflowFramework:
        """Create workflow framework instance."""
        frameworks = {
            "langgraph": LangGraphFramework,
            "langchain": LangChainFramework,
            "autogen": AutoGenFramework,
            "custom": CustomWorkflowFramework
        }
        
        if framework_type not in frameworks:
            raise ValueError(f"Unsupported framework: {framework_type}")
        
        return frameworks[framework_type](config)
```

### 2. Configuration Validation
```python
# REQUIRED: Validate provider configurations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class ValidationResult:
    """Result of provider configuration validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)

class ProviderConfigValidator:
    """Validates provider configurations."""
    
    def validate_llm_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate LLM provider configuration."""
        
        required_fields = ["provider", "api_key", "model"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                errors=[f"Missing required field: {field}" for field in missing_fields]
            )
        
        # Provider-specific validation
        if config["provider"] == "gemini":
            return self._validate_gemini_config(config)
        elif config["provider"] == "openai":
            return self._validate_openai_config(config)
        elif config["provider"] == "anthropic":
            return self._validate_anthropic_config(config)
        elif config["provider"] == "local":
            return self._validate_local_config(config)
        else:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unsupported provider: {config['provider']}"]
            )
```

### 3. Migration Testing
```python
# REQUIRED: Test migration procedures
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class TestResult:
    """Result of a migration test."""
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class MigrationTester:
    """Tests migration procedures between providers."""
    
    async def test_migration(self, from_provider: str, to_provider: str) -> TestResult:
        """Test migration from one provider to another."""
        
        # Create test data
        test_data = self._create_test_data()
        
        # Export from source provider
        exported_data = await self._export_from_provider(from_provider, test_data)
        
        # Import to target provider
        import_result = await self._import_to_provider(to_provider, exported_data)
        
        # Validate migration
        validation_result = await self._validate_migration(test_data, import_result)
        
        return TestResult(
            success=validation_result.is_successful,
            details=validation_result.details,
            recommendations=validation_result.recommendations
        )
```

## Benefits

- **Freedom of Choice**: Users can choose any provider without lock-in
- **Cost Optimization**: Easy comparison and migration between providers
- **Risk Mitigation**: No dependency on single provider availability
- **Future-Proofing**: System remains relevant as new providers emerge
- **Competitive Pricing**: Providers compete for users, driving down costs
- **Innovation**: Access to best features from multiple providers

## Monitoring

### Success Metrics:
- Number of supported providers per component
- Migration success rate between providers
- Cost savings from provider optimization
- User satisfaction with provider choice
- Time to migrate between providers

### Failure Indicators:
- Single provider dependency
- Proprietary data formats
- Difficult migration procedures
- High migration costs
- Limited provider options

## Remember

**"Freedom of choice is freedom from lock-in."**

**"Open standards enable open competition."**

**"Portability is the foundation of user sovereignty."**

This rule is **ALWAYS APPLIED** and must be followed for all:
- Provider selection and integration
- Data storage and management
- API design and implementation
- Configuration management
- Migration procedures
- Cost optimization

**Violations of this rule require immediate remediation to restore provider freedom and choice.**
