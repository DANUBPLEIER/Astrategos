import pygame 
import os 
import socket
import pickle
import threading
import math

White = (255,255,255)
Light_Green = (0, 255, 0)
nr_clients = 0

def lobby(WIN,WIDTH,HEIGHT,FPS,Role,name,Connection , Port = None) :
    pygame.init()


    playeri = []
    Font = pygame.font.Font(None, 40)
    Cerc_draw = []
    Text_draw = []
    Threads = []

    #coordonatele pentru cercuri
    y = HEIGHT/2
    diametru = (WIDTH - 50*3)/6
    for i in range(1,5) :
        x = diametru*i + diametru/2 + 50 *(i-1)
        Cerc_draw.append((x,y))

    #Threadul care se ocupa cu primirea informatiilor de la server
    def reciev_thread_from_server(server) :
        try :
            while True :
                msg = server.recv(1024)
                if len(msg) != 0 :
                    client.send(msg)
                else :
                    server.close()
                    run = False
                    break
        except :
            server.close()
            run = False
    #Threadul care se ocupa cu primirea informatiilor spre un client
    def reciev_thread_from_client(client,cod) :
        playeri.append(("NAME_COOL",0))
        text = Font.render(playeri[len(playeri)-1][0], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (diametru*(Coduri_pozitie_client[cod]+1) + 50*Coduri_pozitie_client[cod] + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append((text,text_rect))
        try :
            while True :
                msg = client.recv(1024)
                if len(msg) != 0 :
                    client.send(msg)
                else :
                    client.close()
                    Killed_Clients.append(cod)
                    break
        except :
            client.close()
            Killed_Clients.append(cod)
        print("Sa oprit threadul clientului nr {cod}")


    #Threadul care va asculta pentru si va acepta clienti
    def host_listen_thread() :
        global nr_clients
        #al catelea client de la inceputul serverului
        cod_client = 0
        while True :
            while nr_clients < 3 :
                    client, address = Connection.accept()
                    print("se intampla")
                    Coduri_pozitie_client[cod_client] = nr_clients 
                    nr_clients += 1
                    CLIENTS.append((client))
                    newthread = threading.Thread(target = reciev_thread_from_client , args =(client,cod_client))
                    cod_client += 1 
                    Client_THREADS.append(newthread)
                    Client_THREADS[len(Client_THREADS)-1].start()


    def draw_window () :
        WIN.fill((255,255,255))
        WIN.blit(Port_text,(25,25))
        WIN.blit(FPS_text,(25,25+40))
        #deseneaza cercurile si info-urile playerilor
        for i in range( len(Cerc_draw)) :
            pygame.draw.circle(WIN,(225, 223, 240),Cerc_draw[i],diametru/2)
            if len(playeri) > i :
                pygame.draw.circle(WIN,White,Cerc_draw[i],diametru/2 - 10)
                Text_draw[i][1].center = (diametru*(i+1) + 50*i + diametru/2,HEIGHT/2 - diametru/2-30)
                WIN.blit(Text_draw[i][0],Text_draw[i][1])

        pygame.display.update()
        

    #Se creaza toate variabilele de care are nevoie Hostul
    if Role == "host" :
        global nr_clients
        nr_clients = 0
        playeri.append((name,0))
        #crearea textului de afisat al Portului
        Port_text = Font.render("Port: " + str(Port), True, Light_Green)
        #crearea textului de afisat al numelui
        text = Font.render(playeri[0][0], True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (diametru + diametru/2,HEIGHT/2 - diametru/2-30)
        Text_draw.append((text,text_rect))
        CLIENTS = []
        Client_THREADS = []
        #threaduri care trebe reunite cu mainul
        Killed_Clients = []
        Coduri_pozitie_client = {}

        Connection.listen()
        Listening_thread = threading.Thread(target = host_listen_thread)
        Listening_thread.start()
    else :
        #Daca threadu care asculta serveru este mort
        Thread_mort = False


    clock = pygame.time.Clock()
    run = True
    while run :
        clock.tick(FPS)
        #Creaza textul pe care il afiseaza pentru FPS-uri
        FPS_text = Font.render("FPS: " + str(math.ceil(clock.get_fps())),True,Light_Green)

        #Verifica daca sunt clients care trebe purged
        while len(Killed_Clients) > 0 :
            nr_clients -= 1
            CLIENTS.pop(Coduri_pozitie_client[Killed_Clients[0]])
            Text_draw.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
            playeri.pop(Coduri_pozitie_client[Killed_Clients[0]] + 1)
            Client_THREADS[Coduri_pozitie_client[Killed_Clients[0]]].join()
            Client_THREADS.pop(Coduri_pozitie_client[Killed_Clients[0]])
            Coduri_pozitie_client.pop(Killed_Clients[0])
            #reactualizare in dictionarul clientilor si pozitiile lor
            for i in Coduri_pozitie_client :
                if Coduri_pozitie_client[i] > Killed_Clients[0] :
                    Coduri_pozitie_client[i] -= 1 
                    Text_draw[Coduri_pozitie_client[i]+1][1].center = (diametru*(Coduri_pozitie_client[i] + 2) + 50*(Coduri_pozitie_client[i] + 1) + diametru/2,HEIGHT/2 - diametru/2-30)
            Killed_Clients.pop(0)

        draw_window()

        #print (Coduri_pozitie_client)
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                os._exit(0)