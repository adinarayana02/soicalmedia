import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from agents.observer_agent import ObserverAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.advisor_agent import AdvisorAgent

def run_test():
    print("--- Starting Agentic AI Math Model Test ---")
    observer = ObserverAgent()
    evaluator = EvaluatorAgent()
    advisor = AdvisorAgent()
    
    # Mock Timeline: User has normal day, then a really bad late night
    now = datetime.utcnow()
    timeline = [
        {"text": "Good morning everybody! Beautiful day.", "timestamp": now - timedelta(hours=14), "type": "message"},
        {"text": "Just ate some great food", "timestamp": now - timedelta(hours=10), "type": "message"},
        {"text": "I'm so exhausted, work was terrible", "timestamp": now - timedelta(hours=4), "type": "message"},
        # Late night (3 AM) + negative + toxic words
        {"text": "I hate everything, falling apart.", "timestamp": now.replace(hour=3, minute=15), "type": "message"},
        {"text": "Can't sleep, so frustrated and angry", "timestamp": now.replace(hour=3, minute=30), "type": "comment"},
        {"text": "giving up on all of this", "timestamp": now.replace(hour=4, minute=0), "type": "message"}
    ]
    
    print("1. Running Observer Agent (Perception)...")
    observed = observer.process_timeline(timeline)
    for event in observed[-3:]:
        sig = event['signals']
        print(f" -> Late Night Event: S={sig['S']:.2f}, LNR={sig['L']:.2f}, T={sig['T']:.2f}, B={sig['B']:.2f}")

    print("\n2. Running Evaluator Agent (Reasoning)...")
    eval_metrics = evaluator.evaluate_session(observed)
    for k, v in eval_metrics.items():
        print(f" -> {k}: {v}")
        
    print("\n3. Running Advisor Agent (Decision)...")
    advice = advisor.generate_advice(eval_metrics)
    print(f" -> Risk Level: {advice['risk_level']}")
    print(f" -> Wellbeing: {advice['wellbeing_score']}")
    print(f" -> Confidence: {advice['confidence']}")
    import json
    parsed_insights = json.loads(advice['insights'])
    print(f" -> Reason: {parsed_insights['reasoning']}")
    print(f" -> Evidence:\n{parsed_insights['evidence']}")
    print("--- Test Complete ---")

if __name__ == "__main__":
    run_test()
