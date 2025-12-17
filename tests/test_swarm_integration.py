import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.append(os.getcwd())

from src.agents.zeus.main import ZeusAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-swarm")

async def test_delegation():
    logger.info("--- Starting Swarm Integration Test ---")
    
    zeus = ZeusAgent()
    
    try:
        # 1. Test Simple Delegation to Hermes
        logger.info("\n[Test 1] Delegating to Hermes (Email)...")
        try:
            hermes_args = {
                "to": ["test@kosmos.ai"],
                "subject": "Swarm Integration Test",
                "body": "Hello from Zeus via MCP!"
            }
            
            result = await zeus.delegate_task("hermes", "send_email", hermes_args)
            logger.info(f"Hermes Result: {result}")
        except Exception as e:
            logger.error(f"Hermes Delegation Failed: {e}")

        # 2. Test Pentarchy Voting (Delegates to Nur, Hephaestus, Athena)
        logger.info("\n[Test 2] Conducting Pentarchy Vote...")
        try:
            # Case A: Auto-Approve (< $50)
            logger.info("Case A: Low Cost ($10)")
            vote_a = await zeus.conduct_pentarchy_vote("prop-001", 10.0, "Low cost tool")
            logger.info(f"Vote A Result: {vote_a}")

            # Case B: Full Vote ($75)
            logger.info("Case B: Medium Cost ($75)")
            vote_b = await zeus.conduct_pentarchy_vote("prop-002", 75.0, "Medium cost tool")
            logger.info(f"Vote B Result: {vote_b}")
            
        except Exception as e:
            logger.error(f"Pentarchy Vote Failed: {e}")

    finally:
        await zeus.shutdown()

    logger.info("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_delegation())
