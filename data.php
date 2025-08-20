<?php
// data.php (未修復示範：請只在本機或可控環境測試)
header("Content-Type: text/html; charset=UTF-8");
$tpl = isset($_GET['tpl']) ? $_GET['tpl'] : '';
$token = isset($_GET['token']) ? $_GET['token'] : '';
$other = isset($_GET['200']) ? $_GET['200'] : '';
?>
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>data.php（未修復）</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans TC', sans-serif; margin: 24px; }
    code, pre { background:#f6f8fa; padding:2px 6px; border-radius:6px }
    .warn { color:#b00020 }
  </style>
</head>
<body>
  <h1>未修復：反射型 XSS（示範）</h1>
  <p>token: <?php echo $token; ?>, 200: <?php echo $other; ?></p>

  <h2 class="warn">tpl 原樣輸出（⚠️ 脆弱）</h2>
  <div id="content" style="border:1px dashed #ccc; padding:12px; min-height:40px;">
    <?php echo $tpl; // 直接輸出 → 造成 XSS ?>
  </div>

  <p>試著訪問例如：<br>
    <code>?tpl=%3Csvg%20onload%3Dalert(1)%3E</code>
  </p>
</body>
</html>
