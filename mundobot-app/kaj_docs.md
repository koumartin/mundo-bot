## Cíl projektu
Cílem projektu bylo vytvořit ovládací panel pro discord bota. Potřeba pro to vznikla ve chvíli, kdy jsem chtěl přidat možnost 
nahrávat vlastní zvuky uživatelům bota. Předcchozí možnost zahrnující posílání linků na Google Drive a následné stahování a 
ukládání z něj se ukázala velmi nepraktická. Hlavním účelem aplikace je tedy zobrazovat, přehrávat, stahovat, přidávat a 
odstraňovat zvukové soubory. Ty jsou pro každý server na kterém je bot přítomný jiné (tedy až na malé množství defaultich zvuků).

## Použití
Aplikace aktuálně běží na mém serveru na adrese `http://185.186.65.20:3000` přičemž http API běží na `http://185.186.65.20:8000`. 
Pro přihlášení je možné použít můj testovací discord účet - údaje v odevzdávacím formuláři. Po přihlášení je možné vidět celou aplikaci, 
vybrat server a přejít do záložky Sounds > Manage. Tam je možné vidět všechny dostupné zvuky a spravovat je. Add lze použít na otevření 
dialogu k přidání nového zvuku. Všechny zvuky se ukádají do MongoDb a jsou dostupné okamžitě i discord botovi. K tomu stačí do libovolného
kanálu na zvoleném serveru napsat `!list_sounds` k zobrazení dostupných zvuků, popřípadě `play_sound {název} {počet=1}` k přehrání.

## Scháma fungování
Jednotlivá bloky aplikace fungují podle následujícího schámatu:  
![diagram](diagram.png)

## Popis implementovaných požadavků
|Název|Splněno|Body|Poznámky|
|---|---|---|---|
|Dokumentace|x|1||
|Validita|x|1||
|Validita|x|2||
|Sémantické značky|x|1|Použita UI knihovna PrimeReact, která značky nepoužívá ale má Aria lables|
|Grafika|x|2|Ikona hudby - vlastní SVG|
|Média|x|1||
|Validace|x|2|Validace zadanéhho názvu a typu nahraného souboru|
|Offline|x|1|Kontrola připojení a případné zobrazení hlášky, když by se měl odeslat request|
|Pokročilé selektory|x|1||
|Vendor|x|1|Automaticky - PostCSS v Next.js|
|CSS transformace|x|2|Součástí animace|
|CSS transition/animace|x|2|Přehrávání zvuku, animace po nahrání zvuku|
|Media queries|x|2|Změna při přechodu pod 960px|
|OOP|x|2|React od OOP ustoupil, proto není nikde použito|
|Framework|x|1|Next.js|
|Pokročilá api|x|3|Drag&Drop a File pro nahrání souboru, cookies|
|Historie|x|2|Vyplývá z použití Next.js routingu|
|Offline #2|x|1|-//-|
|JS SVG|x|2|Nemá smysl pro use case|

Celkem: 36  

### Věci navíc:  
- Implementace OAuth2 přihlášení přes poskytovatele Discord za použití NextAuth
- Session mezi klientem a http serverem za použití JWT
- Pokus o mírné využití nejnovějších technologii Next.js jako je Serverside rendering 
