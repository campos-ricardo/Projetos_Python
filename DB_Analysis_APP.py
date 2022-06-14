## Essa é o bloco principal de processamento para o software de análise dos estados geradores elétricos de uma planta termoelétrica 
###########################################################################################################################
## Inclusação de bibliotecas e funções secundáris

import logging 
LOG_FILENAME = "Traceback.log"
logging.basicConfig(filename =LOG_FILENAME, level=logging.DEBUG)
logging.debug('This message should go to the log file')

logging.debug('This message should go to the log file')

try:

    import matplotlib
    matplotlib.use('webagg')
    import os
    import pandas as pd
    import numpy as np
    from datetime import datetime
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from AM_Threading_2 import Worker, Worker1, Worker2, Worker3
    from matplotlib.figure import Figure
    from scipy.ndimage.interpolation import shift
    import glob
    import threading
    import gc
    import socket
    from PyQt5 import QtCore, QtGui, QtWidgets
    import WindowDBAnalysis
    from Update_Tables import *
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtCore import Qt 
    import sys
    import pyodbc
    import time

    from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PyQt5.QtGui import QIcon

except:

    logging.exception('Got exception on main handler')
    raise




#matplotlib.use('webagg')
#import os
#import pandas as pd
#import numpy as np
#from datetime import datetime
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#from AM_Threading_2 import Worker, Worker1, Worker2, Worker3
#from matplotlib.figure import Figure
#from scipy.ndimage.interpolation import shift
#import glob
#import threading
#import gc
#import socket
#from PyQt5 import QtCore, QtGui, QtWidgets
#import WindowDBAnalysis
#from Update_Tables import *
#from PyQt5.QtWidgets import QMainWindow
#from PyQt5.QtCore import Qt 
#import sys
#import pyodbc
#import time

#from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
#from PyQt5.QtGui import QIcon
##########################################################################################################################

