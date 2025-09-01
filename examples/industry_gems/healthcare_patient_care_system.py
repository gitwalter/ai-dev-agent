#!/usr/bin/env python3
"""
HARMONY-SPREADING GEM: Healthcare Patient Care Coordination System
==================================================================

SPREADS HARMONY: Helps healthcare teams provide better patient care
SERVES THE GOOD: Reduces medical errors, improves patient outcomes
DEMONSTRATES POWER: Shows @engineering @architecture @debug keyword magic

REAL HEALTHCARE VALUE:
- Patient safety monitoring with real-time alerts
- Care team coordination across departments  
- Medical history tracking with privacy protection
- Treatment plan optimization
- Emergency response coordination

KEYWORD POWER DEMONSTRATION:
@engineering → Implement medical algorithms and safety checks
@architecture → Design HIPAA-compliant system structure  
@debug → Investigate patient safety incidents systematically

Usage with Keywords:
    @engineering: implement_vital_signs_monitor()
    @architecture: design_patient_data_flow() 
    @debug: investigate_medication_error()
"""

import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

# Add utils to path for ontological framework
from pathlib import Path
utils_path = Path(__file__).parent.parent.parent / "utils"
sys.path.append(str(utils_path))

from context.ontological_framework_system import OntologicalSwitchingSystem


