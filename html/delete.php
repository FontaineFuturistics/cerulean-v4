<?php
$db = new PDO("sqlite:/data/bookmarks.db");
$userId = null;
if (preg_match('/CN=([A-Za-z0-9]{4})/', $_SERVER['SSL_CLIENT_S_DN'] ?? '', $m)) {
    $userId = $m[1];
}
if ($userId && isset($_GET['kw'])) {
    $db->prepare("DELETE FROM mappings WHERE user_id=? AND keyword=?")
       ->execute([$userId, $_GET['kw']]);
}
header("Location: /");
