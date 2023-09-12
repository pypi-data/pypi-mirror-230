# Password Manager (pw-manager-tool)

Password Manager è un package in Python che permette di gestire le password collegate ai servizi indicati dall'utente. Il programma supporta versioni Python a partire dalla 3.8.x .


# Funzionalità del prodotto

Qui vengono presentate le principali funzionalità del prodotto. Per poter utilizzare qualsiasi funzionalità dell’applicazione, è necessario inserire una master password. Questa viene decisa dall’utente al primo
accesso all’applicazione.

## Aggiungere password associate ad un servizio

L'applicazione permette di associare ad un servizio una password tramite il comando **add NOME_SERVIZIO** da terminale:

    $ pw-manager add esse3
    > Inserire master password
    > Inserire una password per il servizio `esse-3`
    > Password salvata con successo!

## Aggiungere password generate associate ad un servizio

L'applicazione permette di associare ad un servizio una password sicura da 15 caratteri generata proceduralmente tramite il comando **add NOME_SERVIZIO -g** da terminale:

    $ pw-manager add esse3 -g
    > Inserire master password
    > Password generata e salvata con successo!


## Visualizzare una password dato un servizio

L'applicazione permette di visualizzare la password associata ad un servizio tramite il comando **get NOME_SERVIZIO** da terminale:

    $ pw-manager get esse3
    > Inserire master password
    > La password per il servizio `esse3` è: ...

## Rimuovere un servizio

L'applicazione permette di rimuovere un servizio e la password ad esso associata tramite il comando **del NOME_SERVIZIO** da terminale:

     $ pw-manager del esse3
     > Inserire master password
     > Servizio `esse3` eliminato!

## Aggiornare una password

L'applicazione permette di aggiornare la password associata ad un servizio tramite il comando **update NOME_SERVIZIO** da terminale:

    $ pw-manager update esse3
    > Inserire master-password
    > Inserire nuova password per il servizio `esse3`
   
## Visualizzare l'elenco di servizi presenti

L'applicazione permette di visualizzare l'elenco di servizi presenti tramite il comando **list** da terminale:

    $ pw-manager list
    > Inserire master-password
    > Servizi disponibili
    > * esse3
    > * pypi
   
## Esportazione database 

L'applicazione permette di esportare un database con le password ed i servizi ad esso associati tramite il comando **export NOME_DB** da terminale:

    $ pw-manager export passwords.db
    > Inserire master password
    > Database password esportato in `passwords.db`

## Importazione database 
L'applicazione permette di importare un database con le password ed i servizi ad esso associati tramite il comando **import NOME_DB** da terminale:

    $ pw-manager import passwords.db
    > Inserire master password
    > Database password importato da `passwords.db`


# Installazione

Per poter installare il software è necessario eseguire il seguente comando da terminale:

    $ pip install pw-manager-tool

