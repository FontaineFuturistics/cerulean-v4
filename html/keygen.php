<?php
// Generate 4-char user ID
$chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
$id = '';
for ($i=0;$i<4;$i++) $id .= $chars[random_int(0, strlen($chars)-1)];

// Paths
$tmpDir = sys_get_temp_dir();
$caKey = '/etc/ssl/ca/ca.key.pem';
$caCert = '/etc/ssl/ca/ca.crt.pem';

// Create key and CSR
$keyFile = "$tmpDir/$id.key.pem";
$csrFile = "$tmpDir/$id.csr.pem";
$crtFile = "$tmpDir/$id.crt.pem";

exec("openssl genrsa -out $keyFile 2048");
exec("openssl req -new -key $keyFile -subj \"/CN=$id\" -out $csrFile");
exec("openssl x509 -req -in $csrFile -CA $caCert -CAkey $caKey -CAcreateserial -days 365 -out $crtFile");

// Bundle PKCS#12 for browser import
$pkcs12 = "$tmpDir/$id.p12";
exec("openssl pkcs12 -export -out $pkcs12 -inkey $keyFile -in $crtFile -certfile $caCert -passout pass:");

// Send file
header('Content-Type: application/x-pkcs12');
header("Content-Disposition: attachment; filename=\"$id.p12\"");
readfile($pkcs12);
exit;
