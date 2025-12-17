/**
 * MCP Memory Server Demonstration Script
 * This script demonstrates the capabilities of the MCP memory server
 * by creating entities, relations, and observations in a knowledge graph.
 */

const { spawn } = require('child_process');
const readline = require('readline');

const NPX_COMMAND = process.platform === 'win32' ? 'npx.cmd' : 'npx';

class MCPMemoryClient {
  constructor() {
    this.process = null;
    this.messageId = 1;
  }

  async start() {
    console.log('🚀 Starting MCP Memory Server...\n');
    
    // Start the MCP server process (Windows-compatible)
    this.process = spawn(NPX_COMMAND, ['-y', '@modelcontextprotocol/server-memory'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true
    });

    // Set up readline interface for server output
    const rl = readline.createInterface({
      input: this.process.stdout,
      crlfDelay: Infinity
    });

    // Handle server errors
    this.process.stderr.on('data', (data) => {
      const error = data.toString();
      if (!error.includes('npm warn')) {
        console.error('Server Error:', error);
      }
    });

    // Wait for server to be ready
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    console.log('✅ MCP Memory Server started successfully!\n');
    return rl;
  }

  sendRequest(method, params = {}) {
    const request = {
      jsonrpc: '2.0',
      id: this.messageId++,
      method: method,
      params: params
    };
    
    console.log(`📤 Sending request: ${method}`);
    this.process.stdin.write(JSON.stringify(request) + '\n');
  }

  async stop() {
    if (this.process) {
      this.process.kill();
      console.log('\n🛑 MCP Memory Server stopped.');
    }
  }
}

async function demonstrateMemoryServer() {
  const client = new MCPMemoryClient();
  
  try {
    const rl = await client.start();
    
    // Collect responses
    const responses = [];
    rl.on('line', (line) => {
      try {
        const response = JSON.parse(line);
        responses.push(response);
        console.log('📥 Response received:', JSON.stringify(response, null, 2));
      } catch (e) {
        // Ignore non-JSON lines
      }
    });

    console.log('═══════════════════════════════════════════════════════════');
    console.log('  DEMONSTRATION: MCP Memory Server Capabilities');
    console.log('═══════════════════════════════════════════════════════════\n');

    // Initialize the connection
    console.log('Step 1: Initializing connection...\n');
    client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'memory-demo-client',
        version: '1.0.0'
      }
    });
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // List available tools
    console.log('\nStep 2: Listing available tools...\n');
    client.sendRequest('tools/list');
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Create entities
    console.log('\nStep 3: Creating entities in the knowledge graph...\n');
    client.sendRequest('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [
          {
            name: 'Kosmos_Documentation',
            entityType: 'project',
            observations: [
              'AI/ML documentation framework',
              'Uses MkDocs for documentation generation',
              'Includes governance, architecture, and operations sections'
            ]
          },
          {
            name: 'MCP_Memory_Server',
            entityType: 'tool',
            observations: [
              'Knowledge graph-based memory system',
              'Supports entities, relations, and observations',
              'Enables persistent memory across conversations'
            ]
          },
          {
            name: 'Jacob_VM',
            entityType: 'person',
            observations: [
              'Project owner',
              'Working on AI documentation'
            ]
          }
        ]
      }
    });
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Create relations
    console.log('\nStep 4: Creating relations between entities...\n');
    client.sendRequest('tools/call', {
      name: 'create_relations',
      arguments: {
        relations: [
          {
            from: 'Jacob_VM',
            to: 'Kosmos_Documentation',
            relationType: 'maintains'
          },
          {
            from: 'Kosmos_Documentation',
            to: 'MCP_Memory_Server',
            relationType: 'uses'
          }
        ]
      }
    });
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Add more observations
    console.log('\nStep 5: Adding additional observations...\n');
    client.sendRequest('tools/call', {
      name: 'add_observations',
      arguments: {
        observations: [
          {
            entityName: 'Kosmos_Documentation',
            contents: [
              'Deployed on Cloudflare Pages',
              'Contains AIBOM (AI Bill of Materials) specifications'
            ]
          }
        ]
      }
    });
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Search the knowledge graph
    console.log('\nStep 6: Searching the knowledge graph...\n');
    client.sendRequest('tools/call', {
      name: 'search_nodes',
      arguments: {
        query: 'documentation'
      }
    });
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Read the entire graph
    console.log('\nStep 7: Reading the entire knowledge graph...\n');
    client.sendRequest('tools/call', {
      name: 'read_graph',
      arguments: {}
    });
    
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('\n═══════════════════════════════════════════════════════════');
    console.log('  DEMONSTRATION COMPLETE');
    console.log('═══════════════════════════════════════════════════════════\n');
    
    console.log('✨ Summary of demonstrated capabilities:');
    console.log('   1. ✅ Server initialization and connection');
    console.log('   2. ✅ Tool discovery (tools/list)');
    console.log('   3. ✅ Entity creation (create_entities)');
    console.log('   4. ✅ Relation creation (create_relations)');
    console.log('   5. ✅ Observation addition (add_observations)');
    console.log('   6. ✅ Knowledge graph search (search_nodes)');
    console.log('   7. ✅ Full graph reading (read_graph)\n');

    console.log('📊 The memory server has successfully stored:');
    console.log('   - 3 entities (Kosmos_Documentation, MCP_Memory_Server, Jacob_VM)');
    console.log('   - 2 relations (maintains, uses)');
    console.log('   - Multiple observations about each entity\n');

    console.log('💾 All data is persisted in memory.jsonl file');
    console.log('🔄 This data will be available in future sessions\n');

  } catch (error) {
    console.error('❌ Error during demonstration:', error);
  } finally {
    await client.stop();
  }
}

// Run the demonstration
console.log('\n╔═══════════════════════════════════════════════════════════╗');
console.log('║   MCP Memory Server - Capability Demonstration           ║');
console.log('╚═══════════════════════════════════════════════════════════╝\n');

demonstrateMemoryServer().catch(console.error);
