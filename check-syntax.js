const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Simple extraction - find content between <script> and </script> tags
const parts = html.split('<script>');
let foundJS = '';

for (let i = 1; i < parts.length; i++) {
  const scriptContent = parts[i].split('</script>')[0];
  // Skip if it's a script with src attribute
  if (!parts[i-1].endsWith('<script') || parts[i-1].includes('src=')) {
    foundJS += scriptContent + '\n';
  }
}

if (foundJS.trim()) {
  try {
    new Function(foundJS);
    console.log('✅ JavaScript syntax is valid!');
  } catch(e) {
    console.log('❌ JavaScript syntax error:');
    console.log(e.message);
  }
} else {
  console.log('No inline script content found');
}

console.log('Syntax check complete!');
