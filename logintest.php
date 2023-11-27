<?php

// Verbindung zur Datenbank
$servername = "db";
$username = "grup3sql";
$password = "skill59UP86VM";
$dbname = "timecarepro";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Verbindung fehlgeschlagen: " . $conn->connect_error);
}

// Klasse Benutzer
class Benutzer {
    private $email;
    private $passwort;

    public function __construct($email, $passwort) {
        $this->email = $email;
        $this->passwort = $passwort;
    }

    public function istEmailUndPasswortGueltig() {
        global $conn;
        $hashed_passwort = sha1($this->passwort);
        $sql = "SELECT id FROM person WHERE email = ? AND passwort = UNHEX(?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ss", $this->email, $hashed_passwort);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            return true;
        } else {
            return false;
        }
    }
}

// Nutzerdaten einlesen
$email = $_POST['email'];
$passwort = $_POST['passwort'];

// Objekt der Klasse Benutzer erstellen
$benutzer = new Benutzer($email, $passwort);

// Prüfung des Benutzernamens und Passworts
if ($benutzer->istEmailUndPasswortGueltig()) {
    echo "Anmeldung erfolgreich!";
} else {
    echo "Anmeldung fehlgeschlagen! Bitte überprüfen Sie Ihre Email und Passwort.";
}

$conn->close();