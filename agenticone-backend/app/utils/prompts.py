"""
Prompt templates for AI agents
"""
from typing import Dict, List, Any

class PromptTemplates:
    """Prompt templates for different analysis types"""
    
    # General analysis prompts
    GENERAL_ANALYSIS = """
    Analyze the following document and provide a comprehensive assessment:
    
    Document: {document_content}
    
    Please provide:
    1. Key findings and observations
    2. Technical details and specifications
    3. Potential issues or concerns
    4. Recommendations for improvement
    5. Confidence level for your analysis
    """
    
    # Discipline Head prompts
    DISCIPLINE_HEAD_OVERVIEW = """
    As a Discipline Head, analyze this document for overall project coordination:
    
    Document: {document_content}
    
    Focus on:
    1. Project scope and objectives
    2. Risk assessment and mitigation
    3. Compliance with standards and regulations
    4. Key decision points and recommendations
    5. Resource requirements and timeline
    """
    
    # Methods Specialist prompts
    METHODS_ANALYSIS = """
    As a Methods Specialist, analyze this document for engineering methods and procedures:
    
    Document: {document_content}
    
    Focus on:
    1. Engineering methods and techniques used
    2. Procedures and workflows
    3. Best practices and standards
    4. Process optimization opportunities
    5. Quality control measures
    """
    
    # Corrosion Engineer prompts
    CORROSION_ANALYSIS = """
    As a Corrosion Engineer, analyze this document for corrosion-related issues:
    
    Document: {document_content}
    
    Focus on:
    1. Corrosion mechanisms and types
    2. Material selection and properties
    3. Environmental factors affecting corrosion
    4. Prevention and mitigation strategies
    5. Inspection and monitoring methods
    """
    
    # Subsea Engineer prompts
    SUBSEA_ANALYSIS = """
    As a Subsea Engineer, analyze this document for subsea systems and operations:
    
    Document: {document_content}
    
    Focus on:
    1. Subsea systems and components
    2. Riser and flowline systems
    3. Marine environment considerations
    4. Installation and operations
    5. Safety and reliability aspects
    """
    
    # Image analysis prompts
    IMAGE_ANALYSIS = """
    Analyze this image and provide detailed technical assessment:
    
    Image: {image_description}
    
    Please identify:
    1. Equipment and components visible
    2. Technical specifications and measurements
    3. Condition assessment
    4. Potential issues or concerns
    5. Recommendations for action
    """
    
    # Report generation prompts
    REPORT_SUMMARY = """
    Generate an executive summary for the following analysis results:
    
    Analysis Results: {analysis_results}
    
    Include:
    1. Key findings overview
    2. Critical issues identified
    3. Priority recommendations
    4. Overall confidence assessment
    """
    
    # Risk assessment prompts
    RISK_ASSESSMENT = """
    Conduct a comprehensive risk assessment based on the following information:
    
    Document: {document_content}
    
    Evaluate:
    1. Safety risks and hazards
    2. Environmental risks
    3. Operational risks
    4. Financial risks
    5. Regulatory compliance risks
    6. Risk mitigation strategies
    """
    
    # Compliance review prompts
    COMPLIANCE_REVIEW = """
    Review this document for compliance with industry standards and regulations:
    
    Document: {document_content}
    
    Check for:
    1. Industry standards compliance (API, ASME, ASTM, ISO)
    2. Regulatory requirements
    3. Safety standards adherence
    4. Environmental regulations
    5. Quality management systems
    """
    
    # Technical specification prompts
    TECHNICAL_SPECS = """
    Extract and analyze technical specifications from this document:
    
    Document: {document_content}
    
    Identify:
    1. Equipment specifications
    2. Material properties
    3. Performance requirements
    4. Design parameters
    5. Testing and validation requirements
    """
    
    # Quality assurance prompts
    QUALITY_ASSURANCE = """
    Assess the quality assurance aspects of this document:
    
    Document: {document_content}
    
    Evaluate:
    1. Quality control measures
    2. Testing and inspection procedures
    3. Documentation standards
    4. Process validation
    5. Continuous improvement opportunities
    """
    
    @classmethod
    def get_prompt(cls, prompt_type: str, **kwargs) -> str:
        """Get formatted prompt for specific analysis type"""
        prompts = {
            "general_analysis": cls.GENERAL_ANALYSIS,
            "discipline_head": cls.DISCIPLINE_HEAD_OVERVIEW,
            "methods_analysis": cls.METHODS_ANALYSIS,
            "corrosion_analysis": cls.CORROSION_ANALYSIS,
            "subsea_analysis": cls.SUBSEA_ANALYSIS,
            "image_analysis": cls.IMAGE_ANALYSIS,
            "report_summary": cls.REPORT_SUMMARY,
            "risk_assessment": cls.RISK_ASSESSMENT,
            "compliance_review": cls.COMPLIANCE_REVIEW,
            "technical_specs": cls.TECHNICAL_SPECS,
            "quality_assurance": cls.QUALITY_ASSURANCE
        }
        
        prompt_template = prompts.get(prompt_type, cls.GENERAL_ANALYSIS)
        return prompt_template.format(**kwargs)
    
    @classmethod
    def get_agent_prompt(cls, agent_type: str, document_content: str, analysis_type: str = "general") -> str:
        """Get agent-specific prompt"""
        agent_prompts = {
            "discipline_head": cls.DISCIPLINE_HEAD_OVERVIEW,
            "methods_specialist": cls.METHODS_ANALYSIS,
            "corrosion_engineer": cls.CORROSION_ANALYSIS,
            "subsea_engineer": cls.SUBSEA_ANALYSIS
        }
        
        prompt_template = agent_prompts.get(agent_type, cls.GENERAL_ANALYSIS)
        return prompt_template.format(document_content=document_content)
    
    @classmethod
    def get_image_prompt(cls, image_description: str, analysis_type: str = "general") -> str:
        """Get image analysis prompt"""
        return cls.IMAGE_ANALYSIS.format(image_description=image_description)
    
    @classmethod
    def get_report_prompt(cls, analysis_results: str) -> str:
        """Get report generation prompt"""
        return cls.REPORT_SUMMARY.format(analysis_results=analysis_results)
