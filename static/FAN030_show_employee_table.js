        // Überprüfen, ob das Element vorhanden ist
        function elementExists(id) {
            return document.getElementById(id) !== null;
        }

        // Aufruf mit Default Werten
        document.addEventListener('DOMContentLoaded', function() {
            if (elementExists('monat_jahr_dropdown_m')) {
                ladeDropdownDaten_m('monat_jahr_dropdown_m', 'employee_table_container');
            }
        });

        // Aufruf mit übergebenen Werten
        if (elementExists('anzeigenButton_m')) {
            document.getElementById('anzeigenButton_m').addEventListener('click', function() {
                const gewaehlteKombination = document.getElementById('monat_jahr_dropdown_m').value;
                ladeMitarbeiterDaten_m(gewaehlteKombination);
            });
        }


        // Drop-Down laden
        function ladeDropdownDaten_m() {
            if (!elementExists('employee_table_container')) {
                return;
            }
            fetch('/get_employee_dropdown_data')
                .then(response => response.json())
                .then(kombinationen => {
                    const dropdown = document.getElementById('monat_jahr_dropdown_m');
                    for (let i = kombinationen.length - 1; i >= 0; i--) {
                        const kombination = kombinationen[i];
                        let option = new Option(kombination, kombination);
                        dropdown.add(option);
                    }
                    if(kombinationen.length > 0) {
                        dropdown.value = kombinationen[kombinationen.length - 1];
                        ladeMitarbeiterDaten_m(kombinationen[kombinationen.length - 1]);
                    }
                })
                .catch(error => console.error('Fehler beim Laden der Dropdown-Daten:', error));
        }

        // Tabelle Mitarbeiter laden
        function ladeMitarbeiterDaten_m(kombination) {
             if (!elementExists('employee_table_container')) {
                return;
            }
            const [monatName, jahr] = kombination.split(" ");
            const monatNummer = monatNameZuNummer_m(monatName);

            fetch(`/get_employee_data?monat=${monatNummer}&jahr=${jahr}`)
                .then(response => response.json())
                .then(data_m => {

                    updateTable_m(data_m);
                })
                .catch(error => console.error('Fehler beim Laden der Mitarbeiterdaten:', error));
        }

        // Umwandlung Monatsname in Zahl
        function monatNameZuNummer_m(monatName) {
            const monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
            const index = monate.indexOf(monatName);

            if (index === -1) {
                throw new Error('Ungültiger Monatsname');
            }

            return index + 1;
        }

        // Tabellen mitarbeiter
        function updateTable_m(data) {
            const userRole = document.getElementById('userRole_m').getAttribute('data-role');
            if (!userRole) {
                console.error('Element mit ID "userRole" nicht gefunden');
                return;
            }

            const tableContainer = document.getElementById("employee_table_container");
            const noDataMessage = document.getElementById('no-employee-message');

            let alleZeilenHabenMaxFuenfEintraege = true;
            for (let i = 0; i < data.length; i++) {
                if (data[i].length > 5) {
                    alleZeilenHabenMaxFuenfEintraege = false;
                    break; // Beendet die Schleife, sobald eine Zeile mehr als 3 Einträge hat
                }
            }

            if (data.length > 0) {
                // Check if the data is for unbooked clients
                if (alleZeilenHabenMaxFuenfEintraege) {
                    let messageHTML = '<br><h4>Fehlende Buchungen:</h4><br>';
                    data.forEach(client => {
                        messageHTML += `Einträge für ${client[3]}/${client[4]} und Klient ${client[1]} ${client[2]} noch nicht gebucht.<br>`;
                    });
                    messageHTML += '<br><br><br>';
                    tableContainer.innerHTML = messageHTML;
                } else {
                    if (noDataMessage) {
                        noDataMessage.style.display = 'none';
                    }
                    let tableHTML = `<table id="employeeTable">
                                        <thead>
                                            <tr>
                                                <th>Personalnr.</th>
                                                <th>Nachname</th>
                                                <th>Vorname</th>
                                                <th>geleistete Stunden</th>
                                                <th>gefahrene Kilometer</th>
                                            </tr>
                                        </thead>
                                        <tbody>`;

                    data.forEach(arbeiter => {
                        let km = (arbeiter[4] !== null && arbeiter[4] !== undefined) ? arbeiter[4] : 0.0;
                        let km_formatiert = km.toFixed(1);
                        let sperre = arbeiter[5];


                        console.log(arbeiter)
                        tableHTML += `<tr>
                                        <td>${arbeiter[0]}</td>
                                        <td>${arbeiter[1]}</td>
                                        <td>${arbeiter[2]}</td>
                                        <td>${arbeiter[3]}</td>
                                        <td>${km_formatiert}</td>
                                        <td>
                                            <input type="hidden" name="sperre" value="${sperre}">
                                        </td>`;

                        if (userRole === 'Verwaltung' || userRole === 'Geschäftsführung') {
                            tableHTML += `<td>
                                            <button onclick="window.location.href='/account_details/${arbeiter[0]}'">Details</button>
                                          </td>`;
                        }

                        if (userRole !== 'Steuerbüro') {
                            tableHTML += `<td>
                                            <button onclick="window.location.href='/view_time_entries/${arbeiter[0]}'">Zeiteintrag ansehen</button>
                                          </td>`;
                        }

                        if (userRole === 'Verwaltung' || userRole === 'Geschäftsführung') {
                            tableHTML += `<td>
                                            <button onclick="window.location.href='/edit_account/${arbeiter[0]}'">Bearbeiten</button>
                                          </td>`;
                            if (arbeiter[5] === 0) {
                                tableHTML += `<td>
                                                <button onclick="window.location.href='/account_lock/${arbeiter[0]}'">Sperren</button>
                                             </td>`;
                            } else {
                                tableHTML += `<td>
                                                <button onclick="window.location.href='/account_unlock/${arbeiter[0]}'">Entsperren</button>
                                             </td>`;
                            }
                        }

                        tableHTML += `</tr>`;
                    });

                    tableHTML += `</tbody></table>`;
                    tableContainer.innerHTML = tableHTML;
                }
            } else {
                tableContainer.innerHTML = '';
               if (noDataMessage) {
                   noDataMessage.style.display = 'block';
               }
            }
        }
