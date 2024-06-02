Prosty WebScraper napisany w Pythonie(Flask) w ramach przedmiotu Przetwarzanie równoległe i rozproszone.

Testowane pod systemem Linux Debian 12 (bookworm).

Użyte technologie oraz biblioteki:
- Python(Flask - GUI, matplotlib - wykresy, multiprocessing i asyncio(podział zadań - zrównoleglenie), mpld3 - interaktywne wykresy, beautifulsoup4 - przetwarzanie scrapowanych stron jak i ich parsowanie)
- JavaScript(dodaje do linków https:// jak użytkownik nie doda, zabezpieczenie oraz domyslnie nie rozwija list z wynikami scrapowania)
- MongoDB jako baza danych do przechowywania danych o scrapowanych stronach

Podział na rozproszone kontenery:
- Frontend czyli aplikacja napisana w Flasku zapewniająca GUI i łączy się z silnikiem wykonującym całą robote, dodatkowo tutaj tworzone są wykresy wykorzystując dane z bazy mongo
- Engine czyli silnik, który parsuje scrapowane strony wydzielając z nich: numery telefonów, filmy, obrazy i adresy email
- Parsowanie jest rozproszone efektywnie między rdzeniami procesora, z biblioteki multiprocessing za pomocą funkcji cpu.count jest ladowana ilość rdzeni i procesy ustawiane trafiaja do kolejek, które się nie blokują - multiprocessing.Manager() oraz Quene() - taki sposób umożliwia rozsądne skalowanie i znaczne przyspieszenie działania
- Kontener z MongoDB zawierający obraz bazy danych

Kompatybilność z systemami do konteneryzacji:
- Docker
- Kubernetes

Uruchomienie:
- Na początek trzeba zainstalować przynajmniej dockera oraz kubernetesa(jak ktoś nie chce wykorzystywać kubernetesa to nie jest on koniecznie wymagany) wykorzystując instrukcje z stron: https://kubernetes.io/docs/setup/ oraz https://www.docker.com/get-started/

Docker:
- Po pomyślnej instalacji sklonować repozytorium wykorzystując git clone albo pobrać bezpośrednio
- Przejść do folderu z pobranym repozytorium i wpisać docker-compose up --build -d (komenda ta zaciągnie z internetu potrzebne składniki do kontenerów, zbuduje ich obrazy i je uruchomi)
Aplikacja właśnie powinna być dostępna pod adresemip:5000 - oczywiscie adresemip zastąpić swoim IP a jeśli jest to uruchamiane lokalnie to wystarczy localhost

Kubernetes:

Aby uruchomić aplikacje w kubernetesie to trzeba dodatkowo poza krokami wyżej:

- Zatrzymać uruchomione kontenery w dockerze (docker stop nazwa albo poprzez aplikacje Docker Desktop czy inne)
- Po przejściu do folderu z pobranym repozytorium wpisać w celu załadowania lokalnych obrazów(minikube musi być wcześniej zainstalowany) następujące komendy:

minikube image load projekt_engine:latest

minikube image load projekt_frontend:latest

minikube image load mongo:4.4

Po załadowaniu obrazów należy zastosować pliki yaml, aby stworzyły się usługi na bazie obrazów zbudowanych z dockera wykorzystując:

kubectl apply -f frontend-deployment.yaml

kubectl apply -f engine-deployment.yaml

kubectl apply -f mongodb-deployment.yaml

Nie można zapomnieć o uruchomieniu wcześniej kubernetesa wykorzystując minikube start (ewentualnie z flaga --listen-address=0.0.0.0 aby słuchało na każdym interfejsie sieciowym, nie tylko na localhost)

Gotowe, po wejściu w adres IP poda stworzonego przez kubernetes(kubectl get services) i wygenerowaniu adresu proxy można uruchomić aplikacje
W razie jakby ktoś potrzebował uruchomić to w lokalnej sieci to trzeba wykorzystać port forwarding wraz z listen-address 0.0.0.0, wiecej informacji tutaj: https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/

