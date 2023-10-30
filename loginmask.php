<!DOCTYPE html>
<html>
<head>
    <title>Anmeldeformular</title>
</head>
<body>
    <h2>Anmelden</h2>
    <form action="login.php" method="post">
        <label for="benutzername">Benutzername:</label>
        <input type="text" name="benutzername" id="benutzername" required></input>

        <label for="passwort">Passwort:</label>
        <input type="password" name="passwort" id="passwort" required></input>

        <input type="submit" value="Anmelden"></input>
    </form>
</body>
</html>
