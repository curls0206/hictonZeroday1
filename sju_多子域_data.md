# 聖約翰科技大學（sju.edu.tw）多子域 `data.php`「tpl」參數反射型 XSS 漏洞報告

> 報告用途：提供校方/單位修補與驗證；亦可整理為 HITCON ZeroDay 提交內容。附錄包含我們建立的「乾淨 vs 汙染」本地復刻站與資料集產生流程，用於驗證修補前後行為。

---

## 一、摘要（Summary）
在下列多個子域的 `data.php`（或同名路徑）頁面中，URL 參數 **`tpl`** 的內容被未轉義地回顯至頁面，導致 **反射型 XSS（Reflected XSS）**。利用者只需誘導使用者點擊特製連結，即可在受害者瀏覽器執行任意 JavaScript 程式碼。


---

## 二、影響範圍（Affected URLs）
- `http://www.cd.sju.edu.tw/data.php`
- `http://scsb.sju.edu.tw/data.php`
- `http://md.sju.edu.tw/homepage/data.php`

> 以上 URL 的共同點：以 `tpl` 參數回顯內容，且未做適當輸出編碼/過濾。

---

## 三、漏洞細節（Technical Details）
- **漏洞類型**：反射型 XSS（Reflected Cross-Site Scripting）
- **受影響參數**：`tpl`
- **觸發條件**：`tpl` 參數包含可執行之 HTML/JS 片段（如 `<svg onload=...>`、`<img onerror=...>` 等）。

### 1) PoC（最小、不破壞性）
下列任一連結開啟即會觸發彈窗（以 `alert(1)` 為例，僅作為存在性驗證）：
- `http://www.cd.sju.edu.tw/data.php?0=apu40&&submit=e80v0&tpl=%3Csvg%20onload%3Dalert(1)%3E`
- `http://scsb.sju.edu.tw/data.php?afterClose=pne54&tpl=%3Csvg%20onload%3Dalert(1)%3E`
- `http://md.sju.edu.tw/homepage/data.php?200=skt95&token=uwox4&tpl=%3Csvg%20onload%3Dalert(1)%3E`

> `tpl=<svg onload=alert(1)>`（需 URL 編碼）

### 2) 攻擊面與原因研判
伺服器端/前端將 `tpl` 的值直接插入 HTML（如模板輸出或 `innerHTML`），未做 **情境相符的輸出編碼（output encoding）**，導致瀏覽器把惡意字串當成 HTML/腳本解析與執行。

---

## 四、影響（Impact）
- 竊取 Cookie / LocalStorage 資料（若未設 `HttpOnly` 或適當 `SameSite`）。
- 偽造頁面內容與 UI（釣魚、信用卡欄位冒名、偽按鈕行為）。
- 在同域/同 Cookie 作用域下，可能進一步發動 CSRF/權限濫用。

---

## 五、修補建議（Mitigations）
> 核心原則：**輸出端編碼（Output Encoding）優先**，搭配 **CSP** 與 **Cookie 強化** 作為第二道防線。

### 1) 伺服器端輸出編碼（PHP 範例）
```php
<?php
$tpl   = $_GET['tpl']   ?? '';
$token = $_GET['token'] ?? '';
$other = $_GET['200']   ?? '';

function esc($s) { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
?>
<p>token: <?= esc($token) ?>, 200: <?= esc($other) ?></p>
<div><?= esc($tpl) ?></div> <!-- 以純文字方式呈現，避免當成 HTML 執行 -->
```

### 2) 前端 DOM 安全 API（避免 `innerHTML`）
```js
// ❌ 避免：out.innerHTML = userInput;
const out = document.getElementById('out');
out.textContent = userInput; // ✅ 只插入文字節點
```

### 3) 設定 Content Security Policy（CSP）
> 不能取代輸出編碼，但可大幅降低利用成功率。
```
Content-Security-Policy: \
  default-src 'self'; \
  script-src 'self' 'nonce-<RANDOM_NONCE>'; \
  object-src 'none'; \
  base-uri 'self'; \
  frame-ancestors 'self'; \
  upgrade-insecure-requests;
```
- 移除 `unsafe-inline`；對必需的 inline script 使用 `nonce`。

### 4) Cookie 強化
```
Set-Cookie: session=...; HttpOnly; Secure; SameSite=Lax; Path=/; Domain=.sju.edu.tw
```
- `HttpOnly` 防止 JS 讀取；`SameSite` 降低跨站請求風險；`Secure` 僅透過 HTTPS 傳輸。

### 5) 輸入驗證（輔助）
若 `tpl` 僅應為純文字，建議實作 **允許清單**（只允許字母、數字、常見符號），超出直接拒絕或轉成純文字。

---

## 六、驗證修補完成的清單（QA Checklist）
- [ ] 下列 payload 在修補後僅以文字顯示，不會彈窗：
  - `?tpl=%3Csvg%20onload%3Dalert(1)%3E`
  - `?tpl=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E`
  - `?tpl=%22%3E%3Csvg%20onload%3Dalert(1)%3E`
- [ ] 檢視原始碼/Network Response，確認 `<`、`>`、`"`、`'` 皆被 HTML 編碼（如 `&lt;`、`&gt;`）。
- [ ] 前端未以 `innerHTML` 注入來自 `tpl` 的字串（或有嚴格 sanitizer/白名單）。
- [ ] 回應標頭含 CSP，Console 無違規訊息；重要 Cookie 具 `HttpOnly/Secure/SameSite`。

---


## 附錄 A：常用 PoC Payload（皆為非破壞性）
```
<script>alert(1)</script>
<svg onload=alert(1)>
<img src=x onerror=alert(1)>
<img src=x onerror=prompt(document.domain)>
"><svg onload=alert(1)>
```
> 使用時請確保已對 `< > " 空白` 等字元做 URL 編碼。

---