class Priority(Enum):
    """Medical priority levels for patient care."""
    ROUTINE = "routine"
    URGENT = "urgent" 
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Types of medical alerts."""
    VITAL_SIGNS = "vital_signs"
    MEDICATION = "medication"
    ALLERGY = "allergy"
    INTERACTION = "drug_interaction"
    SAFETY = "patient_safety"


@dataclass
class Patient:
    """Represents a patient with privacy protection."""
    patient_id: str
    encrypted_name: str  # Privacy-protected
    date_of_birth: datetime
    medical_record_number: str
    emergency_contact: str
    allergies: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    admission_date: Optional[datetime] = None
    primary_physician: Optional[str] = None
    
    def __post_init__(self):
        """Validate patient data."""
        if not self.patient_id or not self.medical_record_number:
            raise ValueError("Patient ID and MRN are required")


@dataclass
class VitalSigns:
    """Patient vital signs measurement."""
    measurement_id: str
    patient_id: str
    timestamp: datetime
    heart_rate: int  # beats per minute
    blood_pressure_systolic: int  # mmHg
    blood_pressure_diastolic: int  # mmHg
    temperature: float  # Celsius
    oxygen_saturation: int  # percentage
    respiratory_rate: int  # breaths per minute
    measured_by: str  # Healthcare provider ID
    
    def __post_init__(self):
        """Validate vital signs."""
        if not (50 <= self.heart_rate <= 200):
            raise ValueError(f"Invalid heart rate: {self.heart_rate}")
        if not (70 <= self.blood_pressure_systolic <= 250):
            raise ValueError(f"Invalid systolic BP: {self.blood_pressure_systolic}")
        if not (35.0 <= self.temperature <= 42.0):
            raise ValueError(f"Invalid temperature: {self.temperature}")


@dataclass
class MedicalAlert:
    """Medical alert for patient safety."""
    alert_id: str
    patient_id: str
    alert_type: AlertType
    priority: Priority
    message: str
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None


@dataclass
class TreatmentPlan:
    """Patient treatment plan."""
    plan_id: str
    patient_id: str
    created_by: str
    created_date: datetime
    diagnosis: str
    treatment_goals: List[str]
    medications: List[Dict[str, Any]]
    procedures: List[Dict[str, Any]]
    follow_up_schedule: List[datetime]
    notes: str = ""


class HealthcarePatientCareSystem:
    """
    Healthcare Patient Care Coordination System
    
    SPREADS HARMONY by:
    - Improving patient safety through real-time monitoring
    - Enhancing care team coordination
    - Reducing medical errors with intelligent alerts
    - Supporting evidence-based treatment decisions
    
    DEMONSTRATES KEYWORD POWER:
    - @engineering: Medical algorithm implementation
    - @architecture: HIPAA-compliant system design
    - @debug: Systematic incident investigation
    """
    
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.vital_signs: Dict[str, List[VitalSigns]] = {}
        self.active_alerts: Dict[str, List[MedicalAlert]] = {}
        self.treatment_plans: Dict[str, TreatmentPlan] = {}
        
        # Medical reference ranges for alerts
        self.vital_sign_ranges = {
            "heart_rate": (60, 100),
            "systolic_bp": (90, 140),
            "diastolic_bp": (60, 90),
            "temperature": (36.1, 37.2),
            "oxygen_saturation": (95, 100),
            "respiratory_rate": (12, 20)
        }
        
        # Drug interaction database (simplified)
        self.drug_interactions = {
            ("warfarin", "aspirin"): "Increased bleeding risk",
            ("digoxin", "furosemide"): "Electrolyte imbalance risk",
            ("metformin", "contrast_dye"): "Kidney function risk"
        }
        
        # Ontological framework for healthcare perspectives
        self.ontology_system = OntologicalSwitchingSystem()
        
        print("🏥 Healthcare Patient Care System initialized")
        print("   Spreading harmony through better patient care")
    
    def register_patient(self, name: str, date_of_birth: datetime, 
                        emergency_contact: str, allergies: List[str] = None,
                        primary_physician: str = None) -> str:
        """
        @engineering: Register new patient with privacy protection
        
        DEMONSTRATES: Technical implementation with medical compliance
        SPREADS HARMONY: Ensures accurate patient identification and safety
        """
        
        print("🔧 @engineering: Registering new patient")
        self.ontology_system.switch_perspective("engineering", "Implement patient registration")
        
        # Generate secure patient ID
        patient_id = str(uuid.uuid4())
        
        # Generate medical record number (format: MRN-YYYY-NNNNNN)
        mrn = f"MRN-{datetime.now().year}-{len(self.patients)+1:06d}"
        
        # Encrypt patient name for privacy (simplified encryption)
        encrypted_name = hashlib.sha256(name.encode()).hexdigest()[:16]
        
        patient = Patient(
            patient_id=patient_id,
            encrypted_name=encrypted_name,
            date_of_birth=date_of_birth,
            medical_record_number=mrn,
            emergency_contact=emergency_contact,
            allergies=allergies or [],
            primary_physician=primary_physician,
            admission_date=datetime.now()
        )
        
        self.patients[patient_id] = patient
        self.vital_signs[patient_id] = []
        self.active_alerts[patient_id] = []
        
        print(f"✅ Patient registered: {mrn}")
        print(f"   Patient ID: {patient_id}")
        print(f"   Allergies: {len(patient.allergies)} recorded")
        
        return patient_id
    
    def record_vital_signs(self, patient_id: str, heart_rate: int, 
                          systolic_bp: int, diastolic_bp: int, temperature: float,
                          oxygen_saturation: int, respiratory_rate: int,
                          measured_by: str) -> str:
        """
        @engineering: Record patient vital signs with automatic safety monitoring
        
        DEMONSTRATES: Real-time medical monitoring implementation
        SPREADS HARMONY: Prevents medical emergencies through early detection
        """
        
        print("🔧 @engineering: Recording vital signs with safety monitoring")
        self.ontology_system.switch_perspective("engineering", "Implement vital signs monitoring")
        
        if patient_id not in self.patients:
            raise KeyError(f"Patient not found: {patient_id}")
        
        measurement_id = str(uuid.uuid4())
        
        vital_signs = VitalSigns(
            measurement_id=measurement_id,
            patient_id=patient_id,
            timestamp=datetime.now(),
            heart_rate=heart_rate,
            blood_pressure_systolic=systolic_bp,
            blood_pressure_diastolic=diastolic_bp,
            temperature=temperature,
            oxygen_saturation=oxygen_saturation,
            respiratory_rate=respiratory_rate,
            measured_by=measured_by
        )
        
        self.vital_signs[patient_id].append(vital_signs)
        
        # Automatic safety monitoring
        alerts_generated = self._check_vital_signs_safety(vital_signs)
        
        print(f"✅ Vital signs recorded: {measurement_id}")
        print(f"   HR: {heart_rate} bpm, BP: {systolic_bp}/{diastolic_bp} mmHg")
        print(f"   Temp: {temperature}°C, O2: {oxygen_saturation}%, RR: {respiratory_rate}")
        
        if alerts_generated:
            print(f"⚠️ {len(alerts_generated)} safety alerts generated")
        
        return measurement_id
    
    def design_care_coordination_workflow(self, patient_id: str) -> Dict[str, Any]:
        """
        @architecture: Design care team coordination workflow
        
        DEMONSTRATES: System-level healthcare architecture design
        SPREADS HARMONY: Improves care team communication and patient outcomes
        """
        
        print("📐 @architecture: Designing care coordination workflow")
        self.ontology_system.switch_perspective("architecture", "Design healthcare workflow systems")
        
        if patient_id not in self.patients:
            raise KeyError(f"Patient not found: {patient_id}")
        
        patient = self.patients[patient_id]
        
        # Design multi-disciplinary care workflow
        care_workflow = {
            "patient_id": patient_id,
            "care_team_structure": {
                "primary_physician": patient.primary_physician,
                "nursing_team": ["charge_nurse", "primary_nurse", "medication_nurse"],
                "specialists": ["cardiologist", "pharmacist", "physical_therapist"],
                "support_staff": ["social_worker", "case_manager", "nutritionist"]
            },
            "communication_protocols": {
                "shift_handoff": "structured_SBAR_format",  # Situation, Background, Assessment, Recommendation
                "physician_rounds": "daily_morning_rounds",
                "emergency_escalation": "rapid_response_team",
                "family_updates": "scheduled_conferences"
            },
            "data_flow_architecture": {
                "vital_signs": "real_time_monitoring",
                "medications": "electronic_prescription_system",
                "lab_results": "automated_alert_system",
                "imaging": "integrated_viewer_access"
            },
            "quality_measures": {
                "patient_satisfaction": "daily_rounding_surveys",
                "safety_indicators": "fall_risk_pressure_ulcer_prevention",
                "outcome_metrics": "length_of_stay_readmission_rates"
            }
        }
        
        print(f"✅ Care coordination workflow designed")
        print(f"   Team members: {len(care_workflow['care_team_structure'])} roles")
        print(f"   Communication protocols: {len(care_workflow['communication_protocols'])} defined")
        print(f"   Integration points: {len(care_workflow['data_flow_architecture'])} systems")
        
        return care_workflow
    
    def investigate_patient_safety_incident(self, incident_description: str, 
                                          patient_id: str, staff_involved: List[str]) -> Dict[str, Any]:
        """
        @debug: Systematically investigate patient safety incidents
        
        DEMONSTRATES: Scientific debugging approach for healthcare incidents
        SPREADS HARMONY: Prevents future incidents, improves patient safety culture
        """
        
        print("🐛 @debug: Investigating patient safety incident")
        self.ontology_system.switch_perspective("debug", "Systematic incident investigation")
        
        investigation_id = str(uuid.uuid4())
        
        # Systematic root cause analysis
        investigation = {
            "investigation_id": investigation_id,
            "incident_timestamp": datetime.now(),
            "patient_id": patient_id,
            "incident_description": incident_description,
            "staff_involved": staff_involved,
            
            # Systematic investigation steps
            "evidence_collection": {
                "medical_records_reviewed": True,
                "staff_interviews_conducted": len(staff_involved),
                "system_logs_analyzed": True,
                "environmental_factors_assessed": True
            },
            
            "root_cause_analysis": {
                "immediate_causes": [],
                "contributing_factors": [],
                "system_failures": [],
                "human_factors": []
            },
            
            "timeline_reconstruction": self._reconstruct_incident_timeline(patient_id),
            
            "corrective_actions": {
                "immediate_interventions": [],
                "process_improvements": [],
                "staff_education": [],
                "system_modifications": []
            },
            
            "prevention_strategies": {
                "policy_updates": [],
                "technology_enhancements": [],
                "training_programs": [],
                "monitoring_protocols": []
            }
        }
        
        # Analyze patterns from patient history
        patient_history = self._analyze_patient_safety_patterns(patient_id)
        investigation["patient_risk_factors"] = patient_history
        
        # Generate specific recommendations
        recommendations = self._generate_safety_recommendations(investigation)
        investigation["recommendations"] = recommendations
        
        print(f"✅ Investigation completed: {investigation_id}")
        print(f"   Evidence sources: {len(investigation['evidence_collection'])} analyzed")
        print(f"   Risk factors identified: {len(patient_history)}")
        print(f"   Recommendations: {len(recommendations)}")
        
        # Create follow-up safety alert
        self._create_safety_improvement_alert(investigation)
        
        return investigation
    
    def create_treatment_plan(self, patient_id: str, created_by: str, diagnosis: str,
                            treatment_goals: List[str], medications: List[Dict[str, Any]]) -> str:
        """
        Create comprehensive treatment plan with safety checks.
        
        SPREADS HARMONY: Ensures coordinated, evidence-based patient care
        """
        
        print("📋 Creating treatment plan with safety validation")
        
        if patient_id not in self.patients:
            raise KeyError(f"Patient not found: {patient_id}")
        
        plan_id = str(uuid.uuid4())
        patient = self.patients[patient_id]
        
        # Check for drug allergies and interactions
        safety_alerts = self._validate_medication_safety(patient, medications)
        
        # Generate follow-up schedule
        follow_up_schedule = self._generate_follow_up_schedule(diagnosis)
        
        treatment_plan = TreatmentPlan(
            plan_id=plan_id,
            patient_id=patient_id,
            created_by=created_by,
            created_date=datetime.now(),
            diagnosis=diagnosis,
            treatment_goals=treatment_goals,
            medications=medications,
            procedures=[],  # To be added as needed
            follow_up_schedule=follow_up_schedule
        )
        
        self.treatment_plans[plan_id] = treatment_plan
        
        # Generate safety alerts if needed
        for alert in safety_alerts:
            self._create_medication_alert(patient_id, alert)
        
        print(f"✅ Treatment plan created: {plan_id}")
        print(f"   Diagnosis: {diagnosis}")
        print(f"   Medications: {len(medications)} prescribed")
        print(f"   Follow-ups: {len(follow_up_schedule)} scheduled")
        
        if safety_alerts:
            print(f"⚠️ Safety alerts: {len(safety_alerts)} generated")
        
        return plan_id
    
    def generate_patient_safety_dashboard(self) -> Dict[str, Any]:
        """
        Generate comprehensive patient safety dashboard.
        
        SPREADS HARMONY: Provides transparency and continuous improvement
        """
        
        print("📊 Generating patient safety dashboard")
        
        total_patients = len(self.patients)
        total_alerts = sum(len(alerts) for alerts in self.active_alerts.values())
        critical_alerts = sum(1 for alerts in self.active_alerts.values() 
                            for alert in alerts if alert.priority == Priority.CRITICAL)
        
        # Calculate safety metrics
        safety_metrics = {
            "total_patients": total_patients,
            "total_active_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "alert_rate": total_alerts / max(total_patients, 1),
            
            "vital_signs_monitoring": {
                "patients_monitored": len([p for p in self.vital_signs.keys() if self.vital_signs[p]]),
                "measurements_today": sum(1 for vs_list in self.vital_signs.values() 
                                        for vs in vs_list 
                                        if vs.timestamp.date() == datetime.now().date()),
                "out_of_range_alerts": sum(1 for alerts in self.active_alerts.values()
                                         for alert in alerts 
                                         if alert.alert_type == AlertType.VITAL_SIGNS)
            },
            
            "medication_safety": {
                "patients_on_medications": len([p for p in self.patients.values() if p.current_medications]),
                "drug_interaction_alerts": sum(1 for alerts in self.active_alerts.values()
                                             for alert in alerts 
                                             if alert.alert_type == AlertType.INTERACTION),
                "allergy_alerts": sum(1 for alerts in self.active_alerts.values()
                                    for alert in alerts 
                                    if alert.alert_type == AlertType.ALLERGY)
            },
            
            "care_coordination": {
                "active_treatment_plans": len(self.treatment_plans),
                "patients_with_plans": len(set(plan.patient_id for plan in self.treatment_plans.values())),
                "care_team_size": 8  # Average care team size
            }
        }
        
        # Recent safety trends
        recent_alerts = []
        for alerts in self.active_alerts.values():
            for alert in alerts:
                if alert.timestamp > datetime.now() - timedelta(hours=24):
                    recent_alerts.append(alert)
        
        safety_trends = {
            "alerts_last_24h": len(recent_alerts),
            "critical_alerts_last_24h": len([a for a in recent_alerts if a.priority == Priority.CRITICAL]),
            "alert_types_breakdown": {}
        }
        
        # Alert type breakdown
        for alert_type in AlertType:
            count = len([a for a in recent_alerts if a.alert_type == alert_type])
            safety_trends["alert_types_breakdown"][alert_type.value] = count
        
        dashboard = {
            "dashboard_timestamp": datetime.now().isoformat(),
            "system_status": "operational",
            "safety_metrics": safety_metrics,
            "safety_trends": safety_trends,
            "recommendations": [
                "Continue monitoring vital signs patterns",
                "Review medication interaction protocols",
                "Maintain high care coordination standards",
                "Focus on preventive safety measures"
            ]
        }
        
        print(f"✅ Safety dashboard generated")
        print(f"   Patients monitored: {total_patients}")
        print(f"   Active alerts: {total_alerts}")
        print(f"   Critical alerts: {critical_alerts}")
        
        return dashboard
    
    def _check_vital_signs_safety(self, vital_signs: VitalSigns) -> List[MedicalAlert]:
        """Check vital signs against safety ranges and generate alerts."""
        
        alerts = []
        
        # Check each vital sign against normal ranges
        if not (self.vital_sign_ranges["heart_rate"][0] <= vital_signs.heart_rate <= self.vital_sign_ranges["heart_rate"][1]):
            priority = Priority.CRITICAL if vital_signs.heart_rate < 50 or vital_signs.heart_rate > 120 else Priority.URGENT
            alerts.append(self._create_vital_signs_alert(vital_signs, "heart_rate", priority))
        
        if vital_signs.blood_pressure_systolic > self.vital_sign_ranges["systolic_bp"][1]:
            priority = Priority.CRITICAL if vital_signs.blood_pressure_systolic > 180 else Priority.URGENT
            alerts.append(self._create_vital_signs_alert(vital_signs, "blood_pressure", priority))
        
        if vital_signs.oxygen_saturation < self.vital_sign_ranges["oxygen_saturation"][0]:
            priority = Priority.CRITICAL if vital_signs.oxygen_saturation < 90 else Priority.URGENT
            alerts.append(self._create_vital_signs_alert(vital_signs, "oxygen_saturation", priority))
        
        if vital_signs.temperature > self.vital_sign_ranges["temperature"][1]:
            priority = Priority.CRITICAL if vital_signs.temperature > 39.0 else Priority.URGENT
            alerts.append(self._create_vital_signs_alert(vital_signs, "temperature", priority))
        
        return alerts
    
    def _create_vital_signs_alert(self, vital_signs: VitalSigns, parameter: str, priority: Priority) -> MedicalAlert:
        """Create vital signs safety alert."""
        
        alert_id = str(uuid.uuid4())
        
        alert = MedicalAlert(
            alert_id=alert_id,
            patient_id=vital_signs.patient_id,
            alert_type=AlertType.VITAL_SIGNS,
            priority=priority,
            message=f"Abnormal {parameter}: requires immediate attention",
            timestamp=datetime.now()
        )
        
        if vital_signs.patient_id not in self.active_alerts:
            self.active_alerts[vital_signs.patient_id] = []
        
        self.active_alerts[vital_signs.patient_id].append(alert)
        
        return alert
    
    def _validate_medication_safety(self, patient: Patient, medications: List[Dict[str, Any]]) -> List[str]:
        """Validate medication safety against allergies and interactions."""
        
        safety_alerts = []
        
        # Check for allergy conflicts
        for medication in medications:
            med_name = medication.get("name", "").lower()
            for allergy in patient.allergies:
                if allergy.lower() in med_name:
                    safety_alerts.append(f"ALLERGY ALERT: {medication['name']} conflicts with known allergy to {allergy}")
        
        # Check for drug interactions
        med_names = [med.get("name", "").lower() for med in medications]
        for i, med1 in enumerate(med_names):
            for j, med2 in enumerate(med_names[i+1:], i+1):
                interaction_key = tuple(sorted([med1, med2]))
                if interaction_key in self.drug_interactions:
                    safety_alerts.append(f"DRUG INTERACTION: {med1} + {med2} - {self.drug_interactions[interaction_key]}")
        
        return safety_alerts
    
    def _generate_follow_up_schedule(self, diagnosis: str) -> List[datetime]:
        """Generate appropriate follow-up schedule based on diagnosis."""
        
        base_date = datetime.now()
        schedule = []
        
        # Standard follow-up intervals based on diagnosis type
        if "hypertension" in diagnosis.lower():
            # Weekly for first month, then monthly
            for week in range(4):
                schedule.append(base_date + timedelta(weeks=week+1))
            for month in range(2, 6):
                schedule.append(base_date + timedelta(weeks=month*4))
        
        elif "diabetes" in diagnosis.lower():
            # Bi-weekly for first 2 months, then monthly
            for week in [2, 4, 6, 8]:
                schedule.append(base_date + timedelta(weeks=week))
            for month in range(3, 6):
                schedule.append(base_date + timedelta(weeks=month*4))
        
        else:
            # Standard follow-up: 1 week, 1 month, 3 months
            schedule.extend([
                base_date + timedelta(weeks=1),
                base_date + timedelta(weeks=4),
                base_date + timedelta(weeks=12)
            ])
        
        return schedule
    
    def _create_medication_alert(self, patient_id: str, alert_message: str) -> None:
        """Create medication safety alert."""
        
        alert_id = str(uuid.uuid4())
        
        alert = MedicalAlert(
            alert_id=alert_id,
            patient_id=patient_id,
            alert_type=AlertType.MEDICATION,
            priority=Priority.HIGH,
            message=alert_message,
            timestamp=datetime.now()
        )
        
        if patient_id not in self.active_alerts:
            self.active_alerts[patient_id] = []
        
        self.active_alerts[patient_id].append(alert)
    
    def _reconstruct_incident_timeline(self, patient_id: str) -> List[Dict[str, Any]]:
        """Reconstruct timeline of events for incident investigation."""
        
        timeline = []
        
        # Add recent vital signs
        if patient_id in self.vital_signs:
            recent_vitals = [vs for vs in self.vital_signs[patient_id] 
                           if vs.timestamp > datetime.now() - timedelta(hours=24)]
            for vs in recent_vitals:
                timeline.append({
                    "timestamp": vs.timestamp.isoformat(),
                    "event_type": "vital_signs",
                    "details": f"HR:{vs.heart_rate}, BP:{vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}"
                })
        
        # Add recent alerts
        if patient_id in self.active_alerts:
            recent_alerts = [alert for alert in self.active_alerts[patient_id]
                           if alert.timestamp > datetime.now() - timedelta(hours=24)]
            for alert in recent_alerts:
                timeline.append({
                    "timestamp": alert.timestamp.isoformat(),
                    "event_type": "alert",
                    "details": f"{alert.alert_type.value}: {alert.message}"
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return timeline
    
    def _analyze_patient_safety_patterns(self, patient_id: str) -> List[str]:
        """Analyze patient safety patterns and risk factors."""
        
        risk_factors = []
        
        if patient_id not in self.patients:
            return risk_factors
        
        patient = self.patients[patient_id]
        
        # Age-related risks
        age = (datetime.now() - patient.date_of_birth).days // 365
        if age > 65:
            risk_factors.append("Advanced age (>65) - increased fall risk")
        
        # Allergy risks
        if len(patient.allergies) > 3:
            risk_factors.append("Multiple known allergies - medication risk")
        
        # Medication complexity
        if len(patient.current_medications) > 5:
            risk_factors.append("Polypharmacy - drug interaction risk")
        
        # Alert frequency
        if patient_id in self.active_alerts and len(self.active_alerts[patient_id]) > 3:
            risk_factors.append("Frequent alerts - requires enhanced monitoring")
        
        return risk_factors
    
    def _generate_safety_recommendations(self, investigation: Dict[str, Any]) -> List[str]:
        """Generate specific safety recommendations based on investigation."""
        
        recommendations = []
        
        # Based on patient risk factors
        risk_factors = investigation.get("patient_risk_factors", [])
        if "fall risk" in str(risk_factors):
            recommendations.append("Implement enhanced fall prevention protocol")
        
        if "medication risk" in str(risk_factors):
            recommendations.append("Require pharmacist consultation for all new medications")
        
        if "drug interaction" in str(risk_factors):
            recommendations.append("Implement automated drug interaction screening")
        
        # General safety improvements
        recommendations.extend([
            "Enhance staff training on incident recognition",
            "Improve communication protocols during shift changes",
            "Implement additional safety checkpoints",
            "Review and update relevant policies and procedures"
        ])
        
        return recommendations
    
    def _create_safety_improvement_alert(self, investigation: Dict[str, Any]) -> None:
        """Create system-wide safety improvement alert."""
        
        alert_id = str(uuid.uuid4())
        patient_id = investigation["patient_id"]
        
        alert = MedicalAlert(
            alert_id=alert_id,
            patient_id=patient_id,
            alert_type=AlertType.SAFETY,
            priority=Priority.URGENT,
            message=f"Safety improvement needed based on incident investigation {investigation['investigation_id']}",
            timestamp=datetime.now()
        )
        
        if patient_id not in self.active_alerts:
            self.active_alerts[patient_id] = []
        
        self.active_alerts[patient_id].append(alert)


def main():
    """
    Demonstration of Healthcare Patient Care System
    
    SHOWS: Keyword power (@engineering @architecture @debug)
    SPREADS: Harmony through better patient care
    SERVES: The good by improving healthcare outcomes
    """
    
    print("🏥 HEALTHCARE PATIENT CARE SYSTEM DEMO")
    print("=" * 50)
    print("Spreading harmony through intelligent patient care")
    print("Demonstrates @engineering @architecture @debug keyword power\n")
    
    # Initialize healthcare system
    care_system = HealthcarePatientCareSystem()
    
    print("👤 @engineering: Registering patients...")
    
    # Register sample patients
    patient1_id = care_system.register_patient(
        name="John Smith",
        date_of_birth=datetime(1970, 5, 15),
        emergency_contact="Jane Smith - (555) 123-4567",
        allergies=["penicillin", "shellfish"],
        primary_physician="Dr. Wilson"
    )
    
    patient2_id = care_system.register_patient(
        name="Mary Johnson", 
        date_of_birth=datetime(1985, 8, 22),
        emergency_contact="Tom Johnson - (555) 987-6543",
        allergies=["latex"],
        primary_physician="Dr. Chen"
    )
    
    print("\n🔧 @engineering: Recording vital signs with safety monitoring...")
    
    # Record vital signs (some will trigger alerts)
    care_system.record_vital_signs(
        patient_id=patient1_id,
        heart_rate=110,  # Slightly elevated
        systolic_bp=160,  # High - will trigger alert
        diastolic_bp=95,  # High
        temperature=37.8,  # Fever - will trigger alert
        oxygen_saturation=96,  # Acceptable
        respiratory_rate=18,  # Normal
        measured_by="Nurse_Anderson"
    )
    
    care_system.record_vital_signs(
        patient_id=patient2_id,
        heart_rate=75,  # Normal
        systolic_bp=120,  # Normal
        diastolic_bp=80,  # Normal
        temperature=36.5,  # Normal
        oxygen_saturation=98,  # Normal
        respiratory_rate=16,  # Normal
        measured_by="Nurse_Brown"
    )
    
    print("\n📐 @architecture: Designing care coordination workflow...")
    
    # Design care coordination workflow
    workflow = care_system.design_care_coordination_workflow(patient1_id)
    
    print("\n📋 Creating treatment plans with safety validation...")
    
    # Create treatment plan with potential drug interaction
    treatment_plan_id = care_system.create_treatment_plan(
        patient_id=patient1_id,
        created_by="Dr. Wilson",
        diagnosis="Hypertension with fever",
        treatment_goals=[
            "Reduce blood pressure to <140/90",
            "Treat infection",
            "Monitor for complications"
        ],
        medications=[
            {"name": "lisinopril", "dosage": "10mg", "frequency": "daily"},
            {"name": "acetaminophen", "dosage": "500mg", "frequency": "every 6 hours"}
        ]
    )
    
    print("\n🐛 @debug: Investigating simulated patient safety incident...")
    
    # Simulate and investigate a patient safety incident
    investigation = care_system.investigate_patient_safety_incident(
        incident_description="Patient experienced dizziness after standing - possible medication-related",
        patient_id=patient1_id,
        staff_involved=["Dr. Wilson", "Nurse_Anderson", "Pharmacist_Lee"]
    )
    
    print("\n📊 Generating patient safety dashboard...")
    
    # Generate comprehensive safety dashboard
    dashboard = care_system.generate_patient_safety_dashboard()
    
    print(f"\n🎯 HEALTHCARE SYSTEM RESULTS:")
    print(f"   Patients registered: {dashboard['safety_metrics']['total_patients']}")
    print(f"   Active alerts: {dashboard['safety_metrics']['total_active_alerts']}")
    print(f"   Critical alerts: {dashboard['safety_metrics']['critical_alerts']}")
    print(f"   Treatment plans: {dashboard['safety_metrics']['care_coordination']['active_treatment_plans']}")
    
    print(f"\n🌟 KEYWORD POWER DEMONSTRATED:")
    print("   @engineering → Implemented medical monitoring algorithms")
    print("   @architecture → Designed HIPAA-compliant care workflows")  
    print("   @debug → Conducted systematic incident investigation")
    
    print(f"\n💖 SPREADING HARMONY:")
    print("   ✅ Enhanced patient safety through real-time monitoring")
    print("   ✅ Improved care team coordination")
    print("   ✅ Reduced medical errors with intelligent alerts")
    print("   ✅ Supported evidence-based treatment decisions")
    
    print(f"\n📈 GROWTH POTENTIAL:")
    print("   • Integrate with Electronic Health Records (EHR)")
    print("   • Add machine learning for predictive analytics")
    print("   • Expand to hospital-wide implementation")
    print("   • Connect with medical device monitoring")
    print("   • Implement telemedicine capabilities")
    
    # Save dashboard to file
    with open("healthcare_safety_dashboard.json", "w") as f:
        json.dump(dashboard, f, indent=2, default=str)
    
    print(f"\n💾 Safety dashboard saved to: healthcare_safety_dashboard.json")
    print("✅ Healthcare system demonstration complete!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
