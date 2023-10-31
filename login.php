<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $benutzername = $_POST["benutzername"];
    $passwort = $_POST["passwort"];

    // Hier können Sie die Benutzerauthentifizierung implementieren
    // Zum Beispiel, eine Datenbankabfrage, um Benutzerdaten zu überprüfen

    // Wenn die Authentifizierung erfolgreich ist, leiten Sie den Benutzer auf eine Erfolgsseite weiter
    if ($passwort/* Bedingung für erfolgreiche Anmeldung */) {
        header("Location: Inteltest.html");
        exit;
    } else {
        echo "Anmeldung fehlgeschlagen. Bitte überprüfen Sie Ihre Anmeldeinformationen.";
    }
}
?>
