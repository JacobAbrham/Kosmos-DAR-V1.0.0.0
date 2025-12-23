#!/usr/bin/env node

/**
 * KOSMOS Documentation Content Validation Script
 * Validates documentation quality, links, and structure
 */

const fs = require('fs');
const path = require('path');
const { glob } = require('glob');

class ContentValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.docsPath = path.join(__dirname, '..', 'docs');
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
  }

  error(message) {
    this.errors.push(message);
    this.log(message, 'error');
  }

  warning(message) {
    this.warnings.push(message);
    this.log(message, 'warning');
  }

  async validateFrontmatter(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');

      // Check for frontmatter
      if (!lines[0].startsWith('---')) {
        this.warning(`${filePath}: Missing frontmatter`);
        return;
      }

      // Find frontmatter end
      const endIndex = lines.findIndex((line, index) => index > 0 && line.startsWith('---'));
      if (endIndex === -1) {
        this.error(`${filePath}: Unclosed frontmatter`);
        return;
      }

      const frontmatter = lines.slice(1, endIndex).join('\n');

      // Validate required fields
      const requiredFields = ['title', 'description'];
      for (const field of requiredFields) {
        if (!frontmatter.includes(`${field}:`)) {
          this.warning(`${filePath}: Missing required frontmatter field: ${field}`);
        }
      }

      // Check for empty descriptions
      if (frontmatter.includes('description: ""') || frontmatter.includes("description: ''")) {
        this.warning(`${filePath}: Empty description in frontmatter`);
      }

    } catch (err) {
      this.error(`${filePath}: Error reading file - ${err.message}`);
    }
  }

  validateMarkdownSyntax(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');

      // Check for broken links (empty URLs)
      const emptyLinkRegex = /\[([^\]]+)\]\(\s*\)/g;
      let match;
      while ((match = emptyLinkRegex.exec(content)) !== null) {
        this.error(`${filePath}: Empty link found: [${match[1]}]()`);
      }

      // Check for broken image references
      const brokenImageRegex = /!\[([^\]]*)\]\(\s*\)/g;
      while ((match = brokenImageRegex.exec(content)) !== null) {
        this.error(`${filePath}: Broken image reference: ![${match[1]}]()`);
      }

      // Check for unclosed code blocks
      const codeBlockRegex = /```/g;
      const codeBlocks = content.match(codeBlockRegex);
      if (codeBlocks && codeBlocks.length % 2 !== 0) {
        this.error(`${filePath}: Unclosed code block detected`);
      }

      // Check for proper heading hierarchy (no jumping levels)
      const headingRegex = /^(#{1,6})\s/m;
      const headings = [];
      const lines = content.split('\n');
      for (const line of lines) {
        const match = line.match(headingRegex);
        if (match) {
          headings.push(match[1].length);
        }
      }

      for (let i = 1; i < headings.length; i++) {
        if (headings[i] > headings[i - 1] + 1) {
          this.warning(`${filePath}: Heading level jump detected (h${headings[i - 1]} to h${headings[i]})`);
        }
      }

    } catch (err) {
      this.error(`${filePath}: Error validating syntax - ${err.message}`);
    }
  }

  async validateLinks(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');

      // Extract all markdown links
      const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
      let match;
      while ((match = linkRegex.exec(content)) !== null) {
        const linkText = match[1];
        const linkUrl = match[2];

        // Skip external links and anchors
        if (linkUrl.startsWith('http') || linkUrl.startsWith('#') || linkUrl.startsWith('mailto:')) {
          continue;
        }

        // Check relative links
        if (linkUrl.startsWith('./') || linkUrl.startsWith('../') || !linkUrl.includes('/')) {
          const fileDir = path.dirname(filePath);
          const absolutePath = path.resolve(fileDir, linkUrl.split('#')[0]);

          // Check if file exists (remove .md extension if present)
          let targetPath = absolutePath;
          if (!targetPath.endsWith('.md') && !fs.existsSync(targetPath)) {
            targetPath += '.md';
          }

          if (!fs.existsSync(targetPath) && !fs.existsSync(absolutePath)) {
            this.warning(`${filePath}: Broken relative link: ${linkUrl}`);
          }
        }
      }

    } catch (err) {
      this.error(`${filePath}: Error validating links - ${err.message}`);
    }
  }

  async validateFile(filePath) {
    await this.validateFrontmatter(filePath);
    this.validateMarkdownSyntax(filePath);
    await this.validateLinks(filePath);
  }

  async validateAll() {
    this.log('Starting content validation...');

    try {
      // Find all markdown files
      const pattern = path.join(this.docsPath, '**', '*.md');
      const files = await glob(pattern, { ignore: ['**/node_modules/**'] });

      this.log(`Found ${files.length} markdown files to validate`);

      // Validate each file
      for (const file of files) {
        await this.validateFile(file);
      }

      // Summary
      this.log(`\nValidation complete:`);
      this.log(`- Errors: ${this.errors.length}`);
      this.log(`- Warnings: ${this.warnings.length}`);

      if (this.errors.length > 0) {
        this.log('\n❌ Validation failed due to errors');
        process.exit(1);
      } else if (this.warnings.length > 0) {
        this.log('\n⚠️  Validation passed with warnings');
        process.exit(0);
      } else {
        this.log('\n✅ Validation passed successfully');
        process.exit(0);
      }

    } catch (err) {
      this.error(`Validation failed: ${err.message}`);
      process.exit(1);
    }
  }
}

// Run validation if called directly
if (require.main === module) {
  const validator = new ContentValidator();
  validator.validateAll();
}

module.exports = ContentValidator;