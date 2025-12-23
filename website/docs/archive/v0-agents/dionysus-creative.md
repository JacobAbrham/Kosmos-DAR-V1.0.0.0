# Dionysus Creative Agent (DEPRECATED)

:::warning Deprecated Agent
    This agent has been deprecated in KOSMOS V1.0.0. Its responsibilities have been distributed to:
    
    - **ATHENA** - Document processing, knowledge synthesis, research
    - **HESTIA** - Content curation, media management, personalization
    - **IRIS** - Communications, stakeholder messaging
    - **LiteLLM** - Direct LLM access for content generation tasks
    
    Creative content generation is now handled as a capability across relevant agents rather than a dedicated agent.

---

**Domain:** Creative Content Generation & Writing  
**Greek Deity:** Dionysus - God of Wine and Festivity  
**Status:** ~~Active~~ **DEPRECATED**  
**Version:** 1.0.0  
**Deprecated In:** V1.0.0

---

## Overview

Dionysus is the **creative content** agent, handling content generation, writing, and creative tasks. Named after the god of inspiration and creativity, Dionysus produces engaging content across various formats and styles.

### Key Capabilities

- **Content Writing** - Generate articles, reports, documentation
- **Creative Writing** - Stories, marketing copy, descriptions
- **Summarization** - Condense long documents
- **Translation** - Translate between languages
- **Style Adaptation** - Match writing styles

### Supported Actions

| Action | Description | Required Params |
|--------|-------------|-----------------|
| `write_content` | Generate content | `topic`, `format`, `tone` |
| `summarize` | Summarize text | `text`, `length` |
| `translate` | Translate text | `text`, `target_language` |
| `rewrite` | Rewrite in different style | `text`, `style` |
| `proofread` | Check and correct text | `text` |

### MCP Connections

| MCP Server | Purpose |
|------------|---------|
| image-gen-mcp | Image generation |
| audio-mcp | Audio/voice generation |

---

## Deprecation Rationale

Dionysus was a "catch-all" creative agent that didn't align with the V1.0.0 architecture principles:

1. **Content generation** is a core LLM capability accessible via LiteLLM
2. **Document synthesis** moved to ATHENA (knowledge agent)
3. **Communications** moved to IRIS (communications agent)
4. **Media curation** moved to HESTIA (personal & media agent)

Having a dedicated "creative" agent created unnecessary routing overhead. Content generation is now a distributed capability available to all agents via the LiteLLM proxy.

---

**Last Updated:** 2025-12-12  
**Archived:** 2025-12-13
