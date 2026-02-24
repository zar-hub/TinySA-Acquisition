Il setup consiste in due tinysa: uno trasmette l'altro riceve.
La trasmittente è gestita dall'applicazione tinySA-App.exe, la ricevente dalla liberria tinysa.py da cavo usb.

Per poter controllare anche l'applicazione .exe da python abbiamo usato una libreria che prende il controllo del mouse e della tastiera. Sapendo dove sono i tasti possiamo usare l'applicazione in automatico.

Descrizione files:
- tinysa.py  è la libreria per interfacciarsi con il tinysa via cavo
- tinySA-App.exe  è l'applicazione proprietaria 
- bot.py è il nostro bot che usa sia tinysa.py che tinySA-App.exe per fare le misure in modo automatizzato
- interface_scraping.py è l'applicazione che genera il file di interfaccia per il bot (ad esempio arinstInterface.txt)
- arinstInterface.txt contiene l'interfaccia dell'applicazione tinySA-App.exe. La usa il bot per sapere dove sono i pulsanti da premere

Come usare:
Collegare trasmittente e ricevente al PC.
Aprire tinySA-App.exe e selezionare la trasmittente. Lanciare il bot.py 