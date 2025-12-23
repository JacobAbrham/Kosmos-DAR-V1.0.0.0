import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "api/kosmos-api",
    },
    {
      type: "category",
      label: "system",
      items: [
        {
          type: "doc",
          id: "api/root-get",
          label: "Root",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/health-health-get",
          label: "Health",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/ready-ready-get",
          label: "Ready",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "agents",
      items: [
        {
          type: "doc",
          id: "api/list-agents-api-v-1-agents-get",
          label: "List Agents",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-agent-api-v-1-agents-agent-id-get",
          label: "Get Agent",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-capabilities-api-v-1-agents-agent-id-capabilities-get",
          label: "Get Capabilities",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/query-agent-api-v-1-agents-agent-id-query-post",
          label: "Query Agent",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/invoke-tool-api-v-1-agents-agent-id-tools-tool-name-post",
          label: "Invoke Tool",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Authentication",
      items: [
        {
          type: "doc",
          id: "api/list-api-keys-api-v-1-auth-api-keys-get",
          label: "List Api Keys",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/create-api-key-api-v-1-auth-api-keys-post",
          label: "Create Api Key",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/revoke-api-key-api-v-1-auth-api-keys-key-id-delete",
          label: "Revoke Api Key",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/login-api-v-1-auth-login-post",
          label: "Login",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-current-user-info-api-v-1-auth-me-get",
          label: "Get Current User Info",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/refresh-token-api-v-1-auth-refresh-post",
          label: "Refresh Token",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/register-api-v-1-auth-register-post",
          label: "Register",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "chat",
      items: [
        {
          type: "doc",
          id: "api/list-conversations-api-v-1-chat-conversations-get",
          label: "List Conversations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/delete-conversation-api-v-1-chat-conversations-conversation-id-delete",
          label: "Delete Conversation",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/get-conversation-api-v-1-chat-conversations-conversation-id-get",
          label: "Get Conversation",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/set-title-api-v-1-chat-conversations-conversation-id-title-post",
          label: "Set Title",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/send-message-api-v-1-chat-message-post",
          label: "Send Message",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "mcp",
      items: [
        {
          type: "doc",
          id: "api/health-check-all-api-v-1-mcp-health-post",
          label: "Health Check All",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/list-servers-api-v-1-mcp-servers-get",
          label: "List Servers",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/register-server-api-v-1-mcp-servers-post",
          label: "Register Server",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/unregister-server-api-v-1-mcp-servers-server-id-delete",
          label: "Unregister Server",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/check-server-health-api-v-1-mcp-servers-server-id-health-get",
          label: "Check Server Health",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-stats-api-v-1-mcp-stats-get",
          label: "Get Stats",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/list-tools-api-v-1-mcp-tools-get",
          label: "List Tools",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-tool-api-v-1-mcp-tools-server-id-tool-name-get",
          label: "Get Tool",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/invoke-tool-api-v-1-mcp-tools-server-id-tool-name-invoke-post",
          label: "Invoke Tool",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "governance",
      items: [
        {
          type: "doc",
          id: "api/analyze-action-api-v-1-votes-analyze-action-post",
          label: "Analyze Action",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/create-auto-proposal-api-v-1-votes-auto-proposal-post",
          label: "Create Auto Proposal",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-pending-proposals-api-v-1-votes-pending-get",
          label: "Get Pending Proposals",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/list-proposals-api-v-1-votes-proposals-get",
          label: "List Proposals",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/create-proposal-api-v-1-votes-proposals-post",
          label: "Create Proposal",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-proposal-api-v-1-votes-proposals-proposal-id-get",
          label: "Get Proposal",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/resolve-proposal-api-v-1-votes-proposals-proposal-id-resolve-post",
          label: "Resolve Proposal",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/manual-vote-api-v-1-votes-proposals-proposal-id-vote-post",
          label: "Manual Vote",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-voting-stats-api-v-1-votes-stats-get",
          label: "Get Voting Stats",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-thresholds-api-v-1-votes-thresholds-get",
          label: "Get Thresholds",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "websocket",
      items: [
        {
          type: "doc",
          id: "api/get-connection-stats-ws-connections-get",
          label: "Get Connection Stats",
          className: "api-method get",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
