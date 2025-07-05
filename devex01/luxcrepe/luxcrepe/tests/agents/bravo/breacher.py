"""
Breacher Agent - Bravo Fire Team Specialist
Stress testing, boundary pushing, and defensive barrier penetration
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ...base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority
from ....core.scraper import LuxcrepeScraper
from ....core.utils import RetrySession, RateLimiter


class BreacherAgent(BaseAgent):
    """Breacher Agent - Bravo Fire Team Specialist
    
    Responsibilities:
    - Stress testing and load generation
    - Rate limiting and defensive barrier testing
    - Boundary condition exploration
    - System resilience validation
    - Defensive measure circumvention
    """
    
    def __init__(self):
        super().__init__(
            agent_id="BRAVO-002",
            call_sign="SLEDGEHAMMER",
            squad="bravo"
        )
        
        # Breacher capabilities
        self.weapons_systems = [
            "STRESS_TESTING_ARRAY",
            "RATE_LIMIT_BREAKER",
            "BOUNDARY_TESTER",
            "BARRIER_PENETRATOR"
        ]
        
        self.equipment = {
            "load_generators": "OPERATIONAL",
            "stress_tools": "ARMED",
            "barrier_breakers": "READY",
            "resilience_testers": "ACTIVE"
        }
        
        self.intelligence_sources = [
            "STRESS_TEST_RESULTS",
            "BARRIER_RESPONSE_DATA",
            "LOAD_PERFORMANCE_METRICS",
            "SYSTEM_BREAKING_POINTS"
        ]
        
        # Breaching data
        self.stress_test_results: List[Dict[str, Any]] = []
        self.barrier_analysis: Dict[str, Any] = {}
        self.breaking_points: Dict[str, Any] = {}
        self.resilience_metrics: Dict[str, Any] = {}
        
        # Breaching configuration
        self.max_concurrent_requests = 50
        self.stress_test_duration = 30  # seconds
        self.boundary_test_parameters = {
            "max_request_rate": 100,  # requests per second
            "timeout_variations": [1, 5, 10, 30, 60],
            "payload_sizes": [1, 100, 1000, 10000, 100000],  # bytes
            "connection_persistence": [True, False]
        }
        
        self.logger.info("SLEDGEHAMMER: Breacher initialized - Ready to breach defenses")
    
    def get_capabilities(self) -> List[str]:
        """Return breacher capabilities"""
        return [
            "stress_testing",
            "load_generation",
            "rate_limit_testing",
            "boundary_exploration",
            "barrier_penetration",
            "resilience_validation",
            "defensive_circumvention",
            "breaking_point_analysis",
            "system_overload_testing",
            "concurrent_request_handling"
        ]
    
    async def execute_mission(self, mission_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute breacher stress testing and barrier penetration mission"""
        
        self.logger.info("SLEDGEHAMMER: Beginning barrier penetration operations")
        
        target_urls = mission_parameters.get("target_urls", [])
        if not target_urls:
            raise Exception("No targets provided for breaching operations")
        
        # Breaching Phase 1: Defensive Barrier Analysis
        barrier_analysis = await self._analyze_defensive_barriers(target_urls)
        
        # Breaching Phase 2: Stress Testing Operations
        stress_results = await self._conduct_stress_testing(target_urls)
        
        # Breaching Phase 3: Rate Limiting Penetration
        rate_limit_results = await self._test_rate_limiting_barriers(target_urls)
        
        # Breaching Phase 4: Boundary Condition Testing
        boundary_results = await self._test_boundary_conditions(target_urls)
        
        # Breaching Phase 5: System Resilience Validation
        resilience_results = await self._validate_system_resilience(target_urls)
        
        self.logger.info("SLEDGEHAMMER: Barrier penetration complete - All defenses tested")
        
        return {
            "barrier_analysis": barrier_analysis,
            "stress_test_results": stress_results,
            "rate_limiting_tests": rate_limit_results,
            "boundary_condition_tests": boundary_results,
            "resilience_validation": resilience_results,
            "breaking_points_identified": self.breaking_points,
            "penetration_success_rate": self._calculate_penetration_success_rate()
        }
    
    async def _analyze_defensive_barriers(self, target_urls: List[str]) -> Dict[str, Any]:
        """Analyze defensive barriers and protection mechanisms"""
        
        self.logger.info("SLEDGEHAMMER: Analyzing defensive barriers")
        
        analysis = {
            "analysis_type": "DEFENSIVE_BARRIER_ASSESSMENT",
            "targets": {},
            "common_defenses": [],
            "weak_points": [],
            "breach_strategies": {}
        }
        
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            self.logger.debug(f"SLEDGEHAMMER: Analyzing barriers for {url}")
            
            try:
                # Test basic response characteristics
                response = requests.get(url, timeout=10)
                headers = response.headers
                
                barrier_data = {
                    "url": url,
                    "response_time": 0,
                    "server_type": headers.get("server", "UNKNOWN"),
                    "protection_layers": [],
                    "rate_limiting": False,
                    "connection_limits": False,
                    "timeout_handling": "UNKNOWN",
                    "barrier_strength": 0
                }
                
                # Check for protection layers
                protection_indicators = {
                    "cloudflare": ["cf-ray", "cloudflare"],
                    "incapsula": ["incap_ses", "x-iinfo"],
                    "akamai": ["akamai", "x-akamai"],
                    "rate_limiting": ["x-ratelimit", "retry-after"],
                    "load_balancer": ["x-forwarded-for", "x-real-ip"]
                }
                
                for protection, indicators in protection_indicators.items():
                    if any(indicator in str(headers).lower() for indicator in indicators):
                        barrier_data["protection_layers"].append(protection.upper())
                        barrier_data["barrier_strength"] += 2
                
                # Test initial rate limiting
                rate_test = await self._quick_rate_test(url)
                barrier_data["rate_limiting"] = rate_test["detected"]
                if rate_test["detected"]:
                    barrier_data["barrier_strength"] += 3
                
                analysis["targets"][target_id] = barrier_data
                self.barrier_analysis[target_id] = barrier_data
                
                # Identify weak points
                if barrier_data["barrier_strength"] < 3:
                    analysis["weak_points"].append({
                        "target_id": target_id,
                        "weakness": "LOW_BARRIER_STRENGTH",
                        "score": barrier_data["barrier_strength"]
                    })
                
            except Exception as e:
                analysis["targets"][target_id] = {
                    "url": url,
                    "analysis_error": str(e),
                    "barrier_strength": 10  # Unknown = assume strong
                }
        
        # Generate breach strategies
        analysis["breach_strategies"] = self._generate_breach_strategies(analysis)
        
        return analysis
    
    async def _conduct_stress_testing(self, target_urls: List[str]) -> Dict[str, Any]:
        """Conduct comprehensive stress testing"""
        
        self.logger.info("SLEDGEHAMMER: Conducting stress testing operations")
        
        stress_results = {
            "test_type": "STRESS_TESTING",
            "targets": {},
            "load_profiles": [],
            "performance_degradation": {},
            "system_limits": {}
        }
        
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            self.logger.info(f"SLEDGEHAMMER: Stress testing {url}")
            
            try:
                # Progressive load testing
                load_results = await self._progressive_load_test(url)
                
                # Concurrent connection testing
                connection_results = await self._concurrent_connection_test(url)
                
                # Sustained load testing
                sustained_results = await self._sustained_load_test(url)
                
                target_stress_data = {
                    "url": url,
                    "progressive_load": load_results,
                    "concurrent_connections": connection_results,
                    "sustained_load": sustained_results,
                    "breaking_point": self._identify_breaking_point(load_results, connection_results),
                    "resilience_score": self._calculate_resilience_score(load_results, sustained_results)
                }
                
                stress_results["targets"][target_id] = target_stress_data
                self.stress_test_results.append(target_stress_data)
                
                # Update breaking points
                if target_stress_data["breaking_point"]["detected"]:
                    self.breaking_points[target_id] = target_stress_data["breaking_point"]
                
            except Exception as e:
                stress_results["targets"][target_id] = {
                    "url": url,
                    "stress_test_error": str(e)
                }
        
        return stress_results
    
    async def _test_rate_limiting_barriers(self, target_urls: List[str]) -> Dict[str, Any]:
        """Test rate limiting barriers and circumvention techniques"""
        
        self.logger.info("SLEDGEHAMMER: Testing rate limiting barriers")
        
        rate_results = {
            "test_type": "RATE_LIMITING_PENETRATION",
            "targets": {},
            "circumvention_techniques": [],
            "success_rates": {}
        }
        
        circumvention_techniques = [
            {"name": "USER_AGENT_ROTATION", "method": self._test_user_agent_rotation},
            {"name": "IP_ROTATION_SIMULATION", "method": self._test_ip_rotation_simulation},
            {"name": "REQUEST_TIMING_VARIATION", "method": self._test_timing_variation},
            {"name": "HEADER_MANIPULATION", "method": self._test_header_manipulation},
            {"name": "SESSION_ROTATION", "method": self._test_session_rotation}
        ]
        
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            self.logger.debug(f"SLEDGEHAMMER: Rate limit testing {url}")
            
            target_results = {
                "url": url,
                "baseline_rate_limit": None,
                "circumvention_results": {},
                "successful_techniques": [],
                "penetration_success": False
            }
            
            try:
                # Establish baseline rate limit
                baseline = await self._establish_rate_limit_baseline(url)
                target_results["baseline_rate_limit"] = baseline
                
                # Test circumvention techniques
                for technique in circumvention_techniques:
                    technique_name = technique["name"]
                    self.logger.debug(f"SLEDGEHAMMER: Testing {technique_name}")
                    
                    result = await technique["method"](url, baseline)
                    target_results["circumvention_results"][technique_name] = result
                    
                    if result.get("success", False):
                        target_results["successful_techniques"].append(technique_name)
                        target_results["penetration_success"] = True
                
                rate_results["targets"][target_id] = target_results
                
                # Track success rates
                if target_results["successful_techniques"]:
                    rate_results["success_rates"][target_id] = {
                        "techniques_tested": len(circumvention_techniques),
                        "successful_techniques": len(target_results["successful_techniques"]),
                        "success_rate": len(target_results["successful_techniques"]) / len(circumvention_techniques)
                    }
                
            except Exception as e:
                target_results["rate_test_error"] = str(e)
                rate_results["targets"][target_id] = target_results
        
        return rate_results
    
    async def _test_boundary_conditions(self, target_urls: List[str]) -> Dict[str, Any]:
        """Test boundary conditions and edge cases"""
        
        self.logger.info("SLEDGEHAMMER: Testing boundary conditions")
        
        boundary_results = {
            "test_type": "BOUNDARY_CONDITION_TESTING",
            "targets": {},
            "edge_cases": [],
            "boundary_violations": []
        }
        
        boundary_tests = [
            {"name": "EXTREME_TIMEOUTS", "method": self._test_timeout_boundaries},
            {"name": "PAYLOAD_SIZE_LIMITS", "method": self._test_payload_boundaries},
            {"name": "CONNECTION_PERSISTENCE", "method": self._test_connection_boundaries},
            {"name": "HEADER_SIZE_LIMITS", "method": self._test_header_boundaries},
            {"name": "CONCURRENT_LIMITS", "method": self._test_concurrency_boundaries}
        ]
        
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            self.logger.debug(f"SLEDGEHAMMER: Boundary testing {url}")
            
            target_boundary_data = {
                "url": url,
                "boundary_test_results": {},
                "violations_found": [],
                "system_limits": {}
            }
            
            try:
                for test in boundary_tests:
                    test_name = test["name"]
                    self.logger.debug(f"SLEDGEHAMMER: Running {test_name}")
                    
                    result = await test["method"](url)
                    target_boundary_data["boundary_test_results"][test_name] = result
                    
                    if result.get("violation_detected", False):
                        target_boundary_data["violations_found"].append({
                            "test": test_name,
                            "violation": result.get("violation_details", "Unknown")
                        })
                    
                    if "limit_identified" in result:
                        target_boundary_data["system_limits"][test_name] = result["limit_identified"]
                
                boundary_results["targets"][target_id] = target_boundary_data
                
                if target_boundary_data["violations_found"]:
                    boundary_results["boundary_violations"].extend(target_boundary_data["violations_found"])
                
            except Exception as e:
                target_boundary_data["boundary_test_error"] = str(e)
                boundary_results["targets"][target_id] = target_boundary_data
        
        return boundary_results
    
    async def _validate_system_resilience(self, target_urls: List[str]) -> Dict[str, Any]:
        """Validate system resilience under various conditions"""
        
        self.logger.info("SLEDGEHAMMER: Validating system resilience")
        
        resilience_results = {
            "validation_type": "SYSTEM_RESILIENCE",
            "targets": {},
            "resilience_scores": {},
            "failure_modes": [],
            "recovery_capabilities": {}
        }
        
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            self.logger.debug(f"SLEDGEHAMMER: Resilience testing {url}")
            
            try:
                # Test various resilience scenarios
                scenarios = [
                    {"name": "GRADUAL_LOAD_INCREASE", "method": self._test_gradual_load_resilience},
                    {"name": "SUDDEN_SPIKE", "method": self._test_spike_resilience},
                    {"name": "SUSTAINED_PRESSURE", "method": self._test_sustained_pressure_resilience},
                    {"name": "INTERMITTENT_BURSTS", "method": self._test_burst_resilience},
                    {"name": "RECOVERY_TIME", "method": self._test_recovery_resilience}
                ]
                
                target_resilience = {
                    "url": url,
                    "scenario_results": {},
                    "overall_resilience_score": 0,
                    "weak_points": [],
                    "strengths": []
                }
                
                scenario_scores = []
                
                for scenario in scenarios:
                    scenario_name = scenario["name"]
                    result = await scenario["method"](url)
                    
                    target_resilience["scenario_results"][scenario_name] = result
                    scenario_scores.append(result.get("resilience_score", 0))
                    
                    if result.get("resilience_score", 0) < 0.6:
                        target_resilience["weak_points"].append(scenario_name)
                    elif result.get("resilience_score", 0) > 0.8:
                        target_resilience["strengths"].append(scenario_name)
                
                # Calculate overall resilience score
                if scenario_scores:
                    target_resilience["overall_resilience_score"] = sum(scenario_scores) / len(scenario_scores)
                
                resilience_results["targets"][target_id] = target_resilience
                resilience_results["resilience_scores"][target_id] = target_resilience["overall_resilience_score"]
                
                self.resilience_metrics[target_id] = target_resilience
                
            except Exception as e:
                resilience_results["targets"][target_id] = {
                    "url": url,
                    "resilience_test_error": str(e),
                    "overall_resilience_score": 0
                }
        
        return resilience_results
    
    async def _quick_rate_test(self, url: str) -> Dict[str, Any]:
        """Quick test to detect rate limiting"""
        try:
            responses = []
            for i in range(5):
                start_time = time.time()
                response = requests.head(url, timeout=5)
                end_time = time.time()
                
                responses.append({
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "headers": dict(response.headers)
                })
                
                if response.status_code == 429:
                    return {"detected": True, "type": "HTTP_429", "request_number": i+1}
                
                await asyncio.sleep(0.1)
            
            # Check for progressive slowdown
            times = [r["response_time"] for r in responses]
            if len(times) >= 3 and times[-1] > times[0] * 2:
                return {"detected": True, "type": "PROGRESSIVE_SLOWDOWN", "responses": responses}
            
            return {"detected": False, "responses": responses}
            
        except Exception as e:
            return {"detected": False, "error": str(e)}
    
    async def _progressive_load_test(self, url: str) -> Dict[str, Any]:
        """Progressive load testing with increasing request rates"""
        self.logger.debug(f"SLEDGEHAMMER: Progressive load test on {url}")
        
        load_results = {
            "test_phases": [],
            "performance_degradation": False,
            "breaking_point_detected": False,
            "max_sustainable_rate": 0
        }
        
        # Test different request rates: 1, 5, 10, 20, 50 requests per second
        test_rates = [1, 5, 10, 20, 50]
        
        for rate in test_rates:
            phase_start = time.time()
            
            # Run test for 10 seconds at this rate
            test_duration = 10
            total_requests = rate * test_duration
            
            successes = 0
            failures = 0
            response_times = []
            
            try:
                # Use ThreadPoolExecutor for concurrent requests
                with ThreadPoolExecutor(max_workers=min(rate, 20)) as executor:
                    futures = []
                    
                    for i in range(total_requests):
                        future = executor.submit(self._single_request, url)
                        futures.append(future)
                        
                        # Maintain target rate
                        if i < total_requests - 1:
                            time.sleep(1.0 / rate)
                    
                    # Collect results
                    for future in as_completed(futures, timeout=30):
                        try:
                            result = future.result()
                            if result["success"]:
                                successes += 1
                                response_times.append(result["response_time"])
                            else:
                                failures += 1
                        except Exception:
                            failures += 1
            
            except Exception as e:
                failures = total_requests
            
            phase_duration = time.time() - phase_start
            success_rate = successes / total_requests if total_requests > 0 else 0
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            phase_result = {
                "target_rate": rate,
                "actual_duration": phase_duration,
                "total_requests": total_requests,
                "successful_requests": successes,
                "failed_requests": failures,
                "success_rate": success_rate,
                "average_response_time": avg_response_time
            }
            
            load_results["test_phases"].append(phase_result)
            
            # Check for breaking point
            if success_rate < 0.8:
                load_results["breaking_point_detected"] = True
                break
            else:
                load_results["max_sustainable_rate"] = rate
            
            # Small delay between phases
            await asyncio.sleep(2)
        
        # Analyze performance degradation
        if len(load_results["test_phases"]) >= 2:
            first_phase = load_results["test_phases"][0]
            last_phase = load_results["test_phases"][-1]
            
            if last_phase["average_response_time"] > first_phase["average_response_time"] * 1.5:
                load_results["performance_degradation"] = True
        
        return load_results
    
    async def _concurrent_connection_test(self, url: str) -> Dict[str, Any]:
        """Test concurrent connection handling"""
        self.logger.debug(f"SLEDGEHAMMER: Concurrent connection test on {url}")
        
        connection_results = {
            "max_concurrent_tested": 0,
            "connection_limits": {},
            "connection_handling": "UNKNOWN"
        }
        
        # Test different levels of concurrent connections
        concurrency_levels = [5, 10, 25, 50, 100]
        
        for concurrency in concurrency_levels:
            if concurrency > self.max_concurrent_requests:
                break
            
            try:
                start_time = time.time()
                
                # Create concurrent requests
                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    futures = [executor.submit(self._single_request, url) for _ in range(concurrency)]
                    
                    successes = 0
                    failures = 0
                    
                    for future in as_completed(futures, timeout=30):
                        try:
                            result = future.result()
                            if result["success"]:
                                successes += 1
                            else:
                                failures += 1
                        except Exception:
                            failures += 1
                
                end_time = time.time()
                success_rate = successes / concurrency
                
                connection_results["connection_limits"][concurrency] = {
                    "success_rate": success_rate,
                    "total_time": end_time - start_time,
                    "successful_connections": successes,
                    "failed_connections": failures
                }
                
                connection_results["max_concurrent_tested"] = concurrency
                
                # If success rate drops below 80%, we've likely hit a limit
                if success_rate < 0.8:
                    connection_results["connection_handling"] = f"LIMITED_AT_{concurrency}"
                    break
                
            except Exception as e:
                connection_results["connection_limits"][concurrency] = {"error": str(e)}
                break
        
        if connection_results["connection_handling"] == "UNKNOWN":
            connection_results["connection_handling"] = "ROBUST"
        
        return connection_results
    
    async def _sustained_load_test(self, url: str) -> Dict[str, Any]:
        """Test sustained load over time"""
        self.logger.debug(f"SLEDGEHAMMER: Sustained load test on {url}")
        
        sustained_results = {
            "test_duration": self.stress_test_duration,
            "target_rate": 10,  # 10 requests per second
            "performance_over_time": [],
            "stability_score": 0
        }
        
        start_time = time.time()
        end_time = start_time + self.stress_test_duration
        
        # Measure performance in 5-second intervals
        interval_duration = 5
        
        while time.time() < end_time:
            interval_start = time.time()
            interval_requests = sustained_results["target_rate"] * interval_duration
            
            successes = 0
            response_times = []
            
            try:
                for i in range(interval_requests):
                    if time.time() >= end_time:
                        break
                    
                    result = self._single_request(url)
                    if result["success"]:
                        successes += 1
                        response_times.append(result["response_time"])
                    
                    time.sleep(1.0 / sustained_results["target_rate"])
                
                interval_end = time.time()
                interval_performance = {
                    "interval_start": interval_start - start_time,
                    "interval_duration": interval_end - interval_start,
                    "requests_attempted": interval_requests,
                    "successful_requests": successes,
                    "success_rate": successes / interval_requests if interval_requests > 0 else 0,
                    "average_response_time": sum(response_times) / len(response_times) if response_times else 0
                }
                
                sustained_results["performance_over_time"].append(interval_performance)
                
            except Exception as e:
                break
        
        # Calculate stability score
        if sustained_results["performance_over_time"]:
            success_rates = [p["success_rate"] for p in sustained_results["performance_over_time"]]
            avg_success_rate = sum(success_rates) / len(success_rates)
            success_rate_variance = sum((sr - avg_success_rate) ** 2 for sr in success_rates) / len(success_rates)
            
            # Stability score: high average success rate with low variance
            sustained_results["stability_score"] = avg_success_rate * (1 - success_rate_variance)
        
        return sustained_results
    
    def _single_request(self, url: str) -> Dict[str, Any]:
        """Make a single request and return results"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "content_length": len(response.content) if response.content else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "content_length": 0
            }
    
    def _identify_breaking_point(self, load_results: Dict[str, Any], 
                                connection_results: Dict[str, Any]) -> Dict[str, Any]:
        """Identify system breaking points"""
        breaking_point = {
            "detected": False,
            "type": "NONE",
            "threshold": None,
            "details": {}
        }
        
        # Check load test results
        if load_results.get("breaking_point_detected", False):
            breaking_point["detected"] = True
            breaking_point["type"] = "LOAD_THRESHOLD"
            breaking_point["threshold"] = load_results.get("max_sustainable_rate", 0)
            breaking_point["details"]["load_limit"] = load_results["max_sustainable_rate"]
        
        # Check connection results
        connection_limits = connection_results.get("connection_limits", {})
        for concurrency, data in connection_limits.items():
            if isinstance(data, dict) and data.get("success_rate", 1.0) < 0.8:
                breaking_point["detected"] = True
                if breaking_point["type"] == "NONE":
                    breaking_point["type"] = "CONNECTION_LIMIT"
                else:
                    breaking_point["type"] = "MULTIPLE_LIMITS"
                breaking_point["threshold"] = concurrency
                breaking_point["details"]["connection_limit"] = concurrency
                break
        
        return breaking_point
    
    def _calculate_resilience_score(self, load_results: Dict[str, Any], 
                                  sustained_results: Dict[str, Any]) -> float:
        """Calculate overall resilience score"""
        score_components = []
        
        # Load resilience component
        if load_results.get("max_sustainable_rate", 0) >= 20:
            score_components.append(0.9)
        elif load_results.get("max_sustainable_rate", 0) >= 10:
            score_components.append(0.7)
        elif load_results.get("max_sustainable_rate", 0) >= 5:
            score_components.append(0.5)
        else:
            score_components.append(0.2)
        
        # Stability component
        stability_score = sustained_results.get("stability_score", 0)
        score_components.append(stability_score)
        
        # Performance degradation penalty
        if load_results.get("performance_degradation", False):
            score_components.append(0.3)
        else:
            score_components.append(0.8)
        
        return sum(score_components) / len(score_components) if score_components else 0.0
    
    async def _establish_rate_limit_baseline(self, url: str) -> Dict[str, Any]:
        """Establish baseline rate limiting characteristics"""
        baseline = {
            "requests_per_minute": 0,
            "burst_tolerance": 0,
            "enforcement_method": "UNKNOWN",
            "reset_window": "UNKNOWN"
        }
        
        try:
            # Test sustained rate
            sustained_start = time.time()
            sustained_requests = 0
            
            for i in range(60):  # Test for 1 minute
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    sustained_requests += 1
                elif response.status_code == 429:
                    baseline["enforcement_method"] = "HTTP_429"
                    break
                
                time.sleep(1)
            
            baseline["requests_per_minute"] = sustained_requests
            
            # Test burst tolerance
            burst_requests = 0
            for i in range(20):  # Quick burst
                response = requests.head(url, timeout=2)
                if response.status_code == 200:
                    burst_requests += 1
                else:
                    break
            
            baseline["burst_tolerance"] = burst_requests
            
        except Exception as e:
            baseline["baseline_error"] = str(e)
        
        return baseline
    
    async def _test_user_agent_rotation(self, url: str, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Test user agent rotation circumvention"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15"
        ]
        
        try:
            successful_requests = 0
            total_requests = 50
            
            for i in range(total_requests):
                ua = random.choice(user_agents)
                headers = {"User-Agent": ua}
                
                response = requests.head(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
                
                await asyncio.sleep(0.1)
            
            success_rate = successful_requests / total_requests
            baseline_rate = baseline.get("requests_per_minute", 60) / 60  # Convert to per second
            
            return {
                "success": success_rate > baseline_rate * 1.2,  # 20% improvement
                "success_rate": success_rate,
                "baseline_comparison": success_rate / max(baseline_rate, 0.01),
                "requests_completed": successful_requests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_ip_rotation_simulation(self, url: str, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Test IP rotation simulation (using headers)"""
        try:
            # Simulate different IP sources using X-Forwarded-For headers
            fake_ips = [
                "192.168.1.100", "10.0.0.50", "172.16.0.200",
                "203.0.113.15", "198.51.100.25", "233.252.0.10"
            ]
            
            successful_requests = 0
            total_requests = 30
            
            for i in range(total_requests):
                fake_ip = random.choice(fake_ips)
                headers = {
                    "X-Forwarded-For": fake_ip,
                    "X-Real-IP": fake_ip,
                    "X-Originating-IP": fake_ip
                }
                
                response = requests.head(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
                
                await asyncio.sleep(0.2)
            
            success_rate = successful_requests / total_requests
            
            return {
                "success": success_rate > 0.8,
                "success_rate": success_rate,
                "technique": "IP_HEADER_ROTATION",
                "requests_completed": successful_requests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_timing_variation(self, url: str, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Test request timing variation"""
        try:
            successful_requests = 0
            total_requests = 40
            
            for i in range(total_requests):
                # Vary timing between 0.1 and 2.0 seconds
                delay = random.uniform(0.1, 2.0)
                
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
                
                await asyncio.sleep(delay)
            
            success_rate = successful_requests / total_requests
            
            return {
                "success": success_rate > 0.85,
                "success_rate": success_rate,
                "technique": "TIMING_VARIATION",
                "requests_completed": successful_requests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_header_manipulation(self, url: str, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Test header manipulation techniques"""
        try:
            header_variations = [
                {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
                {"Accept": "application/json, text/plain, */*"},
                {"Accept-Language": "en-US,en;q=0.9"},
                {"Accept-Language": "en-GB,en;q=0.8"},
                {"Accept-Encoding": "gzip, deflate, br"},
                {"Cache-Control": "no-cache"},
                {"Pragma": "no-cache"}
            ]
            
            successful_requests = 0
            total_requests = len(header_variations) * 5
            
            for _ in range(5):  # Test each variation 5 times
                for headers in header_variations:
                    response = requests.head(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        successful_requests += 1
                    
                    await asyncio.sleep(0.1)
            
            success_rate = successful_requests / total_requests
            
            return {
                "success": success_rate > 0.8,
                "success_rate": success_rate,
                "technique": "HEADER_MANIPULATION",
                "requests_completed": successful_requests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_session_rotation(self, url: str, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Test session rotation techniques"""
        try:
            successful_requests = 0
            total_requests = 30
            
            # Create multiple sessions
            sessions = [requests.Session() for _ in range(5)]
            
            for i in range(total_requests):
                session = random.choice(sessions)
                
                response = session.head(url, timeout=5)
                if response.status_code == 200:
                    successful_requests += 1
                
                await asyncio.sleep(0.2)
            
            success_rate = successful_requests / total_requests
            
            return {
                "success": success_rate > 0.8,
                "success_rate": success_rate,
                "technique": "SESSION_ROTATION",
                "sessions_used": len(sessions),
                "requests_completed": successful_requests
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_timeout_boundaries(self, url: str) -> Dict[str, Any]:
        """Test timeout boundary conditions"""
        timeout_results = {
            "timeout_tests": {},
            "violation_detected": False,
            "optimal_timeout": 10
        }
        
        for timeout in self.boundary_test_parameters["timeout_variations"]:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=timeout)
                end_time = time.time()
                
                timeout_results["timeout_tests"][timeout] = {
                    "success": response.status_code == 200,
                    "actual_time": end_time - start_time,
                    "status_code": response.status_code
                }
                
                if response.status_code == 200 and end_time - start_time < timeout:
                    timeout_results["optimal_timeout"] = timeout
                
            except requests.exceptions.Timeout:
                timeout_results["timeout_tests"][timeout] = {
                    "success": False,
                    "error": "TIMEOUT",
                    "actual_time": timeout
                }
            except Exception as e:
                timeout_results["timeout_tests"][timeout] = {
                    "success": False,
                    "error": str(e)
                }
        
        return timeout_results
    
    async def _test_payload_boundaries(self, url: str) -> Dict[str, Any]:
        """Test payload size boundaries"""
        payload_results = {
            "payload_tests": {},
            "violation_detected": False,
            "max_payload_size": 0
        }
        
        for size in self.boundary_test_parameters["payload_sizes"]:
            try:
                # Create payload of specified size
                payload = "A" * size
                data = {"test_data": payload}
                
                response = requests.post(url, data=data, timeout=10)
                
                payload_results["payload_tests"][size] = {
                    "success": response.status_code in [200, 405],  # 405 = Method not allowed (expected)
                    "status_code": response.status_code,
                    "response_size": len(response.content) if response.content else 0
                }
                
                if response.status_code in [200, 405]:
                    payload_results["max_payload_size"] = size
                
            except Exception as e:
                payload_results["payload_tests"][size] = {
                    "success": False,
                    "error": str(e)
                }
        
        return payload_results
    
    async def _test_connection_boundaries(self, url: str) -> Dict[str, Any]:
        """Test connection persistence boundaries"""
        connection_results = {
            "persistence_tests": {},
            "violation_detected": False
        }
        
        for persistent in self.boundary_test_parameters["connection_persistence"]:
            try:
                if persistent:
                    # Test persistent connection
                    session = requests.Session()
                    responses = []
                    
                    for i in range(10):
                        response = session.get(url, timeout=5)
                        responses.append(response.status_code)
                    
                    connection_results["persistence_tests"]["persistent"] = {
                        "success": all(code == 200 for code in responses),
                        "response_codes": responses,
                        "connection_reused": True
                    }
                else:
                    # Test non-persistent connections
                    responses = []
                    
                    for i in range(10):
                        response = requests.get(url, timeout=5)
                        responses.append(response.status_code)
                    
                    connection_results["persistence_tests"]["non_persistent"] = {
                        "success": all(code == 200 for code in responses),
                        "response_codes": responses,
                        "connection_reused": False
                    }
                
            except Exception as e:
                connection_results["persistence_tests"][str(persistent)] = {
                    "success": False,
                    "error": str(e)
                }
        
        return connection_results
    
    async def _test_header_boundaries(self, url: str) -> Dict[str, Any]:
        """Test header size boundaries"""
        header_results = {
            "header_tests": {},
            "violation_detected": False
        }
        
        # Test increasingly large headers
        header_sizes = [100, 1000, 5000, 10000]
        
        for size in header_sizes:
            try:
                large_header_value = "X" * size
                headers = {"X-Large-Header": large_header_value}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                header_results["header_tests"][size] = {
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
                
            except Exception as e:
                header_results["header_tests"][size] = {
                    "success": False,
                    "error": str(e)
                }
        
        return header_results
    
    async def _test_concurrency_boundaries(self, url: str) -> Dict[str, Any]:
        """Test concurrency boundaries"""
        concurrency_results = {
            "concurrency_tests": {},
            "violation_detected": False,
            "max_concurrency": 0
        }
        
        concurrency_levels = [5, 10, 25, 50, 100, 200]
        
        for level in concurrency_levels:
            if level > self.max_concurrent_requests:
                break
            
            try:
                with ThreadPoolExecutor(max_workers=level) as executor:
                    futures = [executor.submit(self._single_request, url) for _ in range(level)]
                    
                    successes = 0
                    for future in as_completed(futures, timeout=30):
                        try:
                            result = future.result()
                            if result["success"]:
                                successes += 1
                        except:
                            pass
                
                success_rate = successes / level
                
                concurrency_results["concurrency_tests"][level] = {
                    "success_rate": success_rate,
                    "successful_requests": successes,
                    "total_requests": level
                }
                
                if success_rate >= 0.8:
                    concurrency_results["max_concurrency"] = level
                
            except Exception as e:
                concurrency_results["concurrency_tests"][level] = {
                    "success": False,
                    "error": str(e)
                }
        
        return concurrency_results
    
    async def _test_gradual_load_resilience(self, url: str) -> Dict[str, Any]:
        """Test resilience under gradual load increase"""
        try:
            phases = []
            for rate in [1, 5, 10, 15, 20]:
                phase_start = time.time()
                successes = 0
                
                for i in range(rate * 5):  # 5 seconds at each rate
                    result = self._single_request(url)
                    if result["success"]:
                        successes += 1
                    time.sleep(1.0 / rate)
                
                phase_end = time.time()
                success_rate = successes / (rate * 5)
                
                phases.append({
                    "rate": rate,
                    "success_rate": success_rate,
                    "duration": phase_end - phase_start
                })
                
                if success_rate < 0.7:
                    break
            
            # Calculate resilience score based on maintained performance
            resilience_score = sum(p["success_rate"] for p in phases) / len(phases) if phases else 0
            
            return {
                "resilience_score": resilience_score,
                "phases": phases,
                "degradation_detected": any(p["success_rate"] < 0.8 for p in phases)
            }
            
        except Exception as e:
            return {"resilience_score": 0, "error": str(e)}
    
    async def _test_spike_resilience(self, url: str) -> Dict[str, Any]:
        """Test resilience under sudden load spikes"""
        try:
            # Normal load followed by spike
            normal_rate = 5
            spike_rate = 50
            
            # Normal phase (10 seconds)
            normal_successes = 0
            for i in range(normal_rate * 10):
                result = self._single_request(url)
                if result["success"]:
                    normal_successes += 1
                time.sleep(1.0 / normal_rate)
            
            normal_success_rate = normal_successes / (normal_rate * 10)
            
            # Spike phase (5 seconds)
            spike_successes = 0
            with ThreadPoolExecutor(max_workers=min(spike_rate, 20)) as executor:
                futures = [executor.submit(self._single_request, url) for _ in range(spike_rate * 5)]
                
                for future in as_completed(futures, timeout=30):
                    try:
                        result = future.result()
                        if result["success"]:
                            spike_successes += 1
                    except:
                        pass
            
            spike_success_rate = spike_successes / (spike_rate * 5)
            
            # Recovery phase (10 seconds at normal rate)
            recovery_successes = 0
            for i in range(normal_rate * 10):
                result = self._single_request(url)
                if result["success"]:
                    recovery_successes += 1
                time.sleep(1.0 / normal_rate)
            
            recovery_success_rate = recovery_successes / (normal_rate * 10)
            
            # Calculate resilience score
            resilience_score = (normal_success_rate + spike_success_rate + recovery_success_rate) / 3
            
            return {
                "resilience_score": resilience_score,
                "normal_phase": {"success_rate": normal_success_rate},
                "spike_phase": {"success_rate": spike_success_rate},
                "recovery_phase": {"success_rate": recovery_success_rate},
                "spike_handled": spike_success_rate > 0.5
            }
            
        except Exception as e:
            return {"resilience_score": 0, "error": str(e)}
    
    async def _test_sustained_pressure_resilience(self, url: str) -> Dict[str, Any]:
        """Test resilience under sustained pressure"""
        try:
            duration = 60  # 1 minute of sustained load
            rate = 10  # 10 requests per second
            
            start_time = time.time()
            intervals = []
            
            while time.time() - start_time < duration:
                interval_start = time.time()
                interval_successes = 0
                
                for i in range(rate * 5):  # 5-second intervals
                    if time.time() - start_time >= duration:
                        break
                    
                    result = self._single_request(url)
                    if result["success"]:
                        interval_successes += 1
                    time.sleep(1.0 / rate)
                
                interval_end = time.time()
                success_rate = interval_successes / (rate * 5)
                
                intervals.append({
                    "start_time": interval_start - start_time,
                    "success_rate": success_rate,
                    "duration": interval_end - interval_start
                })
            
            # Calculate resilience score
            success_rates = [i["success_rate"] for i in intervals]
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
            
            # Penalty for degradation over time
            if len(success_rates) >= 2:
                first_half = success_rates[:len(success_rates)//2]
                second_half = success_rates[len(success_rates)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                degradation_penalty = max(0, first_avg - second_avg)
                resilience_score = avg_success_rate - degradation_penalty
            else:
                resilience_score = avg_success_rate
            
            return {
                "resilience_score": max(0, resilience_score),
                "intervals": intervals,
                "average_success_rate": avg_success_rate,
                "performance_stable": resilience_score > 0.7
            }
            
        except Exception as e:
            return {"resilience_score": 0, "error": str(e)}
    
    async def _test_burst_resilience(self, url: str) -> Dict[str, Any]:
        """Test resilience under intermittent bursts"""
        try:
            burst_results = []
            
            # 5 bursts with rest periods
            for burst_num in range(5):
                # Burst phase (20 requests in 2 seconds)
                burst_successes = 0
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(self._single_request, url) for _ in range(20)]
                    
                    for future in as_completed(futures, timeout=10):
                        try:
                            result = future.result()
                            if result["success"]:
                                burst_successes += 1
                        except:
                            pass
                
                burst_success_rate = burst_successes / 20
                
                burst_results.append({
                    "burst_number": burst_num + 1,
                    "success_rate": burst_success_rate,
                    "successful_requests": burst_successes
                })
                
                # Rest period (5 seconds)
                await asyncio.sleep(5)
            
            # Calculate resilience score
            success_rates = [b["success_rate"] for b in burst_results]
            avg_success_rate = sum(success_rates) / len(success_rates)
            
            # Check for consistent performance across bursts
            min_success_rate = min(success_rates)
            consistency_score = min_success_rate / avg_success_rate if avg_success_rate > 0 else 0
            
            resilience_score = avg_success_rate * consistency_score
            
            return {
                "resilience_score": resilience_score,
                "burst_results": burst_results,
                "average_success_rate": avg_success_rate,
                "consistency_score": consistency_score,
                "burst_handling": "GOOD" if resilience_score > 0.7 else "POOR"
            }
            
        except Exception as e:
            return {"resilience_score": 0, "error": str(e)}
    
    async def _test_recovery_resilience(self, url: str) -> Dict[str, Any]:
        """Test recovery time after overload"""
        try:
            # Phase 1: Overload the system
            overload_successes = 0
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(self._single_request, url) for _ in range(100)]
                
                for future in as_completed(futures, timeout=30):
                    try:
                        result = future.result()
                        if result["success"]:
                            overload_successes += 1
                    except:
                        pass
            
            overload_success_rate = overload_successes / 100
            
            # Phase 2: Recovery testing (normal rate)
            recovery_intervals = []
            recovery_start = time.time()
            
            for i in range(6):  # 6 intervals of 10 seconds each
                interval_start = time.time()
                interval_successes = 0
                
                for j in range(10):  # 1 request per second
                    result = self._single_request(url)
                    if result["success"]:
                        interval_successes += 1
                    time.sleep(1)
                
                interval_end = time.time()
                success_rate = interval_successes / 10
                
                recovery_intervals.append({
                    "interval": i + 1,
                    "time_since_overload": interval_end - recovery_start,
                    "success_rate": success_rate
                })
            
            # Calculate recovery metrics
            recovery_times = []
            for interval in recovery_intervals:
                if interval["success_rate"] >= 0.8:  # Considered recovered
                    recovery_times.append(interval["time_since_overload"])
                    break
            
            recovery_time = recovery_times[0] if recovery_times else 60  # Max 60 seconds
            final_success_rate = recovery_intervals[-1]["success_rate"] if recovery_intervals else 0
            
            resilience_score = final_success_rate * (1 - min(recovery_time / 60, 1))  # Penalty for slow recovery
            
            return {
                "resilience_score": resilience_score,
                "overload_success_rate": overload_success_rate,
                "recovery_time_seconds": recovery_time,
                "recovery_intervals": recovery_intervals,
                "final_success_rate": final_success_rate,
                "recovery_achieved": recovery_time < 30
            }
            
        except Exception as e:
            return {"resilience_score": 0, "error": str(e)}
    
    def _generate_breach_strategies(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate breach strategies based on barrier analysis"""
        strategies = {
            "weak_targets": [],
            "moderate_targets": [],
            "strong_targets": []
        }
        
        for target_id, data in analysis.get("targets", {}).items():
            barrier_strength = data.get("barrier_strength", 5)
            
            if barrier_strength <= 3:
                strategies["weak_targets"].append(f"DIRECT_ASSAULT_{target_id}")
            elif barrier_strength <= 6:
                strategies["moderate_targets"].append(f"ENHANCED_TACTICS_{target_id}")
            else:
                strategies["strong_targets"].append(f"SPECIALIZED_APPROACH_{target_id}")
        
        return strategies
    
    def _calculate_penetration_success_rate(self) -> float:
        """Calculate overall penetration success rate"""
        if not self.stress_test_results:
            return 0.0
        
        success_scores = []
        
        for result in self.stress_test_results:
            # Factor in resilience score
            resilience = result.get("resilience_score", 0)
            success_scores.append(resilience)
        
        return sum(success_scores) / len(success_scores) if success_scores else 0.0