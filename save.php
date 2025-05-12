<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['json'])) {
    $json = $_POST['json'];
    $decoded = json_decode($json, true);

    if ($decoded !== null && isset($decoded['tv_channels'])) {
        file_put_contents('channels.json', json_encode($decoded, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        echo "<p>✅ File saved successfully. <a href='editor.php'>Back to editor</a></p>";
    } else {
        echo "<p>❌ Invalid JSON structure. <a href='editor.php'>Back</a></p>";
    }
}
?>
