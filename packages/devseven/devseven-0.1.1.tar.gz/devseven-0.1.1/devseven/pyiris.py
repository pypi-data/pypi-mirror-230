# Databricks notebook source
class PyirisPath(str):

  def split_path(self):
    # Cria array separando o path em partes
    split_path = self.split('/')
    
    # remove do array itens vazios
    for item in split_path:
      if item == '':
        split_path.remove(item)
    
    return split_path

  def get_mount_name(self):
    # Converte o path em array
    split_path = self.split_path()

    # Pega o mount name do path
    return split_path[1]
  
  def get_country(self):
    # Converte o path em array
    split_path = self.split_path()

    # Pega o país do path
    return split_path[2]

  def get_table_name(self):
    # Converte o path em array
    split_path = self.split_path()

    # Pega o tamanho do array
    length = len(split_path)

    # Procura pelo nome do dataset
    pos_table_name = -1
    for i in range(-1, -length, -1):
      if (split_path[i].find('=') < 0) and (split_path[i].find('*') < 0) and (not split_path[i].isnumeric()):
        pos_table_name = i
        break
    
    count = 0
    table_name = split_path[pos_table_name]
    lower_table_name = ''
    for c in table_name:
      if c.isupper() and count == 0:
        lower_table_name += c.lower()
        count += 1
      elif c.isupper() and count > 0:
        lower_table_name += '_' + c.lower()
        count += 1
      elif c.islower():
        lower_table_name += c
        count += 1
    
    return lower_table_name

  def get_relative_path(self):
    # Converte o path em array
    split_path = self.split_path()

    # Pega o tamanho do array
    length = len(split_path)

    # Pega o path relativo do path completo
    relative_path = ''
    for i in range(3, length):
      relative_path += split_path[i]
      if i < length - 1:
        relative_path += '/'
    
    return relative_path

# path_hz = PyirisPath('/mnt/historyzone/Brazil/SolarWinds/WifiPerformance/active=True/')
# print(path_hz)
# print(path_hz.get_mount_name())
# print(path_hz.get_country())
# print(path_hz.get_relative_path())
# print(path_hz.get_table_name())
