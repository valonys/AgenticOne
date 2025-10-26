"""
Corrosion Engineer Agent - Expert in corrosion analysis and prevention
"""
from typing import Dict, List, Any
from app.agents.base_agent import BaseAgent
from app.models.schemas import AnalysisResult

class CorrosionEngineer(BaseAgent):
    """Corrosion Engineer Agent for corrosion analysis and prevention"""
    
    def __init__(self, rag_service, vision_service):
        super().__init__(rag_service, vision_service)
        self.capabilities = [
            "corrosion_analysis",
            "material_selection",
            "prevention_strategies",
            "inspection_methods",
            "cathodic_protection"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    async def analyze(self, document_id: str, analysis_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform corrosion analysis"""
        try:
            await self.update_status("analyzing")
            
            # Preprocess document
            preprocessed = await self.preprocess_document(document_id)
            context = preprocessed["context"]
            relevant_docs = preprocessed["relevant_documents"]
            image_analysis = preprocessed["image_analysis"]
            
            # Perform corrosion analysis
            results = []
            
            # Corrosion mechanism analysis
            mechanism_analysis = await self._analyze_corrosion_mechanisms(context, relevant_docs)
            results.append(mechanism_analysis)
            
            # Material analysis
            material_analysis = await self._analyze_materials(context, relevant_docs)
            results.append(material_analysis)
            
            # Environmental factors
            environmental_analysis = await self._analyze_environmental_factors(context, relevant_docs)
            results.append(environmental_analysis)
            
            # Prevention strategies
            prevention_analysis = await self._analyze_prevention_strategies(context, relevant_docs)
            results.append(prevention_analysis)
            
            # Inspection and monitoring
            inspection_analysis = await self._analyze_inspection_methods(context, relevant_docs)
            results.append(inspection_analysis)
            
            # Postprocess results
            processed_results = await self.postprocess_results(results)
            
            # Save analysis
            analysis_id = await self.save_analysis({
                "document_id": document_id,
                "agent_type": "corrosion_engineer",
                "analysis_type": analysis_type,
                "results": [result.dict() for result in results],
                "confidence": processed_results["confidence"],
                "recommendations": processed_results["recommendations"]
            })
            
            await self.update_status("completed")
            
            return {
                "analysis_id": analysis_id,
                "results": [result.dict() for result in results],
                "confidence": processed_results["confidence"],
                "recommendations": processed_results["recommendations"]
            }
            
        except Exception as e:
            await self.update_status("error", {"error": str(e)})
            raise
    
    async def _analyze_corrosion_mechanisms(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze corrosion mechanisms and types"""
        findings = []
        confidence = 0.8
        
        content_lower = context["content"].lower()
        
        # Corrosion mechanism indicators
        corrosion_keywords = ["corrosion", "rust", "oxidation", "pitting", "crevice", "galvanic"]
        corrosion_count = sum(1 for keyword in corrosion_keywords if keyword in content_lower)
        
        if corrosion_count > 0:
            findings.append(f"Identified {corrosion_count} corrosion-related terms")
            confidence += 0.1
        
        # Specific corrosion types
        corrosion_types = ["pitting", "crevice", "galvanic", "stress", "intergranular", "uniform"]
        found_types = [corr_type for corr_type in corrosion_types if corr_type in content_lower]
        
        if found_types:
            findings.append(f"Corrosion types identified: {', '.join(found_types)}")
            confidence += 0.15
        
        # Electrochemical processes
        if "electrochemical" in content_lower or "anode" in content_lower or "cathode" in content_lower:
            findings.append("Electrochemical processes identified")
            confidence += 0.1
        
        # Corrosion rate indicators
        if "rate" in content_lower and ("corrosion" in content_lower or "mpy" in content_lower):
            findings.append("Corrosion rate considerations present")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Corrosion Mechanisms",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"corrosion_indicators": corrosion_count, "corrosion_types": found_types}
        )
    
    async def _analyze_materials(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze materials and their corrosion resistance"""
        findings = []
        confidence = 0.75
        
        content_lower = context["content"].lower()
        
        # Material indicators
        material_keywords = ["steel", "stainless", "aluminum", "copper", "titanium", "alloy"]
        material_count = sum(1 for keyword in material_keywords if keyword in content_lower)
        
        if material_count > 0:
            findings.append(f"Identified {material_count} material-related terms")
            confidence += 0.1
        
        # Specific materials
        materials = ["carbon steel", "stainless steel", "duplex", "super duplex", "inconel", "hastelloy"]
        found_materials = [mat for mat in materials if mat in content_lower]
        
        if found_materials:
            findings.append(f"Materials identified: {', '.join(found_materials)}")
            confidence += 0.15
        
        # Material properties
        if "hardness" in content_lower or "tensile" in content_lower or "yield" in content_lower:
            findings.append("Material properties discussed")
            confidence += 0.1
        
        # Corrosion resistance
        if "resistance" in content_lower and ("corrosion" in content_lower or "chemical" in content_lower):
            findings.append("Corrosion resistance considerations present")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Material Analysis",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"material_indicators": material_count, "materials": found_materials}
        )
    
    async def _analyze_environmental_factors(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze environmental factors affecting corrosion"""
        findings = []
        confidence = 0.8
        
        content_lower = context["content"].lower()
        
        # Environmental indicators
        env_keywords = ["temperature", "pressure", "ph", "oxygen", "chloride", "sulfide", "co2"]
        env_count = sum(1 for keyword in env_keywords if keyword in content_lower)
        
        if env_count > 0:
            findings.append(f"Identified {env_count} environmental factors")
            confidence += 0.1
        
        # Specific environmental conditions
        conditions = ["sour", "sweet", "acidic", "alkaline", "saline", "marine"]
        found_conditions = [cond for cond in conditions if cond in content_lower]
        
        if found_conditions:
            findings.append(f"Environmental conditions: {', '.join(found_conditions)}")
            confidence += 0.15
        
        # Temperature effects
        if "temperature" in content_lower and ("high" in content_lower or "low" in content_lower):
            findings.append("Temperature effects identified")
            confidence += 0.1
        
        # Chemical composition
        if "composition" in content_lower or "concentration" in content_lower:
            findings.append("Chemical composition considerations present")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Environmental Factors",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"environmental_indicators": env_count, "conditions": found_conditions}
        )
    
    async def _analyze_prevention_strategies(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze corrosion prevention strategies"""
        findings = []
        confidence = 0.8
        
        content_lower = context["content"].lower()
        
        # Prevention strategy indicators
        prevention_keywords = ["coating", "paint", "cathodic", "inhibitor", "protection", "prevention"]
        prevention_count = sum(1 for keyword in prevention_keywords if keyword in content_lower)
        
        if prevention_count > 0:
            findings.append(f"Identified {prevention_count} prevention strategies")
            confidence += 0.1
        
        # Specific prevention methods
        prevention_methods = ["cathodic protection", "coating", "inhibitor", "anodic protection", "design"]
        found_methods = [method for method in prevention_methods if method in content_lower]
        
        if found_methods:
            findings.append(f"Prevention methods: {', '.join(found_methods)}")
            confidence += 0.15
        
        # Coating systems
        if "coating" in content_lower or "paint" in content_lower:
            findings.append("Coating systems identified")
            confidence += 0.1
        
        # Cathodic protection
        if "cathodic" in content_lower and "protection" in content_lower:
            findings.append("Cathodic protection system identified")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Prevention Strategies",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"prevention_indicators": prevention_count, "methods": found_methods}
        )
    
    async def _analyze_inspection_methods(self, context: Dict[str, Any], relevant_docs: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze inspection and monitoring methods"""
        findings = []
        confidence = 0.75
        
        content_lower = context["content"].lower()
        
        # Inspection indicators
        inspection_keywords = ["inspection", "monitoring", "ndt", "ultrasonic", "radiographic", "magnetic"]
        inspection_count = sum(1 for keyword in inspection_keywords if keyword in content_lower)
        
        if inspection_count > 0:
            findings.append(f"Identified {inspection_count} inspection-related terms")
            confidence += 0.1
        
        # NDT methods
        ndt_methods = ["ultrasonic", "radiographic", "magnetic particle", "dye penetrant", "eddy current"]
        found_ndt = [method for method in ndt_methods if method in content_lower]
        
        if found_ndt:
            findings.append(f"NDT methods: {', '.join(found_ndt)}")
            confidence += 0.15
        
        # Monitoring systems
        if "monitoring" in content_lower and ("system" in content_lower or "equipment" in content_lower):
            findings.append("Monitoring systems identified")
            confidence += 0.1
        
        # Inspection frequency
        if "frequency" in content_lower and ("inspection" in content_lower or "monitoring" in content_lower):
            findings.append("Inspection frequency considerations present")
            confidence += 0.1
        
        return self.create_analysis_result(
            category="Inspection Methods",
            findings=findings,
            confidence=min(confidence, 1.0),
            details={"inspection_indicators": inspection_count, "ndt_methods": found_ndt}
        )
