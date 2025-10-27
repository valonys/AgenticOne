"""
Persistent Storage Service for Agent Conversations
Handles conversation persistence across sessions using localStorage and backend storage
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class ConversationStorage:
    """Handles persistent storage of agent conversations"""
    
    def __init__(self):
        self.storage_key_prefix = "agenticone_conversation_"
        self.user_key_prefix = "agenticone_user_"
    
    def save_conversation_to_local(
        self, 
        user_email: str, 
        agent_role: str, 
        messages: List[Dict[str, Any]]
    ) -> None:
        """Save conversation to localStorage"""
        try:
            storage_key = f"{self.storage_key_prefix}{user_email}_{agent_role}"
            conversation_data = {
                "user_email": user_email,
                "agent_role": agent_role,
                "messages": messages,
                "last_updated": datetime.now().isoformat(),
                "message_count": len(messages)
            }
            
            # Store in localStorage (this will be called from frontend)
            if typeof window !== 'undefined' and window.localStorage:
                window.localStorage.setItem(storage_key, JSON.stringify(conversation_data))
                
        except Exception as e:
            print(f"Error saving conversation to local storage: {e}")
    
    def load_conversation_from_local(
        self, 
        user_email: str, 
        agent_role: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Load conversation from localStorage"""
        try:
            storage_key = f"{self.storage_key_prefix}{user_email}_{agent_role}"
            
            if typeof window !== 'undefined' and window.localStorage:
                stored_data = window.localStorage.getItem(storage_key)
                if stored_data:
                    conversation_data = JSON.parse(stored_data)
                    return conversation_data.get("messages", [])
                    
        except Exception as e:
            print(f"Error loading conversation from local storage: {e}")
        
        return None
    
    def save_user_session(
        self, 
        user_email: str, 
        user_name: str, 
        selected_agent: str,
        rag_sources: Dict[str, Any],
        uploaded_files: List[Dict[str, Any]]
    ) -> None:
        """Save user session data"""
        try:
            session_data = {
                "user_email": user_email,
                "user_name": user_name,
                "selected_agent": selected_agent,
                "rag_sources": rag_sources,
                "uploaded_files": uploaded_files,
                "last_session": datetime.now().isoformat()
            }
            
            if typeof window !== 'undefined' and window.localStorage:
                window.localStorage.setItem(
                    f"{self.user_key_prefix}{user_email}", 
                    JSON.stringify(session_data)
                )
                
        except Exception as e:
            print(f"Error saving user session: {e}")
    
    def load_user_session(self, user_email: str) -> Optional[Dict[str, Any]]:
        """Load user session data"""
        try:
            if typeof window !== 'undefined' and window.localStorage:
                stored_data = window.localStorage.getItem(f"{self.user_key_prefix}{user_email}")
                if stored_data:
                    return JSON.parse(stored_data)
                    
        except Exception as e:
            print(f"Error loading user session: {e}")
        
        return None
    
    def clear_user_data(self, user_email: str) -> None:
        """Clear all user data from localStorage"""
        try:
            if typeof window !== 'undefined' and window.localStorage:
                # Clear all conversation keys for this user
                keys_to_remove = []
                for i in range(window.localStorage.length):
                    key = window.localStorage.key(i)
                    if key and (key.startswith(f"{self.storage_key_prefix}{user_email}_") or 
                               key === f"{self.user_key_prefix}{user_email}"):
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    window.localStorage.removeItem(key)
                    
        except Exception as e:
            print(f"Error clearing user data: {e}")
    
    def get_all_user_conversations(self, user_email: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all conversations for a user"""
        conversations = {}
        
        try:
            if typeof window !== 'undefined' and window.localStorage:
                for i in range(window.localStorage.length):
                    key = window.localStorage.key(i)
                    if key and key.startswith(f"{self.storage_key_prefix}{user_email}_"):
                        agent_role = key.split('_')[-1]  # Extract agent role
                        stored_data = window.localStorage.getItem(key)
                        if stored_data:
                            conversation_data = JSON.parse(stored_data)
                            conversations[agent_role] = conversation_data.get("messages", [])
                            
        except Exception as e:
            print(f"Error getting all user conversations: {e}")
        
        return conversations

# Global instance
conversation_storage = ConversationStorage()
