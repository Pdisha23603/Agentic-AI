"""
Advanced Test Suite - Using FoodDeliveryAgent as a Module
Demonstrates various usage patterns and customization options.
"""

import sys

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from food_delivery_agent_improved import (
    FoodDeliveryAgent, 
    TOOL_SCHEMAS, 
    check_restaurant_status,
    get_estimated_delivery_time,
    apply_discount,
    file_complaint
)
import json


def test_1_basic_usage():
    """Test 1: Basic agent usage with default queries."""
    print("\n" + "="*80)
    print("TEST 1: Basic Agent Usage")
    print("="*80)
    
    agent = FoodDeliveryAgent("Test1Bot")
    
    queries = [
        "Is Burger Barn open?",
        "Track order ORD002",
    ]
    
    for query in queries:
        result = agent.think(query)
        print(f"\nQ: {query}")
        print(f"A: {result}")
    
    print(f"\nSession Queries: {len(agent.session_log)}")


def test_2_direct_tool_calls():
    """Test 2: Direct tool function calls without agent routing."""
    print("\n" + "="*80)
    print("TEST 2: Direct Tool Function Calls")
    print("="*80)
    
    print("\n1. Direct check_restaurant_status:")
    result = check_restaurant_status("Pizza Palace")
    print(result)
    
    print("\n2. Direct get_estimated_delivery_time:")
    result = get_estimated_delivery_time("ORD001")
    print(result)
    
    print("\n3. Direct apply_discount:")
    result = apply_discount("ORD002", "quality issue")
    print(result)
    
    print("\n4. Direct file_complaint:")
    result = file_complaint("ORD003", "Food was too spicy")
    print(result)


def test_3_multiple_agents():
    """Test 3: Multiple agent instances with different personalities."""
    print("\n" + "="*80)
    print("TEST 3: Multiple Agents with Different Names")
    print("="*80)
    
    agents = [
        FoodDeliveryAgent("PizzaBot"),
        FoodDeliveryAgent("SushiBot"),
        FoodDeliveryAgent("TacoBot"),
    ]
    
    test_queries = [
        ("Is Pizza Palace open?", "PizzaBot"),
        ("When will ORD003 arrive?", "SushiBot"),
        ("I need a discount for ORD004 due to missing items", "TacoBot"),
    ]
    
    for query, bot_name in test_queries:
        bot = next(a for a in agents if a.agent_name == bot_name)
        result = bot.think(query)
        print(f"\n[{bot_name}] Q: {query}")
        print(f"[{bot_name}] A: {result[:80]}...")


def test_4_error_handling():
    """Test 4: Error handling and edge cases."""
    print("\n" + "="*80)
    print("TEST 4: Error Handling & Edge Cases")
    print("="*80)
    
    agent = FoodDeliveryAgent("TestBot")
    
    test_cases = [
        "Random gibberish query that makes no sense",
        "",  # Empty query
        "Restaurant xyz123 that doesn't exist",
        "Discount reason that doesn't exist",
    ]
    
    for i, query in enumerate(test_cases, 1):
        if query:  # Skip empty string in display
            result = agent.think(query)
            status = "✓ HANDLED" if "✗" in result or "❌" in result else "✓ PROCESSED"
            print(f"\n{i}. Query: {query}")
            print(f"   Result: {result[:100]}...")
            print(f"   Status: {status}")


def test_5_session_analysis():
    """Test 5: Session log analysis and statistics."""
    print("\n" + "="*80)
    print("TEST 5: Session Analysis & Statistics")
    print("="*80)
    
    agent = FoodDeliveryAgent("AnalysisBot")
    
    # Process multiple queries
    queries = [
        "Is Sushi Spot open?",
        "Track my order ORD001",
        "Can I get a discount for order ORD002?",
        "File complaint about order ORD003",
        "Check Curry House hours",
        "When will ORD004 be delivered?",
    ]
    
    for query in queries:
        agent.think(query)
    
    # Analyze session
    log = agent.get_session_log()
    print(f"\nTotal Queries: {len(log)}")
    
    tool_counts = {}
    for _, tool, _ in log:
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    print("\nTools Used:")
    for tool, count in sorted(tool_counts.items()):
        print(f"  • {tool}: {count} call(s)")
    
    print("\nFirst Query:", log[0][0] if log else "None")
    print("Last Query:", log[-1][0] if log else "None")


