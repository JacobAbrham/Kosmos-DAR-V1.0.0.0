#!/bin/bash
# Fix unescaped < symbols in markdown tables that cause MDX compilation errors

# Find all markdown files and fix < followed by numbers in tables
find /workspaces/Kosmos-DAR-V1.0.0.0/docs/docusaurus-new/docs -name "*.md" -type f | while read file; do
    # Replace < with &lt; when followed by a number in table cells
    sed -i 's/| \(<[0-9]\+%\?\)/| \&lt;\1/g' "$file"
    sed -i 's/| \(<[0-9]\+[hmins]\)/| \&lt;\1/g' "$file"  
    sed -i 's/| \(<[0-9]\+\.[0-9]\+%\?\)/| \&lt;\1/g' "$file"
    sed -i 's/| \(<[0-9]\+s\)/| \&lt;\1/g' "$file"
    sed -i 's/| \(<[0-9]\+ms\)/| \&lt;\1/g' "$file"
    sed -i 's/(Target: \(<[0-9]\+%\?\)/(Target: \&lt;\1/g' "$file"
    sed -i 's/(target: \(<[0-9]\+%\?\)/(target: \&lt;\1/g' "$file"
done

echo "✅ Fixed < symbols in markdown files"
