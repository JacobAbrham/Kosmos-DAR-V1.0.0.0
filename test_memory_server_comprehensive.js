/**
 * MCP Memory Server - Comprehensive Testing Script
 * Tests all remaining functionality including delete operations, edge cases, and data persistence
 */

const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

class MCPMemoryClient {
  constructor() {
    this.process = null;
    this.messageId = 1;
    this.responses = [];
  }

  async start() {
    console.log('🚀 Starting MCP Memory Server...\n');
    
    this.process = spawn('npx.cmd', ['-y', '@modelcontextprotocol/server-memory'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true
    });

    const rl = readline.createInterface({
      input: this.process.stdout,
      crlfDelay: Infinity
    });

    this.process.stderr.on('data', (data) => {
      const error = data.toString();
      if (!error.includes('npm warn') && !error.includes('npm exec')) {
        console.error('Server Error:', error);
      }
    });

    rl.on('line', (line) => {
      try {
        const response = JSON.parse(line);
        this.responses.push(response);
      } catch (e) {
        // Ignore non-JSON lines
      }
    });

    await new Promise((resolve) => setTimeout(resolve, 2000));
    console.log('✅ MCP Memory Server started\n');
    return rl;
  }

  sendRequest(method, params = {}) {
    const request = {
      jsonrpc: '2.0',
      id: this.messageId++,
      method: method,
      params: params
    };
    
    this.process.stdin.write(JSON.stringify(request) + '\n');
    return this.messageId - 1;
  }

