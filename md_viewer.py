"""
Lightweight Markdown Viewer/Editor
Double-click any .md file to view it rendered in your browser.
Uses a local HTTP server for save support.
marked.js (CDN) for rendering + highlight.js for code blocks.
"""

import sys
import os
import json
import html
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, unquote
import mimetypes

# Globals set in main()
MD_PATH = ""
HOST = "127.0.0.1"
PORT = 0  # auto-assigned


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence console output

    def do_GET(self):
        if self.path == "/":
            self._serve_page()
        elif self.path == "/content":
            self._serve_content()
        else:
            self._serve_static()

    def _serve_static(self):
        """Serve files relative to the markdown file's directory (for images etc.)."""
        rel_path = unquote(self.path.lstrip("/"))
        base_dir = os.path.realpath(os.path.dirname(MD_PATH))
        file_path = os.path.realpath(os.path.join(base_dir, rel_path))
        if not file_path.startswith(base_dir + os.sep):
            self.send_error(403)
            return
        if not os.path.isfile(file_path):
            self.send_error(404)
            return
        content_type, _ = mimetypes.guess_type(file_path)
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def do_POST(self):
        if self.path == "/save":
            self._handle_save()
        elif self.path == "/shutdown":
            self.send_response(200)
            self.end_headers()
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        else:
            self.send_error(404)

    def _serve_content(self):
        """Return current file content as JSON."""
        with open(MD_PATH, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"content": content}).encode("utf-8"))

    def _handle_save(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)
        content = data.get("content", "")
        try:
            with open(MD_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def _serve_page(self):
        with open(MD_PATH, "r", encoding="utf-8", errors="replace") as f:
            raw_md = f.read()

        filename = os.path.basename(MD_PATH)
        folder = os.path.dirname(MD_PATH)
        md_json = json.dumps(raw_md)

        page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(filename)}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.css">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
    background: #f5f5f5;
    color: #212121;
  }}

  .toolbar {{
    position: sticky;
    top: 0;
    z-index: 10;
    background: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    padding: 8px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }}

  .toolbar .filename {{
    font-weight: 600;
    font-size: 14px;
    color: #424242;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}

  .toolbar .path {{
    font-size: 11px;
    color: #9e9e9e;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}

  .toolbar button {{
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    cursor: pointer;
    color: #424242;
    transition: all 0.15s;
    white-space: nowrap;
  }}

  .toolbar button:hover {{
    background: #e8e8e8;
  }}

  .toolbar button.active {{
    background: #1976d2;
    color: white;
    border-color: #1565c0;
  }}

  .toolbar button.save-btn {{
    background: #2e7d32;
    color: white;
    border-color: #1b5e20;
    display: none;
  }}

  .toolbar button.save-btn:hover {{
    background: #388e3c;
  }}

  .toolbar button.save-btn.unsaved {{
    display: inline-block;
  }}

  .toolbar .save-status {{
    font-size: 12px;
    color: #9e9e9e;
    white-space: nowrap;
  }}

  .container {{
    max-width: 900px;
    margin: 24px auto;
    padding: 0 24px;
  }}

  /* Rendered view */
  .rendered {{
    background: #ffffff;
    border-radius: 8px;
    padding: 32px 40px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    line-height: 1.7;
  }}

  .rendered h1 {{ font-size: 2em; margin: 0.8em 0 0.4em; padding-bottom: 0.3em; border-bottom: 1px solid #eee; }}
  .rendered h2 {{ font-size: 1.5em; margin: 0.8em 0 0.4em; padding-bottom: 0.2em; border-bottom: 1px solid #eee; }}
  .rendered h3 {{ font-size: 1.25em; margin: 0.8em 0 0.4em; }}
  .rendered h4 {{ font-size: 1.1em; margin: 0.8em 0 0.4em; }}
  .rendered p {{ margin: 0.6em 0; }}
  .rendered ul, .rendered ol {{ margin: 0.5em 0; padding-left: 2em; }}
  .rendered li {{ margin: 0.25em 0; }}
  .rendered blockquote {{
    border-left: 4px solid #1976d2;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f8f9fa;
    color: #555;
  }}
  .rendered code {{
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
  }}
  .rendered pre {{
    background: #f6f8fa;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 1em 0;
  }}
  .rendered pre code {{
    background: none;
    padding: 0;
    font-size: 0.85em;
  }}
  .rendered table {{
    border-collapse: collapse;
    width: auto;
    min-width: 100%;
    margin: 1em 0;
  }}
  .rendered th, .rendered td {{
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
  }}
  .rendered th {{
    background: #f5f5f5;
    font-weight: 600;
  }}
  .rendered tr:nth-child(even) {{
    background: #fafafa;
  }}
  .rendered img {{
    max-width: 100%;
    border-radius: 4px;
  }}
  .rendered a {{
    color: #1976d2;
    text-decoration: none;
  }}
  .rendered a:hover {{
    text-decoration: underline;
  }}
  .rendered hr {{
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 1.5em 0;
  }}

  /* Split view */
  .container.split-mode {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    max-width: 100%;
  }}

  .container.split-mode .rendered {{
    max-height: calc(100vh - 80px);
    overflow-y: auto;
  }}

  .container.split-mode .raw-view {{
    display: block !important;
  }}

  .container.split-mode .raw-view textarea {{
    min-height: calc(100vh - 80px);
  }}

  /* Raw/edit view */
  .raw-view {{
    display: none;
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}

  .raw-view .CodeMirror {{
    height: auto;
    min-height: 80vh;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 14px;
    line-height: 1.6;
    border: none;
    border-radius: 8px;
    padding: 8px 0;
  }}

  .container.split-mode .raw-view .CodeMirror {{
    min-height: calc(100vh - 80px);
    height: calc(100vh - 80px);
  }}
</style>
</head>
<body>

<div class="toolbar">
  <div class="filename">{html.escape(filename)}</div>
  <div class="path" title="{html.escape(folder)}">{html.escape(folder)}</div>
  <button id="btnView" class="active" onclick="showView()">View</button>
  <button id="btnEdit" onclick="showEdit()">Edit</button>
  <button id="btnSplit" onclick="showSplit()">Split</button>
  <button id="btnSave" class="save-btn" onclick="saveFile()">Save</button>
  <span id="saveStatus" class="save-status"></span>
</div>

<div class="container">
  <div class="rendered" id="rendered"></div>
  <div class="raw-view" id="rawView">
    <div id="editorHost"></div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.1/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/mode/markdown/markdown.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/mode/xml/xml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/addon/mode/overlay.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/mode/gfm/gfm.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.18/addon/edit/continuelist.min.js"></script>
<script>
  const rawMd = {md_json};
  let savedContent = rawMd;
  let dirty = false;

  marked.setOptions({{
    highlight: function(code, lang) {{
      if (lang && hljs.getLanguage(lang)) {{
        return hljs.highlight(code, {{ language: lang }}).value;
      }}
      return hljs.highlightAuto(code).value;
    }},
    breaks: true,
    gfm: true
  }});

  // Add id attributes to headings for anchor navigation
  marked.use({{
    hooks: {{
      postprocess: function(html) {{
        return html.replace(/<h([1-6])>(.*?)<\/h[1-6]>/g, function(match, level, content) {{
          const slug = content.replace(/<[^>]*>/g, '').toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
          return '<h' + level + ' id="' + slug + '">' + content + '</h' + level + '>';
        }});
      }}
    }}
  }});

  const rendered = document.getElementById('rendered');
  const rawView = document.getElementById('rawView');
  const btnView = document.getElementById('btnView');
  const btnEdit = document.getElementById('btnEdit');
  const btnSave = document.getElementById('btnSave');
  const btnSplit = document.getElementById('btnSplit');
  const saveStatus = document.getElementById('saveStatus');

  // Initialize CodeMirror
  const cm = CodeMirror(document.getElementById('editorHost'), {{
    value: rawMd,
    mode: 'gfm',
    theme: 'default',
    lineNumbers: true,
    lineWrapping: true,
    tabSize: 4,
    indentWithTabs: false,
    extraKeys: {{
      'Enter': 'newlineAndIndentContinueMarkdownList',
      'Ctrl-S': function() {{ if (dirty) saveFile(); }},
      'Cmd-S': function() {{ if (dirty) saveFile(); }}
    }}
  }});

  mermaid.initialize({{ startOnLoad: false, theme: 'default' }});

  function renderMermaid() {{
    document.querySelectorAll('pre code.language-mermaid').forEach(function(block) {{
      const pre = block.parentElement;
      const div = document.createElement('div');
      div.className = 'mermaid';
      div.textContent = block.textContent;
      pre.replaceWith(div);
    }});
    mermaid.run();
  }}

  // Expand container width when tables are wider than the default 900px
  function adjustContainerWidth() {{
    const container = document.querySelector('.container');
    // Split mode uses full viewport width via CSS — skip JS override
    if (container.classList.contains('split-mode')) {{
      container.style.maxWidth = '';
      return;
    }}
    const tables = rendered.querySelectorAll('table');
    let maxTableWidth = 0;
    tables.forEach(function(t) {{
      if (t.scrollWidth > maxTableWidth) maxTableWidth = t.scrollWidth;
    }});
    // 128px = card padding (40*2) + container padding (24*2)
    const needed = maxTableWidth + 128;
    container.style.maxWidth = (needed > 900 ? needed + 'px' : '');
  }}

  rendered.innerHTML = marked.parse(rawMd);
  renderMermaid();
  adjustContainerWidth();

  // Handle anchor links — scroll within the page instead of requesting the server
  rendered.addEventListener('click', function(e) {{
    const link = e.target.closest('a');
    if (link && link.getAttribute('href') && link.getAttribute('href').startsWith('#')) {{
      e.preventDefault();
      const id = decodeURIComponent(link.getAttribute('href').substring(1));
      const target = document.getElementById(id);
      if (target) {{
        target.scrollIntoView({{ behavior: 'smooth' }});
        history.replaceState(null, '', '#' + id);
      }}
    }}
  }});

  // Track changes + live preview in split mode
  let splitTimer = null;
  cm.on('changes', function() {{
    const val = cm.getValue();
    dirty = (val !== savedContent);
    btnSave.classList.toggle('unsaved', dirty);
    if (dirty) {{
      saveStatus.textContent = 'Unsaved changes';
      saveStatus.style.color = '#e65100';
    }} else {{
      saveStatus.textContent = '';
    }}
    if (mode === 'split') {{
      clearTimeout(splitTimer);
      splitTimer = setTimeout(function() {{
        rendered.innerHTML = marked.parse(cm.getValue());
        renderMermaid();
        adjustContainerWidth();
      }}, 300);
    }}
  }});

  let mode = 'view';

  function showView() {{
    mode = 'view';
    rendered.innerHTML = marked.parse(cm.getValue());
    renderMermaid();
    rendered.style.display = 'block';
    rawView.style.display = 'none';
    document.querySelector('.container').className = 'container';
    btnView.classList.add('active');
    btnEdit.classList.remove('active');
    btnSplit.classList.remove('active');
    adjustContainerWidth();
  }}

  function showEdit() {{
    mode = 'edit';
    rendered.style.display = 'none';
    rawView.style.display = 'block';
    document.querySelector('.container').className = 'container';
    btnEdit.classList.add('active');
    btnView.classList.remove('active');
    btnSplit.classList.remove('active');
    setTimeout(function() {{ cm.refresh(); cm.focus(); }}, 10);
  }}

  function showSplit() {{
    mode = 'split';
    rendered.innerHTML = marked.parse(cm.getValue());
    renderMermaid();
    rendered.style.display = 'block';
    rawView.style.display = 'block';
    document.querySelector('.container').className = 'container split-mode';
    btnSplit.classList.add('active');
    btnView.classList.remove('active');
    btnEdit.classList.remove('active');
    adjustContainerWidth();
    setTimeout(function() {{ cm.refresh(); cm.focus(); }}, 10);
  }}

  async function saveFile() {{
    saveStatus.textContent = 'Saving...';
    saveStatus.style.color = '#9e9e9e';
    try {{
      const resp = await fetch('/save', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ content: cm.getValue() }})
      }});
      const result = await resp.json();
      if (result.ok) {{
        savedContent = cm.getValue();
        dirty = false;
        btnSave.classList.remove('unsaved');
        saveStatus.textContent = 'Saved';
        saveStatus.style.color = '#2e7d32';
        setTimeout(() => {{ if (!dirty) saveStatus.textContent = ''; }}, 2000);
      }} else {{
        saveStatus.textContent = 'Save failed: ' + (result.error || 'Unknown error');
        saveStatus.style.color = '#c62828';
      }}
    }} catch (err) {{
      saveStatus.textContent = 'Save failed: ' + err.message;
      saveStatus.style.color = '#c62828';
    }}
  }}

  // Warn before leaving with unsaved changes
  window.addEventListener('beforeunload', function(e) {{
    if (dirty) {{
      e.preventDefault();
      e.returnValue = '';
    }}
  }});
</script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


def main():
    global MD_PATH

    if len(sys.argv) < 2:
        print("Usage: md_viewer.py <file.md>")
        print("Or set as default program for .md files in Windows.")
        sys.exit(1)

    MD_PATH = os.path.abspath(sys.argv[1])

    if not os.path.isfile(MD_PATH):
        print(f"File not found: {MD_PATH}")
        sys.exit(1)

    server = HTTPServer((HOST, 0), Handler)
    port = server.server_address[1]

    # Open browser then serve until browser tab is closed / user stops
    url = f"http://{HOST}:{port}/"
    threading.Timer(0.3, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
