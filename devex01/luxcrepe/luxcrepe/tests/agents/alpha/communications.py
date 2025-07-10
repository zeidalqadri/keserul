"""
Communications Agent - Alpha Squad Communications
Inter-agent coordination, reporting, and message routing
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import queue
import threading
from dataclasses import dataclass, field
from enum import Enum

from ...base_agent import BaseAgent, MissionStatus, ThreatLevel, ReportPriority, SITREPReport, NineLine


class MessageType(Enum):
    """Types of military communications"""
    SITREP = "SITREP"           # Situation Report
    NINE_LINE = "9LINE"         # Emergency Report
    INTSUM = "INTSUM"           # Intelligence Summary
    OPSUM = "OPSUM"             # Operations Summary
    WARNING_ORDER = "WARNO"     # Warning Order
    OPERATION_ORDER = "OPORD"   # Operation Order
    SPOT_REPORT = "SPOTREP"     # Spot Report
    COMMAND_MSG = "COMMAND"     # Command Message
    STATUS_UPDATE = "STATUS"    # Status Update
    EMERGENCY = "EMERGENCY"     # Emergency Communication


@dataclass
class MilitaryMessage:
    """Standard military message format"""
    message_id: str
    message_type: MessageType
    from_agent: str
    to_agents: List[str]
    timestamp: datetime
    priority: ReportPriority
    classification: str
    subject: str
    content: Dict[str, Any]
    acknowledgment_required: bool = False
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "from": self.from_agent,
            "to": self.to_agents,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "classification": self.classification,
            "subject": self.subject,
            "content": self.content,
            "acknowledgment_required": self.acknowledgment_required,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


class CommunicationsAgent(BaseAgent):
    """Communications Agent - Alpha Squad Communications
    
    Responsibilities:
    - Inter-agent message routing and delivery
    - Communication protocol enforcement
    - Message logging and archival
    - Emergency communication procedures
    - Network status monitoring
    - Secure communications management
    """
    
    def __init__(self):
        super().__init__(
            agent_id="ALPHA-003",
            call_sign="RADIO",
            squad="alpha"
        )
        
        # Communications capabilities
        self.weapons_systems = [
            "SECURE_COMMUNICATIONS",
            "MESSAGE_ROUTING",
            "PROTOCOL_ENFORCEMENT",
            "EMERGENCY_PROCEDURES"
        ]
        
        self.equipment = {
            "radio_systems": "OPERATIONAL",
            "encryption_modules": "ACTIVE",
            "message_processors": "ONLINE",
            "backup_channels": "STANDBY"
        }
        
        self.intelligence_sources = [
            "MESSAGE_TRAFFIC",
            "NETWORK_STATUS",
            "COMM_PATTERNS",
            "SIGNAL_ANALYSIS"
        ]
        
        # Communications infrastructure
        self.message_queue: queue.Queue = queue.Queue()
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.message_log: List[MilitaryMessage] = []
        self.acknowledgments: Dict[str, List[str]] = {}
        self.emergency_procedures: Dict[str, Callable] = {}
        
        # Network status tracking
        self.network_status: Dict[str, Any] = {
            "status": "OPERATIONAL",
            "active_connections": 0,
            "message_throughput": 0,
            "error_rate": 0.0,
            "last_heartbeat": datetime.now()
        }
        
        # Communication channels
        self.channels: Dict[str, List[str]] = {
            "COMMAND_NET": [],      # Command and control
            "ADMIN_NET": [],        # Administrative traffic
            "INTEL_NET": [],        # Intelligence sharing
            "TACTICAL_NET": [],     # Tactical coordination
            "EMERGENCY_NET": []     # Emergency communications
        }
        
        # Message processing
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.SITREP: self._handle_sitrep,
            MessageType.NINE_LINE: self._handle_nine_line,
            MessageType.INTSUM: self._handle_intelligence_summary,
            MessageType.EMERGENCY: self._handle_emergency,
            MessageType.COMMAND_MSG: self._handle_command_message,
            MessageType.STATUS_UPDATE: self._handle_status_update
        }
        
        # Start communications processing
        self._start_communications_processing()
        
        self.logger.info("RADIO: Communications Agent initialized - All nets operational")
    
    def get_capabilities(self) -> List[str]:
        """Return communications capabilities"""
        return [
            "message_routing",
            "secure_communications",
            "protocol_enforcement",
            "emergency_procedures",
            "network_monitoring",
            "traffic_analysis",
            "encryption_services",
            "multi_channel_coordination",
            "acknowledgment_tracking",
            "communications_intelligence"
        ]
    
    async def execute_mission(self, mission_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute communications mission"""
        
        self.logger.info("RADIO: Establishing communications for mission")
        
        mission_id = mission_parameters.get("mission_id", "UNKNOWN")
        participating_agents = mission_parameters.get("agents", [])
        
        # Communications Phase 1: Network Initialization
        network_setup = await self._initialize_mission_network(mission_id, participating_agents)
        
        # Communications Phase 2: Protocol Establishment
        protocols = await self._establish_communication_protocols(mission_parameters)
        
        # Communications Phase 3: Traffic Monitoring
        monitoring_results = await self._monitor_mission_communications(mission_id)
        
        # Communications Phase 4: Message Processing and Routing
        routing_stats = await self._process_mission_traffic()
        
        # Communications Phase 5: Network Teardown
        teardown_results = await self._teardown_mission_network(mission_id)
        
        self.logger.info("RADIO: Mission communications complete")
        
        return {
            "network_initialization": network_setup,
            "communication_protocols": protocols,
            "monitoring_results": monitoring_results,
            "message_routing_stats": routing_stats,
            "network_teardown": teardown_results,
            "total_messages_processed": len(self.message_log),
            "network_performance": self.network_status
        }
    
    async def _initialize_mission_network(self, mission_id: str, agents: List[str]) -> Dict[str, Any]:
        """Initialize communications network for mission"""
        
        self.logger.info("RADIO: Initializing mission communications network")
        
        # Register all participating agents
        for agent_id in agents:
            self.register_agent(agent_id, {
                "status": "ACTIVE",
                "last_contact": datetime.now(),
                "message_count": 0,
                "channel_assignments": ["COMMAND_NET", "TACTICAL_NET"]
            })
        
        # Establish communication channels
        self.channels["COMMAND_NET"] = [a for a in agents if "ALPHA" in a]
        self.channels["TACTICAL_NET"] = agents
        self.channels["INTEL_NET"] = [a for a in agents if "ALPHA-002" in a or "DELTA" in a]
        
        # Initialize mission-specific protocols
        mission_protocols = {
            "authentication_required": True,
            "encryption_level": "AES_256",
            "message_retention": "24_HOURS",
            "priority_routing": True,
            "emergency_escalation": True
        }
        
        # Send initialization message to all agents
        init_message = MilitaryMessage(
            message_id=f"INIT_{mission_id}_{int(datetime.now().timestamp())}",
            message_type=MessageType.WARNING_ORDER,
            from_agent=self.agent_id,
            to_agents=agents,
            timestamp=datetime.now(),
            priority=ReportPriority.IMMEDIATE,
            classification="UNCLASSIFIED",
            subject="COMMUNICATIONS INITIALIZATION",
            content={
                "mission_id": mission_id,
                "communication_protocols": mission_protocols,
                "channel_assignments": self.channels,
                "emergency_procedures": "STANDARD_SEAL_PROTOCOLS"
            },
            acknowledgment_required=True,
            expires_at=datetime.now() + timedelta(minutes=30)
        )
        
        await self._broadcast_message(init_message)
        
        return {
            "network_status": "INITIALIZED",
            "agents_registered": len(agents),
            "channels_established": len(self.channels),
            "protocols_loaded": mission_protocols,
            "initialization_time": datetime.now().isoformat()
        }
    
    async def _establish_communication_protocols(self, mission_params: Dict[str, Any]) -> Dict[str, Any]:
        """Establish mission-specific communication protocols"""
        
        self.logger.info("RADIO: Establishing communication protocols")
        
        # Determine protocol requirements based on mission type
        mission_type = mission_params.get("mission_type", "STANDARD")
        threat_level = mission_params.get("threat_level", ThreatLevel.GREEN.value)
        
        protocols = {
            "message_authentication": True,
            "end_to_end_encryption": True,
            "message_compression": False,
            "priority_queue_enabled": True,
            "heartbeat_interval": 30,  # seconds
            "timeout_settings": {
                "message_delivery": 10,
                "acknowledgment": 5,
                "emergency_response": 2
            },
            "retry_policies": {
                "max_retries": 3,
                "retry_interval": 2,
                "exponential_backoff": True
            }
        }
        
        # Adjust protocols based on threat level
        if threat_level in [ThreatLevel.ORANGE.value, ThreatLevel.RED.value]:
            protocols.update({
                "message_compression": True,
                "burst_transmission": True,
                "frequency_hopping": True,
                "stealth_mode": True
            })
        
        # Configure emergency procedures
        self.emergency_procedures = {
            "MISSION_ABORT": self._emergency_abort_procedure,
            "AGENT_DOWN": self._emergency_agent_down_procedure,
            "COMMUNICATIONS_COMPROMISED": self._emergency_comms_compromised_procedure,
            "EXTRACTION_REQUIRED": self._emergency_extraction_procedure
        }
        
        return protocols
    
    async def _monitor_mission_communications(self, mission_id: str) -> Dict[str, Any]:
        """Monitor communications during mission execution"""
        
        self.logger.info("RADIO: Monitoring mission communications")
        
        monitoring_start = datetime.now()
        monitoring_data = {
            "monitoring_start": monitoring_start.isoformat(),
            "message_statistics": {},
            "network_performance": {},
            "security_events": [],
            "anomalies_detected": []
        }
        
        # Monitor for a brief period (in real implementation, this would be continuous)
        await asyncio.sleep(1)
        
        # Collect statistics
        monitoring_data["message_statistics"] = {
            "total_messages": len(self.message_log),
            "messages_by_type": self._count_messages_by_type(),
            "messages_by_priority": self._count_messages_by_priority(),
            "average_message_size": self._calculate_average_message_size(),
            "peak_throughput": self._calculate_peak_throughput()
        }
        
        # Network performance metrics
        monitoring_data["network_performance"] = {
            "latency_average": 0.05,  # seconds
            "packet_loss_rate": 0.0,
            "bandwidth_utilization": 0.15,
            "error_rate": self.network_status["error_rate"],
            "uptime_percentage": 100.0
        }
        
        # Check for anomalies
        anomalies = self._detect_communication_anomalies()
        if anomalies:
            monitoring_data["anomalies_detected"] = anomalies
            self.threat_level = ThreatLevel.YELLOW
        
        return monitoring_data
    
    async def _process_mission_traffic(self) -> Dict[str, Any]:
        """Process and route mission communications traffic"""
        
        self.logger.info("RADIO: Processing mission communications traffic")
        
        processing_stats = {
            "messages_processed": 0,
            "messages_routed": 0,
            "messages_failed": 0,
            "average_processing_time": 0.0,
            "routing_efficiency": 0.0
        }
        
        processed_messages = 0
        total_processing_time = 0.0
        
        # Process queued messages
        while not self.message_queue.empty():
            try:
                start_time = datetime.now()
                message = self.message_queue.get_nowait()
                
                # Route message based on type and priority
                await self._route_message(message)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                total_processing_time += processing_time
                processed_messages += 1
                processing_stats["messages_processed"] += 1
                processing_stats["messages_routed"] += 1
                
            except queue.Empty:
                break
            except Exception as e:
                processing_stats["messages_failed"] += 1
                self.logger.error(f"RADIO: Message processing failed: {str(e)}")
        
        # Calculate statistics
        if processed_messages > 0:
            processing_stats["average_processing_time"] = total_processing_time / processed_messages
            processing_stats["routing_efficiency"] = (processing_stats["messages_routed"] / 
                                                    processing_stats["messages_processed"]) * 100
        
        return processing_stats
    
    async def _teardown_mission_network(self, mission_id: str) -> Dict[str, Any]:
        """Teardown mission communications network"""
        
        self.logger.info("RADIO: Tearing down mission communications network")
        
        # Send mission complete notification
        completion_message = MilitaryMessage(
            message_id=f"COMPLETE_{mission_id}_{int(datetime.now().timestamp())}",
            message_type=MessageType.OPSUM,
            from_agent=self.agent_id,
            to_agents=list(self.agent_registry.keys()),
            timestamp=datetime.now(),
            priority=ReportPriority.ROUTINE,
            classification="UNCLASSIFIED",
            subject="MISSION COMMUNICATIONS COMPLETE",
            content={
                "mission_id": mission_id,
                "network_status": "TEARDOWN_INITIATED",
                "final_statistics": {
                    "total_messages": len(self.message_log),
                    "active_agents": len(self.agent_registry),
                    "mission_duration": "UNKNOWN"
                }
            }
        )
        
        await self._broadcast_message(completion_message)
        
        # Archive mission communications
        archive_data = {
            "mission_id": mission_id,
            "total_messages": len(self.message_log),
            "message_archive": [msg.to_dict() for msg in self.message_log],
            "agent_statistics": self.agent_registry.copy(),
            "network_performance": self.network_status.copy()
        }
        
        # Reset for next mission
        self.message_log.clear()
        self.agent_registry.clear()
        self.acknowledgments.clear()
        
        # Reset channels to standby
        for channel in self.channels:
            self.channels[channel].clear()
        
        return {
            "teardown_status": "COMPLETE",
            "messages_archived": archive_data["total_messages"],
            "archive_location": f"MISSION_{mission_id}_COMMS_ARCHIVE",
            "teardown_time": datetime.now().isoformat()
        }
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> None:
        """Register agent in communications network"""
        self.agent_registry[agent_id] = agent_info
        self.logger.info(f"RADIO: Agent {agent_id} registered in communications network")
    
    async def send_message(self, message: MilitaryMessage) -> bool:
        """Send message through communications network"""
        try:
            # Validate message
            if not self._validate_message(message):
                self.logger.error(f"RADIO: Message validation failed: {message.message_id}")
                return False
            
            # Add to queue for processing
            self.message_queue.put(message)
            self.message_log.append(message)
            
            # Process immediately if high priority
            if message.priority in [ReportPriority.FLASH, ReportPriority.IMMEDIATE]:
                await self._route_message(message)
            
            self.logger.info(f"RADIO: Message {message.message_id} queued for delivery")
            return True
            
        except Exception as e:
            self.logger.error(f"RADIO: Failed to send message: {str(e)}")
            return False
    
    async def _broadcast_message(self, message: MilitaryMessage) -> None:
        """Broadcast message to all recipients"""
        for recipient in message.to_agents:
            if recipient in self.agent_registry:
                await self._deliver_message_to_agent(recipient, message)
            else:
                self.logger.warning(f"RADIO: Recipient {recipient} not found in registry")
    
    async def _route_message(self, message: MilitaryMessage) -> None:
        """Route message based on type and priority"""
        
        # Priority-based routing
        if message.priority == ReportPriority.FLASH:
            # Immediate delivery to all recipients
            await self._broadcast_message(message)
        elif message.priority == ReportPriority.IMMEDIATE:
            # High priority delivery
            await self._broadcast_message(message)
        else:
            # Standard delivery queue
            await self._broadcast_message(message)
        
        # Handle specific message types
        if message.message_type in self.message_handlers:
            await self.message_handlers[message.message_type](message)
    
    async def _deliver_message_to_agent(self, agent_id: str, message: MilitaryMessage) -> None:
        """Deliver message to specific agent"""
        try:
            # Update agent statistics
            if agent_id in self.agent_registry:
                self.agent_registry[agent_id]["message_count"] += 1
                self.agent_registry[agent_id]["last_contact"] = datetime.now()
            
            # Track acknowledgments if required
            if message.acknowledgment_required:
                if message.message_id not in self.acknowledgments:
                    self.acknowledgments[message.message_id] = []
                # In real implementation, would wait for actual acknowledgment
                self.acknowledgments[message.message_id].append(agent_id)
            
            self.logger.debug(f"RADIO: Message {message.message_id} delivered to {agent_id}")
            
        except Exception as e:
            self.logger.error(f"RADIO: Failed to deliver message to {agent_id}: {str(e)}")
    
    def _validate_message(self, message: MilitaryMessage) -> bool:
        """Validate message format and content"""
        
        # Check required fields
        if not all([message.message_id, message.from_agent, message.to_agents]):
            return False
        
        # Check message type is valid
        if not isinstance(message.message_type, MessageType):
            return False
        
        # Check priority is valid
        if not isinstance(message.priority, ReportPriority):
            return False
        
        # Check expiration
        if message.expires_at and message.expires_at < datetime.now():
            return False
        
        return True
    
    async def _handle_sitrep(self, message: MilitaryMessage) -> None:
        """Handle SITREP messages"""
        self.logger.info(f"RADIO: Processing SITREP from {message.from_agent}")
        
        # Forward SITREPs to command channel
        if message.from_agent not in self.channels["COMMAND_NET"]:
            # Relay to command net
            command_agents = self.channels["COMMAND_NET"]
            if command_agents:
                relay_message = MilitaryMessage(
                    message_id=f"RELAY_{message.message_id}",
                    message_type=MessageType.SITREP,
                    from_agent=self.agent_id,
                    to_agents=command_agents,
                    timestamp=datetime.now(),
                    priority=message.priority,
                    classification=message.classification,
                    subject=f"RELAYED: {message.subject}",
                    content=message.content
                )
                await self._broadcast_message(relay_message)
    
    async def _handle_nine_line(self, message: MilitaryMessage) -> None:
        """Handle 9-Line emergency reports"""
        self.logger.warning(f"RADIO: Processing 9-Line emergency report from {message.from_agent}")
        
        # Escalate to emergency procedures
        await self._emergency_escalation(message)
        
        # Ensure all command agents receive 9-Line
        command_agents = self.channels["COMMAND_NET"]
        if command_agents:
            for agent in command_agents:
                await self._deliver_message_to_agent(agent, message)
    
    async def _handle_intelligence_summary(self, message: MilitaryMessage) -> None:
        """Handle intelligence summary messages"""
        self.logger.info(f"RADIO: Processing INTSUM from {message.from_agent}")
        
        # Route to intelligence network
        intel_agents = self.channels["INTEL_NET"]
        for agent in intel_agents:
            if agent != message.from_agent:
                await self._deliver_message_to_agent(agent, message)
    
    async def _handle_emergency(self, message: MilitaryMessage) -> None:
        """Handle emergency communications"""
        self.logger.error(f"RADIO: EMERGENCY MESSAGE from {message.from_agent}")
        
        # Immediate broadcast to all agents
        await self._broadcast_message(message)
        
        # Activate emergency procedures
        emergency_type = message.content.get("emergency_type", "UNKNOWN")
        if emergency_type in self.emergency_procedures:
            await self.emergency_procedures[emergency_type](message)
    
    async def _handle_command_message(self, message: MilitaryMessage) -> None:
        """Handle command messages"""
        self.logger.info(f"RADIO: Processing COMMAND message from {message.from_agent}")
        
        # Commands are routed based on authority level
        # For now, broadcast to tactical net
        tactical_agents = self.channels["TACTICAL_NET"]
        for agent in tactical_agents:
            if agent != message.from_agent:
                await self._deliver_message_to_agent(agent, message)
    
    async def _handle_status_update(self, message: MilitaryMessage) -> None:
        """Handle status update messages"""
        self.logger.debug(f"RADIO: Processing status update from {message.from_agent}")
        
        # Update agent status in registry
        if message.from_agent in self.agent_registry:
            status_data = message.content.get("status", {})
            self.agent_registry[message.from_agent].update(status_data)
    
    def _count_messages_by_type(self) -> Dict[str, int]:
        """Count messages by type"""
        counts = {}
        for message in self.message_log:
            msg_type = message.message_type.value
            counts[msg_type] = counts.get(msg_type, 0) + 1
        return counts
    
    def _count_messages_by_priority(self) -> Dict[str, int]:
        """Count messages by priority"""
        counts = {}
        for message in self.message_log:
            priority = message.priority.value
            counts[priority] = counts.get(priority, 0) + 1
        return counts
    
    def _calculate_average_message_size(self) -> float:
        """Calculate average message size"""
        if not self.message_log:
            return 0.0
        
        total_size = sum(len(json.dumps(msg.to_dict())) for msg in self.message_log)
        return total_size / len(self.message_log)
    
    def _calculate_peak_throughput(self) -> float:
        """Calculate peak message throughput"""
        # Simplified calculation
        if len(self.message_log) > 0:
            return len(self.message_log) / 60.0  # messages per minute
        return 0.0
    
    def _detect_communication_anomalies(self) -> List[str]:
        """Detect communication anomalies"""
        anomalies = []
        
        # Check for high error rates
        if self.network_status["error_rate"] > 0.05:
            anomalies.append("HIGH_ERROR_RATE")
        
        # Check for unusual message patterns
        if len(self.message_log) > 100:
            anomalies.append("HIGH_MESSAGE_VOLUME")
        
        # Check for agent connectivity issues
        down_agents = [agent_id for agent_id, info in self.agent_registry.items()
                      if (datetime.now() - info["last_contact"]).total_seconds() > 120]
        if down_agents:
            anomalies.append(f"AGENTS_UNRESPONSIVE_{len(down_agents)}")
        
        return anomalies
    
    async def _emergency_escalation(self, message: MilitaryMessage) -> None:
        """Handle emergency escalation procedures"""
        self.logger.warning("RADIO: Initiating emergency escalation procedures")
        
        # Set network to emergency status
        self.network_status["status"] = "EMERGENCY"
        self.threat_level = ThreatLevel.RED
        
        # Notify all command agents
        emergency_notification = MilitaryMessage(
            message_id=f"EMERGENCY_ESCALATION_{int(datetime.now().timestamp())}",
            message_type=MessageType.EMERGENCY,
            from_agent=self.agent_id,
            to_agents=self.channels["COMMAND_NET"],
            timestamp=datetime.now(),
            priority=ReportPriority.FLASH,
            classification="URGENT",
            subject="EMERGENCY ESCALATION INITIATED",
            content={
                "original_message": message.to_dict(),
                "escalation_reason": "9_LINE_RECEIVED",
                "recommended_action": "IMMEDIATE_RESPONSE_REQUIRED"
            }
        )
        
        await self._broadcast_message(emergency_notification)
    
    async def _emergency_abort_procedure(self, message: MilitaryMessage) -> None:
        """Execute mission abort procedures"""
        self.logger.error("RADIO: Executing MISSION ABORT procedures")
        
        # Broadcast abort to all agents
        abort_message = MilitaryMessage(
            message_id=f"ABORT_{int(datetime.now().timestamp())}",
            message_type=MessageType.COMMAND_MSG,
            from_agent=self.agent_id,
            to_agents=list(self.agent_registry.keys()),
            timestamp=datetime.now(),
            priority=ReportPriority.FLASH,
            classification="URGENT",
            subject="MISSION ABORT - IMMEDIATE",
            content={
                "command": "ABORT_MISSION",
                "reason": message.content.get("reason", "UNKNOWN"),
                "extraction_point": "DESIGNATED_RALLY_POINT",
                "abort_time": datetime.now().isoformat()
            }
        )
        
        await self._broadcast_message(abort_message)
    
    async def _emergency_agent_down_procedure(self, message: MilitaryMessage) -> None:
        """Handle agent down emergency"""
        self.logger.error("RADIO: Agent down emergency procedures")
        
        down_agent = message.content.get("agent_id", "UNKNOWN")
        
        # Remove from active registry
        if down_agent in self.agent_registry:
            self.agent_registry[down_agent]["status"] = "DOWN"
        
        # Notify command structure
        agent_down_message = MilitaryMessage(
            message_id=f"AGENT_DOWN_{int(datetime.now().timestamp())}",
            message_type=MessageType.SPOT_REPORT,
            from_agent=self.agent_id,
            to_agents=self.channels["COMMAND_NET"],
            timestamp=datetime.now(),
            priority=ReportPriority.IMMEDIATE,
            classification="URGENT",
            subject=f"AGENT DOWN: {down_agent}",
            content={
                "down_agent": down_agent,
                "last_contact": self.agent_registry.get(down_agent, {}).get("last_contact", "UNKNOWN"),
                "recommended_action": "REDISTRIBUTE_WORKLOAD"
            }
        )
        
        await self._broadcast_message(agent_down_message)
    
    async def _emergency_comms_compromised_procedure(self, message: MilitaryMessage) -> None:
        """Handle communications compromise"""
        self.logger.error("RADIO: Communications compromise detected")
        
        # Switch to backup protocols
        self.network_status["status"] = "COMPROMISED_BACKUP_ACTIVE"
        
        # Notify all agents to switch to secure backup channels
        backup_message = MilitaryMessage(
            message_id=f"BACKUP_COMMS_{int(datetime.now().timestamp())}",
            message_type=MessageType.WARNING_ORDER,
            from_agent=self.agent_id,
            to_agents=list(self.agent_registry.keys()),
            timestamp=datetime.now(),
            priority=ReportPriority.FLASH,
            classification="SECRET",
            subject="SWITCH TO BACKUP COMMUNICATIONS",
            content={
                "reason": "PRIMARY_COMMS_COMPROMISED",
                "backup_protocols": "ENCRYPTED_SECONDARY_CHANNELS",
                "authentication": "ENHANCED_CHALLENGE_RESPONSE"
            }
        )
        
        await self._broadcast_message(backup_message)
    
    async def _emergency_extraction_procedure(self, message: MilitaryMessage) -> None:
        """Handle emergency extraction"""
        self.logger.error("RADIO: Emergency extraction procedures")
        
        extraction_message = MilitaryMessage(
            message_id=f"EXTRACTION_{int(datetime.now().timestamp())}",
            message_type=MessageType.WARNING_ORDER,
            from_agent=self.agent_id,
            to_agents=list(self.agent_registry.keys()),
            timestamp=datetime.now(),
            priority=ReportPriority.FLASH,
            classification="URGENT",
            subject="EMERGENCY EXTRACTION INITIATED",
            content={
                "extraction_reason": message.content.get("reason", "UNKNOWN"),
                "rally_point": "PRIMARY_EXTRACTION_POINT",
                "timeline": "IMMEDIATE",
                "cover_protocols": "MAINTAIN_STEALTH"
            }
        )
        
        await self._broadcast_message(extraction_message)
    
    def _start_communications_processing(self) -> None:
        """Start background communications processing"""
        def process_communications():
            """Background thread for processing communications"""
            while True:
                try:
                    # Update network status
                    self.network_status["last_heartbeat"] = datetime.now()
                    self.network_status["active_connections"] = len(self.agent_registry)
                    
                    # Clean up expired messages
                    self._cleanup_expired_messages()
                    
                    # Sleep for heartbeat interval
                    import time
                    time.sleep(30)  # 30 second heartbeat
                    
                except Exception as e:
                    self.logger.error(f"RADIO: Communications processing error: {str(e)}")
        
        # Start background thread
        comm_thread = threading.Thread(target=process_communications, daemon=True)
        comm_thread.start()
    
    def _cleanup_expired_messages(self) -> None:
        """Clean up expired messages"""
        current_time = datetime.now()
        
        # Remove expired messages from log
        self.message_log = [msg for msg in self.message_log 
                           if not msg.expires_at or msg.expires_at > current_time]
        
        # Clean up old acknowledgments
        expired_acks = [msg_id for msg_id, acks in self.acknowledgments.items()
                       if len(acks) == 0]  # Simplified cleanup
        
        for msg_id in expired_acks:
            del self.acknowledgments[msg_id]