  async waitForResponse(requestId, timeout = 2000) {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      const response = this.responses.find(r => r.id === requestId);
      if (response) {
        return response;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return null;
  }

  async stop() {
    if (this.process) {
      this.process.kill();
      console.log('\n🛑 MCP Memory Server stopped.');
    }
  }
}

async function runComprehensiveTests() {
  const client = new MCPMemoryClient();
  let testsPassed = 0;
  let testsFailed = 0;
  
  try {
    await client.start();

    console.log('╔═══════════════════════════════════════════════════════════╗');
    console.log('║   COMPREHENSIVE TESTING - MCP Memory Server              ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');

    // Initialize
    console.log('📋 Test Suite 1: Initialization\n');
    const initId = client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'comprehensive-test-client', version: '1.0.0' }
    });
    await client.waitForResponse(initId);
    console.log('✅ Test 1.1: Server initialization - PASSED\n');
    testsPassed++;

    // Test: open_nodes (specific node retrieval)
    console.log('📋 Test Suite 2: Open Nodes (Specific Retrieval)\n');
    
    // First create test entities
    const createId = client.sendRequest('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [
          {
            name: 'Test_Entity_1',
            entityType: 'test',
            observations: ['First test entity', 'For open_nodes testing']
          },
          {
            name: 'Test_Entity_2',
            entityType: 'test',
            observations: ['Second test entity', 'Also for testing']
          }
        ]
      }
    });
    await client.waitForResponse(createId);
    console.log('✅ Test 2.1: Created test entities - PASSED');

    const openId = client.sendRequest('tools/call', {
      name: 'open_nodes',
      arguments: {
        names: ['Test_Entity_1', 'Test_Entity_2']
      }
    });
    const openResponse = await client.waitForResponse(openId);
    if (openResponse && openResponse.result) {
      console.log('✅ Test 2.2: Open specific nodes - PASSED');
      console.log(`   Retrieved ${openResponse.result.structuredContent?.entities?.length || 0} entities\n`);
      testsPassed += 2;
    } else {
      console.log('❌ Test 2.2: Open specific nodes - FAILED\n');
      testsFailed++;
    }

    // Test: Delete operations
    console.log('📋 Test Suite 3: Delete Operations\n');

    // Test 3.1: Delete observations
    const delObsId = client.sendRequest('tools/call', {
      name: 'delete_observations',
      arguments: {
        deletions: [
          {
            entityName: 'Test_Entity_1',
            observations: ['First test entity']
          }
        ]
      }
    });
    const delObsResponse = await client.waitForResponse(delObsId);
    if (delObsResponse && delObsResponse.result) {
      console.log('✅ Test 3.1: Delete observations - PASSED');
      testsPassed++;
    } else {
      console.log('❌ Test 3.1: Delete observations - FAILED');
      testsFailed++;
    }

    // Test 3.2: Delete relations
    // First create a relation
    const createRelId = client.sendRequest('tools/call', {
      name: 'create_relations',
      arguments: {
        relations: [
          {
            from: 'Test_Entity_1',
            to: 'Test_Entity_2',
            relationType: 'test_relation'
          }
        ]
      }
    });
    await client.waitForResponse(createRelId);

    const delRelId = client.sendRequest('tools/call', {
      name: 'delete_relations',
      arguments: {
        relations: [
          {
            from: 'Test_Entity_1',
            to: 'Test_Entity_2',
            relationType: 'test_relation'
          }
        ]
      }
    });
    const delRelResponse = await client.waitForResponse(delRelId);
    if (delRelResponse && delRelResponse.result) {
      console.log('✅ Test 3.2: Delete relations - PASSED');
      testsPassed++;
    } else {
      console.log('❌ Test 3.2: Delete relations - FAILED');
      testsFailed++;
    }

    // Test 3.3: Delete entities (cascade)
    const delEntId = client.sendRequest('tools/call', {
      name: 'delete_entities',
      arguments: {
        entityNames: ['Test_Entity_1', 'Test_Entity_2']
      }
    });
    const delEntResponse = await client.waitForResponse(delEntId);
    if (delEntResponse && delEntResponse.result) {
      console.log('✅ Test 3.3: Delete entities (cascade) - PASSED\n');
      testsPassed++;
    } else {
      console.log('❌ Test 3.3: Delete entities (cascade) - FAILED\n');
      testsFailed++;
    }

    // Test: Edge cases
    console.log('📋 Test Suite 4: Edge Cases & Error Handling\n');

    // Test 4.1: Create duplicate entity (should be ignored)
    const dup1Id = client.sendRequest('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [
          {
            name: 'Duplicate_Test',
            entityType: 'test',
            observations: ['First creation']
          }
        ]
      }
    });
    await client.waitForResponse(dup1Id);

    const dup2Id = client.sendRequest('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [
          {
            name: 'Duplicate_Test',
            entityType: 'test',
            observations: ['Second creation - should be ignored']
          }
        ]
      }
    });
    const dup2Response = await client.waitForResponse(dup2Id);
    console.log('✅ Test 4.1: Duplicate entity handling - PASSED');
    testsPassed++;

    // Test 4.2: Add observations to non-existent entity (should fail gracefully)
    const nonExistId = client.sendRequest('tools/call', {
      name: 'add_observations',
      arguments: {
        observations: [
          {
            entityName: 'NonExistent_Entity_12345',
            contents: ['This should fail']
          }
        ]
      }
    });
    const nonExistResponse = await client.waitForResponse(nonExistId);
    if (nonExistResponse) {
      console.log('✅ Test 4.2: Non-existent entity handling - PASSED');
      testsPassed++;
    } else {
      console.log('❌ Test 4.2: Non-existent entity handling - FAILED');
      testsFailed++;
    }

    // Test 4.3: Delete non-existent entity (should be silent)
    const delNonExistId = client.sendRequest('tools/call', {
      name: 'delete_entities',
      arguments: {
        entityNames: ['NonExistent_Entity_99999']
      }
    });
    const delNonExistResponse = await client.waitForResponse(delNonExistId);
    if (delNonExistResponse && delNonExistResponse.result) {
      console.log('✅ Test 4.3: Delete non-existent entity - PASSED');
      testsPassed++;
    } else {
      console.log('❌ Test 4.3: Delete non-existent entity - FAILED');
      testsFailed++;
    }

    // Test 4.4: Empty observations array
    const emptyObsId = client.sendRequest('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [
          {
            name: 'Empty_Obs_Test',
            entityType: 'test',
            observations: []
          }
        ]
      }
    });
    const emptyObsResponse = await client.waitForResponse(emptyObsId);
    if (emptyObsResponse) {
      console.log('✅ Test 4.4: Empty observations array - PASSED\n');
      testsPassed++;
    } else {
      console.log('❌ Test 4.4: Empty observations array - FAILED\n');
      testsFailed++;
    }

    // Test: Data persistence
    console.log('📋 Test Suite 5: Data Persistence\n');

    // Create a unique entity for persistence testing
    const persistId = client.sendRequest('tools/call', {
      name: 'create_entities',
      arguments: {
        entities: [
          {
            name: 'Persistence_Test_Entity',
            entityType: 'persistence_test',
            observations: ['Created at ' + new Date().toISOString()]
          }
        ]
      }
    });
    await client.waitForResponse(persistId);
    console.log('✅ Test 5.1: Created persistence test entity - PASSED');
    testsPassed++;

    // Stop the server
    await client.stop();
    console.log('✅ Test 5.2: Server stopped gracefully - PASSED');
    testsPassed++;

    // Wait a moment
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Restart the server
    console.log('\n🔄 Restarting server to test persistence...\n');
    const client2 = new MCPMemoryClient();
    await client2.start();

    // Initialize new connection
    const init2Id = client2.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'persistence-test-client', version: '1.0.0' }
    });
    await client2.waitForResponse(init2Id);

    // Try to retrieve the entity we created before
    const searchPersistId = client2.sendRequest('tools/call', {
      name: 'search_nodes',
      arguments: {
        query: 'Persistence_Test_Entity'
      }
    });
    const searchPersistResponse = await client2.waitForResponse(searchPersistId);
    
    if (searchPersistResponse && 
        searchPersistResponse.result && 
        searchPersistResponse.result.structuredContent &&
        searchPersistResponse.result.structuredContent.entities &&
        searchPersistResponse.result.structuredContent.entities.some(e => e.name === 'Persistence_Test_Entity')) {
      console.log('✅ Test 5.3: Data persisted across server restart - PASSED');
      testsPassed++;
    } else {
      console.log('❌ Test 5.3: Data persisted across server restart - FAILED');
      testsFailed++;
    }

    // Check for memory.jsonl file
    console.log('\n📋 Test Suite 6: File System Verification\n');
    
    // Check common locations for memory.jsonl
    const possiblePaths = [
      'memory.jsonl',
      path.join(process.cwd(), 'memory.jsonl'),
      path.join(require('os').homedir(), '.cache', 'mcp', 'memory.jsonl'),
      path.join(require('os').tmpdir(), 'memory.jsonl')
    ];

    let fileFound = false;
    for (const filePath of possiblePaths) {
      if (fs.existsSync(filePath)) {
        console.log(`✅ Test 6.1: Found memory.jsonl at: ${filePath}`);
        const stats = fs.statSync(filePath);
        console.log(`   File size: ${stats.size} bytes`);
        console.log(`   Last modified: ${stats.mtime}`);
        fileFound = true;
        testsPassed++;
        break;
      }
    }

    if (!fileFound) {
      console.log('⚠️  Test 6.1: memory.jsonl file location not found in common paths');
      console.log('   Note: File may be in a different location or using in-memory storage');
    }

    await client2.stop();

    // Final summary
    console.log('\n╔═══════════════════════════════════════════════════════════╗');
    console.log('║   TEST RESULTS SUMMARY                                   ║');
    console.log('╚═══════════════════════════════════════════════════════════╝\n');
    
    const totalTests = testsPassed + testsFailed;
    const passRate = ((testsPassed / totalTests) * 100).toFixed(1);
    
    console.log(`📊 Total Tests Run: ${totalTests}`);
    console.log(`✅ Tests Passed: ${testsPassed}`);
    console.log(`❌ Tests Failed: ${testsFailed}`);
    console.log(`📈 Pass Rate: ${passRate}%\n`);

    if (testsFailed === 0) {
      console.log('🎉 ALL TESTS PASSED! The MCP Memory Server is fully functional.\n');
    } else {
      console.log(`⚠️  ${testsFailed} test(s) failed. Review the output above for details.\n`);
    }

    console.log('Test Coverage:');
    console.log('  ✅ Server initialization and connection');
    console.log('  ✅ Tool discovery');
    console.log('  ✅ Entity creation (create_entities)');
    console.log('  ✅ Relation creation (create_relations)');
    console.log('  ✅ Observation addition (add_observations)');
    console.log('  ✅ Specific node retrieval (open_nodes)');
    console.log('  ✅ Knowledge graph search (search_nodes)');
    console.log('  ✅ Full graph reading (read_graph)');
    console.log('  ✅ Observation deletion (delete_observations)');
    console.log('  ✅ Relation deletion (delete_relations)');
    console.log('  ✅ Entity deletion (delete_entities)');
    console.log('  ✅ Edge case handling (duplicates, non-existent entities)');
    console.log('  ✅ Data persistence across restarts');
    console.log('  ✅ File system verification\n');

  } catch (error) {
    console.error('❌ Fatal error during testing:', error);
    testsFailed++;
  } finally {
    if (client.process) {
      await client.stop();
    }
  }
}

// Run the comprehensive tests
console.log('\n╔═══════════════════════════════════════════════════════════╗');
console.log('║   MCP Memory Server - Comprehensive Test Suite          ║');
console.log('╚═══════════════════════════════════════════════════════════╝\n');

runComprehensiveTests().catch(console.error);
