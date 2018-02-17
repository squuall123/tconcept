    Chargement du fichier utilisateur contenant les numéros de badges depuis le réseau (voir exemple fichier excel)

    Quel méthode de rapatriement ? (http/ftp/ssh) ? disque reseau partagé sous windows type SMB:// xxxxxx

    Ecran invité, attente d'un scan (du point de vue soft on attends une entrée clavier, caractère de fin de saisie ? Return ?) automatique un "return" est envoyer par le lecteur code barre en fin de chaîne je crois que c'est chr(13)

    Si utilisateur pas dans la liste alors affichage d'un écran d'erreur et retour écran d'accueil  exacte,... affichage "utilisateur non autorisé" ou "utilisateur non inscrit"

    Attente scan de la réference du faisceaux à tester idem que pour le user pour les messages "référence non trouvée" ou "fichier manquant" si pas les 2 fichiers presents

    affichage avec le nom du programme actif (à récupérer dans le fichier de config xxx.txt) et transfert du programme vers la carte

    Attente confirmation utilisateur ou début de test ? le test est lancer par une entrée logique du raspberry (GPIO 0)

    Chargement des points à tester depuis le fichier CSV (deja realiser à l'etape 4)

    Message d'erreur si fichier inexistant

    Vider liste préalable dans le contrôleur  operation a effectuer avant d'envoyer le programme

    Envoie courant test et seuil de continuité info contenu dans le fichier de configuration xxx.txt

    Où se trouve ces infos ? sous forme de nom de variable type AAAAA = 123

    Envoie de la liste des points à tester (pour l'instant seul mode mais il faudra regarder le type de test à effectuer) liste à envoyer etape 4 prevoir les differents mode de test (nous testerons dans un premier temps uniquement la continuité)

    Envoie de la commande de test (TC start chk) suite appuie sur GPIO 0

    si programme de test complet et sans erreurs lancer l'impression de l'étiquette (chaine de caractere ZPL dans le fichier xxx.txt) on vous envoie un fichier exemple

11 l'utilisateur scan le code barre imprimé de l'etiquette ("affichage attente de controle etiquette")
12 le programme se remet en attente de l'entrée GPIO 0 pour relancer un test


13 si le programme de test trouve un défaut
( signaler l'info à l’opérateur avec les commentaires contenu dans le fichier CSV)

    boucler sur les défauts jusqu’à suppression de tous les défauts et ou si l’opérateur scanne le code "ANNULATION"


14 remise a zero (LOG OFF) en scannant le code "LOG OUT"
nota : au demarrage du raspberry on demande le code utilisateur

15 operation de debug et maintenance

    au cours du cycle ou au demarrage si le code d'un responsable ou maintenance est entré une fenêtre de debug apparait dans un coin pour visualiser tous les echanges de UART.



16 Pour la gestion de l'UART:

    Gestion des retours erreur de la carte et affichage en conséquence ok voir 13

    Suivant le type d'erreur: impression sur l'imprimante on imprime sur imprimante que si le test est complet

    Timeout sur la ligne si pas de réponse oui en cas de non reponse de la carte après 2 secondes afficgher un erreur ("defaut de communication")

    Essais de renvoyer une fois et affichage d'erreur si ne répond pas une fois seulement


17 De manière générale:

    Prévoir un mode log pour le surveiller l'état du programme. oui voir 15

    Générer un fichier type csv avec les données clefs voir exemple






# Jusqu'ici pour moi c'est le programme de base sur lequel je travaillerai en priorité et que je m'engage à vous livrer sous 5 jours

# Ici ce sont les options sur lesquels je travaillerai dans un deuxième temps

    Si erreur dans le test de continuité, affichage par LED ok

    prévoir un espace pour le test de résistance et de diodeok

    Afficher les commentaires sur le compte rendu imprimante en cas d'erreur ok
