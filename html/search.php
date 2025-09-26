<?php
$usr = $_GET['usr'] ?? '';
$q   = $_GET['q'] ?? '';
$db = new PDO("sqlite:/data/bookmarks.db");
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Fetch user mappings
$stmt = $db->prepare("SELECT keyword, url FROM mappings WHERE user_id=?");
$stmt->execute([$usr]);
$list = $stmt->fetchAll(PDO::FETCH_KEY_PAIR);

// Exact match
if (isset($list[$q])) {
    echo "<html><head><meta http-equiv='refresh' content='0;url={$list[$q]}'></head></html>";
    exit;
}

// Fuzzy search
$distances = [];
foreach ($list as $kw => $url) {
    $d = levenshtein($q, $kw);
    $distances[$kw] = $d;
}
asort($distances);
$best = array_keys($distances, reset($distances));

// Configurable error margin: 30% of length
$margin = ceil(strlen($q) * 0.3);
$closest = array_filter($best, function($kw) use ($distances, $margin) {
    return $distances[$kw] <= $margin;
});

if (count($closest) === 1) {
    $url = $list[array_shift($closest)];
    echo "<html><head><meta http-equiv='refresh' content='0;url=$url'></head></html>";
} else {
    echo "<h3>No exact match for “".htmlspecialchars($q)."”. Closest:</h3><ul>";
    foreach (array_slice($closest, 0, 10) as $kw) {
        $u = htmlspecialchars($list[$kw]);
        echo "<li><a href=\"?usr=$usr&q=$kw\">$kw → $u</a></li>";
    }
    echo "</ul>";
}
