import numpy as np
import pandas as pd
import pyodbc



# Conjunto de String utilizado para realizar a busca, atualização ou modificação ds dados do banco de dados  

# Comando SQL insert vai colocar novos dados na tabela, sem apagar os antigos. Os dados sempre serão inseridos 
# na parte de baixo da tabela, não no topo. No caso do PYODBC a estrutura vai ser 'INSERT INTO' + 'nome da tabela'+ 
# 'tuple com nome das colunas' + 'VALUES'+ 'indicação do tupple com a quantidade de valores que serão inseridos'
# A ordem na qual os dados vão asusmir os valores das interrogações, será igual a ordem na qual a função recebeu o tupple
#  
insert_gen_rank_data = """ 

            INSERT INTO ps.dbo.GEN_RANK(GEN_IDX,RANK,MAX_RANK,MIN_RANK)
            VALUES (?,?,?,?)
"""

# Comando SQL update vai atualizar os dados da tabela, apagando os antigos.
# No caso do PYODBC a estrutura vai ser 'UPDATE' + 'nome da tabela'+ 
# 'Nome da coluna' +'= ?'+ 'WHERE' + 'Nome da Coluna ' + '=?'. Caso não queira uma linha específica, 
# utilizar o operando '*' que vai atualizar todas as linha com o mesmo valor. O comando GETDATE(), vai inserir
# o timestamp do horário no qual o dado for colocado no servidor 


update_gen_rank_data = """ 

            UPDATE ps.dbo.GEN_RANK SET  RANK = ?, MAX_RANK = ?, MIN_RANK = ?, E3TimeStamp = GETDATE()  WHERE GEN_IDX = ?

"""

##############################################################################################################################

update_gen_rank_data_test = """ 

            UPDATE ps.dbo.GEN_RANK_TEST SET  RANK = ?, MAX_RANK = ?, MIN_RANK = ?, E3TimeStamp = GETDATE()  WHERE GEN_IDX = ?

"""

###############################################################################################################################

update_gen_rank_data_timeStamp = """ 

            UPDATE ps.dbo.GEN_RANK_TEST SET  E3TimeStamp = GETDATE()  WHERE GEN_IDX = ?

"""

###############################################################################################################################

update_gen_log_data = """ 

            INSERT INTO ps.dbo.GEN_LOG(GEN_IDX,E3TimeStamp,CRITICIDADE,VALOR_LOG,VARIACAO_RANK) VALUES (?,GETDATE(),?,?,?)

"""

###############################################################################################################################

update_timestamp_gen_rank_data = """ 

            UPDATE ps.dbo.GEN_RANK SET E3TimeStamp = ?  WHERE GEN_IDX = 1

"""


################################################################################################################################

insert_timestamp_gen_rank_data = """ 

            INSERT INTO ps.dbo.GEN_RANK(E3TimeStamp)
            VALUES (?)

"""

##################################################################################################################################
insert_hist_rank_data = """ 

            INSERT INTO ps.dbo.GEN_HIST_RANK (GEN_IDX,E3TimeStamp,RANK) VALUES (?,GETDATE(),?)

 """


 ###############################################################################################################################

insert_hist_rank_data_test = """ 

            INSERT INTO ps.dbo.GEN_HIST_RANK_TEST (GEN_IDX,E3TimeStamp,RANK) VALUES (?,GETDATE(),?)

 """
 ################################################################################################################################

 ###############################################################################################################################

insert_idx_log_table = """ 

            INSERT INTO ps.dbo.GEN_LOG (GEN_IDX,E3TimeStamp) VALUES (?,GETDATE())

 """
 ################################################################################################################################



 # O comando SELECT escolhe quais dados da tabela serão apresentados ao usuário, neste caso,transferido para um DataFrame. A estrutura será 'SELECT' + 'NOME DA COLUNA' + 'FROM' + 'NOME DA TABELA'.
 # Caso deseja transferir toda a tabela, utilizar o operador '*' no lugar do nome da coluna

