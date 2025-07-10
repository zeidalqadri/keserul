"""
Base Agent Framework for SEAL-Grade Multi-Agent Test Squad
"""

import time
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime


class MissionStatus(Enum):
    """Mission status classifications"""
    STANDBY = "STANDBY"
    INFIL = "INFIL"
    TARGET = "TARGET" 
    ASSAULT = "ASSAULT"
    CONSOLIDATE = "CONSOLIDATE"
    EXFIL = "EXFIL"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    ABORT = "ABORT"


class ThreatLevel(Enum):
    """Threat level classifications"""
    GREEN = "GREEN"      # No threat
    YELLOW = "YELLOW"    # Elevated risk
    ORANGE = "ORANGE"    # High risk
    RED = "RED"          # Critical threat
    BLACK = "BLACK"      # Mission failure


class ReportPriority(Enum):
    """Military reporting priority levels"""
    FLASH = "FLASH"          # < 5 seconds
    IMMEDIATE = "IMMEDIATE"  # < 30 seconds
    PRIORITY = "PRIORITY"    # < 2 minutes
    ROUTINE = "ROUTINE"      # < 15 minutes
    DEFERRED = "DEFERRED"    # < 24 hours


@dataclass
class SITREPReport:
    """Situation Report - Military standard reporting format"""
    agent_id: str
    mission_id: str
    timestamp: datetime
    status: MissionStatus
    threat_level: ThreatLevel
    priority: ReportPriority
    location: str
    personnel: Dict[str, str]
    equipment: Dict[str, str]
    situation: str
    mission_progress: str
    ammunition: Dict[str, Any]
    casualties: List[str]
    immediate_needs: List[str]
    eta_completion: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SITREP to dictionary format"""
        return {
            "agent_id": self.agent_id,
            "mission_id": self.mission_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "threat_level": self.threat_level.value,
            "priority": self.priority.value,
            "location": self.location,
            "personnel": self.personnel,
            "equipment": self.equipment,
            "situation": self.situation,
            "mission_progress": self.mission_progress,
            "ammunition": self.ammunition,
            "casualties": self.casualties,
            "immediate_needs": self.immediate_needs,
            "eta_completion": self.eta_completion.isoformat() if self.eta_completion else None
        }


@dataclass
class NineLine:
    """9-Line standardized reporting format for critical issues"""
    line1_location: str              # Location of incident
    line2_radio_frequency: str       # Radio frequency/comms channel
    line3_precedence: ReportPriority # Message precedence
    line4_equipment: str             # Special equipment required
    line5_patients: int              # Number of patients/issues
    line6_security: str              # Security at pickup site
    line7_marking_method: str        # Method of marking site
    line8_patient_nationality: str   # Patient nationality/system type
    line9_terrain_obstacles: str     # Terrain/obstacles description
    
    def format_message(self) -> str:
        """Format as standard 9-Line message"""
        return f"""
