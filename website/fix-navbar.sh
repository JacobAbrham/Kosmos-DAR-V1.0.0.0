#!/bin/bash
# Temporary fix for API navbar item

echo "Fixing Docusaurus navbar configuration..."

# Create a temporary file with the corrected configuration
cat > temp-navbar-fix.txt << 'EOF'
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentation',
        },
        // Temporarily disabled until API docs are generated
        // {
        //   type: 'doc',
        //   docId: 'api/index',
        //   position: 'left',
        //   label: 'API',
        // },
EOF

echo "Created temporary fix file. Manual editing required."
echo "Please manually edit docusaurus.config.ts and replace the API navbar section."