select_operating_data = """ 

            SELECT Ligado FROM  ps.dbo.GeradoresAtual
 """

 # Esse comando é mais complexo, porque utiliza os comandos LIKE, ORDER BY. O 'ORDER BY' vai ordernar a tabela de acordo com uma coluna e se vai ser ascendente 'ASC' ou descendente 'DSC'. No caso vai ser de 
 # acordo com a coluna do nome da tabela. O operador 'LIKE'  

list_all_tables_querry = """ SELECT TABLE_NAME FROM ps.INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME NOT LIKE '%_Fields' AND TABLE_NAME NOT LIKE '%RANK' AND TABLE_NAME LIKE 'GEN%' ORDER BY TABLE_NAME ASC """ 


list_all_tables_querry_test = """ SELECT TABLE_NAME FROM ps.INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME NOT LIKE '%_Fields' AND TABLE_NAME NOT LIKE '%RANK' AND TABLE_NAME NOT LIKE '%TEST' AND TABLE_NAME LIKE 'GEN%' AND TABLE_NAME NOT LIKE '%LOG' AND TABLE_NAME NOT LIKE 'GEN_MANUT%' AND TABLE_NAME NOT LIKE 'GEN_TROCA%' ORDER BY TABLE_NAME ASC """ 


select_rank_hist = """ 

            SELECT * FROM  ps.dbo.GEN_RANK
 """


# Função irá atualizar a tabela de valores máximos e mínimos dos rankings. Passar por referência um dataframe da tabela de rankings
# e um vetor com os rankings atuais 

def function_update_rank_table(rank_table,ranks):


    for i in np.arange(0,len(ranks),1):
        
        if(ranks[i]<rank_table['MIN_RANK'][i]):
                
                rank_table['MIN_RANK'][i] = ranks[i]

        if(ranks[i]>rank_table['MAX_RANK'][i]):
                
                rank_table['MAX_RANK'][i] = ranks[i]

        rank_table['RANK'][i]  = ranks[i]


# Essa função tem como objetivo atualiazar a tabela de ranks que está no servidor. Receberá por referência o objeto conector, tabela de rank atualizada
# e a string contendo o comando a ser executado no banco de dados 
def function_update_rank_DB_table(con,querry,table):

    # Quando for inserir ou dar update em múltiplas linhas da tabela, é necessário transformar as colunas de dados em uma lista de tuples
    # e utilizar o comando executemany. Este comando funciona como um loop e inseri linha a linha da lista

    cursor = con.cursor()
    cursor.commit()

    print('Updating ranking data')
    cursor.executemany(querry, (list(zip(*((table['RANK'],table['MAX_RANK'],table['MIN_RANK'],table['GEN_IDX']))))))

# Essa função tem como objetivo atualiazar a tabela de ranks que está no servidor. Receberá por referência o objeto conector, tabela de rank atualizada
# e a string contendo o comando a ser executado no banco de dados 
def function_update_rank_DB_table_TimeStamp(con,querry,table):

    # Quando for inserir ou dar update em múltiplas linhas da tabela, é necessário transformar as colunas de dados em uma lista de tuples
    # e utilizar o comando executemany. Este comando funciona como um loop e inseri linha a linha da lista

    cursor = con.cursor()
    cursor.commit()

    print('Updating Time_Stamp')

    for i in np.arange(0,len(table['GEN_IDX']),1):

        #print(table['GEN_IDX'][i])
        cursor.execute(querry, (int(table['GEN_IDX'][i])))


# Essa função irá verificar se algum gerador está em funcionamento e devolve uma flag indicando o estado. Receberá por referência o objeto conector 
# e a querry para recuperar essa tablea do banco de dados
def function_check_gen_status(con,querry):

    # A biblioteca pandas possui um comando que converte uma tabela SQL em um dataframe. O comando só precisa do objeto conector e o comando em SQL
    # Os nomes das colunas do dataframe serão os nomes das colunas da tabela do banco de dados  
    active_generator_table = pd.read_sql_query(querry, con)
    if(np.sum(np.array(active_generator_table['Ligado']))):
        
        return True

    else:

        return False


