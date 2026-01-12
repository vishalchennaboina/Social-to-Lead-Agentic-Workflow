# Social-to-Lead Agentic Workflow - AutoStream

This project implements a conversational AI agent for AutoStream, a SaaS product that provides automated video editing tools for content creators. The agent can understand user intent, answer product questions, identify high-intent leads, and trigger backend actions.

## How to Run the Project Locally

1. Clone the repository:
```bash
git clone <repository-url>
cd social-to-lead-agentic-workflow
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the agent:
```bash
python simple_agent.py
```

Alternatively, you can run the demo script to see the agent capabilities:
```bash
python demo_script.py
```

## Architecture Explanation

The agent is built with a modular architecture that separates concerns:

1. Intent Classification: Uses regex patterns to identify user intent
2. Knowledge Base: Stores product information in JSON format
3. State Management: Tracks conversation state and collected information
4. Tool Execution: Handles lead capture when all information is collected
5. Response Generation: Creates appropriate responses based on context

The state management system maintains context across multiple conversation turns, allowing the agent to remember collected lead details and continue conversations appropriately. The system properly handles conditional routing based on intent, enabling the agent to switch between different behaviors (answering questions vs. collecting lead information) seamlessly.

## WhatsApp Deployment Question

To integrate this agent with WhatsApp using Webhooks, I would implement the following approach:

1. Create a webhook endpoint that listens for incoming WhatsApp messages via the WhatsApp Business API
2. Transform the incoming message format to match the agent's input expectations
3. Process the message through the agent graph
4. Return the agent's response back to the WhatsApp Business API to send to the user
5. Implement session management to maintain conversation state per user using a database or Redis
6. Add message queuing to handle rate limits and ensure reliable delivery

The state management system I've implemented would need to be adapted to store conversation state keyed by WhatsApp user IDs, allowing the agent to maintain context across multiple interactions with the same user.