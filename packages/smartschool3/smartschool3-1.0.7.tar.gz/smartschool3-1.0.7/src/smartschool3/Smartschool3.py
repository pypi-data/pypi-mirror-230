import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class Smartschool3:
    def __init__(self, email, password):
        # Je inloggegevens van Smartschool
        self.email = email
        self.password = password

        # De session id om ons te kunnen laten identificeren door Smartschool
        self.sessionId = ''

        # Een sessie die de cookies bijhoudt
        self.session = ''

    # De basis van een request naar viio.smartschool.be
    def _send_request(self, path, method, payload):

        # De request verzenden
        req = self.session.request(method, "https://viio.smartschool.be" + path, data=payload, allow_redirects=True)

        # De response in een HTML-string
        body = req.text

        return body

    def _retrieve_session_id(self):
        # Onze ssion voor de cookies resetten
        self.session = requests.Session()

        # De generation time, token en de session id verkrijgen
        login_page = self._send_request("/login", "GET", "")

        # Een DOM object maken van de HTML string met de bs4 library
        html_doc = BeautifulSoup(login_page, "lxml")

        # De generation time en token declareren
        generation_time = html_doc.find(id="login_form__generationTime")['value']
        token = html_doc.find(id="login_form__token")['value']

        # De payload opbouwen
        payload = {
            "login_form[_username]": self.email,
            "login_form[_password]": self.password,
            "login_form[_generationTime]": generation_time,
            "login_form[_token]": token
        }

        # Inloggen op Smartschool, zodat de cookies kunnen worden geupdated
        self._send_request("/login", "POST", payload)

    def agenda(self, aantalWekenVerder):
        # De session id updaten
        self._retrieve_session_id()

        # De datum van maandag
        vandaag = datetime.now()
        dagen_voor_maandag = vandaag.weekday()
        if dagen_voor_maandag == 0:
            dagen_voor_maandag = 7
        maandag = vandaag - timedelta(
                                        days=dagen_voor_maandag,
                                        hours=vandaag.hour,
                                        minutes=vandaag.minute,
                                        seconds=vandaag.second,
                                        microseconds=vandaag.microsecond
                                      )

        # De tijd verder zetten, als de gebruiker de agenda van een andere week zou willen
        maandag = maandag + timedelta(weeks=aantalWekenVerder)

        # De datum van zondag
        zondag = maandag + timedelta(days=6)

        """ De timestamp in seconden voor beide datums
        (De Smartschool API accepteerd alleen timestamps in seconden) """
        timestampMaandag = int(maandag.timestamp())
        timestampZondag = int(zondag.timestamp())

        # De agenda opvragen
        body = self._send_request("/index.php?module=Agenda&file=dispatcher", "POST", {
            "command":
                f"""
                <request>
                    <command>
                        <subsystem>agenda</subsystem>
                        <action>get lessons</action>
                        <params>
                            <param name="startDateTimestamp"><![CDATA[{timestampMaandag}]]></param>
                            <param name="endDateTimestamp"><![CDATA[{timestampZondag}]]></param>
                            <param name="filterType"><![CDATA[false]]></param>
                            <param name="filterID"><![CDATA[false]]></param>
                            <param name="gridType"><![CDATA[2]]></param>
                            <param name="classID"><![CDATA[0]]></param>
                            <param name="endDateTimestampOld"><![CDATA[{timestampZondag}]]></param>
                            <param name="forcedTeacher"><![CDATA[0]]></param>
                            <param name="forcedClass"><![CDATA[0]]></param>
                            <param name="forcedClassroom"><![CDATA[0]]></param>
                            <param name="assignmentTypeID"><![CDATA[1]]></param>
                        </params>
                    </command>
                </request>
                """
        })

        # Een XML DOM object maken van de agenda
        agenda = BeautifulSoup(body, "xml")

        # De dictionary waar we alle informatie over alle lessen gaan opslaan
        lessen_info = {
            0: {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}},
            1: {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}},
            2: {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}},
            3: {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}},
            4: {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}}
        }

        # De lessen uit het XML document halen
        lessen = agenda.find_all('lesson')

        # Een dictionary dat een "hourID" kan omzetten naar een index van ["0" (lesuur 1)] tot ["8" (lesuur 8)]
        hour_id_naar_index = {
            "152": 0,
            "154": 1,
            "156": 2,
            "158": 3,
            "160": 4,
            "162": 5,
            "164": 6,
            "166": 7,
            "168": 8
        }

        # Voor alle lessen
        les_counter = 0
        for les in lessen:
            # De juiste index voor het "lessenInfo" object bepalen
            dag_van_de_week = datetime.strptime(les.find("date").text, "%Y-%m-%d").weekday()
            uur_index = hour_id_naar_index[les.find("hourID").text]

            # Alle nodige informatie over deze les aan de "lessen_info" dictionary toevoegen
            lessen_info[dag_van_de_week][uur_index] = {
                "datum": les.find("date").text,
                "lesuur": les.find("hour").text,
                "titel": les.find("courseTitle").text,
                "klasNaam": les.find("klassenTitle").text,
                "leerkracht": les.find("teacher").text,
                "klasLokaal": les.find("classroomTitle").text,
                "opdrachten": { # Deze informatie moet nog opgehaald worden
                    "taken": [],
                    "toetsen": [],
                    "aankondigingen": []
                }
            }

            # De opdrachten en notities ophalen
            body = self._send_request("/index.php?module=Agenda&file=dispatcher", "POST", {
                "command":
                    f"""
                    <request>
                        <command>
                            <subsystem>agenda</subsystem>
                            <action>show form</action>
                            <params>
                                <param name="momentID"><![CDATA[{les.find("momentID").text}]]></param>
                                <param name="lessonID"><![CDATA[{les.find("lessonID").text}]]></param>
                                <param name="classIDs"><![CDATA[{les.find("classIDs").text}]]></param>
                                <param name="filterType"><![CDATA[false]]></param>
                                <param name="filterID"><![CDATA[false]]></param>
                                <param name="dateID"><![CDATA[]]></param>
                                <param name="assignmentIDs"><![CDATA[]]></param>
                                <param name="activityID"><![CDATA[0]]></param>
                                <param name="gridType"><![CDATA[2]]></param>
                                <param name="tab_to_show"><![CDATA[0]]></param>
                                <param name="show_assignment"><![CDATA[0]]></param>
                            </params>
                        </command>
                    </request>
                    """
            })

            # Een XML DOM object maken voor de opdrachten en notities
            opdrachten_en_notities = BeautifulSoup(body, "xml")

            # De opdrachten uit het XML document halen
            opdrachten = opdrachten_en_notities.find_all("assignment")

            # Een dictionary dat een "type" kan omzetten naar de soort van de opdracht
            type_naar_soort_opdracht = {
                "0": "taken",
                "1": "toetsen",
            }

            # Voor alle opdrachten
            for opdracht in opdrachten:
                # Taak of toets
                opdracht_soort =  type_naar_soort_opdracht[opdracht.find("type").text]

                # Aankondiging of niet
                if opdracht.find("startAssignment").text == '1':
                    opdracht_soort = 'aankondigingen'

                # Alle nodige informatie over deze les aan de "lessenInfo.opdrachten" array toevoegen
                lessen_info[dag_van_de_week][uur_index]["opdrachten"][opdracht_soort].append({
                    "beschrijving": opdracht.find("description").text
                })

            les_counter += 1

        return lessen_info