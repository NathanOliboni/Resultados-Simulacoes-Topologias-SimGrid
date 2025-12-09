#!/bin/bash

# Verificar se foi fornecido um número como argumento
if [ $# -ne 1 ] || ! [[ $1 =~ ^[0-9]+$ ]]; then
    echo "Uso: $0 <número_de_nós>"
    echo "Exemplo: $0 360"
    exit 1
fi

# Número de nós definido pelo usuário
num_nodes=$1

# Nome do arquivo de saída
output_file="hostfile.txt"

# Gerar as entradas para cada nó
for ((i=0; i<num_nodes; i++)); do
    echo "node${i}.simgrid.org" >> hostfile.txt
done

echo "Arquivo $output_file criado com sucesso com $num_nodes nós."
