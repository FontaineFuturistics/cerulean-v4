<?php
// Paths and DB
$dbFile = '/data/bookmarks.db';
if (!file_exists(dirname($dbFile))) {
    mkdir(dirname($dbFile), 0700, true);
}
$pdo = new PDO("sqlite:$dbFile");
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
// Initialize tables
$pdo->exec("
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS mappings (
    user_id TEXT,
    keyword TEXT,
    url TEXT,
    PRIMARY KEY (user_id, keyword),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  );
");

$clientDn = $_SERVER['SSL_CLIENT_S_DN'] ?? '';
$clientVerify = $_SERVER['SSL_CLIENT_VERIFY'] ?? 'NONE';

// No cert presented: offer generation
if ($clientVerify !== 'SUCCESS') {
    echo '<h2>Create Your Identity Certificate</h2>';
    echo '<form method="post" action="keygen.php">';
    echo '<button type="submit">Download Certificate</button>';
    echo '</form>';
    exit;
}

// Extract user ID from cert CN
preg_match('/CN=([A-Za-z0-9]{4})/', $clientDn, $m);
$userId = $m[1] ?? null;

// If user not in DB, register
if ($userId && !$pdo->query("SELECT 1 FROM users WHERE id='$userId'")->fetch()) {
    $pdo->prepare("INSERT INTO users (id) VALUES (?)")->execute([$userId]);
}

echo "<h2>Welcome, User $userId</h2>";
echo '<h3>Your Mappings</h3>';
$mappings = $pdo->prepare("SELECT keyword, url FROM mappings WHERE user_id=? ORDER BY rowid DESC");
$mappings->execute([$userId]);

echo '<form method="post" action="index.php">';
echo 'Keyword: <input name="keyword" required> ';
echo 'URL: <input name="url" required> ';
echo '<button type="submit">Add Mapping</button>';
echo '</form>';

if ($_SERVER['REQUEST_METHOD']==='POST' && $_POST['keyword']) {
    $pdo->prepare("INSERT OR REPLACE INTO mappings (user_id,keyword,url) VALUES (?,?,?)")
        ->execute([$userId, $_POST['keyword'], $_POST['url']]);
    header("Location: /");
    exit;
}

echo '<ul>';
foreach ($mappings as $row) {
    $k = htmlspecialchars($row['keyword']);
    $u = htmlspecialchars($row['url']);
    echo "<li>$k → <a href=\"$u\" target=\"_blank\">$u</a> ";
    echo "<a href=\"delete.php?kw=$k\"><img src=\"trash.png\" alt=\"Del\" width=\"16\"></a></li>";
}
echo '</ul>';