class Ui_Programa_csv(object):

    ## Função de inicialização do algoritmo
    def __init__(self):

        global cnxn, table_list,idxGeradores, operating_generators, KVA_anterior, time_Stamp_array, partidas,iteration_count
        global variaveis_comp, N, idx12Cilindros

        #LOG_FILENAME = "Traceback.log"
        #logging.basicConfig(filename =LOG_FILENAME, level=logging.DEBUG)

        matplotlib.use('webagg')

        ## Cria a variável da jnela principal ao adicionar tudo que foi criado no programa QtDesigner
        self.UMain = WindowDBAnalysis.Ui_MainWindow()
        ## Cria um objeto Main Window do QtWidget
        self.ViewWindow = QtWidgets.QMainWindow()
        ## Ajusta a resolução da tela
        self.ViewWindow.setGeometry(0,0,1600,785)
        self.UMain.setupUi(self.ViewWindow)

        ## Esse bloco vai ser responsável por criar as threads
        self.threadpool = QtCore.QThreadPool()
        ## Configura o número máximo de threads que podem ter durante a execuçãod o código
        self.threadpool.setMaxThreadCount(6)
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        ## Inicializa flag de controle

        time.sleep(2)

        self.notInterrupt_IniciarProcessar = True
        self.interromper_Processo = False
        self.flagDirvazio = False
       
        #variaveis_comp = np.zeros((2,6,(100)))
        #print(variaveis_comp[0,:,0].shape)
        #variaveis_comp[0,:,0] = [1,1,1,1,1,1]
        #print(variaveis_comp[0,:,0])

        self.event_stop = threading.Event()

        ## Inicializa quase todas as variáveis que serão utilizadas durante o algoritmo
        #self.function_Init_Variaveis()
        print("Variaveis de peso inicializadas")

        ## Cria as janelas pop up que irão informar se ocorreu algum erro
        self.UMain.MessagBox = QtWidgets.QMessageBox()
        self.UMain.MessagBox.setWindowTitle('Error')
        self.UMain.MessagBox.setText('')
        self.UMain.MessagBox.setIcon(QtWidgets.QMessageBox.Information)
        self.UMain.MessagBox.setStandardButtons(QtWidgets.QMessageBox.Ok)

        ## Cria as janelas pop up que irão informar se ocorreu algum erro
        self.UMain.MessagBox_2 = QtWidgets.QMessageBox()
        self.UMain.MessagBox_2.setWindowTitle('Aviso')
        self.UMain.MessagBox_2.setText('')
        self.UMain.MessagBox_2.setIcon(QtWidgets.QMessageBox.Information)
        self.UMain.MessagBox_2.setStandardButtons(QtWidgets.QMessageBox.Ok)

        ## Carrega a imagem que vai ficar como o ícone na bandeja da área de trabalho
        self.trayIcon = QSystemTrayIcon(QIcon('system_tray.png'),parent = app)
        ## Mensagem que vai aparecer ao passar o mouse por cima do ícone
        self.trayIcon.setToolTip('Analise_Temperatura')

        print("Telas de aviso e System Tray inicializados")

        ## Configura as mensagens que irão aparecer em uma janela ao se clicar com o botão -direito
        ## Essas mensagens irão indicar a ação que vai ocorrer caso seja clicada
        menu = QMenu()
        ## Termina a exeução do programa
        exitAction = menu.addAction('Exit')
        exitAction.triggered.connect(app.quit)
        ## Fecha a janela de comparaão de variáveis
        closeAction = menu.addAction('Close Window')
        closeAction.triggered.connect(self.ViewWindow.hide)
        ## Abre a janela de comparações
        openAction = menu.addAction('Open Window')
        openAction.triggered.connect(self.ViewWindow.show)

        self.trayIcon.setContextMenu(menu)


        print("Inicializando Windgets")
        time.sleep(2)

        ### Conecta os botões as suas funções
        #self.function_home()


        ## Inicializa os widgets
        self.function_Init_Widgets()

        ## Se conecta ao bacno de dados utilizando as credenciais criadas no gerenciador
        cnxn = self.function_external_connect_to_database('ps','PS-REMOTO','**','*******')

        ## Dá um delay para deixar a conexão com BD dar uma estabelecida
        time.sleep(2)

        ## executa uma querry que irá recuperar o nome de todas as tabelas que são responsáveis por 
        ## guardar so dados dos geradores. Esse nomes serã usados futuramente
        table_list = function_list_DB_table(cnxn,list_all_tables_querry_test)

        print("Nomes das tabelas recuperadas")
        time.sleep(2)

        ## esses delays foram colcoados como preocupação. Caso venha a ocorer alguma problema 
        ## na inicialização, retornar com os delays
        #time.sleep(3)
        
        ## Inicializa o vetor de índices dos geradores de acordo com o tamanho do vetor de nomes 
        idxGeradores = np.zeros(len(table_list['TABLE_NAME']),dtype = int)

        
        N = len(idxGeradores)

        print("Indice dos geradores inicializados")
        time.sleep(2)

        # Esse loop vai detectar todos os geradores presentes no banco de dados e gerar uma lista 
        # de inteiros com os números dos mesmos
        for i in np.arange(0,len(table_list['TABLE_NAME']),1):

            ## Converte a variável com o nome do gerador para o tipo string
            temp = str(table_list['TABLE_NAME'][i])

            ## Retira da string com o nome da tabela o índice do gerador
            ## E vai preenchendo o vetor de índices
            idxGeradores[i] = int(re.findall(r'\d+',temp)[0])

        print("Indice dos geradores preenchido")
        time.sleep(2)

        print("Todas as variáveis iniciais criadas")

        print(table_list)
   
        idx12Cilindros = [1, 2 ,3, 4, 5, 6, 26, 27, 28, 29, 30, 31, 51, 52, 53, 54, 55, 56, 76, 77, 78, 79]

        data_inicial = ""

        data_final = ""

        operating_generators = 0

        self.function_home()

    ######################################################################
    ## As próximas duas funções irão lançar a janela e lançar o ícone que 
    ## irá ficar na bandeja da área de trabalho 
    def function_LaunchWindow(self):
        
        print("Funcao Tela")
        self.ViewWindow.show()

    def function_LaunchTrayIcon(self):
        
        print("Funcao Icone de sistema")
        self.trayIcon.show()
   
    ######################################################################
 
    ######################################################################
    ## Cria o worker para thread que vai conter a função calcular score
    def function_btn_ProcessarDados(self):

        print("Inicializando Processamento de dados")
        worker6 = Worker3(self.function_calcular_Score)
        worker6.signals.progress.connect(self.progress_fn)
        worker6.signals.error.connect(self.function_error_CSV)
        self.threadpool.start(worker6)
        
    ######################################################################

    ######################################################################
    ## Check type of analysis

    def function_analysis(self,analysis_vector):



        if(self.UMain.temp_cilindro.isChecked()):

            analysis_vector[0] = 1

        if(self.UMain.max_min.isChecked()):

            analysis_vector[1] = 1

        if(self.UMain.save_to_csv.isChecked()):

            analysis_vector[2] = 1

        if(self.UMain.ranque_arrefecimento.isChecked()):

            analysis_vector[3] = 1

        if(self.UMain.grafico_temperatura.isChecked()):

            analysis_vector[4] = 1

        if(self.UMain.analise_limites_inferiores.isChecked()):

            analysis_vector[5] = 1

        if(self.UMain.analise_temperatura_media.isChecked()):

            analysis_vector[6] = 1

        print("Vetor de Análises")
        print(analysis_vector)



    ######################################################################

    ## Atualiza o valor exibido na barra de progresso
    def progress_fn(self, n):

        print("%d%% done" % n)
        self.UMain.progressBar.setValue(n)
    ######################################################################

    ##############################################################################################################################################################
    ## Essa função conecta com o banco de dados presente em rede externa e retorna o objeto conector.
    ## Todos os parâmetros dessa função são strings.
    def function_external_connect_to_database(self,db_name,db_server_name,db_usernmame,db_password):

        ## Essa é a string que vai ser utilizada pelo porgrama em Python para se conectar com o BD
        cnxn_str = 'DRIVER={SQL Server};SERVER=' + db_server_name + ';DATABASE=' + db_name + ';UID=' + db_usernmame + ';PWD=' + db_password + ''

    
        # Para debugar imprime a string no console para ver se está correta
        print(cnxn_str)

        #time.sleep(5)

        try:
 
            ## Utiliza o comando connect da biblioteca pyodbc para se conectar ao BD
            cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + db_server_name + ';DATABASE=' + db_name + ';UID=' + db_usernmame + ';PWD=' + db_password + '')
            print("Connected to Database")

        except Exception as e: print(e)

        ## Dá um atraso para dar tempo para o banco de dados 
        time.sleep(1)

        ## Retorna o obejto conector para ser utilizado no resto do programa
        return cnxn 

    ###############################################################################################################################################################

    ####################################################################
    ## Cria uma série de diferenciação independente do tipo de variável
    def difference_timeSeries(self,dataset, interval=1):

       ## Cria uma lista vazia
        diff = list()

        ## Esse loop vai realizar a diferença entre todos os elementos 
        ## do vetor de acordo com o intervalo escolhido. E vai 
        ## juntando com o que já existe utilizando append.

        for i in range(interval, len(dataset)):

            value = dataset[i] - dataset[i - interval]
            diff.append(value)

        ## Retorna o vetor de diferença
        return (diff)
    ##############################################################################

    ###############################################################################
    ## 

    def function_calcular_tempo_gerador(self,x,idx):

        if(self.function_is_tupple_empty(idx)):
    
           temp_sum = 0
 
        else:
        
           time_array = np.array(x)
           temp_diff = np.array(self.difference_timeSeries(time_array[idx]))

           if((temp_diff.size)):

               idx_temp_corrigido = np.where(temp_diff < np.timedelta64(15,'m'))          
               temp_sum = np.timedelta64(np.sum(temp_diff[idx_temp_corrigido]),'m')

           else:

               temp_sum = 0

       
        return temp_sum

    ################################################################################
    ## Essa função atualiza quais geradores possuem. 
    ## A função não está sendo utilizada nessa versão do software, porque isso está 
    ## sendo feito com automaticamente com as informações do BD. Mas caso queira 
    ## modificar o programa para ler arquivos CSV, utilizar esse programa.

    def function_atualizar_Geradores(self):

        self.UMain.geradoresfaltando = self.UMain.lineEdit.text()
        for i in range(0,len(self.UMain.geradoresfaltando),3):

            print(int(self.UMain.geradoresfaltando[i:i + 2]))

        print("Geradores Atualizados")
    ################################################################################

    ################################################################################




    ################################################################################

    ############################################################################
    ## Essa função somente agrupa todas as funções que vão atualizar todos
    ## pontos do código ligado aos pesos e cálculo do AHP 
    def function_atalizar_variaveis_calcular_AHP(self):


        self.function_AtualizarPesos()
        self.function_calcular_AHP()
        function_update_all_textbox()
    ############################################################################      
    ############################################################################
    ## Essa função somente vai ser executada quando estiver utilizando arquivos 
    ## CSV, então verifica qual diretório contém os arquivos de extensão CSV 

    def function_AtualizarDir(self):
        
            global dir

            dir = self.UMain.path.text()
            print("Diretorio Atualizado")
    ############################################################################

    ############################################################################
    ## Apesar dos nome com CSV, essa função só vai indicar se ocorreu algum erro
    ## durante a execução do código e se o mesmo estava processando dados com os
    ## geradores parados ou ativos
    def function_error_CSV(self): 
   
       global operating_generators

       if(operating_generators):

        #self.UMain.MessagBox.setWindowTitle('Erro:')
        self.UMain.MessagBox.setText('Ocorreu algum erro com os geradores funcionando')
        self.UMain.MessagBox.show()
      
       else:

        self.UMain.MessagBox.setText('Ocorreu algum erro com os geradores parados')
        self.UMain.MessagBox.show()
    ################################################################################

    ################################################################################
    ## Essa função funciona como um ponto central para o programa, no qual vai 
    ## se certificar que todos os botões estejam funcionanado corretamente

    def function_home(self):

        #self.UMain.btn_Atualizar_Variaveis_AHP.clicked.connect(self.function_AtualizarPesos)
        self.UMain.btn_Exec.clicked.connect(self.function_btn_ProcessarDados)
        self.UMain.salvaDir.clicked.connect(self.function_Conf_bntBrowseDir)

    #################################################################################

    #################################################################################
    def autolabel(self,rects,ax):
     """Attach a text label above each bar in *rects*, displaying its height."""
     for rect in rects:
        height = round(rect.get_height(),2)
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',fontsize = 4, rotation = 90)



    ####################################################################################

    #############################################################################################################################################################################################
    ## Configura as janelas para escolha da pasta com os arrquivos CSV. Essa função também se mantém no arquivo, para caso queira executar com arquivos CSV

    def function_Conf_bntBrowseDir(self):

        global dir
        #print('BotÃo Browse Diretorio')
        
        #self.UBeamformer.Arquivo = QtWidgets.QWidget()
        ## Cria o objeto janela de diálogo interativa
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        try:
            
            ## Abre a janela interativa e salva o diretório escolhido pelo usuário
            dir = QtWidgets.QFileDialog.getExistingDirectory(self.UMain.VBrowseDir, "Open Directory","/home", QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
                                                         

        except Exception as e:

            print(str(e))

        self.function_create_directories(dir)

        ## Escreve o caminho para o diretório na caixa de texto designada
        self.UMain.path.setText(dir)

        print("Diretório Selecionado")
    ############################################################################################################################################################################################

    ############################################################################################################################################################################################
    ## Cria pastas que irão guardar os gráficos

    def function_create_directories(self,dir):
        
        # Cria o dretório para a análise de temperatura de cilindro
        directory = "Graficos_Analise_Temperatura_Cilindro"

        path = os.path.join(dir, directory) 
        if(os.path.isdir(path)):

            print("Directory already existis") 

        else:

            os.mkdir(path)
            print("Directory '% s' created" % directory) 

        # Cria o dretório para a análise de máximas e mínimas
        directory = "Analise_Max_Min"
        path = os.path.join(dir, directory) 
        if(os.path.isdir(path)):

            print("Directory already existis") 

        else:

            os.mkdir(path)
            print("Directory '% s' created" % directory) 

        # Cria o dretório para a análise de máximas e mínimas
        directory = "Analise_Temperatura_Liquidos"
        path = os.path.join(dir, directory) 
        if(os.path.isdir(path)):

            print("Directory already existis") 

        else:

            os.mkdir(path)
            print("Directory '% s' created" % directory) 

        # Cria o dretório para a análise de temperaturas médias
        directory = "Analise_Temperatura_Media"
        path = os.path.join(dir, directory) 
        if(os.path.isdir(path)):

            print("Directory already existis") 

        else:

            os.mkdir(path)
            print("Directory '% s' created" % directory) 

        # Cria o dretório para a análise de temperaturas inferiores
        directory = "Graficos_50_20"
        path = os.path.join(dir, directory) 
        if(os.path.isdir(path)):

            print("Directory already existis") 

        else:

            os.mkdir(path)
            print("Directory '% s' created" % directory) 




    #############################################################################################################################################################################################

    ###############################################################################################################
    ## Verifica se alguma estrutura que não seja um tupples está vazia 
    def function_is_empty(self,any_structure):
        if((any_structure)):
            #print('Structure is not empty.')s
            return False
        else:
            #print('Structure is empty.')
            return True


    ## Esta função verifica se um tupple está vazio, muito importante pelo fato dos bancos de dados
    ## relacionais utilizarem tupples para qualquer tipo de operação no Python
    def function_is_tupple_empty(self,any_structure):
        if((any(map(len, any_structure)))):
            #print('Structure is not empty.')
            return False
        else:
            #print('Structure is empty.')
            return True


    ################################################################################################################

    ################################################################################################################
    ## Principal trecho do algoritmo, no qual ocorrerá o calculo das notas, importação dos dados do banco de dados
    ## importação dos dados da tabelas CSV e gravação dos dados nas tabelas do Banco de Dados

    def function_calcular_Score(self,error,progress_callback,interrupt,finished):
        
        global operating_generators, N,cnxn
        global dir
        global result, varAnalisadaNew,idxNew
        global idxGeradores,table_list,partidas, time_Stamp_array, KVA_anterior,iteration_count,idx12Cilindros
            
        
        analysis_check_vector = np.zeros(7)
        print("Iniciando processamento dados")
        ## Label dos dados a serem salvos
        Colums_hist = ['GEN_IDX','MEDIA_INTERCOOLER','TEMPO_INTERCOOLER','MEDIA_LIQUIDO','TEMPO_LIQUIDO','MEDIA_OLEO','TEMPO_OLEO','RELIGAMENTOS','TEMPO_60',
                        'TEMPO_73','TEMPO_100','CONSUMO_PARTIDA','NUMERO_DE_AMOSTRAS','FinalE3TimeStamp']
       


        self.function_analysis(analysis_check_vector)
    

        print(idxGeradores)
        time.sleep(3)
        print("Iniciar Porcessamento de dados ")

        data_inicial = self.UMain.data_inicial.text()
        data_final = self.UMain.data_final.text()
        print(data_inicial)
        print(data_final)


        if(np.sum(analysis_check_vector) and not (self.function_is_empty(data_inicial) or  self.function_is_empty(data_final))):

            operating_generators = 1

            Intercooler_Mean = np.zeros(N)
            Combustivel_Mean = np.zeros(N)
            Arrefecimento_Mean = np.zeros(N)

            Intercooler_Max = np.zeros(N)
            Combustivel_Max = np.zeros(N)
            Arrefecimento_Max = np.zeros(N)
    
            tempoIntercooler = np.zeros(N) * np.timedelta64(0,'m')  
            tempoCombustivel = np.zeros(N) * np.timedelta64(0,'m')  
            tempoArrefecimento = np.zeros(N) * np.timedelta64(0,'m')  

            temp_cilindro_A1 = np.zeros(N) * np.timedelta64(0,'m')  
            temp_cilindro_A2 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_A3 = np.zeros(N) * np.timedelta64(0,'m')   
            temp_cilindro_A4 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_A5 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_A6 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_A7 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_A8 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B1 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B2 = np.zeros(N) * np.timedelta64(0,'m')   
            temp_cilindro_B3 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B4 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B5 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B6 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B7 = np.zeros(N) * np.timedelta64(0,'m')    
            temp_cilindro_B8 = np.zeros(N) * np.timedelta64(0,'m')    

            tempKW_Cilindro_A1 = np.zeros(N) * np.timedelta64(0,'m')  
            tempKW_Cilindro_A2 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_A3 = np.zeros(N) * np.timedelta64(0,'m')   
            tempKW_Cilindro_A4 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_A5 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_A6 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_A7 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_A8 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B1 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B2 = np.zeros(N) * np.timedelta64(0,'m')   
            tempKW_Cilindro_B3 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B4 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B5 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B6 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B7 = np.zeros(N) * np.timedelta64(0,'m')    
            tempKW_Cilindro_B8 = np.zeros(N) * np.timedelta64(0,'m')    

            min_cilindro_A1 = np.zeros(N)
            min_cilindro_A2 = np.zeros(N)
            min_cilindro_A3 = np.zeros(N)
            min_cilindro_A4 = np.zeros(N)
            min_cilindro_A5 = np.zeros(N)
            min_cilindro_A6 = np.zeros(N)
            min_cilindro_A7 = np.zeros(N)
            min_cilindro_A8 = np.zeros(N)
            min_cilindro_B1 = np.zeros(N)
            min_cilindro_B2 = np.zeros(N)
            min_cilindro_B3 = np.zeros(N)
            min_cilindro_B4 = np.zeros(N)
            min_cilindro_B5 = np.zeros(N)
            min_cilindro_B6 = np.zeros(N)
            min_cilindro_B7 = np.zeros(N)
            min_cilindro_B8 = np.zeros(N)



            max_cilindro_A1 = np.zeros(N)
            max_cilindro_A2 = np.zeros(N)
            max_cilindro_A3 = np.zeros(N)
            max_cilindro_A4 = np.zeros(N)
            max_cilindro_A5 = np.zeros(N)
            max_cilindro_A6 = np.zeros(N)
            max_cilindro_A7 = np.zeros(N)
            max_cilindro_A8 = np.zeros(N)
            max_cilindro_B1 = np.zeros(N)
            max_cilindro_B2 = np.zeros(N)
            max_cilindro_B3 = np.zeros(N)
            max_cilindro_B4 = np.zeros(N)
            max_cilindro_B5 = np.zeros(N)
            max_cilindro_B6 = np.zeros(N)
            max_cilindro_B7 = np.zeros(N)
            max_cilindro_B8 = np.zeros(N)

            mean_cilindro_A1 = np.zeros(N)
            mean_cilindro_A2 = np.zeros(N)
            mean_cilindro_A3 = np.zeros(N)
            mean_cilindro_A4 = np.zeros(N)
            mean_cilindro_A5 = np.zeros(N)
            mean_cilindro_A6 = np.zeros(N)
            mean_cilindro_A7 = np.zeros(N)
            mean_cilindro_A8 = np.zeros(N)
            mean_cilindro_B1 = np.zeros(N)
            mean_cilindro_B2 = np.zeros(N)
            mean_cilindro_B3 = np.zeros(N)
            mean_cilindro_B4 = np.zeros(N)
            mean_cilindro_B5 = np.zeros(N)
            mean_cilindro_B6 = np.zeros(N)
            mean_cilindro_B7 = np.zeros(N)
            mean_cilindro_B8 = np.zeros(N)

            first_time_Cil_16_list =  0
            first_time_Cil_12_list =  0

            time.sleep(3)

            progress_callback.emit((0 / (N - 2)) * 100)

            for n in range(N): 

                ## Emite o callback para a barra de progressos
                progress_callback.emit((n / (N - 2)) * 100)
        
                print("Indice Atual")
                print(n)              

                select_operating_data = ' SELECT * FROM  ps.dbo.'+str(table_list['TABLE_NAME'][n])+" WHERE [E3TimeStamp] BETWEEN '"+ data_inicial+ "' AND '"+data_final+"' ORDER BY [E3TimeStamp] ASC"
        
                num = pd.read_sql_query(select_operating_data, cnxn)        


                cilindro_A1 = np.array(num['A1'])
                cilindro_A2 = np.array(num['A2'])
                cilindro_A3 = np.array(num['A3'])
                cilindro_A4 = np.array(num['A4'])
                cilindro_A5 = np.array(num['A5'])
                cilindro_A6 = np.array(num['A6'])
                cilindro_A7 = np.array(num['A7'])
                cilindro_A8 = np.array(num['A8'])
                cilindro_B1 = np.array(num['B1'])
                cilindro_B2 = np.array(num['B2'])
                cilindro_B3 = np.array(num['B3'])
                cilindro_B4 = np.array(num['B4'])
                cilindro_B5 = np.array(num['B5'])
                cilindro_B6 = np.array(num['B6'])
                cilindro_B7 = np.array(num['B7'])
                cilindro_B8 = np.array(num['B8'])

                # Importar valores de KVA 
                KVA =np.array(num['KVA'])
                KW = np.array(num['KW'])

                # Colocar os índices das vairáveis indicadas abaixo
                TempeIntercooler = np.array(num['ICT'])
                TempeCombustivel = np.array(num['FT'])
                TempeArrefecimento = np.array(num['L_Temp'])

                # Transforma strings de data e dataseries e adiciona o índices        
                idx = pd.Series(np.r_[0:(len(num['E3TimeStamp']))])
                t = pd.to_datetime(num['E3TimeStamp'])

                # Calcular os valores médios de temperatura
                Intercooler_Mean[n] = np.mean(TempeIntercooler)
                Combustivel_Mean[n] = np.mean(TempeCombustivel)
                Arrefecimento_Mean[n] = np.mean(TempeArrefecimento)

                # Calcular os valores máximos de temperatura
                Intercooler_Max[n] = np.max(TempeIntercooler)
                Combustivel_Max[n] = np.max(TempeCombustivel)
                Arrefecimento_Max[n] = np.max(TempeArrefecimento)

                # Transfomra em dataframe e organiza em ordem crescentes        # Transfomra em dataframe e organiza em ordem crescentes
                t = pd.DataFrame({'Index':idx,'TimeStamp':t})
   
                t_sorted = t.sort_values(by=['TimeStamp'])

                # Criar função para substituir o 2500 por 0
                cilindro_A1[np.where(cilindro_A1 > 2000)] = 0        
                cilindro_A2[np.where(cilindro_A2 > 2000)] = 0        
                cilindro_A3[np.where(cilindro_A3 > 2000)] = 0        
                cilindro_A4[np.where(cilindro_A4 > 2000)] = 0        
                cilindro_A5[np.where(cilindro_A5 > 2000)] = 0        
                cilindro_A6[np.where(cilindro_A6 > 2000)] = 0        
                cilindro_A7[np.where(cilindro_A7 > 2000)] = 0        
                cilindro_A8[np.where(cilindro_A8 > 2000)] = 0        
                cilindro_B1[np.where(cilindro_B1 > 2000)] = 0        
                cilindro_B2[np.where(cilindro_B2 > 2000)] = 0        
                cilindro_B3[np.where(cilindro_B3 > 2000)] = 0        
                cilindro_B4[np.where(cilindro_B4 > 2000)] = 0        
                cilindro_B5[np.where(cilindro_B5 > 2000)] = 0        
                cilindro_B6[np.where(cilindro_B6 > 2000)] = 0        
                cilindro_B7[np.where(cilindro_B7 > 2000)] = 0        
                cilindro_B8[np.where(cilindro_B8 > 2000)] = 0       

                # Determina quais momentos o motor estava gerando 

                idx_generating = np.where(KW>0)

                gen_time = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_generating),'m').astype(int)

                time.sleep(1)


                # Média dos valores de temperatura para cada cilindro em potência válida

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):       

                            mean_cilindro_A1[n] = np.mean(cilindro_A1[(np.where(KVA > 0))].astype(float))            

                else:

                            mean_cilindro_A1[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):      

                    mean_cilindro_A2[n] = np.mean(cilindro_A2[(np.where(KVA > 0))].astype(float))          
                else:

                    mean_cilindro_A2[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):       

                    mean_cilindro_A3[n] = np.mean(cilindro_A3[(np.where(KVA > 0))].astype(float))            
                else:

                    mean_cilindro_A3[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):        

                    mean_cilindro_A4[n] = np.mean(cilindro_A4[(np.where(KVA > 0))].astype(float))          

                else:

                    mean_cilindro_A4[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):        

                    mean_cilindro_A5[n] = np.mean(cilindro_A5[(np.where(KVA > 0))].astype(float))          

                else:

                    mean_cilindro_A5[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):        

                    mean_cilindro_A6[n] = np.mean(cilindro_A6[(np.where(KVA > 0))].astype(float))

                else:

                    mean_cilindro_A6[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):  

                    mean_cilindro_A7[n] = np.mean(cilindro_A7[(np.where(KVA > 0))].astype(float)) 

                else:

                    mean_cilindro_A7[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):       

                    mean_cilindro_A8[n] = np.mean(cilindro_A8[(np.where(KVA > 0))].astype(float))    

                else:

                    mean_cilindro_A8[n] = 0


                if(not self.function_is_tupple_empty(np.where(KVA > 0))):      

                    mean_cilindro_B1[n] = np.mean(cilindro_B1[(np.where(KVA > 0))].astype(float))   
                else:

                    mean_cilindro_B1[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):      

                    mean_cilindro_B2[n] = np.mean(cilindro_B2[(np.where(KVA > 0))].astype(float))            

                else:

                    mean_cilindro_B2[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):      

                    mean_cilindro_B3[n] = np.mean(cilindro_B3[(np.where(KVA > 0))].astype(float))           

                else:

                    mean_cilindro_B3[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):       

                    mean_cilindro_B4[n] = np.mean(cilindro_B4[(np.where(KVA > 0))].astype(float))       

                else:

                    mean_cilindro_B4[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))): 

                    mean_cilindro_B5[n] = np.mean(cilindro_B5[(np.where(KVA > 0))].astype(float)) 

                else:

                    mean_cilindro_B5[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):   

                    mean_cilindro_B6[n] = np.mean(cilindro_B6[(np.where(KVA > 0))].astype(float))         

                else:

                    mean_cilindro_B6[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):

                    mean_cilindro_B7[n] = np.mean(cilindro_B7[(np.where(KVA > 0))].astype(float))      

                else:

                    mean_cilindro_B7[n] = 0

                if(not self.function_is_tupple_empty(np.where(KVA > 0))):       

                    mean_cilindro_B8[n] = np.mean(cilindro_B8[(np.where(KVA > 0))].astype(float))        

                else:

                    mean_cilindro_B8[n] = 0


                # Achar máximos e mínimos para cada cilindro

                if(not self.function_is_tupple_empty(np.where(cilindro_A1 > 50))):       

                    min_cilindro_A1[n] = np.min(cilindro_A1[(np.where(cilindro_A1 > 50))].astype(float))            

                else:

                    min_cilindro_A1[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A2 > 50))):      

                    min_cilindro_A2[n] = np.min(cilindro_A2[(np.where(cilindro_A2 > 50))].astype(float))          
                else:

                    min_cilindro_A2[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A3 > 50))):       

                    min_cilindro_A3[n] = np.min(cilindro_A3[(np.where(cilindro_A3 > 50))].astype(float))            
                else:

                    min_cilindro_A3[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A4 > 50))):        

                    min_cilindro_A4[n] = np.min(cilindro_A4[(np.where(cilindro_A4 > 50))].astype(float))          

                else:

                    min_cilindro_A4[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A5 > 50))):        

                    min_cilindro_A5[n] = np.min(cilindro_A5[(np.where(cilindro_A5 > 50))].astype(float))  
            
                else:

                    min_cilindro_A5[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A6 > 50))):        

                    min_cilindro_A6[n] = np.min(cilindro_A6[(np.where(cilindro_A6 > 50))].astype(float))

                else:

                    min_cilindro_A6[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A7 > 50))):  

                    min_cilindro_A7[n] = np.min(cilindro_A7[(np.where(cilindro_A7 > 50))].astype(float)) 

                else:

                    min_cilindro_A7[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_A8 > 50))):       

                    min_cilindro_A8[n] = np.min(cilindro_A8[(np.where(cilindro_A8 > 50))].astype(float))    

                else:

                    min_cilindro_A8[n] = 0


                if(not self.function_is_tupple_empty(np.where(cilindro_B1 > 50))):      

                    min_cilindro_B1[n] = np.min(cilindro_B1[(np.where(cilindro_B1 > 50))].astype(float))   
                else:

                    min_cilindro_B1[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B2 > 50))):      

                    min_cilindro_B2[n] = np.min(cilindro_B2[(np.where(cilindro_B2 > 50))].astype(float))            

                else:

                    min_cilindro_B2[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B3 > 50))):      

                    min_cilindro_B3[n] = np.min(cilindro_B3[(np.where(cilindro_B3 > 50))].astype(float))           

                else:

                    min_cilindro_B3[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B4 > 50))):       

                    min_cilindro_B4[n] = np.min(cilindro_B4[(np.where(cilindro_B4 > 50))].astype(float))       

                else:

                    min_cilindro_B4[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B5 > 50))): 

                    min_cilindro_B5[n] = np.min(cilindro_B5[(np.where(cilindro_B5 > 50))].astype(float)) 

                else:

                    min_cilindro_B5[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B6 > 50))):   

                    min_cilindro_B6[n] = np.min(cilindro_B6[(np.where(cilindro_B6 > 50))].astype(float))         

                else:

                    min_cilindro_B6[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B7 > 50))):

                    min_cilindro_B7[n] = np.min(cilindro_B7[(np.where(cilindro_B7 > 50))].astype(float))      

                else:

                    min_cilindro_B7[n] = 0

                if(not self.function_is_tupple_empty(np.where(cilindro_B8 > 50))):       

                    min_cilindro_B8[n] = np.min(cilindro_B8[(np.where(cilindro_B8 > 50))].astype(float))        

                else:

                    min_cilindro_B8[n] = 0

                max_cilindro_A1[n] = np.max(cilindro_A1)
                max_cilindro_A2[n] = np.max(cilindro_A2)
                max_cilindro_A3[n] = np.max(cilindro_A3)
                max_cilindro_A4[n] = np.max(cilindro_A4)
                max_cilindro_A5[n] = np.max(cilindro_A5)
                max_cilindro_A6[n] = np.max(cilindro_A6)
                max_cilindro_A7[n] = np.max(cilindro_A7)
                max_cilindro_A8[n] = np.max(cilindro_A8)
                max_cilindro_B1[n] = np.max(cilindro_B1)
                max_cilindro_B2[n] = np.max(cilindro_B2)
                max_cilindro_B3[n] = np.max(cilindro_B3)
                max_cilindro_B4[n] = np.max(cilindro_B4)
                max_cilindro_B5[n] = np.max(cilindro_B5)
                max_cilindro_B6[n] = np.max(cilindro_B6)
                max_cilindro_B7[n] = np.max(cilindro_B7)
                max_cilindro_B8[n] = np.max(cilindro_B8)    

                if(self.function_is_empty(self.UMain.max_temp_bico_injetor.text())):

                    limite_max = 0
                  
                else:

                    limite_max = float(self.UMain.max_temp_bico_injetor.text())

                    idx_A1 = np.where(((cilindro_A1 > limite_max)))        
                    idx_A2 = np.where(((cilindro_A2 >  limite_max)))        
                    idx_A3 = np.where(((cilindro_A3 >  limite_max)))       
                    idx_A4 = np.where(((cilindro_A4 >  limite_max)))     
                    idx_A5 = np.where(((cilindro_A5 >  limite_max)))       
                    idx_A6 = np.where(((cilindro_A6 >  limite_max)))       
                    idx_A7 = np.where(((cilindro_A7 >  limite_max)))    
                    idx_A8 = np.where(((cilindro_A8 >  limite_max)))    
                    idx_B1 = np.where(((cilindro_B1 >  limite_max)))     
                    idx_B2 = np.where(((cilindro_B2 >  limite_max)))      
                    idx_B3 = np.where(((cilindro_B3 >  limite_max)))        
                    idx_B4 = np.where(((cilindro_B4 >  limite_max)))        
                    idx_B5 = np.where(((cilindro_B5 >  limite_max)))    
                    idx_B6 = np.where(((cilindro_B6 >  limite_max)))       
                    idx_B7 = np.where(((cilindro_B7 >  limite_max)))        
                    idx_B8 = np.where(((cilindro_B8 >  limite_max)))   

                    temp_cilindro_A1[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A1),'m')
                    temp_cilindro_A2[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A2),'m')
                    temp_cilindro_A3[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A3),'m')
                    temp_cilindro_A4[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A4),'m')
                    temp_cilindro_A5[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A5),'m')
                    temp_cilindro_A6[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A6),'m')
                    temp_cilindro_A7[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A7),'m')
                    temp_cilindro_A8[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_A8),'m')
                    temp_cilindro_B1[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B1),'m')
                    temp_cilindro_B2[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B2),'m')
                    temp_cilindro_B3[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B3),'m')
                    temp_cilindro_B4[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B4),'m')
                    temp_cilindro_B5[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B5),'m')
                    temp_cilindro_B6[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B6),'m')
                    temp_cilindro_B7[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B7),'m')
                    temp_cilindro_B8[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_B8),'m')


                idxKW12Cil = np.where(KW>700)
                idxKW16Cil = np.where(KW>940)

                limite_min_inferior = self.UMain.limite_min_inf_cilindro.text()
                limite_min_superior = self.UMain.limite_min_sup_cilindro.text()
                print(limite_min_inferior)
                print(limite_min_superior)

                if((self.function_is_empty(limite_min_inferior) or self.function_is_empty(limite_min_superior))):

                    limite_min_inferior = 0
                    limite_min_superior = 0

                else:

                    limite_min_inferior = float(limite_min_inferior)
                    limite_min_superior = float(limite_min_superior)

                    if(self.function_is_tupple_empty(np.where(idxGeradores[n] == idx12Cilindros))):

                        idxKW_A1 = np.where((cilindro_A1[idxKW16Cil] > limite_min_inferior)&(cilindro_A1[idxKW16Cil] <limite_min_superior ))        
                        idxKW_A2 = np.where((cilindro_A2[idxKW16Cil] > limite_min_inferior)&(cilindro_A2[idxKW16Cil] <limite_min_superior ))       
                        idxKW_A3 = np.where((cilindro_A3[idxKW16Cil] > limite_min_inferior)&(cilindro_A3[idxKW16Cil] <limite_min_superior ))          
                        idxKW_A4 = np.where((cilindro_A4[idxKW16Cil] > limite_min_inferior)&(cilindro_A4[idxKW16Cil] <limite_min_superior ))        
                        idxKW_A5 = np.where((cilindro_A5[idxKW16Cil] > limite_min_inferior)&(cilindro_A5[idxKW16Cil] <limite_min_superior ))    
                        idxKW_A6 = np.where((cilindro_A6[idxKW16Cil] > limite_min_inferior)&(cilindro_A6[idxKW16Cil] <limite_min_superior ))          
                        idxKW_A7 = np.where((cilindro_A7[idxKW16Cil] > limite_min_inferior)&(cilindro_A7[idxKW16Cil] <limite_min_superior ))        
                        idxKW_A8 = np.where((cilindro_A8[idxKW16Cil] > limite_min_inferior)&(cilindro_A8[idxKW16Cil] <limite_min_superior ))       
                        idxKW_B1 = np.where((cilindro_B1[idxKW16Cil] > limite_min_inferior)&(cilindro_B1[idxKW16Cil] <limite_min_superior ))         
                        idxKW_B2 = np.where((cilindro_B2[idxKW16Cil] > limite_min_inferior)&(cilindro_B2[idxKW16Cil] <limite_min_superior ))        
                        idxKW_B3 = np.where((cilindro_B3[idxKW16Cil] > limite_min_inferior)&(cilindro_B3[idxKW16Cil] <limite_min_superior ))            
                        idxKW_B4 = np.where((cilindro_B4[idxKW16Cil] > limite_min_inferior)&(cilindro_B4[idxKW16Cil] <limite_min_superior ))          
                        idxKW_B5 = np.where((cilindro_B5[idxKW16Cil] > limite_min_inferior)&(cilindro_B5[idxKW16Cil] <limite_min_superior ))    
                        idxKW_B6 = np.where((cilindro_B6[idxKW16Cil] > limite_min_inferior)&(cilindro_B6[idxKW16Cil] <limite_min_superior ))         
                        idxKW_B7 = np.where((cilindro_B7[idxKW16Cil] > limite_min_inferior)&(cilindro_B7[idxKW16Cil] <limite_min_superior ))           
                        idxKW_B8 = np.where((cilindro_B8[idxKW16Cil] > limite_min_inferior)&(cilindro_B8[idxKW16Cil] <limite_min_superior ))      



                    else:

                        idxKW_A1 = np.where((cilindro_A1[idxKW12Cil] > limite_min_inferior)&(cilindro_A1[idxKW12Cil] <limite_min_superior ))        
                        idxKW_A2 = np.where((cilindro_A2[idxKW12Cil] > limite_min_inferior)&(cilindro_A2[idxKW12Cil] <limite_min_superior ))       
                        idxKW_A3 = np.where((cilindro_A3[idxKW12Cil] > limite_min_inferior)&(cilindro_A3[idxKW12Cil] <limite_min_superior ))          
                        idxKW_A4 = np.where((cilindro_A4[idxKW12Cil] > limite_min_inferior)&(cilindro_A4[idxKW12Cil] <limite_min_superior ))        
                        idxKW_A5 = np.where((cilindro_A5[idxKW12Cil] > limite_min_inferior)&(cilindro_A5[idxKW12Cil] <limite_min_superior ))    
                        idxKW_A6 = np.where((cilindro_A6[idxKW12Cil] > limite_min_inferior)&(cilindro_A6[idxKW12Cil] <limite_min_superior ))          
                        idxKW_A7 = np.where((cilindro_A7[idxKW12Cil] > limite_min_inferior)&(cilindro_A7[idxKW12Cil] <limite_min_superior ))        
                        idxKW_A8 = np.where((cilindro_A8[idxKW12Cil] > limite_min_inferior)&(cilindro_A8[idxKW12Cil] <limite_min_superior ))       
                        idxKW_B1 = np.where((cilindro_B1[idxKW12Cil] > limite_min_inferior)&(cilindro_B1[idxKW12Cil] <limite_min_superior ))         
                        idxKW_B2 = np.where((cilindro_B2[idxKW12Cil] > limite_min_inferior)&(cilindro_B2[idxKW12Cil] <limite_min_superior ))        
                        idxKW_B3 = np.where((cilindro_B3[idxKW12Cil] > limite_min_inferior)&(cilindro_B3[idxKW12Cil] <limite_min_superior ))            
                        idxKW_B4 = np.where((cilindro_B4[idxKW12Cil] > limite_min_inferior)&(cilindro_B4[idxKW12Cil] <limite_min_superior ))          
                        idxKW_B5 = np.where((cilindro_B5[idxKW12Cil] > limite_min_inferior)&(cilindro_B5[idxKW12Cil] <limite_min_superior ))    
                        idxKW_B6 = np.where((cilindro_B6[idxKW12Cil] > limite_min_inferior)&(cilindro_B6[idxKW12Cil] <limite_min_superior ))         
                        idxKW_B7 = np.where((cilindro_B7[idxKW12Cil] > limite_min_inferior)&(cilindro_B7[idxKW12Cil] <limite_min_superior ))           
                        idxKW_B8 = np.where((cilindro_B8[idxKW12Cil] > limite_min_inferior)&(cilindro_B8[idxKW12Cil] <limite_min_superior ))      


                    tempKW_Cilindro_A1[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A1),'m')
                    tempKW_Cilindro_A2[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A2),'m')
                    tempKW_Cilindro_A3[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A3),'m')
                    tempKW_Cilindro_A4[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A4),'m')
                    tempKW_Cilindro_A5[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A5),'m')
                    tempKW_Cilindro_A6[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A6),'m')
                    tempKW_Cilindro_A7[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A7),'m')
                    tempKW_Cilindro_A8[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_A8),'m')
                    tempKW_Cilindro_B1[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B1),'m')
                    tempKW_Cilindro_B2[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B2),'m')
                    tempKW_Cilindro_B3[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B3),'m')
                    tempKW_Cilindro_B4[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B4),'m')
                    tempKW_Cilindro_B5[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B5),'m')
                    tempKW_Cilindro_B6[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B6),'m')
                    tempKW_Cilindro_B7[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B7),'m')
                    tempKW_Cilindro_B8[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idxKW_B8),'m')




                if(self.function_is_empty(self.UMain.max_temp_combustivel.text()) or self.function_is_empty(self.UMain.max_temp_Intercooler.text()) or self.UMain.max_temp_arrefecimento.text()):

                    limite_max_combustivel = 1000
                    limite_max_intercooler = 1000
                    limite_max_arrefecimento = 1000

                    idx_Combustivel = np.where(((TempeCombustivel > limite_max_combustivel)))        
                    idx_Intercooler = np.where(((TempeIntercooler >  limite_max_intercooler)))        
                    idx_TempeArrefecimento = np.where(((TempeArrefecimento >  limite_max_arrefecimento)))       

                else:

                    
                    limite_max_combustivel = float(self.UMain.max_temp_combustivel.text())
                    limite_max_intercooler = float(self.UMain.max_temp_Intercooler.text())
                    limite_max_arrefecimento = float(self.UMain.max_temp_arrefecimento.text())

                    idx_Combustivel = np.where(((TempeCombustivel > limite_max_combustivel)))        
                    idx_Intercooler = np.where(((TempeIntercooler >  limite_max_intercooler)))        
                    idx_TempeArrefecimento = np.where(((TempeArrefecimento >  limite_max_arrefecimento)))     

                    tempoIntercooler[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_Intercooler),'m')
                    tempoCombustivel[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_Combustivel),'m')
                    tempoArrefecimento[n] = np.timedelta64(self.function_calcular_tempo_gerador(t_sorted.TimeStamp,idx_TempeArrefecimento),'m')






            
                #if(self.function_is_tupple_empty(np.where(idxGeradores[n] == idx12Cilindros))):

                ##########################################################################################################################################
                ## Gera a lista de geradores de 16 cilindros de acordo com a média da potência gerada e o tempo de geração para as temperaturas inferiores
         
                if(analysis_check_vector[5]):

                    if(self.function_is_tupple_empty(np.where(idxGeradores[n] == idx12Cilindros))):

                    # Plotar gráfico referente ao tempo de cada cilindro acima do limite

                        plot_array_50_20 = np.array([tempKW_Cilindro_A1[n].astype(int),tempKW_Cilindro_A2[n].astype(int),tempKW_Cilindro_A3[n].astype(int),tempKW_Cilindro_A4[n].astype(int),
                                                tempKW_Cilindro_A5[n].astype(int),tempKW_Cilindro_A6[n].astype(int),tempKW_Cilindro_A7[n].astype(int),tempKW_Cilindro_A8[n].astype(int),
                                                tempKW_Cilindro_B1[n].astype(int),tempKW_Cilindro_B2[n].astype(int),tempKW_Cilindro_B3[n].astype(int),tempKW_Cilindro_B4[n].astype(int),
                                                tempKW_Cilindro_B5[n].astype(int),tempKW_Cilindro_B6[n].astype(int),tempKW_Cilindro_B7[n].astype(int),tempKW_Cilindro_B8[n].astype(int)])

            


                        xt = np.arange(1,len(plot_array_50_20) + 1,1)      

                        xlabel = ['Cilindro A1','Cilindro A2','Cilindro A3','Cilindro A4','Cilindro A5','Cilindro A6','Cilindro A7','Cilindro A8',
                                    'Cilindro B1','Cilindro B2','Cilindro B3','Cilindro B4','Cilindro B5','Cilindro B6','Cilindro B7','Cilindro B8']
        
                        fig, ax = plt.subplots()

                        rect = ax.bar(xt, plot_array_50_20,align = 'center')

                        ax.set_xticks(np.arange(1,len(plot_array_50_20) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de atividade entre os limites inferiores com geração acima 940KW dos cilindros do Gerador ' + str(idxGeradores[n].astype(int))+' '+data_inicial + '-' + data_final,fontsize = 6)      
                        ax.set_ylabel('Tempo funcionamento acima do limite [min]')

                        ax.set_ylim([0,None])

                        self.autolabel(rect,ax)

                        fig.tight_layout()

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Graficos_50_20/Gerador '+str(idxGeradores[n].astype(int)) + '.png')     

                        plt.clf()
                        plt.close('all')
                        del xt, plot_array_50_20
                        gc.collect()

                    else:

                                        

                        plot_array_50_20 = np.array([tempKW_Cilindro_A1[n].astype(int),tempKW_Cilindro_A2[n].astype(int),tempKW_Cilindro_A3[n].astype(int),tempKW_Cilindro_A4[n].astype(int),
                                               tempKW_Cilindro_A5[n].astype(int),tempKW_Cilindro_A6[n].astype(int),
                                               tempKW_Cilindro_B1[n].astype(int),tempKW_Cilindro_B2[n].astype(int),tempKW_Cilindro_B3[n].astype(int),tempKW_Cilindro_B4[n].astype(int),
                                               tempKW_Cilindro_B5[n].astype(int),tempKW_Cilindro_B6[n].astype(int)])

            


                        xt = np.arange(1,len(plot_array_50_20) + 1,1)      

                        xlabel = ['Cilindro A1','Cilindro A2','Cilindro A3','Cilindro A4','Cilindro A5','Cilindro A6',
                                  'Cilindro B1','Cilindro B2','Cilindro B3','Cilindro B4','Cilindro B5','Cilindro B6']
        
                        fig, ax = plt.subplots()

                        rect = ax.bar(xt, plot_array_50_20,align = 'center')

                        ax.set_xticks(np.arange(1,len(plot_array_50_20) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de atividade entre os limites inferiores com geração de 700KW dos cilindros do Gerador ' + str(idxGeradores[n].astype(int))+' ' +data_inicial + '-' + data_final,fontsize = 6)      

                        ax.set_ylabel('Tempo funcionamento acima do limite [min]')

                        ax.set_ylim([0,None])

                       # ax.grid()

                        self.autolabel(rect,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Graficos_50_20/Gerador '+str(idxGeradores[n].astype(int)) + '.png')     

                        plt.clf()
                        plt.close('all')
                        del xt, plot_array_50_20
                        gc.collect()

                #######################################################################################################################################################################################
                #######################################################################################################################################################################################
                # Análise das temperaturas dos cilindros para verificar quantos minutos cada um ficou acima da média

                if(analysis_check_vector[0]):

                      if(self.function_is_tupple_empty(np.where(idxGeradores[n] == idx12Cilindros))):

                # Plotar gráfico referente ao tempo de cada cilindro acima do limite

                        plot_array = np.array([temp_cilindro_A1[n].astype(int),temp_cilindro_A2[n].astype(int),temp_cilindro_A3[n].astype(int),temp_cilindro_A4[n].astype(int),
                                               temp_cilindro_A5[n].astype(int),temp_cilindro_A6[n].astype(int),temp_cilindro_A7[n].astype(int),temp_cilindro_A8[n].astype(int),
                                               temp_cilindro_B1[n].astype(int),temp_cilindro_B2[n].astype(int),temp_cilindro_B3[n].astype(int),temp_cilindro_B4[n].astype(int),
                                               temp_cilindro_B5[n].astype(int),temp_cilindro_B6[n].astype(int),temp_cilindro_B7[n].astype(int),temp_cilindro_B8[n].astype(int)])

            


                        xt = np.arange(1,len(plot_array) + 1,1)      

                        xlabel = ['Cilindro A1','Cilindro A2','Cilindro A3','Cilindro A4','Cilindro A5','Cilindro A6','Cilindro A7','Cilindro A8',
                                  'Cilindro B1','Cilindro B2','Cilindro B3','Cilindro B4','Cilindro B5','Cilindro B6','Cilindro B7','Cilindro B8']
        
                        fig, ax = plt.subplots()

                        rect = ax.bar(xt, plot_array,align = 'center')

                        ax.set_xticks(np.arange(1,len(plot_array) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de atividade dos cilindros do Gerador ' + str(idxGeradores[n].astype(int))+' ' +data_inicial +' - '+ data_final ,fontsize = 8)      

                        ax.set_ylabel('Tempo funcionamento acima do limite [min]')

                        ax.set_ylim([0,None])

                       # ax.grid()

                        self.autolabel(rect,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Graficos_Analise_Temperatura_Cilindro/Gerador '+str(idxGeradores[n].astype(int)) +'.png')     

                        plt.clf()
                        plt.close('all')
                        del xt, plot_array
                        gc.collect()

                      else:

                          
                        plot_array = np.array([temp_cilindro_A1[n].astype(int),temp_cilindro_A2[n].astype(int),temp_cilindro_A3[n].astype(int),temp_cilindro_A4[n].astype(int),
                                               temp_cilindro_A5[n].astype(int),temp_cilindro_A6[n].astype(int),
                                               temp_cilindro_B1[n].astype(int),temp_cilindro_B2[n].astype(int),temp_cilindro_B3[n].astype(int),temp_cilindro_B4[n].astype(int),
                                               temp_cilindro_B5[n].astype(int),temp_cilindro_B6[n].astype(int)])



                        xt = np.arange(1,len(plot_array) + 1,1)      

                        xlabel = ['Cilindro A1','Cilindro A2','Cilindro A3','Cilindro A4','Cilindro A5','Cilindro A6',
                                  'Cilindro B1','Cilindro B2','Cilindro B3','Cilindro B4','Cilindro B5','Cilindro B6']
        
                        fig, ax = plt.subplots()

                        rect = ax.bar(xt, plot_array,align = 'center')

                        ax.set_xticks(np.arange(1,len(plot_array) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de atividade dos cilindros do Gerador ' + str(idxGeradores[n].astype(int)) +' ' +data_inicial +' - '+ data_final ,fontsize = 8)      

                        ax.set_ylabel('Tempo funcionamento acima do limite [min]')

                        ax.set_ylim([0,None])


                        self.autolabel(rect,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Graficos_Analise_Temperatura_Cilindro/Gerador '+str(idxGeradores[n].astype(int)) +'.png')      

                        plt.clf()
                        plt.close('all')
                        del xt, plot_array
                        gc.collect()

                ###########################################################################################################################################################################################
                ###########################################################################################################################################################################################
                ## Plotagem das temperaturas máximas e mínimas de cada cilindro para cada gerador
                if(analysis_check_vector[1]):


                  if(self.function_is_tupple_empty(np.where(idxGeradores[n] == idx12Cilindros))):

                # Plotar gráfico referente ao minimo e máximo de cada Gerador


                        max_plot_array = np.array([max_cilindro_A1[n].astype(float),max_cilindro_A2[n].astype(float),max_cilindro_A3[n].astype(float),max_cilindro_A4[n].astype(float),
                                              max_cilindro_A5[n].astype(float),max_cilindro_A6[n].astype(float),max_cilindro_A7[n].astype(float),max_cilindro_A8[n].astype(float),
                                               max_cilindro_B1[n].astype(float),max_cilindro_B2[n].astype(float),max_cilindro_B3[n].astype(float),max_cilindro_B4[n].astype(float),
                                               max_cilindro_B5[n].astype(float),max_cilindro_B6[n].astype(float),max_cilindro_B7[n].astype(float),max_cilindro_B8[n].astype(float)])

                        min_plot_array = np.array([min_cilindro_A1[n].astype(float),min_cilindro_A2[n].astype(float),min_cilindro_A3[n].astype(float),min_cilindro_A4[n].astype(float),
                                               min_cilindro_A5[n].astype(float),min_cilindro_A6[n].astype(float),min_cilindro_A7[n].astype(float),min_cilindro_A8[n].astype(float),
                                               min_cilindro_B1[n].astype(float),min_cilindro_B2[n].astype(float),min_cilindro_B3[n].astype(float),min_cilindro_B4[n].astype(float),
                                               min_cilindro_B5[n].astype(float),min_cilindro_B6[n].astype(float),min_cilindro_B7[n].astype(float),min_cilindro_B8[n].astype(float)])

  
                        width = 0.35  # the width of the bars

                        xlabel = ['Cilindro A1','Cilindro A2','Cilindro A3','Cilindro A4','Cilindro A5','Cilindro A6','Cilindro A7','Cilindro A8',
                                  'Cilindro B1','Cilindro B2','Cilindro B3','Cilindro B4','Cilindro B5','Cilindro B6', 'Cilindro B7','Cilindro B8']

              

                        xt = np.arange(1,len(xlabel) + 1,1)     
        
                        fig, ax = plt.subplots()

                        rects1 = ax.bar(xt - width / 2, max_plot_array, width, label='Max Temp')       
                        rects2 = ax.bar(xt + width / 2, min_plot_array, width, label='Min Temp')        


                        ax.set_xticks((np.arange(1,len(xlabel)+1,1)))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de temperatura máxima e mínima dos cilindros do Gerador_' + str(idxGeradores[n].astype(int))+' '+data_inicial +' - '+ data_final ,fontsize = 8)   
                        ax.set_ylabel('Temperatura Cilindro [°C]')

                        ax.set_ylim([0,None])


                        self.autolabel(rects1,ax)
                        self.autolabel(rects2,ax)

                        fig.set_tight_layout(True)


                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Analise_Max_Min/Gerador ' + str(idxGeradores[n].astype(int)) + '.png')        

                        plt.clf()
                        plt.close('all')
                        del xt, max_plot_array, min_plot_array
                        gc.collect()

                  else:



                        max_plot_array = np.array([max_cilindro_A1[n].astype(float),max_cilindro_A2[n].astype(float),max_cilindro_A3[n].astype(float),max_cilindro_A4[n].astype(float),
                                               max_cilindro_A5[n].astype(float),max_cilindro_A6[n].astype(float),
                                               max_cilindro_B1[n].astype(float),max_cilindro_B2[n].astype(float),max_cilindro_B3[n].astype(float),max_cilindro_B4[n].astype(float),
                                               max_cilindro_B5[n].astype(float),max_cilindro_B6[n].astype(float),])

                        min_plot_array = np.array([min_cilindro_A1[n].astype(float),min_cilindro_A2[n].astype(float),min_cilindro_A3[n].astype(float),min_cilindro_A4[n].astype(float),
                                               min_cilindro_A5[n].astype(float),min_cilindro_A6[n].astype(float),
                                               min_cilindro_B1[n].astype(float),min_cilindro_B2[n].astype(float),min_cilindro_B3[n].astype(float),min_cilindro_B4[n].astype(float),
                                               min_cilindro_B5[n].astype(float),min_cilindro_B6[n].astype(float)])


  
                        width = 0.35  # the width of the bars

                        xlabel = ['Cilindro A1','Cilindro A2','Cilindro A3','Cilindro A4','Cilindro A5','Cilindro A6',
                                  'Cilindro B1','Cilindro B2','Cilindro B3','Cilindro B4','Cilindro B5','Cilindro B6']

                 
                        xt = np.arange(1,len(xlabel) + 1,1)     
        
                        fig, ax = plt.subplots()

                        rects1 = ax.bar(xt - width / 2, max_plot_array, width, label='Max Temp')       
                        rects2 = ax.bar(xt + width / 2, min_plot_array, width, label='Min Temp')        


                        ax.set_xticks((np.arange(1,len(xlabel)+1,1)))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de temperatura máxima e mínima dos cilindros do Gerador_' + str(idxGeradores[n].astype(int)) +' ' + data_inicial +' - '+ data_final ,fontsize = 8)   

                        ax.set_ylabel('Temperatura Cilindro [°C]')

                        ax.set_ylim([0,None])

                        self.autolabel(rects1,ax)
                        self.autolabel(rects2,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Analise_Max_Min/Gerador ' + str(idxGeradores[n].astype(int)) + '.png')     
                        
                        plt.clf()
                        plt.close('all')
                        del xt, max_plot_array, min_plot_array
                        gc.collect()

                    ########################################################################################################################################################################################
                    #######################################################################################################################################################################################
                    ## Análise para as temperaturas médias

                  if(analysis_check_vector[6]):


                    if(self.function_is_tupple_empty(np.where(idxGeradores[n] == idx12Cilindros))):
                      
                        mean_plot_array = np.array([mean_cilindro_A1[n].astype(int),mean_cilindro_A2[n].astype(int),mean_cilindro_A3[n].astype(int),mean_cilindro_A4[n].astype(int),
                                               mean_cilindro_A5[n].astype(int),mean_cilindro_A6[n].astype(int),mean_cilindro_A8[n].astype(int),mean_cilindro_A8[n].astype(int),
                                               mean_cilindro_B1[n].astype(int),mean_cilindro_B2[n].astype(int),mean_cilindro_B3[n].astype(int),mean_cilindro_B4[n].astype(int),
                                               mean_cilindro_B5[n].astype(int),mean_cilindro_B6[n].astype(int),mean_cilindro_B7[n].astype(int),mean_cilindro_B8[n].astype(int)])

                        fig, ax = plt.subplots()

                        xt = np.arange(1,len(mean_plot_array) + 1,1)     
  
                        rect = ax.bar(xt, mean_plot_array,align = 'center')

                        ax.set_xticks(np.arange(1,len(mean_plot_array) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de temperatura média dos cilindros do Gerador ' + str(idxGeradores[n].astype(int)) +' ' + data_inicial +' - '+ data_final ,fontsize = 8)           

                        ax.set_ylabel('Temperatura média dos cilindros com motor em funcionamento [°C]')

                        ax.set_ylim([0,None])

                        self.autolabel(rect,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Analise_Temperatura_Media/Gerador ' + str(idxGeradores[n].astype(int)) + '.png')     
                        
                        plt.clf()
                        plt.close('all')
                        del xt, mean_plot_array
                        gc.collect()

                    else:

                        mean_plot_array = np.array([mean_cilindro_A1[n].astype(int),mean_cilindro_A2[n].astype(int),mean_cilindro_A3[n].astype(int),mean_cilindro_A4[n].astype(int),
                                               mean_cilindro_A5[n].astype(int),mean_cilindro_A6[n].astype(int),
                                               mean_cilindro_B1[n].astype(int),mean_cilindro_B2[n].astype(int),mean_cilindro_B3[n].astype(int),mean_cilindro_B4[n].astype(int),
                                               mean_cilindro_B5[n].astype(int),mean_cilindro_B6[n].astype(int)])


                        fig, ax = plt.subplots()

                        xt = np.arange(1,len(mean_plot_array) + 1,1)     
  
                        rect = ax.bar(xt, mean_plot_array,align = 'center')

                        ax.set_xticks(np.arange(1,len(mean_plot_array) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de temperatura média dos cilindros do Gerador ' + str(idxGeradores[n].astype(int))+' '+ data_inicial +' - '+ data_final ,fontsize = 8)   
                        ax.set_ylabel('Temperatura média dos cilindros com motor em funcionamento [°C]')

                        ax.set_ylim([0,None])

                        self.autolabel(rect,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir +'/Analise_Temperatura_Media/Gerador ' + str(idxGeradores[n].astype(int)) + '.png')      

                        plt.clf()
                        plt.close('all')
                        del xt, mean_plot_array
                        gc.collect()

        
                   ###########################################################################################################################################################################################
                   ###########################################################################################################################################################################################


                #finalPos = 11

                if(analysis_check_vector[2]):



                    Tabela_Ordem = pd.DataFrame(np.transpose([idxGeradores,Arrefecimento_Mean,Arrefecimento_Max,tempoArrefecimento.astype(int),Intercooler_Mean,Intercooler_Max,tempoIntercooler.astype(int),Combustivel_Mean,Combustivel_Max,tempoCombustivel.astype(int)]), columns = ['Indice_Geradores','Temp_Arrefecimento_Medio','Temp_Arrefecimento_Max','Tempo Arrefecimento','Temp_Intercooler_Medio','Temp_Intercooler_Max','Tempo Intercooler','Temp_Combustivel_Medio','Temp_Combustivel_Max','Tempo Combustivel'])

                    Tabela_Ordem.to_csv(dir + '/Analise_Liquidos.csv',sep=',',index=False)

                #######################################################################################################################################################################

                if(analysis_check_vector[3]):

                    idxArrefecimento = np.argsort(tempoArrefecimento)
        
                    plt.figure(dpi=1200)

                    fig, ax = plt.subplots()
        
                    rects1 = ax.bar(idxGeradores,tempoArrefecimento[idxArrefecimento].astype(float))   

                    xlabel =  [str(e) for e in idxArrefecimento.astype(int)]
          
                    width = 0.15  # the width of the bars
         
                    xt = np.arange(1,len(xlabel) + 1,1)   

                    ax.set_xticks(np.arange(1,len(idxArrefecimento) + 1,1))

                    ax.set_xticklabels(xlabel)

                    ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                    ax.tick_params(axis = 'x',labelsize = 5)

                    ax.set_title('Ranking de tempo de funcionamento com líquido de Arrefecimento acima do limite ',fontsize = 8)      

                    ax.set_ylabel('Tempo de funcionamento acima do limite [min]')

                    ax.legend()

                    ax.set_ylim([0,None])

                    self.autolabel(rects1,ax)

                    fig.set_tight_layout(True)

                    ax.figure.canvas.draw()

                    fig.savefig(dir + '/Analise_Liquido.png',dpi =600) 



            ######################################################################################################################################################################################################


                if(analysis_check_vector[4]):

                    finalPos = 11

                    for i in np.arange(0,finalPos,1):


   
                        arrefecimentoPlot = np.array(tempoArrefecimento[(i*int(N/finalPos)):((i+1)*int(N/finalPos))])
                        intercoolerPlot = np.array(tempoIntercooler[(i*int(N/finalPos)):((i+1)*int(N/finalPos))])
                        combustivelPlot = np.array(tempoCombustivel[(i*int(N/finalPos)):((i+1)*int(N/finalPos))])
    
        
                        plt.figure(dpi=1200)

                        fig, ax = plt.subplots()
        

                        xlabel = ['Gerador '+str(int(item)) for item in np.array(idxGeradores[(i*int(N/finalPos)):((i+1)*int(N/finalPos))])]
          
                        width = 0.15  # the width of the bars
         
                        xt = np.arange(1,len(xlabel) + 1,1)   

        

                        rects1 = ax.bar(xt - width, arrefecimentoPlot.astype(float), width, label='Arrefecimento')       
                        rects2 = ax.bar(xt , intercoolerPlot.astype(float), width, label='Intercooler')  
                        rects3 = ax.bar(xt + width, combustivelPlot.astype(float), width, label='Combustivel')

   

                        ax.set_xticks(np.arange(1,len(arrefecimentoPlot) + 1,1))

                        ax.set_xticklabels(xlabel,rotation = 90) # Reorganiza os ticks do eixo X para representar os índices dos geradores

                        ax.tick_params(axis = 'x',labelsize = 5)

                        ax.set_title('Analise de tempo de funcionamento com líquidos acima do limite Geradores ' +str(int(N/finalPos)*i+1)+'-'+str((i+1)*int(N/finalPos))+ data_inicial +' - '+ data_final ,fontsize = 8)   

                        ax.set_ylabel('Tempo de funcionamento acima do limite [min]')

                        ax.legend()

                        ax.set_ylim([0,None])

                        # ax.grid()

                        self.autolabel(rects1,ax)
                        self.autolabel(rects2,ax)
                        self.autolabel(rects3,ax)

                        fig.set_tight_layout(True)

                        ax.figure.canvas.draw()

                        fig.savefig(dir+'/Analise_Temperatura_Liquidos/Gerador_' +str(int(N/finalPos)*i+1)+'-'+str((i+1)*int(N/finalPos))+'.png',dpi =600,fontsize = 8)    

                        plt.clf()
                        plt.close('all')
                        del xt, arrefecimentoPlot, intercoolerPlot, combustivelPlot
                        gc.collect()
                      

            operating_generators = 0

            progress_callback.emit(0)

        else:

                 progress_callback.emit((0 / (N - 2)) * 100)
                 self.UMain.MessagBox_2.setText('Nenhuma caixa foi selecionada')
                 self.UMain.MessagBox_2.show()
            


    ##################################################################################################

    def function_Init_Widgets(self):

        self.UMain.VBrowseDir = QtWidgets.QWidget()

    ###################################################################################################





## Bloco de execução Main       
if __name__ == "__main__":
   
    ## Cria o objeto janela principal 
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

   # try:

    LOG_FILENAME = "Traceback.log"
    logging.basicConfig(filename =LOG_FILENAME, level=logging.DEBUG)

    ## Executa o algoritmo que irá inicializar a parte gráfica 

    try:
         ui = Ui_Programa_csv()  

    except Exception:

        logging.exception("Fatal error in main loop")


    ## Executa a rotina que irá executar o ícone que controla a abertura das janelas de comparação
    ui.function_LaunchTrayIcon()
    ### Irá começar a processar os dados dos geradores
    #ui.function_btn_ProcessarDados()

    #except Exception:

        #logging.exception("Fatal error in main loop")

    #ui.function_LaunchWindow()
    
    sys.exit(app.exec_())
