from functools import wraps
import sentry_sdk
from flask import current_app
from prometheus_flask_exporter import PrometheusMetrics
from elasticapm.contrib.flask import ElasticAPM

def init_monitoring(app):
    """Initialize monitoring and error tracking"""
    
    # Sentry error tracking
    sentry_sdk.init(
        dsn=app.config.get('SENTRY_DSN'),
        environment=app.config.get('ENV'),
        traces_sample_rate=1.0,
        profiles_sample_rate=0.5,
    )
    
    # Prometheus metrics
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Application info', version='1.0.0')
    
    # Request latency metrics
    metrics.histogram(
        'http_request_duration_seconds',
        'HTTP request latency',
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
    )
    
    # Custom business metrics
    metrics.counter(
        'mental_health_checks_total',
        'Number of mental health checks performed'
    )
    metrics.counter(
        'ai_suggestions_total',
        'Number of AI suggestions generated'
    )
    metrics.counter(
        'high_risk_cases_total',
        'Number of high risk cases detected'
    )
    
    # Elastic APM for performance monitoring
    apm = ElasticAPM(app)
    
    # Decorator for tracking high-risk cases
    def track_high_risk(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, dict) and result.get('risk_flag'):
                metrics.counter('high_risk_cases_total').inc()
            return result
        return decorated_function
    
    # Decorator for tracking AI usage
    def track_ai_usage(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            metrics.counter('ai_suggestions_total').inc()
            return result
        return decorated_function
    
    return {
        'metrics': metrics,
        'apm': apm,
        'track_high_risk': track_high_risk,
        'track_ai_usage': track_ai_usage
    }