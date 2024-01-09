        // Aufruf mit Default Werten
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Hallo')
            ladeDropdownDaten_k('monat_jahr_dropdown_k','client_table_container');
            console.log('Hi')
        });

        // Aufruf mit übergebenen Werten
        document.getElementById('anzeigenButton_k').addEventListener('click', function() {
            const gewaehlteKombination = document.getElementById('monat_jahr_dropdown_k').value;
            ladeKlientenDaten_k(gewaehlteKombination);
        });

        // Drop-Down laden
        function ladeDropdownDaten_k() {
            console.log('Im here')
            fetch('/get_client_dropdown_data')
                .then(response => response.json())
                .then(kombinationen => {
                    const dropdown = document.getElementById('monat_jahr_dropdown_k');
                    for (let i = kombinationen.length - 1; i >= 0; i--) {
                        const kombination = kombinationen[i];
                        let option = new Option(kombination, kombination);
                        dropdown.add(option);
                    }
                    if(kombinationen.length > 0) {
                        dropdown.value = kombinationen[kombinationen.length - 1];
                        ladeKlientenDaten_k(kombinationen[kombinationen.length - 1]);
                    }
                })
                .catch(error => console.error('Fehler beim Laden der Dropdown-Daten:', error));
        }

        //Tabellen laden
        function ladeKlientenDaten_k(kombination) {
            const [monatName, jahr] = kombination.split(" ");
            const monatNummer = monatNameZuNummer_k(monatName);


            fetch(`/get_clients_data?monat=${monatNummer}&jahr=${jahr}`)
                .then(response => response.json())
                .then(data => {
                    updateTable_k(data);
                })
                .catch(error => console.error('Fehler beim Laden der Klientendaten:', error));
        }

        // Umwandlung Monatsname in Zahl
        function monatNameZuNummer_k(monatName) {
            const monate = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
            const index = monate.indexOf(monatName);

            if (index === -1) {
                throw new Error('Ungültiger Monatsname');
            }

            return index + 1;
        }

        // Tabellen Layout und Einfügen Daten
        function updateTable_k(data) {
            const userRole = document.getElementById('userRole').getAttribute('data-role');
            const tableContainer = document.getElementById("clients_table_container");
            const noDataMessage = document.getElementById('no-clients-message');
            if (data.length > 0) {
                if (noDataMessage) {
                    noDataMessage.style.display = 'none';
                }
                let tableHTML = `<table>
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Nachname</th>
                                            <th>Vorname</th>
                                            <th>Fachkraftkontingent</th>
                                            <th>Hilfskraftkontingent</th>
                                            <th>Fachkraftsaldo</th>
                                            <th>Hilfskraftsaldo</th>
                                            <th>Fallverantwortung</th>
                                        </tr>
                                    </thead>
                                    <tbody>`;

                data.forEach(client => {
                    tableHTML += `<tr>
                                    <td>${client[0]}</td>
                                    <td>${client[2]}</td>
                                    <td>${client[1]}</td>
                                    <td>${client[3]}</td>
                                    <td>${client[4]}</td>
                                    <td>${client[5]}</td>
                                    <td>${client[6]}</td>
                                    <td>${client[7]}</td>`;

                    if (userRole === 'Verwaltung' || userRole === 'Geschäftsführung') {
                        tableHTML += `<td>
                                        <button onclick="window.location.href='/client_details/${client[0]}'">Details</button>
                                      </td>`;
                    }

                    if (userRole === 'Sachbearbeiter/Kostenträger'){
                        tableHTML += `<td>
                                        <button onclick="window.location.href='/access_hours_km_clients/${client[0]}'">Zeiteintrag ansehen</button>
                                      </td>`;
                    }
                    else {
                        tableHTML += `<td>
                                        <button onclick="window.location.href='/client_supervision_hours/${client[0]}'">Zeiteintrag ansehen</button>
                                      </td>`;
                    }

                    if (userRole === 'Verwaltung' || userRole === 'Geschäftsführung') {
                        tableHTML += `<td>
                                        <button onclick="window.location.href='/edit_client/${client[0]}'">Bearbeiten</button>
                                      </td>`;
                    }

                    tableHTML += `</tr>`;
                });

                tableHTML += `</tbody></table>`;
                tableContainer.innerHTML = tableHTML;
            } else {
                tableContainer.innerHTML = '';
                if (noDataMessage) {
                    noDataMessage.style.display = 'block';
                }
            }
        }
