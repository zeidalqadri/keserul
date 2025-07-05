"""
Assault Agent - Bravo Fire Team Primary Operator
Core functionality validation and primary mission execution
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json

from ...base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority
from ....core.scraper import LuxcrepeScraper
from ....core.utils import RetrySession
from ....ml.extractors import HybridExtractor


class AssaultAgent(BaseAgent):
    """Assault Agent - Bravo Fire Team Primary Operator
    
    Responsibilities:
    - Core functionality validation and testing
    - Primary scraping mission execution
    - Data extraction and quality validation
    - Target engagement and objective completion
    - Mission success/failure determination
    """
    
    def __init__(self):
        super().__init__(
            agent_id="BRAVO-003",
            call_sign="HAMMER",
            squad="bravo"
        )
        
        # Assault capabilities
        self.weapons_systems = [
            "PRIMARY_SCRAPER",
            "EXTRACTION_ENGINE", 
            "VALIDATION_SUITE",
            "QUALITY_ANALYZER"
        ]
        
        self.equipment = {
            "scraping_tools": "LOADED",
            "extraction_engine": "ARMED",
            "validation_systems": "ACTIVE",
            "quality_controls": "ENABLED"
        }
        
        self.intelligence_sources = [
            "EXTRACTION_RESULTS",
            "QUALITY_METRICS",
            "PERFORMANCE_DATA",
            "SUCCESS_INDICATORS"
        ]
        
        # Assault data
        self.extraction_results: List[Dict[str, Any]] = []
        self.quality_metrics: Dict[str, Any] = {}
        self.performance_data: Dict[str, Any] = {}
        self.mission_objectives: Dict[str, Any] = {}
        
        # Assault configuration
        self.extraction_targets = [
            "product_names",
            "prices", 
            "descriptions",
            "availability",
            "images",
            "specifications",
            "reviews",
            "ratings"
        ]
        
        self.quality_thresholds = {
            "extraction_success_rate": 0.85,
            "data_completeness": 0.80,
            "accuracy_score": 0.90,
            "response_time": 5.0  # seconds
        }
        
        self.validation_criteria = {
            "required_fields": ["name", "price"],
            "optional_fields": ["description", "availability", "images"],
            "data_types": {
                "price": ["float", "str"],
                "name": ["str"],
                "availability": ["bool", "str"]
            }
        }
        
        self.logger.info("HAMMER: Assault Agent initialized - Ready for primary assault")
    
    def get_capabilities(self) -> List[str]:
        """Return assault capabilities"""
        return [
            "primary_scraping",
            "data_extraction", 
            "quality_validation",
            "core_functionality_testing",
            "mission_execution",
            "objective_completion",
            "success_determination",
            "performance_assessment",
            "extraction_optimization",
            "multi_target_engagement"
        ]
    
    async def execute_mission(self, mission_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute primary assault mission with full data extraction"""
        
        self.logger.info("HAMMER: Beginning primary assault operations")
        
        target_urls = mission_parameters.get("target_urls", [])
        if not target_urls:
            raise Exception("No targets provided for assault")
        
        extraction_requirements = mission_parameters.get("extraction_requirements", self.extraction_targets)
        quality_requirements = mission_parameters.get("quality_thresholds", self.quality_thresholds)
        
        # Assault Phase 1: Target Engagement
        engagement_results = await self._engage_targets(target_urls)
        
        # Assault Phase 2: Primary Data Extraction
        extraction_results = await self._execute_primary_extraction(target_urls, extraction_requirements)
        
        # Assault Phase 3: Quality Validation and Assessment
        quality_assessment = await self._validate_extraction_quality(extraction_results, quality_requirements)
        
        # Assault Phase 4: Performance Analysis
        performance_analysis = await self._analyze_assault_performance(extraction_results, quality_assessment)
        
        # Assault Phase 5: Mission Success Determination
        mission_result = await self._determine_mission_success(
            engagement_results, extraction_results, quality_assessment, performance_analysis
        )
        
        self.logger.info("HAMMER: Primary assault operations complete")
        
        return {
            "target_engagement": engagement_results,
            "extraction_results": extraction_results,
            "quality_assessment": quality_assessment,
            "performance_analysis": performance_analysis,
            "mission_result": mission_result,
            "assault_summary": self._generate_assault_summary(mission_result)
        }
    
    async def _engage_targets(self, target_urls: List[str]) -> Dict[str, Any]:
        """Engage targets and establish access"""
        
        self.logger.info("HAMMER: Engaging targets for assault")
        
        engagement_results = {
            "targets_engaged": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "connection_details": {},
            "access_established": False
        }
        
        successful_targets = []
        
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            self.logger.debug(f"HAMMER: Engaging target {target_id}: {url}")
            
            try:
                # Establish connection with target
                start_time = time.time()
                response = requests.get(url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                connection_time = time.time() - start_time
                
                if response.status_code == 200:
                    engagement_results["successful_connections"] += 1
                    successful_targets.append(url)
                    
                    engagement_results["connection_details"][target_id] = {
                        "status": "CONNECTED",
                        "response_code": response.status_code,
                        "connection_time": connection_time,
                        "content_size": len(response.content),
                        "headers": dict(response.headers)
                    }
                    
                else:
                    engagement_results["failed_connections"] += 1
                    engagement_results["connection_details"][target_id] = {
                        "status": "FAILED",
                        "response_code": response.status_code,
                        "error": f"HTTP {response.status_code}"
                    }
                
            except Exception as e:
                engagement_results["failed_connections"] += 1
                engagement_results["connection_details"][target_id] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                self.logger.warning(f"HAMMER: Target engagement failed for {url}: {str(e)}")
            
            engagement_results["targets_engaged"] += 1
        
        # Determine if access is established
        success_rate = engagement_results["successful_connections"] / len(target_urls)
        engagement_results["access_established"] = success_rate >= 0.5
        engagement_results["success_rate"] = success_rate
        
        if not engagement_results["access_established"]:
            self.threat_level = ThreatLevel.YELLOW
            self.logger.warning("HAMMER: Limited target access - adjusting assault parameters")
        
        return engagement_results
    
    async def _execute_primary_extraction(self, target_urls: List[str], 
                                        extraction_requirements: List[str]) -> Dict[str, Any]:
        """Execute primary data extraction operations"""
        
        self.logger.info("HAMMER: Executing primary data extraction")
        
        extraction_results = {
            "extraction_method": "HYBRID_ML_ENHANCED",
            "targets_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extracted_data": {},
            "extraction_statistics": {},
            "performance_metrics": {}
        }
        
        # Initialize ML-enhanced extractor
        try:
            extractor = HybridExtractor()
            self.logger.debug("HAMMER: ML extractor initialized")
        except Exception as e:
            self.logger.warning(f"HAMMER: ML extractor unavailable, using basic extraction: {str(e)}")
            extractor = None
        
        # Process each target
        for i, url in enumerate(target_urls):
            target_id = f"target_{i+1}"
            extraction_start = time.time()
            
            try:
                self.logger.debug(f"HAMMER: Extracting from {target_id}: {url}")
                
                # Primary extraction using LuxcrepeScraper
                scraper = LuxcrepeScraper()
                raw_data = await self._scrape_target(scraper, url)
                
                # Enhanced extraction using ML if available
                if extractor and raw_data:
                    enhanced_data = await self._enhance_extraction(extractor, raw_data, url)
                    extracted_data = self._merge_extraction_data(raw_data, enhanced_data)
                else:
                    extracted_data = raw_data
                
                # Validate extracted data against requirements
                validated_data = self._validate_extracted_data(extracted_data, extraction_requirements)
                
                extraction_time = time.time() - extraction_start
                
                extraction_results["extracted_data"][target_id] = {
                    "url": url,
                    "extraction_timestamp": datetime.now().isoformat(),
                    "extraction_time": extraction_time,
                    "data": validated_data,
                    "fields_extracted": list(validated_data.keys()),
                    "extraction_success": len(validated_data) > 0
                }
                
                if len(validated_data) > 0:
                    extraction_results["successful_extractions"] += 1
                else:
                    extraction_results["failed_extractions"] += 1
                
            except Exception as e:
                extraction_time = time.time() - extraction_start
                extraction_results["failed_extractions"] += 1
                extraction_results["extracted_data"][target_id] = {
                    "url": url,
                    "extraction_timestamp": datetime.now().isoformat(),
                    "extraction_time": extraction_time,
                    "error": str(e),
                    "extraction_success": False
                }
                self.logger.error(f"HAMMER: Extraction failed for {url}: {str(e)}")
            
            extraction_results["targets_processed"] += 1
        
        # Calculate extraction statistics
        extraction_results["extraction_statistics"] = self._calculate_extraction_statistics(extraction_results)
        
        return extraction_results
    
    async def _scrape_target(self, scraper: LuxcrepeScraper, url: str) -> Dict[str, Any]:
        """Scrape target using primary scraper"""
        
        try:
            # Configure scraper for assault mission
            scraper.configure({
                "delay_range": (1, 3),
                "max_retries": 2,
                "timeout": 15
            })
            
            # Execute scraping
            results = await asyncio.get_event_loop().run_in_executor(
                None, scraper.scrape_url, url
            )
            
            return results if results else {}
            
        except Exception as e:
            self.logger.warning(f"HAMMER: Primary scraping failed: {str(e)}")
            return {}
    
    async def _enhance_extraction(self, extractor: HybridExtractor, 
                                raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance extraction using ML-based extractor"""
        
        try:
            # Use ML extractor to enhance data
            enhanced_results = await asyncio.get_event_loop().run_in_executor(
                None, extractor.extract_from_data, raw_data, url
            )
            
            return enhanced_results if enhanced_results else {}
            
        except Exception as e:
            self.logger.warning(f"HAMMER: ML enhancement failed: {str(e)}")
            return {}
    
    def _merge_extraction_data(self, raw_data: Dict[str, Any], 
                             enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge raw and enhanced extraction data"""
        
        merged_data = raw_data.copy()
        
        # Merge enhanced data, prioritizing ML results where available
        for key, value in enhanced_data.items():
            if value and (key not in merged_data or not merged_data[key]):
                merged_data[key] = value
            elif value and key in merged_data:
                # For overlapping data, prefer ML enhanced if confidence is high
                if isinstance(value, dict) and "confidence" in value:
                    if value.get("confidence", 0) > 0.8:
                        merged_data[key] = value
        
        return merged_data
    
    def _validate_extracted_data(self, data: Dict[str, Any], 
                               requirements: List[str]) -> Dict[str, Any]:
        """Validate extracted data against requirements"""
        
        validated_data = {}
        
        for requirement in requirements:
            if requirement in data and data[requirement]:
                # Basic data type validation
                if requirement in self.validation_criteria["data_types"]:
                    expected_types = self.validation_criteria["data_types"][requirement]
                    value = data[requirement]
                    
                    # Check if value matches expected types
                    if any(isinstance(value, eval(t)) for t in expected_types):
                        validated_data[requirement] = value
                    else:
                        self.logger.debug(f"HAMMER: Data type validation failed for {requirement}")
                else:
                    validated_data[requirement] = data[requirement]
        
        return validated_data
    
    async def _validate_extraction_quality(self, extraction_results: Dict[str, Any],
                                         quality_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extraction quality against requirements"""
        
        self.logger.info("HAMMER: Validating extraction quality")
        
        quality_assessment = {
            "overall_quality_score": 0.0,
            "quality_metrics": {},
            "quality_passed": False,
            "quality_issues": [],
            "recommendations": []
        }
        
        total_targets = extraction_results["targets_processed"]
        successful_extractions = extraction_results["successful_extractions"]
        
        # Calculate quality metrics
        extraction_success_rate = successful_extractions / total_targets if total_targets > 0 else 0
        
        # Data completeness assessment
        completeness_scores = []
        accuracy_scores = []
        response_times = []
        
        for target_id, target_data in extraction_results["extracted_data"].items():
            if target_data.get("extraction_success", False):
                # Completeness: required fields present
                required_fields = self.validation_criteria["required_fields"]
                extracted_fields = target_data.get("fields_extracted", [])
                completeness = len([f for f in required_fields if f in extracted_fields]) / len(required_fields)
                completeness_scores.append(completeness)
                
                # Response time
                response_times.append(target_data.get("extraction_time", 0))
                
                # Accuracy estimation (simplified)
                data_quality = self._assess_data_accuracy(target_data.get("data", {}))
                accuracy_scores.append(data_quality)
        
        # Calculate aggregate metrics
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        quality_assessment["quality_metrics"] = {
            "extraction_success_rate": extraction_success_rate,
            "data_completeness": avg_completeness,
            "accuracy_score": avg_accuracy,
            "average_response_time": avg_response_time
        }
        
        # Check against quality requirements
        quality_checks = []
        
        if extraction_success_rate >= quality_requirements["extraction_success_rate"]:
            quality_checks.append("EXTRACTION_RATE_PASSED")
        else:
            quality_assessment["quality_issues"].append("LOW_EXTRACTION_SUCCESS_RATE")
        
        if avg_completeness >= quality_requirements["data_completeness"]:
            quality_checks.append("COMPLETENESS_PASSED")
        else:
            quality_assessment["quality_issues"].append("INSUFFICIENT_DATA_COMPLETENESS")
        
        if avg_accuracy >= quality_requirements["accuracy_score"]:
            quality_checks.append("ACCURACY_PASSED")
        else:
            quality_assessment["quality_issues"].append("LOW_DATA_ACCURACY")
        
        if avg_response_time <= quality_requirements["response_time"]:
            quality_checks.append("RESPONSE_TIME_PASSED")
        else:
            quality_assessment["quality_issues"].append("SLOW_RESPONSE_TIME")
        
        # Overall quality determination
        quality_assessment["quality_passed"] = len(quality_checks) >= 3
        quality_assessment["overall_quality_score"] = len(quality_checks) / 4.0
        
        # Generate recommendations
        if quality_assessment["quality_issues"]:
            quality_assessment["recommendations"] = self._generate_quality_recommendations(
                quality_assessment["quality_issues"]
            )
        
        return quality_assessment
    
    def _assess_data_accuracy(self, data: Dict[str, Any]) -> float:
        """Assess data accuracy (simplified heuristic)"""
        
        accuracy_score = 1.0
        
        # Check for common accuracy indicators
        for key, value in data.items():
            if not value or value == "":
                accuracy_score -= 0.1
            elif isinstance(value, str):
                # Check for placeholder text or obvious errors
                suspicious_patterns = ["lorem ipsum", "placeholder", "test", "xxx", "n/a"]
                if any(pattern in value.lower() for pattern in suspicious_patterns):
                    accuracy_score -= 0.2
                # Check for proper formatting
                if key == "price" and not any(char.isdigit() for char in str(value)):
                    accuracy_score -= 0.3
        
        return max(0.0, accuracy_score)
    
    def _generate_quality_recommendations(self, quality_issues: List[str]) -> List[str]:
        """Generate recommendations for quality improvement"""
        
        recommendations = []
        
        if "LOW_EXTRACTION_SUCCESS_RATE" in quality_issues:
            recommendations.append("IMPROVE_TARGET_SELECTION")
            recommendations.append("ENHANCE_SCRAPING_ROBUSTNESS")
        
        if "INSUFFICIENT_DATA_COMPLETENESS" in quality_issues:
            recommendations.append("EXPAND_EXTRACTION_SELECTORS")
            recommendations.append("IMPROVE_FIELD_DETECTION")
        
        if "LOW_DATA_ACCURACY" in quality_issues:
            recommendations.append("ENHANCE_DATA_VALIDATION")
            recommendations.append("IMPLEMENT_CONFIDENCE_SCORING")
        
        if "SLOW_RESPONSE_TIME" in quality_issues:
            recommendations.append("OPTIMIZE_SCRAPING_PERFORMANCE")
            recommendations.append("IMPLEMENT_PARALLEL_PROCESSING")
        
        return recommendations
    
    async def _analyze_assault_performance(self, extraction_results: Dict[str, Any],
                                         quality_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall assault performance"""
        
        self.logger.info("HAMMER: Analyzing assault performance")
        
        performance_analysis = {
            "performance_score": 0.0,
            "efficiency_metrics": {},
            "resource_utilization": {},
            "scalability_assessment": {},
            "performance_grade": "F"
        }
        
        # Calculate efficiency metrics
        total_time = sum(
            target_data.get("extraction_time", 0) 
            for target_data in extraction_results["extracted_data"].values()
        )
        
        targets_processed = extraction_results["targets_processed"]
        successful_extractions = extraction_results["successful_extractions"]
        
        performance_analysis["efficiency_metrics"] = {
            "total_processing_time": total_time,
            "average_time_per_target": total_time / targets_processed if targets_processed > 0 else 0,
            "throughput_targets_per_minute": (targets_processed / total_time) * 60 if total_time > 0 else 0,
            "success_rate": successful_extractions / targets_processed if targets_processed > 0 else 0
        }
        
        # Resource utilization (simplified)
        performance_analysis["resource_utilization"] = {
            "memory_efficiency": "ACCEPTABLE",  # Would measure actual memory in real implementation
            "network_efficiency": "GOOD" if total_time < 30 else "MODERATE",
            "cpu_utilization": "OPTIMAL"  # Would measure actual CPU in real implementation
        }
        
        # Scalability assessment
        avg_time_per_target = performance_analysis["efficiency_metrics"]["average_time_per_target"]
        
        if avg_time_per_target < 2.0:
            scalability_rating = "EXCELLENT"
            estimated_capacity = "> 1000 targets/hour"
        elif avg_time_per_target < 5.0:
            scalability_rating = "GOOD"
            estimated_capacity = "500-1000 targets/hour"
        elif avg_time_per_target < 10.0:
            scalability_rating = "MODERATE"
            estimated_capacity = "100-500 targets/hour"
        else:
            scalability_rating = "LIMITED"
            estimated_capacity = "< 100 targets/hour"
        
        performance_analysis["scalability_assessment"] = {
            "scalability_rating": scalability_rating,
            "estimated_capacity": estimated_capacity,
            "bottlenecks_identified": self._identify_bottlenecks(extraction_results)
        }
        
        # Overall performance score
        quality_score = quality_assessment["overall_quality_score"]
        efficiency_score = min(1.0, 5.0 / avg_time_per_target) if avg_time_per_target > 0 else 0
        success_rate = performance_analysis["efficiency_metrics"]["success_rate"]
        
        performance_analysis["performance_score"] = (quality_score * 0.4 + efficiency_score * 0.3 + success_rate * 0.3)
        
        # Performance grade
        score = performance_analysis["performance_score"]
        if score >= 0.9:
            performance_analysis["performance_grade"] = "A"
        elif score >= 0.8:
            performance_analysis["performance_grade"] = "B"
        elif score >= 0.7:
            performance_analysis["performance_grade"] = "C"
        elif score >= 0.6:
            performance_analysis["performance_grade"] = "D"
        else:
            performance_analysis["performance_grade"] = "F"
        
        return performance_analysis
    
    def _identify_bottlenecks(self, extraction_results: Dict[str, Any]) -> List[str]:
        """Identify performance bottlenecks"""
        
        bottlenecks = []
        
        # Analyze extraction times
        extraction_times = [
            target_data.get("extraction_time", 0)
            for target_data in extraction_results["extracted_data"].values()
            if target_data.get("extraction_success", False)
        ]
        
        if extraction_times:
            avg_time = sum(extraction_times) / len(extraction_times)
            max_time = max(extraction_times)
            
            if max_time > avg_time * 3:
                bottlenecks.append("INCONSISTENT_RESPONSE_TIMES")
            
            if avg_time > 5.0:
                bottlenecks.append("SLOW_EXTRACTION_SPEED")
        
        # Check failure patterns
        failed_count = extraction_results["failed_extractions"]
        total_count = extraction_results["targets_processed"]
        
        if failed_count / total_count > 0.2:
            bottlenecks.append("HIGH_FAILURE_RATE")
        
        return bottlenecks
    
    async def _determine_mission_success(self, engagement_results: Dict[str, Any],
                                       extraction_results: Dict[str, Any],
                                       quality_assessment: Dict[str, Any],
                                       performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall mission success"""
        
        self.logger.info("HAMMER: Determining mission success")
        
        mission_result = {
            "mission_status": MissionStatus.PLANNING.value,
            "success_probability": 0.0,
            "critical_success_factors": {},
            "mission_objectives_met": {},
            "overall_assessment": "",
            "next_phase_recommendation": ""
        }
        
        # Evaluate critical success factors
        access_established = engagement_results["access_established"]
        extraction_successful = extraction_results["successful_extractions"] > 0
        quality_passed = quality_assessment["quality_passed"]
        performance_acceptable = performance_analysis["performance_score"] >= 0.6
        
        mission_result["critical_success_factors"] = {
            "target_access": access_established,
            "data_extraction": extraction_successful,
            "quality_standards": quality_passed,
            "performance_requirements": performance_acceptable
        }
        
        # Count successful factors
        success_count = sum(1 for factor in mission_result["critical_success_factors"].values() if factor)
        
        # Mission objectives assessment
        mission_result["mission_objectives_met"] = {
            "primary_objectives": success_count >= 3,
            "secondary_objectives": success_count >= 2,
            "minimum_viable": success_count >= 1
        }
        
        # Overall mission determination
        if success_count == 4:
            mission_result["mission_status"] = MissionStatus.SUCCESS.value
            mission_result["success_probability"] = 0.95
            mission_result["overall_assessment"] = "MISSION_ACCOMPLISHED"
            mission_result["next_phase_recommendation"] = "PROCEED_TO_FULL_DEPLOYMENT"
        elif success_count == 3:
            mission_result["mission_status"] = MissionStatus.PARTIAL_SUCCESS.value
            mission_result["success_probability"] = 0.75
            mission_result["overall_assessment"] = "PARTIAL_SUCCESS_OPTIMIZATION_REQUIRED"
            mission_result["next_phase_recommendation"] = "OPTIMIZE_AND_RETRY"
        elif success_count >= 1:
            mission_result["mission_status"] = MissionStatus.PLANNING.value
            mission_result["success_probability"] = 0.50
            mission_result["overall_assessment"] = "MISSION_NEEDS_ADJUSTMENT"
            mission_result["next_phase_recommendation"] = "REVISE_APPROACH"
        else:
            mission_result["mission_status"] = MissionStatus.FAILED.value
            mission_result["success_probability"] = 0.25
            mission_result["overall_assessment"] = "MISSION_FAILED"
            mission_result["next_phase_recommendation"] = "ABORT_OR_MAJOR_REVISION"
        
        # Update agent status based on mission result
        if mission_result["mission_status"] == MissionStatus.SUCCESS.value:
            self.mission_status = MissionStatus.SUCCESS
            self.threat_level = ThreatLevel.GREEN
        elif mission_result["mission_status"] == MissionStatus.PARTIAL_SUCCESS.value:
            self.mission_status = MissionStatus.IN_PROGRESS
            self.threat_level = ThreatLevel.YELLOW
        else:
            self.mission_status = MissionStatus.FAILED
            self.threat_level = ThreatLevel.ORANGE
        
        return mission_result
    
    def _calculate_extraction_statistics(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed extraction statistics"""
        
        stats = {
            "total_targets": extraction_results["targets_processed"],
            "successful_targets": extraction_results["successful_extractions"],
            "failed_targets": extraction_results["failed_extractions"],
            "success_rate": 0.0,
            "average_fields_per_target": 0.0,
            "total_data_points": 0,
            "field_extraction_rates": {}
        }
        
        if stats["total_targets"] > 0:
            stats["success_rate"] = stats["successful_targets"] / stats["total_targets"]
        
        # Calculate field-level statistics
        field_counts = {}
        successful_extractions = []
        
        for target_data in extraction_results["extracted_data"].values():
            if target_data.get("extraction_success", False):
                fields = target_data.get("fields_extracted", [])
                successful_extractions.append(len(fields))
                stats["total_data_points"] += len(fields)
                
                for field in fields:
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        if successful_extractions:
            stats["average_fields_per_target"] = sum(successful_extractions) / len(successful_extractions)
        
        # Field extraction rates
        for field, count in field_counts.items():
            stats["field_extraction_rates"][field] = count / stats["successful_targets"] if stats["successful_targets"] > 0 else 0
        
        return stats
    
    def _generate_assault_summary(self, mission_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate assault mission summary"""
        
        return {
            "assault_outcome": mission_result["mission_status"],
            "success_probability": mission_result["success_probability"],
            "key_achievements": [
                factor for factor, status in mission_result["critical_success_factors"].items() if status
            ],
            "areas_for_improvement": [
                factor for factor, status in mission_result["critical_success_factors"].items() if not status
            ],
            "recommendation": mission_result["next_phase_recommendation"],
            "assault_completed_at": datetime.now().isoformat()
        }