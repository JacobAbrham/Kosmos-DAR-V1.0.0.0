/**
 * Sequential Thinking MCP Server Demonstration
 * 
 * This script demonstrates the capabilities of the Sequential Thinking MCP server
 * by solving a complex problem using structured, step-by-step reasoning.
 */

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

async function demonstrateSequentialThinking() {
  console.log('=== Sequential Thinking MCP Server Demonstration ===\n');

  // Initialize the MCP client
  const transport = new StdioClientTransport({
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-sequential-thinking']
  });

  const client = new Client({
    name: 'sequential-thinking-demo',
    version: '1.0.0'
  }, {
    capabilities: {}
  });

  try {
    await client.connect(transport);
    console.log('✓ Connected to Sequential Thinking MCP server\n');

    // List available tools
    const tools = await client.listTools();
    console.log('Available tools:');
    tools.tools.forEach(tool => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });
    console.log('\n');

    // Demonstrate the sequential_thinking tool
    console.log('=== Problem: Design a scalable microservices architecture ===\n');

    // Step 1: Initial thought
    console.log('Step 1: Initial Analysis');
    const step1 = await client.callTool({
      name: 'sequential_thinking',
      arguments: {
        thought: 'To design a scalable microservices architecture, I need to consider several key aspects: service decomposition, communication patterns, data management, and deployment strategy. Let me start by identifying the core services needed.',
        nextThoughtNeeded: true,
        thoughtNumber: 1,
        totalThoughts: 5
      }
    });
    console.log('Response:', JSON.stringify(step1, null, 2));
    console.log('\n');

    // Step 2: Service decomposition
    console.log('Step 2: Service Decomposition');
    const step2 = await client.callTool({
      name: 'sequential_thinking',
      arguments: {
        thought: 'Breaking down the system into microservices: 1) API Gateway for routing, 2) Authentication Service for user management, 3) Business Logic Services for core functionality, 4) Data Services for persistence. Each service should be independently deployable and scalable.',
        nextThoughtNeeded: true,
        thoughtNumber: 2,
        totalThoughts: 5
      }
    });
    console.log('Response:', JSON.stringify(step2, null, 2));
    console.log('\n');

    // Step 3: Communication patterns
    console.log('Step 3: Communication Patterns');
    const step3 = await client.callTool({
      name: 'sequential_thinking',
      arguments: {
        thought: 'For inter-service communication, I should use: synchronous REST/gRPC for request-response patterns, and asynchronous message queues (like RabbitMQ or Kafka) for event-driven communication. This ensures loose coupling and better fault tolerance.',
        nextThoughtNeeded: true,
        thoughtNumber: 3,
        totalThoughts: 6,
        needsMoreThoughts: true
      }
    });
    console.log('Response:', JSON.stringify(step3, null, 2));
    console.log('\n');

    // Step 4: Revision - reconsidering data management
    console.log('Step 4: Revising Data Management Strategy');
    const step4 = await client.callTool({
      name: 'sequential_thinking',
      arguments: {
        thought: 'Wait, I need to reconsider the data management approach. Instead of a single data service, each microservice should own its database (database per service pattern). This ensures true independence and prevents tight coupling through shared databases.',
        nextThoughtNeeded: true,
        thoughtNumber: 4,
        totalThoughts: 6,
        isRevision: true,
        revisesThought: 2
      }
    });
    console.log('Response:', JSON.stringify(step4, null, 2));
    console.log('\n');

    // Step 5: Deployment and scaling
    console.log('Step 5: Deployment and Scaling Strategy');
    const step5 = await client.callTool({
      name: 'sequential_thinking',
      arguments: {
        thought: 'For deployment, use containerization (Docker) with orchestration (Kubernetes). Implement horizontal pod autoscaling based on CPU/memory metrics. Use service mesh (like Istio) for traffic management, security, and observability.',
        nextThoughtNeeded: true,
        thoughtNumber: 5,
        totalThoughts: 6
      }
    });
    console.log('Response:', JSON.stringify(step5, null, 2));
    console.log('\n');

    // Step 6: Final synthesis
    console.log('Step 6: Final Architecture Summary');
    const step6 = await client.callTool({
      name: 'sequential_thinking',
      arguments: {
        thought: 'Final architecture: API Gateway → Independent microservices (each with own DB) → Message queue for async communication → Containerized deployment on Kubernetes → Service mesh for observability. This design ensures scalability, fault tolerance, and independent service evolution.',
        nextThoughtNeeded: false,
        thoughtNumber: 6,
        totalThoughts: 6
      }
    });
    console.log('Response:', JSON.stringify(step6, null, 2));
    console.log('\n');

    console.log('=== Demonstration Complete ===');
    console.log('\nKey Features Demonstrated:');
    console.log('✓ Breaking down complex problems into steps');
    console.log('✓ Dynamic adjustment of total thoughts needed');
    console.log('✓ Revision of previous thinking');
    console.log('✓ Structured problem-solving process');
    console.log('✓ Context maintenance across multiple steps');

  } catch (error) {
    console.error('Error during demonstration:', error);
    throw error;
  } finally {
    await client.close();
    console.log('\n✓ Disconnected from server');
  }
}

// Run the demonstration
if (require.main === module) {
  demonstrateSequentialThinking()
    .then(() => {
      console.log('\n✓ Demonstration completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n✗ Demonstration failed:', error);
      process.exit(1);
    });
}

module.exports = { demonstrateSequentialThinking };
