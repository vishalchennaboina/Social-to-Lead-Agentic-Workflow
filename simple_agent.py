import json
import re
from typing import Dict, List

# Load knowledge base
def load_knowledge_base():
    with open('knowledge_base.json', 'r') as f:
        return json.load(f)

# Mock lead capture tool
def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Captures lead information when user shows high intent to purchase.
    Requires name, email, and creator platform.
    """
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return f"Lead captured successfully: {name}, {email}, {platform}"

# Intent classification function
def classify_intent(user_message: str) -> str:
    user_message_lower = user_message.lower()
    
    # Check for high-intent lead FIRST (highest priority)
    # Look for explicit intent to purchase/sign up regardless of other content
    high_intent_keywords = [
        'want to buy', 'sign up', 'get started', 'purchase', 'order', 'subscribe', 
        'try now', 'ready to start', 'interested in buying', 'would like to purchase',
        'i\'d like to subscribe', 'i\'m ready to purchase', 'i want to try', 
        'sounds good.*sign up', 'looks good.*try', 'yes.*sign up', 'need this',
        'ready to buy', 'going to subscribe', 'will purchase', 'decided to buy'
    ]
    
    for keyword in high_intent_keywords:
        if re.search(r'\b' + keyword.replace(' ', r'\s+') + r'\b', user_message_lower, re.IGNORECASE):
            return "high_intent_lead"
    
    # Check for casual greeting
    greeting_keywords = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good day', 'hi there']
    for keyword in greeting_keywords:
        if re.search(r'\b' + keyword + r'\b', user_message_lower, re.IGNORECASE):
            # But if it also contains purchase intent, prioritize that
            for hi_keyword in high_intent_keywords:
                if re.search(r'\b' + hi_keyword.replace(' ', r'\s+') + r'\b', user_message_lower, re.IGNORECASE):
                    return "high_intent_lead"
            return "casual_greeting"
    
    # Check for pricing/product inquiry (including policies)
    pricing_keywords = ['price', 'cost', 'pricing', 'plan', 'subscription', 'payment', 
                       'dollar', 'monthly', 'yearly', 'how much', 'what do you charge',
                       'tell me about.*pricing', 'tell me about.*plan', 'tell me about.*cost']
    policy_keywords = ['policy', 'policies', 'refund', 'support', 'terms', 'condition']
    
    # Combine pricing and policy keywords for product inquiry
    all_product_keywords = pricing_keywords + policy_keywords
    
    for keyword in all_product_keywords:
        if re.search(r'\b' + keyword + r'\b', user_message_lower, re.IGNORECASE):
            # If pricing/policy query also contains high intent, prioritize high intent
            for hi_keyword in high_intent_keywords:
                if re.search(r'\b' + hi_keyword.replace(' ', r'\s+') + r'\b', user_message_lower, re.IGNORECASE):
                    return "high_intent_lead"
            return "product_pricing_inquiry"
    
    # Default to general inquiry if no specific intent detected
    return "general_inquiry"

# Simple state management class
class SimpleAgentState:
    def __init__(self):
        self.messages: List[str] = []
        self.current_intent: str = ""
        self.collected_info: Dict[str, str] = {}
        self.conversation_history: List[str] = []

    def add_message(self, message: str):
        self.messages.append(message)

    def update_intent(self, intent: str):
        self.current_intent = intent

    def add_to_history(self, entry: str):
        self.conversation_history.append(entry)

# Simple agent implementation
class SimpleAutoStreamAgent:
    def __init__(self):
        self.state = SimpleAgentState()
        self.knowledge_base = load_knowledge_base()
    
    def process_intent(self, user_message: str) -> str:
        # First check if we were already collecting lead info
        was_collecting_lead = self.is_collecting_lead_info()
        
        # Always extract info first (this happens regardless of intent classification)
        self.extract_user_info(user_message)
        
        # Classify intent based on the message
        intent = classify_intent(user_message)
        
        # If we were already collecting lead info, continue that process
        # regardless of the current message's intent classification
        if was_collecting_lead or intent == "high_intent_lead":
            self.state.update_intent("high_intent_lead")  # Ensure we stay in lead collection mode
            return self.handle_lead_collection(user_message)
        
        # Otherwise, use the classified intent
        self.state.update_intent(intent)
        
        if intent == "casual_greeting":
            return self.handle_greeting()
        elif intent == "product_pricing_inquiry":
            return self.handle_pricing_inquiry(user_message)
        else:
            return self.handle_general_inquiry()
    
    def is_collecting_lead_info(self) -> bool:
        """Check if we're currently collecting lead information"""
        # Check if we have a high-intent lead or have already started collecting information
        # and are missing required information
        return (
            self.state.current_intent == "high_intent_lead" or 
            len(self.state.collected_info) > 0  # We've collected at least some info
        ) and not self.has_all_lead_info()
    
    def handle_greeting(self) -> str:
        return "Hello! I'm the AutoStream assistant. I help content creators learn about our automated video editing tools. How can I assist you today?"
    
    def handle_pricing_inquiry(self, user_message: str) -> str:
        # Prepare response based on knowledge base
        response_parts = []
        
        message_lower = user_message.lower()
        
        # Check if this is a pricing-related query
        is_pricing_query = any(keyword in message_lower for keyword in [
            'price', 'cost', 'pricing', 'plan', 'subscription', 'payment', 
            'dollar', 'monthly', 'yearly', 'how much', 'what do you charge',
            'tell me about.*pricing', 'tell me about.*plan', 'tell me about.*cost'
        ])
        
        # Check if this is a policy-related query
        is_policy_query = any(keyword in message_lower for keyword in [
            'policy', 'policies', 'refund', 'support', 'terms', 'condition'
        ])
        
        if is_pricing_query:
            response_parts.append("Here are our pricing plans:")
            response_parts.append("")
            response_parts.append("**Basic Plan:**")
            response_parts.append(f"- Price: {self.knowledge_base['pricing_features']['basic_plan']['price']}")
            response_parts.append(f"- Videos: {self.knowledge_base['pricing_features']['basic_plan']['videos_per_month']}")
            response_parts.append(f"- Resolution: {self.knowledge_base['pricing_features']['basic_plan']['resolution']}")
            response_parts.append("")
            response_parts.append("**Pro Plan:**")
            response_parts.append(f"- Price: {self.knowledge_base['pricing_features']['pro_plan']['price']}")
            response_parts.append(f"- Videos: {self.knowledge_base['pricing_features']['pro_plan']['videos_per_month']}")
            response_parts.append(f"- Resolution: {self.knowledge_base['pricing_features']['pro_plan']['resolution']}")
            response_parts.append(f"- Features: {', '.join(self.knowledge_base['pricing_features']['pro_plan']['features'])}")
        
        if is_policy_query:
            if response_parts:  # Add a separator if we already have pricing info
                response_parts.append("")
            response_parts.append("Our company policies:")
            response_parts.append(f"- Refund Policy: {self.knowledge_base['company_policies']['refunds']}")
            response_parts.append(f"- Support Policy: {self.knowledge_base['company_policies']['support']}")
        
        # If neither pricing nor policy matched, provide general info
        if not response_parts:
            # General product information
            response_parts.append("AutoStream is a SaaS product that provides automated video editing tools for content creators.")
            response_parts.append("We offer two plans - Basic and Pro with different features and pricing.")
            response_parts.append("Would you like to know more about our pricing or features?")
        
        return "\n".join(response_parts)
    
    def handle_high_intent_lead(self, user_message: str) -> str:
        # Check if we have all required information
        if self.has_all_lead_info():
            # Execute the mock lead capture tool
            result = mock_lead_capture(
                name=self.state.collected_info['name'],
                email=self.state.collected_info['email'],
                platform=self.state.collected_info['platform']
            )
            return "Thanks for confirming your interest! I've captured your information and our team will reach out to get you started with AutoStream."
        else:
            # Request missing information
            return self.request_missing_info()
    
    def handle_lead_collection(self, user_message: str) -> str:
        """Handle the lead collection process"""
        # Check if we have all required information
        if self.has_all_lead_info():
            # Execute the mock lead capture tool
            result = mock_lead_capture(
                name=self.state.collected_info['name'],
                email=self.state.collected_info['email'],
                platform=self.state.collected_info['platform']
            )
            # Reset the state after successful lead capture
            self.state.current_intent = ""
            self.state.collected_info.clear()  # Clear collected info after successful capture
            return "Thank you! Your information has been captured. We'll contact you shortly about getting started with AutoStream."
        else:
            # Request missing information
            return self.request_missing_info()
    
    def extract_user_info(self, message: str):
        """Extract user information from the message"""
        message_lower = message.lower()
        
        # Extract name
        name_patterns = [
            r'my name is ([a-zA-Z\s]+)',
            r'i am ([a-zA-Z\s]+)',
            r'this is ([a-zA-Z\s]+)',
            r'call me ([a-zA-Z\s]+)',
            r'i\'?m ([a-zA-Z\s]+)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).strip().split()[0].capitalize()  # Take first name
                if name:  # Make sure we got a valid name
                    self.state.collected_info['name'] = name
                    break
        
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, message)
        if email_match:
            self.state.collected_info['email'] = email_match.group()
        
        # Extract platform
        platforms = ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook', 'linkedin']
        for platform in platforms:
            if platform in message_lower:
                self.state.collected_info['platform'] = platform.capitalize()
                break
    
    def has_all_lead_info(self) -> bool:
        """Check if we have all required lead information"""
        return ('name' in self.state.collected_info and 
                'email' in self.state.collected_info and 
                'platform' in self.state.collected_info)
    
    def request_missing_info(self) -> str:
        """Request any missing lead information"""
        missing_items = []
        if 'name' not in self.state.collected_info:
            missing_items.append('name')
        if 'email' not in self.state.collected_info:
            missing_items.append('email')
        if 'platform' not in self.state.collected_info:
            missing_items.append('creator platform')
        
        if missing_items:
            return f"I need some information to set you up: Could you please provide your {' and '.join(missing_items)}?"
        else:
            return "Thank you! Your information has been captured. We'll contact you shortly about getting started with AutoStream."
    
    def handle_general_inquiry(self) -> str:
        return "I'm here to help you learn about AutoStream, our automated video editing tool for content creators. What would you like to know?"

# Main function to run the simple agent
def run_simple_agent():
    agent = SimpleAutoStreamAgent()
    
    print("Simple AutoStream Assistant is ready! Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Assistant: Goodbye!")
            break
        
        response = agent.process_intent(user_input)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    run_simple_agent()