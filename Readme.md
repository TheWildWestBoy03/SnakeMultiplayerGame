### Nume: Pogan Alexandru-Mihail 

Taskuri implementate:
1) Sarpele este de lungime de 4. Acest lucru este asigurat de generarea initiala a acestuia, in server-side, precum si de strategia implementata in 
cadrul serverului, prin care in cadrul rezolvarii unei cereri de tip MOVE, se scoate in general coada sarpelui si se calculeaza noul cap, mai putin in cazul
in care directia dorita este opusa ultimei directii.
2) Generarea si consumul de fructe se realizeaza de catre server, insa randarea se realizeaza tot de catre client. Acesta din urma transmite o cerere de tipul
GET_FRUITS, prin care obtine toate fructele existente in joc. Ca sa nu se spawneze prea multe fructe, am convenit ca rata de spawn sa fie de 0.5%. Serverul gestioneaza
consumul fructelor prin verificarea coliziunilor intre fructele generate in joc si capetele celor doi serpi, in cadrul requestului de MOVE. Atunci cand coliziunea se
realizeaza, fructul este sters din lista fructelor si serverul atribuite scorul aferent fructului, conform expeditorului cererii de MOVE.
3) Cand serpii se ciocnesc de pereti(in cazul meu, peretii sunt incadrati in chenarul ecranului, din motive de simplitate), atunci se termina jocul, serverul
inchizand conexiunile cu clientii, afisandu-se totodata un mesaj sugestiv cu cine a castigat si cine a pierdut.
4) Exista un mesaj transmis de tip LOGIN, in care jucatorii transmit tokenul lor de login, pentru a fi verificat de server. O observatie importanta este faptul ca in
momentul in care unul din jucatori nu se poate loga, atunci meciul se inchide, iar celalalt jucator castiga din oficiu. De asemenea, logarea nu se realizeaza la run time,
clientii avand la dispozitie token-urile direct din cod. Totusi, verificarea token-ului pe server se realizeaza corect.
5) Exista un mesaj transmis de tip START_GAME, prin care jucatorii cer serverului sa le puna la dispozitie tipul de input. By default, jocul se bazeaza pe input
continuu, adica daca nu apesi pe nimic, serpii nu se misca.
6) Mesajul de trimitere a inputului este de tip MOVE
7) Orice mesaj de input are si un raspuns din partea serverului, cu pozitiile aferente serpilor actualizate.
8) Jocul functioneaza pe 30 de frame-uri pe secunda. Acest lucru este posibil prin setarea unui pygame clock pe 30, lucru realizat in client, deoarece acesta este
cel care randeaza graficele.
9) Jocul ofera suport pentru fix doi clienti. Acestia nu se pot misca unul peste celalalt, fiind blocanti.

Instalare joc:
1) Clonati repository-ul
2) Folositi orice IDE/Editor, pentru a accesa codul.
3) Asigurati-va ca aveti instalat Python, versiunea >3, precum si modul pygame.(pip install pygame)
4) Rulati prima data serverul. (python3 server.py)
5) Rulati ulterior clientul. (python3 client.py)