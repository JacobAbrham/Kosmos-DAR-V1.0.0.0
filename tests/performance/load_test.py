"""
Performance tests using k6-compatible Python wrapper.
Run with: k6 run tests/performance/load_test.js
"""
import json

# k6 JavaScript test script
K6_SCRIPT = """
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const chatLatency = new Trend('chat_latency');
const voteLatency = new Trend('vote_latency');

// Test configuration
export const options = {
    stages: [
        { duration: '30s', target: 10 },   // Ramp up
        { duration: '1m', target: 50 },    // Stay at 50 users
        { duration: '30s', target: 100 },  // Peak load
        { duration: '1m', target: 100 },   // Stay at peak
        { duration: '30s', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'],  // 95% requests under 2s
        http_req_failed: ['rate<0.01'],     // Error rate under 1%
        errors: ['rate<0.05'],              // Custom error rate under 5%
        chat_latency: ['p(95)<3000'],       // Chat p95 under 3s
        vote_latency: ['p(95)<5000'],       // Vote p95 under 5s
    },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function() {
    group('Health Checks', function() {
        const healthRes = http.get(`${BASE_URL}/health`);
        check(healthRes, {
            'health status 200': (r) => r.status === 200,
            'health response valid': (r) => r.json('status') === 'ok',
        }) || errorRate.add(1);
        
        const readyRes = http.get(`${BASE_URL}/ready`);
        check(readyRes, {
            'ready status 200': (r) => r.status === 200,
        }) || errorRate.add(1);
    });
    
    group('Chat API', function() {
        const startTime = Date.now();
        
        const chatRes = http.post(
            `${BASE_URL}/api/v1/chat/message`,
            JSON.stringify({
                content: 'Hello from k6 load test',
            }),
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        
        chatLatency.add(Date.now() - startTime);
        
        check(chatRes, {
            'chat status 200': (r) => r.status === 200,
            'chat has conversation_id': (r) => r.json('conversation_id') !== undefined,
            'chat has content': (r) => r.json('content') !== undefined,
        }) || errorRate.add(1);
    });
    
    group('Agents API', function() {
        const listRes = http.get(`${BASE_URL}/api/v1/agents`);
        check(listRes, {
            'agents list 200': (r) => r.status === 200,
            'agents is array': (r) => Array.isArray(r.json()),
        }) || errorRate.add(1);
        
        const zeusRes = http.get(`${BASE_URL}/api/v1/agents/zeus`);
        check(zeusRes, {
            'zeus status 200': (r) => r.status === 200,
            'zeus has name': (r) => r.json('name') === 'Zeus',
        }) || errorRate.add(1);
    });
    
    group('Voting API', function() {
        const startTime = Date.now();
        
        const propRes = http.post(
            `${BASE_URL}/api/v1/votes/proposals`,
            JSON.stringify({
                title: `Load Test Proposal ${Date.now()}`,
                description: 'This is a proposal created during load testing',
                cost: Math.random() * 1000,
                risk_level: 'low',
            }),
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        
        voteLatency.add(Date.now() - startTime);
        
        check(propRes, {
            'proposal status 200': (r) => r.status === 200,
            'proposal has id': (r) => r.json('proposal_id') !== undefined,
        }) || errorRate.add(1);
    });
    
    group('MCP API', function() {
        const serversRes = http.get(`${BASE_URL}/api/v1/mcp/servers`);
        check(serversRes, {
            'mcp servers 200': (r) => r.status === 200,
        }) || errorRate.add(1);
        
        const toolsRes = http.get(`${BASE_URL}/api/v1/mcp/tools`);
        check(toolsRes, {
            'mcp tools 200': (r) => r.status === 200,
        }) || errorRate.add(1);
    });
    
    sleep(1);
}

export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'results/k6_summary.json': JSON.stringify(data),
    };
}

function textSummary(data, opts) {
    // Simple text summary
    const checks = data.metrics.checks;
    const reqs = data.metrics.http_reqs;
    const duration = data.metrics.http_req_duration;
    
    return `
=== KOSMOS Load Test Results ===

Total Requests: ${reqs.values.count}
Failed Requests: ${data.metrics.http_req_failed.values.rate * 100}%

Response Time:
  - Avg: ${duration.values.avg.toFixed(2)}ms
  - P95: ${duration.values['p(95)'].toFixed(2)}ms
  - P99: ${duration.values['p(99)'].toFixed(2)}ms

Custom Metrics:
  - Chat P95: ${data.metrics.chat_latency?.values['p(95)']?.toFixed(2) || 'N/A'}ms
  - Vote P95: ${data.metrics.vote_latency?.values['p(95)']?.toFixed(2) || 'N/A'}ms
  - Error Rate: ${(data.metrics.errors?.values?.rate || 0) * 100}%

Checks Passed: ${checks.values.passes}/${checks.values.passes + checks.values.fails}
`;
}
"""


def generate_k6_script(output_path: str = "tests/performance/load_test.js"):
    """Generate the k6 load test script."""
    with open(output_path, "w") as f:
        f.write(K6_SCRIPT)
    print(f"Generated k6 script at {output_path}")
    print("Run with: k6 run tests/performance/load_test.js")


if __name__ == "__main__":
    generate_k6_script()