9-LINE REPORT:
LINE 1: {self.line1_location}
LINE 2: {self.line2_radio_frequency}
LINE 3: {self.line3_precedence.value}
LINE 4: {self.line4_equipment}
LINE 5: {self.line5_patients}
LINE 6: {self.line6_security}
LINE 7: {self.line7_marking_method}
LINE 8: {self.line8_patient_nationality}
LINE 9: {self.line9_terrain_obstacles}
"""


class BaseAgent(ABC):
    """Base class for all SEAL test agents"""
    
    def __init__(self, agent_id: str, call_sign: str, squad: str):
        self.agent_id = agent_id
        self.call_sign = call_sign
        self.squad = squad
        self.mission_id: Optional[str] = None
        self.status = MissionStatus.STANDBY
        self.threat_level = ThreatLevel.GREEN
        
        # Communication setup
        self.radio_frequency = f"FREQ_{squad.upper()}"
        self.logger = logging.getLogger(f"SEAL.{squad}.{call_sign}")
        
        # Mission tracking
        self.mission_start_time: Optional[datetime] = None
        self.mission_data: Dict[str, Any] = {}
        self.test_results: List[Dict[str, Any]] = []
        
        # Agent capabilities
        self.weapons_systems: List[str] = []
        self.equipment: Dict[str, str] = {}
        self.intelligence_sources: List[str] = []
        
        # Communication handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.sitrep_interval = 30  # seconds
        self.last_sitrep = datetime.now()
        
        self.logger.info(f"Agent {self.call_sign} ({self.agent_id}) initialized in {squad} squad")
    
    @abstractmethod
    async def execute_mission(self, mission_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary mission"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    async def deploy(self, mission_id: str, mission_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy agent for mission"""
        self.mission_id = mission_id
        self.mission_start_time = datetime.now()
        self.status = MissionStatus.INFIL
        
        self.logger.info(f"DEPLOYMENT: {self.call_sign} deploying for mission {mission_id}")
        
        try:
            # INFIL Phase
            await self._phase_infil(mission_parameters)
            
            # TARGET Phase
            await self._phase_target(mission_parameters)
            
            # ASSAULT Phase
            result = await self._phase_assault(mission_parameters)
            
            # CONSOLIDATE Phase
            await self._phase_consolidate(result)
            
            # EXFIL Phase
            await self._phase_exfil()
            
            self.status = MissionStatus.COMPLETE
            self.logger.info(f"MISSION COMPLETE: {self.call_sign} successfully completed mission {mission_id}")
            
            return {
                "status": "SUCCESS",
                "agent_id": self.agent_id,
                "mission_id": mission_id,
                "results": result,
                "execution_time": (datetime.now() - self.mission_start_time).total_seconds()
            }
            
        except Exception as e:
            self.status = MissionStatus.FAILED
            self.threat_level = ThreatLevel.RED
            
            # Send 9-Line report for critical failure
            nine_line = NineLine(
                line1_location=f"Agent {self.call_sign}",
                line2_radio_frequency=self.radio_frequency,
                line3_precedence=ReportPriority.FLASH,
                line4_equipment="ERROR_RECOVERY",
                line5_patients=1,
                line6_security="COMPROMISED",
                line7_marking_method="LOG_TRACE",
                line8_patient_nationality="SYSTEM",
                line9_terrain_obstacles=str(e)
            )
            
            self.logger.error(f"MISSION FAILED: {nine_line.format_message()}")
            
            return {
                "status": "FAILED",
                "agent_id": self.agent_id,
                "mission_id": mission_id,
                "error": str(e),
                "nine_line": nine_line.format_message()
            }
    
    async def _phase_infil(self, parameters: Dict[str, Any]) -> None:
        """Infiltration phase - setup and preparation"""
        self.status = MissionStatus.INFIL
        self.logger.info(f"INFIL: {self.call_sign} beginning infiltration")
        
        # Send SITREP
        await self._send_sitrep("Infiltration phase initiated")
        
        # Perform pre-mission checks
        await self._perform_equipment_check()
        await self._establish_communications()
        
        self.logger.info(f"INFIL COMPLETE: {self.call_sign} infiltration successful")
    
    async def _phase_target(self, parameters: Dict[str, Any]) -> None:
        """Target acquisition phase"""
        self.status = MissionStatus.TARGET
        self.logger.info(f"TARGET: {self.call_sign} acquiring targets")
        
        await self._send_sitrep("Target acquisition phase")
        await self._analyze_target_environment(parameters)
        
        self.logger.info(f"TARGET ACQUIRED: {self.call_sign} targets identified")
    
    async def _phase_assault(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct action phase - execute primary mission"""
        self.status = MissionStatus.ASSAULT
        self.logger.info(f"ASSAULT: {self.call_sign} beginning assault phase")
        
        await self._send_sitrep("Assault phase initiated - executing primary mission")
        
        # Execute the agent's specific mission
        result = await self.execute_mission(parameters)
        
        self.logger.info(f"ASSAULT COMPLETE: {self.call_sign} primary mission executed")
        return result
    
    async def _phase_consolidate(self, results: Dict[str, Any]) -> None:
        """Consolidation phase - secure results and assess"""
        self.status = MissionStatus.CONSOLIDATE
        self.logger.info(f"CONSOLIDATE: {self.call_sign} consolidating results")
        
        await self._send_sitrep("Consolidation phase - securing results")
        
        # Store results and perform damage assessment
        self.test_results.append(results)
        await self._battle_damage_assessment(results)
        
        self.logger.info(f"CONSOLIDATE COMPLETE: {self.call_sign} results secured")
    
    async def _phase_exfil(self) -> None:
        """Exfiltration phase - clean extraction"""
        self.status = MissionStatus.EXFIL
        self.logger.info(f"EXFIL: {self.call_sign} beginning exfiltration")
        
        await self._send_sitrep("Exfiltration phase - mission complete")
        await self._cleanup_operations()
        
        self.logger.info(f"EXFIL COMPLETE: {self.call_sign} successfully extracted")
    
    async def _send_sitrep(self, situation: str) -> None:
        """Send situation report"""
        if (datetime.now() - self.last_sitrep).total_seconds() >= self.sitrep_interval:
            sitrep = SITREPReport(
                agent_id=self.agent_id,
                mission_id=self.mission_id or "UNKNOWN",
                timestamp=datetime.now(),
                status=self.status,
                threat_level=self.threat_level,
                priority=ReportPriority.ROUTINE,
                location=f"Agent {self.call_sign}",
                personnel={self.call_sign: "OPERATIONAL"},
                equipment=self.equipment,
                situation=situation,
                mission_progress=f"{self.status.value} phase",
                ammunition={"test_cases": "SUFFICIENT"},
                casualties=[],
                immediate_needs=[]
            )
            
            self.logger.info(f"SITREP: {json.dumps(sitrep.to_dict(), indent=2)}")
            self.last_sitrep = datetime.now()
    
    async def _perform_equipment_check(self) -> None:
        """Perform equipment and systems check"""
        self.logger.debug(f"EQUIPMENT CHECK: {self.call_sign} checking systems")
        
        # Check basic capabilities
        capabilities = self.get_capabilities()
        for capability in capabilities:
            self.equipment[capability] = "OPERATIONAL"
        
        self.logger.debug(f"EQUIPMENT STATUS: All systems operational")
    
    async def _establish_communications(self) -> None:
        """Establish communication channels"""
        self.logger.debug(f"COMMS: {self.call_sign} establishing communications on {self.radio_frequency}")
        
        # Test communication channels
        await asyncio.sleep(0.1)  # Simulate comm check
        
        self.logger.debug(f"COMMS: Communication established")
    
    async def _analyze_target_environment(self, parameters: Dict[str, Any]) -> None:
        """Analyze target environment for threats and opportunities"""
        self.logger.debug(f"TARGET ANALYSIS: {self.call_sign} analyzing environment")
        
        # Perform threat assessment
        threat_indicators = parameters.get("threat_indicators", [])
        if threat_indicators:
            self.threat_level = ThreatLevel.YELLOW
            self.logger.warning(f"THREAT DETECTED: Elevated threat level")
        
        self.logger.debug(f"TARGET ANALYSIS: Environment assessment complete")
    
    async def _battle_damage_assessment(self, results: Dict[str, Any]) -> None:
        """Assess battle damage and mission effectiveness"""
        self.logger.debug(f"BDA: {self.call_sign} performing battle damage assessment")
        
        # Analyze results for success/failure indicators
        success_rate = results.get("success_rate", 0.0)
        if success_rate < 0.8:
            self.threat_level = ThreatLevel.YELLOW
            self.logger.warning(f"BDA: Mission effectiveness below threshold: {success_rate}")
        
        self.logger.debug(f"BDA: Assessment complete - {success_rate*100}% effectiveness")
    
    async def _cleanup_operations(self) -> None:
        """Perform cleanup operations"""
        self.logger.debug(f"CLEANUP: {self.call_sign} performing cleanup operations")
        
        # Clean up any temporary resources
        await asyncio.sleep(0.1)
        
        self.logger.debug(f"CLEANUP: Operations complete")
    
    def challenge_response(self, challenge: str) -> str:
        """Respond to authentication challenge"""
        # Simple challenge-response authentication
        responses = {
            "THUNDER": "FLASH",
            "STEEL": "RAIN", 
            "EAGLE": "THUNDER",
            "WARRIOR": "SPIRIT"
        }
        return responses.get(challenge, "UNKNOWN")
    
    async def receive_message(self, sender_id: str, message: Dict[str, Any]) -> None:
        """Receive message from another agent"""
        message_type = message.get("type", "UNKNOWN")
        
        if message_type in self.message_handlers:
            await self.message_handlers[message_type](sender_id, message)
        else:
            self.logger.warning(f"COMMS: Unknown message type {message_type} from {sender_id}")
    
    def get_mission_status(self) -> Dict[str, Any]:
        """Get current mission status"""
        return {
            "agent_id": self.agent_id,
            "call_sign": self.call_sign,
            "squad": self.squad,
            "mission_id": self.mission_id,
            "status": self.status.value,
            "threat_level": self.threat_level.value,
            "mission_start_time": self.mission_start_time.isoformat() if self.mission_start_time else None,
            "equipment": self.equipment,
            "test_results_count": len(self.test_results)
        }