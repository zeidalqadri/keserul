import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from models import PromptRequest, PromptResponse, RunSummary, ErrorResponse
from typing import Optional, List
import uuid
import datetime
import time
import logging
import sys
import os

from fastapi_auth_oidc import OIDCAuthFactory
from prometheus_client import Histogram # Import Histogram

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# We'll handle optimizer imports dynamically to avoid path issues
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from prompt_optimizer_bot.utils.optimize_prompt import optimize_prompt
    from shared.cost_manager import get_cost_manager, CostReport
    optimizer_available = True
except ImportError as e:
    logger.warning(f"Optimizer dependencies not available: {e}")
    optimizer_available = False
    # Create stub classes to prevent import errors
    class CostReport:
        def __init__(self):
            self.total_cost = 0.0
            self.prompt_tokens = 0
            self.completion_tokens = 0
            self.run_id = ""
    
    def optimize_prompt(*args, **kwargs):
        raise HTTPException(status_code=503, detail="Optimizer service not available")
    
    def get_cost_manager():
        class DummyCostManager:
            def track_cost(self, *args, **kwargs):
                pass
            def get_total_cost(self):
                return 0.0
        return DummyCostManager()

# Load environment variables
load_dotenv()

# Configure OIDC
OIDC_ISSUER_URL = os.getenv("OIDC_ISSUER_URL")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")
OIDC_ROLES_CLAIM = os.getenv("OIDC_ROLES_CLAIM", "roles") # Default to 'roles' if not specified

if not all([OIDC_ISSUER_URL, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET]):
    logger.warning("Missing one or more OIDC environment variables. OIDC authentication will be disabled.")
    oidc_enabled = False
else:
    oidc_enabled = True
    # Create OIDC auth factory with issuer URL
    # The package will automatically discover configuration from the issuer
    OIDCAuth = OIDCAuthFactory(issuer=OIDC_ISSUER_URL)

app = FastAPI()

# Define Prometheus metrics for API latency
REQUEST_LATENCY_HISTOGRAM = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# Middleware to track API latency
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Exclude health check from metrics for cleaner data
    endpoint = request.url.path
    if endpoint != "/health":
        REQUEST_LATENCY_HISTOGRAM.labels(method=request.method, endpoint=endpoint).observe(process_time)
        logger.info(f"Request {request.method} {endpoint} took {process_time:.4f}s")

    return response

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5173",  # Default Vite development server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CostManager (it will start Prometheus server if enabled)
cost_manager = get_cost_manager() if optimizer_available else None

# In-memory store for completed optimization runs
# This will store CostReport objects directly and be used by /optimizer/runs
completed_optimization_runs: List[CostReport] = []

# In-memory cache for /optimizer/runs endpoint
runs_cache = {
    "data": None,
    "timestamp": 0.0
}

# Dependency to get current user and check roles
def get_current_user(user: dict = Depends(OIDCAuth() if oidc_enabled else lambda: {"sub": "anonymous", "roles": ["operator", "observer"]})):
    if not oidc_enabled:
        return {"sub": "anonymous", "roles": ["operator", "observer"]} # Allow all if OIDC is disabled for local dev
    return user

def check_roles(required_roles: List[str]):
    def role_checker(user: dict = Depends(get_current_user)):
        user_roles = user.get(OIDC_ROLES_CLAIM, [])
        if not isinstance(user_roles, list):
            user_roles = [user_roles] # Handle case where roles claim is a single string
        
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user
    return role_checker


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/optimizer/runs", response_model=List[RunSummary], responses={404: {"model": ErrorResponse}})
async def get_optimization_runs(
    limit: int = Query(10, ge=1, le=100, description="Number of recent runs to fetch"),
    since: Optional[str] = Query(None, description="Fetch runs since this ISO-formatted timestamp"),
    current_user: dict = Depends(check_roles(["observer", "operator"]))
):
    """Fetches recent prompt optimization runs."""
    current_time = time.time()
    # Check if cache is valid (e.g., within 2 seconds)
    if runs_cache["data"] is not None and (current_time - runs_cache["timestamp"]) < 2:
        logger.info("Returning /optimizer/runs from cache.")
        return runs_cache["data"][:limit] # Ensure limit is applied to cached data

    # Convert stored CostReport objects to RunSummary for API response
    summaries = []
    for report in reversed(completed_optimization_runs): # Show most recent first
        if since:
            # TODO: Implement proper timestamp filtering if needed for large data sets
            pass
        
        summaries.append(RunSummary(
            run_id=report.metadata.get("run_id", "unknown"),
            timestamp=datetime.datetime.fromtimestamp(report.start_time).isoformat(),
            original_prompt_snippet=report.metadata.get("original_prompt_snippet", ""),
            cost=report.total_cost,
            tokens=report.total_tokens,
            latency=report.duration(),
            status=report.metadata.get("status", "unknown")
        ))
    
    # Cache the new data
    runs_cache["data"] = summaries
    runs_cache["timestamp"] = current_time

    return summaries[:limit]

@app.post("/optimizer/optimize", response_model=PromptResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def trigger_optimization(
    request: PromptRequest,
    current_user: dict = Depends(check_roles(["operator"]))
):
    """Triggers a manual prompt optimization run and returns the result."""
    operation_id = str(uuid.uuid4())
    original_prompt_snippet = request.prompt[:100] + "..." if len(request.prompt) > 100 else request.prompt

    # Start cost tracking for this operation
    operation_report = cost_manager.start_operation(
        operation_name="prompt_optimization",
        metadata={
            "run_id": operation_id,
            "original_prompt_snippet": original_prompt_snippet,
            "strategy": request.strategy,
            "user_sub": current_user.get("sub"), # Add user info to metadata
            "user_roles": current_user.get(OIDC_ROLES_CLAIM)
        }
    )

    optimized_prompt = ""
    status = "failure"
    error_message = None

    try:
        # Call the actual optimization function
        # Provide a dummy expected_output as it's required by optimize_prompt but not from frontend
        optimized_prompt = optimize_prompt(
            user_message=request.prompt,
            expected_output="This is a dummy expected output for optimization evaluation.",
            strategy=request.strategy or "orchestrator"  # Provide a default strategy if None
        )
        status = "success"

    except Exception as e:
        logger.error(f"Prompt optimization failed for run {operation_id}: {e}")
        error_message = str(e)
    finally:
        # Finalize the operation report regardless of success or failure
        if operation_report:
            operation_report.metadata["status"] = status
            cost_manager.complete_operation("prompt_optimization")
            completed_optimization_runs.append(operation_report)

        # Invalidate the /optimizer/runs cache
        runs_cache["data"] = None
        runs_cache["timestamp"] = 0.0

        # Ensure optimized_prompt is a string
        if not isinstance(optimized_prompt, str):
            optimized_prompt = str(optimized_prompt) # Coerce to string if not already

        return PromptResponse(
            optimized_prompt=optimized_prompt.strip(),
            cost=operation_report.total_cost,
            tokens=operation_report.total_tokens,
            latency=operation_report.duration(),
            status=status,
            error_message=error_message
        ) 