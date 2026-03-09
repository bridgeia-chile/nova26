with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add animations script before app.js
old_script = '<script src="app.js"></script>'
new_script = '<script src="animations.js" type="module"></script>\n    <script src="app.js"></script>'
content = content.replace(old_script, new_script)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully updated index.html')
