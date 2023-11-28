<?php

define('DB_NAME', 'timecarepro');
define('DB_USER', 'grup3sql');
define('DB_PASSWORD', 'skill59UP86VM');
define('DB_HOST', 'db');

$pdo = new PDO("mysql:host=" . DB_HOST . "; dbname=" . DB_NAME, DB_USER, DB_PASSWORD);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);