def test_6_schema_inspection():
    """Test 6: Inspect MCP schemas."""
    print("\n" + "="*80)
    print("TEST 6: MCP Schema Inspection")
    print("="*80)
    
    print(f"\nTotal Schemas: {len(TOOL_SCHEMAS)}")
    
    for schema in TOOL_SCHEMAS:
        print(f"\nTool: {schema['name']}")
        print(f"  Description: {schema['description']}")
        print(f"  Required Parameters: {', '.join(schema['parameters']['required'])}")
        
        props = schema['parameters']['properties']
        for param_name, param_info in props.items():
            print(f"    - {param_name}: {param_info.get('description', 'N/A')}")


def test_7_batch_processing():
    """Test 7: Process batch of queries efficiently."""
    print("\n" + "="*80)
    print("TEST 7: Batch Processing")
    print("="*80)
    
    agent = FoodDeliveryAgent("BatchBot")
    
    batch_queries = [
        "Is Pizza Palace open now?",
        "When will order ORD001 arrive?",
        "Give me a discount for late delivery on ORD002",
        "File complaint: wrong items in ORD003",
        "Check if Taco Town is open",
        "Track ORD004",
    ]
    
    print(f"\nProcessing {len(batch_queries)} queries...")
    results = []
    
    for query in batch_queries:
        result = agent.think(query)
        results.append((query, result))
    
    print(f"✓ Processed {len(results)} queries successfully")
    
    # Summary
    success_count = sum(1 for _, result in results if "✓" in result)
    print(f"✓ Successful Results: {success_count}/{len(results)}")
    print(f"  Success Rate: {(success_count/len(results)*100):.1f}%")


def test_8_custom_queries():
    """Test 8: Advanced custom queries."""
    print("\n" + "="*80)
    print("TEST 8: Advanced Custom Queries")
    print("="*80)
    
    agent = FoodDeliveryAgent("AdvancedBot")
    
    advanced_queries = [
        "Hi, I ordered from Pizza Palace yesterday, order ORD001",
        "My food from Curry House came cold, need to file a complaint with order ORD003",
        "Order ORD002 hasn't arrived yet and I've been waiting, can I get some compensation?",
        "Is Burger Barn still open? I want to place an order",
        "The item I ordered from Taco Town was missing, can you help me? Order ORD004",
    ]
    
    for i, query in enumerate(advanced_queries, 1):
        result = agent.think(query)
        print(f"\nQuery {i}: {query}")
        print(f"Response: {result[:120]}...")
    
    # Print final summary
    agent.print_session_summary()


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FOOD DELIVERY AGENT - ADVANCED TEST SUITE")
    print("="*80)
    
    tests = [
        ("Basic Usage", test_1_basic_usage),
        ("Direct Tool Calls", test_2_direct_tool_calls),
        ("Multiple Agents", test_3_multiple_agents),
        ("Error Handling", test_4_error_handling),
        ("Session Analysis", test_5_session_analysis),
        ("Schema Inspection", test_6_schema_inspection),
        ("Batch Processing", test_7_batch_processing),
        ("Advanced Queries", test_8_custom_queries),
    ]
    
    completed = 0
    for test_name, test_func in tests:
        try:
            test_func()
            completed += 1
            print(f"\n✓ {test_name}: PASSED")
        except Exception as e:
            print(f"\n✗ {test_name}: FAILED - {str(e)}")
    
    # Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Completed: {completed}/{len(tests)}")
    print(f"Success Rate: {(completed/len(tests)*100):.1f}%")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
