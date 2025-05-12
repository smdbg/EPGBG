<?php
$jsonPath = 'channels.json';
$jsonData = file_exists($jsonPath) ? file_get_contents($jsonPath) : '{"tv_channels":[]}';
?>
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Edit Channels</title>
  
  <!-- JSONEditor CSS -->
  <link href="https://cdn.jsdelivr.net/npm/jsoneditor@latest/dist/jsoneditor.min.css" rel="stylesheet" type="text/css">

  <!-- JSONEditor JS -->
  <script src="https://cdn.jsdelivr.net/npm/jsoneditor@latest/dist/jsoneditor.min.js"></script>

  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    #editor {
      width: 100%;
      height: 600px;
      border: 1px solid #ccc;
    }
    button {
      margin-top: 10px;
      padding: 10px 20px;
      font-size: 16px;
    }
  </style>
</head>
<body>
  <h2>Edit Channels</h2>
  <form method="post" action="save.php" onsubmit="beforeSubmit()">
    <div id="editor"></div>
    <input type="hidden" name="json" id="jsonField">
    <br>
    <button type="submit">💾 Save Changes</button>
  </form>

  <script>
    const container = document.getElementById("editor");

const editor = new JSONEditor(container, {
  mode: 'tree',
  modes: ['tree', 'code'],
  search: true,
  statusBar: true,
  enableSort: true,       // ✅ Allow reordering via drag-and-drop
  enableTransform: false  // ✅ Optional: disables raw JSON-to-CSV etc.
});
    // Set initial data
    editor.set(<?= $jsonData ?>);

    // Before form submission
    function beforeSubmit() {
      const data = editor.get();
      document.getElementById('jsonField').value = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
