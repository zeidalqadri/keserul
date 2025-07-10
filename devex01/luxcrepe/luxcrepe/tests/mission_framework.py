"""
Mission Execution Framework for SEAL-Grade Multi-Agent Test Squad
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid

from .base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority


class MissionType(Enum):
    """Types of missions"""
    DIRECT_ACTION = "DA"           # Core functionality testing
    SPECIAL_RECON = "SR"           # Intelligence gathering
    UNCONVENTIONAL_WARFARE = "UW" # Adversarial testing
    FOREIGN_INTERNAL_DEFENSE = "FID" # System defense testing


class OperationSecurity(Enum):
    """Operation security levels"""
    UNCLASSIFIED = "UNCLASSIFIED"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"
    TOP_SECRET = "TOP_SECRET"


@dataclass
class MissionParameters:
    """Mission parameters and configuration"""
    mission_id: str
    mission_type: MissionType
    target_system: str
    objectives: List[str]
    success_criteria: Dict[str, Any]
    time_limit: timedelta
    security_level: OperationSecurity
    resources_required: List[str]
    threat_assessment: Dict[str, Any]
    rules_of_engagement: Dict[str, Any]
    extraction_plan: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "mission_id": self.mission_id,
            "mission_type": self.mission_type.value,
            "target_system": self.target_system,
            "objectives": self.objectives,
            "success_criteria": self.success_criteria,
            "time_limit_minutes": self.time_limit.total_seconds() / 60,
            "security_level": self.security_level.value,
            "resources_required": self.resources_required,
            "threat_assessment": self.threat_assessment,
            "rules_of_engagement": self.rules_of_engagement,
            "extraction_plan": self.extraction_plan
        }


class MissionOrchestrator:
    """Orchestrates multi-agent missions"""
    
    def __init__(self):
        self.logger = logging.getLogger("SEAL.COMMAND")
        self.active_missions: Dict[str, Dict[str, Any]] = {}
        self.agent_registry: Dict[str, BaseAgent] = {}
        self.squad_organization: Dict[str, List[str]] = {
            "alpha": [],
            "bravo": [],
            "charlie": [],
            "delta": []
        }
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the command structure"""
        self.agent_registry[agent.agent_id] = agent
        squad = agent.squad.lower()
        if squad in self.squad_organization:
            self.squad_organization[squad].append(agent.agent_id)
        
        self.logger.info(f"REGISTRY: Agent {agent.call_sign} registered in {squad} squad")
    
    async def execute_mission(self, mission_params: MissionParameters, 
                            selected_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute a mission with specified or auto-selected agents"""
        
        mission_id = mission_params.mission_id
        self.logger.info(f"MISSION START: Initiating mission {mission_id}")
        
        # Auto-select agents if not specified
        if not selected_agents:
            selected_agents = self._auto_select_agents(mission_params)
        
        # Validate agent selection
        if not self._validate_agent_selection(selected_agents, mission_params):
            return {
                "status": "FAILED",
                "error": "Invalid agent selection for mission requirements",
                "mission_id": mission_id
            }
        
        # Initialize mission tracking
        mission_data = {
            "id": mission_id,
            "parameters": mission_params,
            "agents": selected_agents,
            "start_time": datetime.now(),
            "status": "ACTIVE",
            "results": {},
            "threat_level": ThreatLevel.GREEN
        }
        self.active_missions[mission_id] = mission_data
        
        try:
            # Execute mission phases
            results = await self._execute_mission_phases(mission_params, selected_agents)
            
            mission_data["status"] = "COMPLETED"
            mission_data["end_time"] = datetime.now()
            mission_data["results"] = results
            
            self.logger.info(f"MISSION SUCCESS: Mission {mission_id} completed successfully")
            
            return {
                "status": "SUCCESS",
                "mission_id": mission_id,
                "results": results,
                "execution_time": (mission_data["end_time"] - mission_data["start_time"]).total_seconds(),
                "agents_deployed": len(selected_agents)
            }
            
        except Exception as e:
            mission_data["status"] = "FAILED" 
            mission_data["error"] = str(e)
            mission_data["end_time"] = datetime.now()
            
            self.logger.error(f"MISSION FAILED: Mission {mission_id} failed: {str(e)}")
            
            # Execute emergency extraction
            await self._emergency_extraction(selected_agents)
            
            return {
                "status": "FAILED",
                "mission_id": mission_id,
                "error": str(e),
                "agents_deployed": len(selected_agents)
            }
    
    def _auto_select_agents(self, mission_params: MissionParameters) -> List[str]:
        """Automatically select optimal agents for mission"""
        selected = []
        
        # Always include mission commander
        alpha_agents = self.squad_organization["alpha"]
        if alpha_agents:
            selected.append(alpha_agents[0])  # Mission commander
        
        # Select agents based on mission type
        if mission_params.mission_type == MissionType.DIRECT_ACTION:
            # Bravo team for direct action
            bravo_agents = self.squad_organization["bravo"]
            selected.extend(bravo_agents[:2])  # Pointman + Assault
            
        elif mission_params.mission_type == MissionType.SPECIAL_RECON:
            # Charlie team for specialized operations
            charlie_agents = self.squad_organization["charlie"]
            selected.extend(charlie_agents[:2])  # Engineer + Sniper
            
        elif mission_params.mission_type == MissionType.UNCONVENTIONAL_WARFARE:
            # Mixed team for adversarial testing
            bravo_agents = self.squad_organization["bravo"]
            charlie_agents = self.squad_organization["charlie"]
            selected.append(bravo_agents[1] if len(bravo_agents) > 1 else bravo_agents[0])  # Breacher
            selected.append(charlie_agents[0] if charlie_agents else None)  # Demolitions
        
        # Always include Delta overwatch
        delta_agents = self.squad_organization["delta"]
        if delta_agents:
            selected.append(delta_agents[0])  # Spotter
        
        # Filter out None values
        selected = [agent_id for agent_id in selected if agent_id is not None]
        
        self.logger.info(f"AUTO-SELECT: Selected agents {selected} for mission type {mission_params.mission_type.value}")
        return selected
    
    def _validate_agent_selection(self, agent_ids: List[str], 
                                mission_params: MissionParameters) -> bool:
        """Validate that selected agents can fulfill mission requirements"""
        
        # Check all agents exist and are available
        for agent_id in agent_ids:
            if agent_id not in self.agent_registry:
                self.logger.error(f"VALIDATION: Agent {agent_id} not found in registry")
                return False
            
            agent = self.agent_registry[agent_id]
            if agent.status != MissionStatus.STANDBY:
                self.logger.error(f"VALIDATION: Agent {agent.call_sign} not available (status: {agent.status})")
                return False
        
        # Check minimum team composition
        squads_represented = set()
        for agent_id in agent_ids:
            agent = self.agent_registry[agent_id]
            squads_represented.add(agent.squad.lower())
        
        # Must have at least command (alpha) and one operational squad
        if "alpha" not in squads_represented:
            self.logger.error("VALIDATION: No command agent (Alpha squad) selected")
            return False
        
        # Check mission-specific requirements
        required_capabilities = mission_params.resources_required
        available_capabilities = set()
        
        for agent_id in agent_ids:
            agent = self.agent_registry[agent_id]
            available_capabilities.update(agent.get_capabilities())
        
        missing_capabilities = set(required_capabilities) - available_capabilities
        if missing_capabilities:
            self.logger.error(f"VALIDATION: Missing required capabilities: {missing_capabilities}")
            return False
        
        self.logger.info("VALIDATION: Agent selection validated successfully")
        return True
    
    async def _execute_mission_phases(self, mission_params: MissionParameters,
                                    agent_ids: List[str]) -> Dict[str, Any]:
        """Execute mission with all selected agents"""
        
        agents = [self.agent_registry[agent_id] for agent_id in agent_ids]
        
        # Convert mission parameters to dict for agents
        mission_dict = mission_params.to_dict()
        
        # Deploy all agents concurrently
        self.logger.info(f"DEPLOY: Deploying {len(agents)} agents for mission {mission_params.mission_id}")
        
        deployment_tasks = []
        for agent in agents:
            task = asyncio.create_task(
                agent.deploy(mission_params.mission_id, mission_dict),
                name=f"deploy_{agent.call_sign}"
            )
            deployment_tasks.append(task)
        
        # Wait for all agents to complete with timeout
        timeout_seconds = mission_params.time_limit.total_seconds()
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*deployment_tasks, return_exceptions=True),
                timeout=timeout_seconds
            )
            
            # Process results
            mission_results = {
                "agents": {},
                "overall_success": True,
                "total_agents": len(agents),
                "successful_agents": 0,
                "failed_agents": 0
            }
            
            for i, result in enumerate(results):
                agent = agents[i]
                
                if isinstance(result, Exception):
                    mission_results["agents"][agent.call_sign] = {
                        "status": "FAILED",
                        "error": str(result)
                    }
                    mission_results["failed_agents"] += 1
                    mission_results["overall_success"] = False
                else:
                    mission_results["agents"][agent.call_sign] = result
                    if result.get("status") == "SUCCESS":
                        mission_results["successful_agents"] += 1
                    else:
                        mission_results["failed_agents"] += 1
                        mission_results["overall_success"] = False
            
            return mission_results
            
        except asyncio.TimeoutError:
            self.logger.error(f"TIMEOUT: Mission {mission_params.mission_id} exceeded time limit")
            
            # Cancel remaining tasks
            for task in deployment_tasks:
                if not task.done():
                    task.cancel()
            
            raise Exception(f"Mission timeout after {timeout_seconds} seconds")
    
    async def _emergency_extraction(self, agent_ids: List[str]) -> None:
        """Execute emergency extraction for failed mission"""
        self.logger.warning("EMERGENCY EXTRACTION: Initiating emergency extraction procedures")
        
        for agent_id in agent_ids:
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                agent.status = MissionStatus.ABORT
                agent.threat_level = ThreatLevel.RED
                
                self.logger.warning(f"EXTRACT: Agent {agent.call_sign} set to abort status")
        
        # Allow time for agents to abort safely
        await asyncio.sleep(1.0)
        
        self.logger.info("EMERGENCY EXTRACTION: Extraction complete")
    
    def get_mission_status(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific mission"""
        if mission_id in self.active_missions:
            mission_data = self.active_missions[mission_id]
            
            # Get agent statuses
            agent_statuses = {}
            for agent_id in mission_data["agents"]:
                if agent_id in self.agent_registry:
                    agent = self.agent_registry[agent_id]
                    agent_statuses[agent.call_sign] = agent.get_mission_status()
            
            return {
                "mission_id": mission_id,
                "status": mission_data["status"],
                "start_time": mission_data["start_time"].isoformat(),
                "threat_level": mission_data["threat_level"].value,
                "agents": agent_statuses
            }
        
        return None
    
    def get_operational_status(self) -> Dict[str, Any]:
        """Get overall operational status"""
        
        # Count agents by status
        agent_counts = {
            "total": len(self.agent_registry),
            "standby": 0,
            "deployed": 0,
            "failed": 0
        }
        
        for agent in self.agent_registry.values():
            if agent.status == MissionStatus.STANDBY:
                agent_counts["standby"] += 1
            elif agent.status in [MissionStatus.INFIL, MissionStatus.TARGET, 
                                MissionStatus.ASSAULT, MissionStatus.CONSOLIDATE, 
                                MissionStatus.EXFIL]:
                agent_counts["deployed"] += 1
            elif agent.status in [MissionStatus.FAILED, MissionStatus.ABORT]:
                agent_counts["failed"] += 1
        
        # Mission counts
        mission_counts = {
            "active": len([m for m in self.active_missions.values() if m["status"] == "ACTIVE"]),
            "completed": len([m for m in self.active_missions.values() if m["status"] == "COMPLETED"]),
            "failed": len([m for m in self.active_missions.values() if m["status"] == "FAILED"])
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "command_status": "OPERATIONAL",
            "agents": agent_counts,
            "missions": mission_counts,
            "squad_organization": {
                squad: len(agents) for squad, agents in self.squad_organization.items()
            }
        }