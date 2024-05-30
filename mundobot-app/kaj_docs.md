## Cíl projektu
Cílem projektu bylo vytvořit ovládací panel pro discord bota. Potřeba pro to vznikla ve chvíli, kdy jsem chtěl přidat možnost 
nahrávat vlastní zvuky uživatelům bota. Předcchozí možnost zahrnující posílání linků na Google Drive a následné stahování a 
ukládání z něj se ukázala velmi nepraktická. Hlavním účelem aplikace je tedy zobrazovat, přehrávat, stahovat, přidávat a 
odstraňovat zvukové soubory. Ty jsou pro každý server na kterém je bot přítomný jiné (tedy až na malé množství defaultich zvuků).

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
|CSS transformace|?|2||
|CSS transition/animace|x|2|Přehrávání zvuku, animace po nahrání zvuku|
|Media queries|x|2|Změna při přechodu pod 960px|
|OOP|x|2|React od OOP ustoupil, proto není nikde použito|
|Framework|x|1|Next.js|
|Pokročilá api|x|3|Drag&Drop a File pro nahrání souboru, cookies|
|Historie|x|2|Vyplývá z použití Next.js routingu|
|Offline #2|x|1|-//-|
|JS SVG|x|2|Nemá smysl pro use case|