# Essa função insere os novos dados na tabela de histórico de ranks dos geradores 
def function_update_hist_rank_data(con,querry,rank_table):

    print('Updating history ranking data')

    cursor = con.cursor()
    cursor.commit()

    cursor.executemany(querry,(list(zip(*((rank_table['GEN_IDX'],rank_table['RANK']))))))

    cursor.close()
    
## Essa função é para a atualização dos valores do LOG no supervisório do gerador
def function_update_log_table(con,querry,log_table):

    print('Updating Log Table')

    cursor = con.cursor()
    cursor.commit()

    cursor.executemany(querry,(list(zip(*((log_table['GEN_IDX'],log_table['CRITICIDADE'],log_table['VALOR_LOG'],log_table['VARIACAO_RANK']))))))

    cursor.close()

# Essa função salva os dados históricos em um arquivo CSV para uso futuro
 
def function_save_hist_variables_to_CSV(Table):

    try:

        Table.to_CSV(r'C:\Users\Ricardo Barbosa\Documents\mySQL_Python_V4\Hist_Variable_Table.csv',sep=',',decimal='.')

    except Exception as e: print(e)



def function_list_DB_table(con,querry):

     #try:

            table_list = pd.read_sql_query(querry, con) 

            return table_list

     #except Exception as e: print(e)
##################################################################################################################
##
def function_find_critical_states(critical_array,status_array):

        if (status_array<0.15):
            critical_array=0

        if ((status_array>0.15)and(status_array<0.35)):
            critical_array=1

        if ((status_array>0.35)and(status_array<0.60)):
            critical_array=2

        if (status_array>0.60):
            critical_array=3

#################################################################################################################

##################################################################################################################
## Função para determinar qual variável teve a maior mudança percentual, caso ocorra uma mudança negativa no score
## A ordem dos índices é tempoInterCooler,tempoLiquido,horimetro,numeroReligamento,consumo, consumo_Partida
def function_find_log_value(log_valor,max_diff_idx,diff_porct):

        # Caso seja a primeira que o código esteja sendo executado, escrever que não há dados
        if((max_diff_idx == -2)):

                  log_valor = "Ainda nao ha dados para comparacao"
                  print(log_valor)

        # Caso não ocorra mudança nas variáveis do gerador, por estar desligado ou realmente não ter
        # ocorrido mudanças
        elif(max_diff_idx == -1):

                  log_valor = "Nenhuma variavel sofreu alteracao"
                  print(log_valor)


        else:

                
                # Existem diversos tipos de combinação que podem ocorrer enquanto a mudança do Log
                # Podem ocorrer variações em 6 variáveis diferentes com 5 graus de variação:
                # Nenhuma, Leve, Moderada, Alta e Significativa

                if (diff_porct == 0):
                    State_string = "Teve nenhuma mudanca no"

                elif ((diff_porct>0)and(diff_porct<0.15)):
                    State_string = "Teve mudanca leve no"

                elif ((diff_porct>0.15)and(diff_porct<0.35)):
                    State_string = "Teve mudanca moderada no"

                elif ((diff_porct>0.35)and(diff_porct<0.60)):
                    State_string = "Teve mudanca alta no"

                else:
                    State_string = "Teve mudanca significativa no"


                # Uma string para cada variável e cada variação foi montada e ao determinar qual delas será utilizada
                # unir as string e salvar na variável 

                if (max_diff_idx == 0):
                    Var_string = " TempoInterCooler "

                elif (max_diff_idx == 1):
                    Var_string = " TempoLiquido "

                elif (max_diff_idx == 2):
                    Var_string = " Horimetro "

                elif (max_diff_idx == 3):
                    Var_string = " Numero Religamento "

                elif (max_diff_idx == 4):
                    Var_string = " Consumo "

                else:
                    Var_string = " Consumo na Partida "


                log_valor =  State_string + Var_string
                print(log_valor)

#####################################################################################################################       