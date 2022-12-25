import pygame 
import os 
import socket
import pickle
import threading
import time


pygame.init()

White = (255,255,255)
Gri = (225, 223, 240)
Red = (255, 0, 0)
Blue =(0, 0, 255)
Green =(0, 150, 0)
Yellow = (255,255,0)
Orange = (255, 150, 0)
Purple = (150, 0, 255)
Pink = (255, 0, 255)
Cyan = (60, 160, 255)
Light_Green = (0, 255, 0)
Player_Colors = [White,Blue,Red,Green,Yellow,Orange,Purple,Pink,Cyan]

HEADERSIZE = 10
SPACE = "          "
Font = pygame.font.Font(None, 30)

run = True
timer = 120

Confirmatii_timer = 0


#De stiut map_position este un nr de la 1 la 4 care reprezinta ce pozitie ii apartine acestei instante pe harta
def gameplay (WIN,WIDTH,HEIGHT,FPS,Role,Connection,playeri,Pozitie,CLIENTS,Coduri_pozitie_client,map_name,map_position) :
    global run
    global timer 
    global Confirmatii_timer


    WIN.fill((255,255,255))
    pygame.display.update()

    #adresa pentru txt-ul hartii pe care se afla playeri
    map_adres = "Maps\info" + map_name + ".txt"


    def draw_window () :

        #desenarea Ui - ului 
        #Partea de sus
        pygame.draw.rect(WIN,(225, 223, 240),(0,0,WIDTH,HEIGHT/25))
        pygame.draw.rect(WIN,(0, 0, 0),(0,HEIGHT/25,WIDTH,5))
        #turn part
        pygame.draw.rect(WIN,Player_Colors[playeri[Whos_turn][1]],((WIDTH-260)/2,0,260,HEIGHT*2/25 + 5))
        pygame.draw.rect(WIN,(225, 223, 240),((WIDTH-250)/2,0,250,HEIGHT*2/25 ))
        text = Font.render(playeri[Whos_turn][0]+"'s TURN", True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2,20)
        WIN.blit(text,text_rect)
        text = Font.render("Timer: "+("  "+str(timer))[-3:], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (WIDTH/2,60)
        WIN.blit(text,text_rect)
        
        pygame.display.update()

    #Functia cu care serverul asculta pentru mesajele unui client
    def reciev_thread_from_client(client,cod) :
        global Confirmatii_timer
        try :
            while True :
                header = client.recv(10)
                header = header.decode("utf-8")
                if len(header) != 0 :
                    data_recv = client.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    #se va proceseaza mesajul de la clinet
                    if data_recv[0] == "timer is zero" :
                        Confirmatii_timer = Confirmatii_timer + 1
                else :
                    client.close()
                    Killed_Clients.append(cod)
                    break
        except :
            client.close()
            Killed_Clients.append(cod)

    #Functia clientului care asculta pentru mesaje de la server
    def reciev_thread_from_server(server) :
        global run
        try :
            while True :
                header = server.recv(10)
                header = header.decode("utf-8")

                if len(header) != 0 :
                    data_recv = server.recv(int(header))
                    data_recv = pickle.loads(data_recv)
                    if data_recv[0] == "I_died...Fuck_off":
                        server.close()
                        run = False
                        break
                    else :
                        Changes_from_server.append(data_recv)
                else :
                    server.close()
                    run = False
                    break
        except :
            server.close()
            run = False

    #Un thread care va functiona la host care are rolul sa tina cont de cat timp trece in timpul jocului
    def timer_thread ():
        global timer
        while True :
            time.sleep(1)
            if timer > 0 :
                timer = timer - 1
                Transmit_to_all.append((("a second passed",None),None))

    #variabilele necesare indiferent de rol
    Whos_turn = 0
    turn_time = 30
    timer = turn_time
    # Incarcarea variabilelor necesare rolurilor de host si client
    if Role == "host" :
        Confirmatii_timer = 0
        Client_THREADS = []
        Killed_Clients = []
        Transmit_to_all = []
        #restart listening threads
        for i in range(len(CLIENTS)) :
            newthread = threading.Thread(target = reciev_thread_from_client , args =(CLIENTS[i][0],CLIENTS[i][1]))
            Client_THREADS.append(newthread)
            Client_THREADS[len(Client_THREADS)-1].start() 
        time_thread = threading.Thread(target = timer_thread)
        time_thread.start() 
    else :
        #restart listenig to the server
        recv_from_server = threading.Thread(target = reciev_thread_from_server, args = (Connection,))
        recv_from_server.start()
        Changes_from_server = []
        timer_notification_sent = False
        next_turn = False


    clock = pygame.time.Clock()
    run=True
    while run == True :
        clock.tick(FPS)
        #afiseaza totul
        draw_window()

        #se actualizeaza variabilele care au legatura cu comunicarea dintre server si client
        if Role == "host":
            # se verifica daca un player sa deconectat 
            while len(Killed_Clients) > 0 :
                Transmit_to_all.append((("leftplayer",Coduri_pozitie_client[Killed_Clients[0]] + 1),None))
                CLIENTS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                playeri.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
                #modificarea turelor
                if Whos_turn == Coduri_pozitie_client[Killed_Clients[0]] + 1 :
                    timer = turn_time
                    Whos_turn += 1
                    if Whos_turn >= len(playeri) :
                        Whos_turn = 0
                elif Whos_turn > Whos_turn == Coduri_pozitie_client[Killed_Clients[0]] + 1 :
                    Whos_turn -= 1
                Client_THREADS[Coduri_pozitie_client[Killed_Clients[0]]].join()
                Client_THREADS.pop(Coduri_pozitie_client[Killed_Clients[0]])
                Coduri_pozitie_client.pop(Killed_Clients[0])
                #reactualizare in dictionarul clientilor si pozitiile lor
                for i in Coduri_pozitie_client :
                    if Coduri_pozitie_client[i] > Killed_Clients[0] :
                        Coduri_pozitie_client[i] -= 1 
                Killed_Clients.pop(0)
            #Se verifica daca este ceva de transmis la ceilalti playeri
            while len(Transmit_to_all) > 0 :
                data_send = pickle.dumps(Transmit_to_all[0][0])
                data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                for i in range(len(CLIENTS)) :
                    if Transmit_to_all[0][1] == None or Coduri_pozitie_client[Transmit_to_all[0][1]] != i  :
                        CLIENTS[i][0].send(data_send)
                Transmit_to_all.pop(0)
        else :
            #Se verifica daca serverul a trimis lucruri spre acest client
            while len(Changes_from_server) > 0 :
                if Changes_from_server[0][0] == "leftplayer" :
                    playeri.pop(Changes_from_server[0][1])
                    if Whos_turn == Changes_from_server[0][1] :
                        timer = turn_time
                        Whos_turn += 1
                        if Whos_turn >= len(playeri) :
                            Whos_turn = 0
                    elif Whos_turn > Whos_turn == Changes_from_server[0][1] :
                        Whos_turn -= 1
                    if Changes_from_server[0][1] < Pozitie :
                        Pozitie -= 1 
                elif Changes_from_server[0][0] == "a second passed" :
                    timer = timer - 1
                elif Changes_from_server[0][0] == "next_turn" :
                    next_turn = True
                Changes_from_server.pop(0)

        if timer == 0 :
            if Role == "host" :
                if Confirmatii_timer == len(CLIENTS) :
                    Transmit_to_all.append((("next_turn",None),None))
                    #se schimba cel care joaca
                    Whos_turn += 1 
                    if Whos_turn == len(playeri) :
                        Whos_turn = 0
                    timer = turn_time
                    Confirmatii_timer = 0
            else :
                if timer_notification_sent == False :
                    data_send = pickle.dumps(("timer is zero",None))
                    data_send = bytes((SPACE +str(len(data_send)))[-HEADERSIZE:], 'utf-8') + data_send
                    Connection.send(data_send)
                    timer_notification_sent = True
                elif next_turn == True :
                    #se schimba cel care joaca
                    Whos_turn += 1 
                    if Whos_turn == len(playeri) :
                        Whos_turn = 0
                    timer = turn_time
                    timer_notification_sent = False
                    next_turn = False


        #The event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)

    #finalul functiei si returnarea variabilelor necesare care s-ar fi putut schimba
    if Role == "host" :
        return playeri, CLIENTS, Coduri_pozitie_client
    else :
        print(run)
        return playeri,Pozitie 

