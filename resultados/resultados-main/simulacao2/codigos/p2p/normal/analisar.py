import pandas as pd

def analisar_trace_completo(nome_arquivo_trace):
    """
    Analisa um arquivo de trace Paje, extraindo a ação do processo de origem
    e o estado do processo de destino para cada comunicação.

    Args:
        nome_arquivo_trace (str): O caminho para o arquivo .trace.

    Returns:
        pandas.DataFrame: Um DataFrame com a análise completa.
    """
    state_definitions = {}
    current_rank_states = {}
    links_started = {}
    communications = []

    print(f"Analisando o arquivo: {nome_arquivo_trace}")

    with open(nome_arquivo_trace, 'r') as f:
        for line in f:
            if line.startswith('%') or not line.strip():
                continue

            parts = line.split()
            event_type = parts[0]

            try:
                # 5: PajeDefineEntityValue (Define o nome de um estado)
                if event_type == '5' and parts[2] == '2':
                    state_id = parts[1]
                    state_name = parts[3].strip('"')
                    state_definitions[state_id] = state_name

                # 12: PajePushState (Um rank entra em um estado)
                elif event_type == '12':
                    rank_id = parts[3]
                    state_id = parts[4]
                    current_rank_states[rank_id] = state_id

                # 15: PajeStartLink (Início de uma comunicação)
                elif event_type == '15':
                    start_time = float(parts[1])
                    origin_rank = parts[5]
                    key = parts[6]

                    origin_action = "Unknown"
                    if origin_rank in current_rank_states:
                        state_id = current_rank_states[origin_rank]
                        if state_id in state_definitions:
                            origin_action = state_definitions[state_id]

                    links_started[key] = {
                        'start_time': start_time,
                        'origin': origin_rank,
                        'origin_action': origin_action
                    }

                # 16: PajeEndLink (Fim de uma comunicação)
                elif event_type == '16':
                    end_time = float(parts[1])
                    destination_rank = parts[5]
                    key = parts[6]

                    if key in links_started:
                        start_info = links_started.pop(key)
                        
                        # --- ALTERAÇÃO PRINCIPAL AQUI ---
                        # Captura também o estado do processo de destino
                        destination_state = "Unknown"
                        if destination_rank in current_rank_states:
                            state_id = current_rank_states[destination_rank]
                            if state_id in state_definitions:
                                destination_state = state_definitions[state_id]

                        communications.append({
                            'Rank Origem': start_info['origin'],
                            'Rank Destino': destination_rank,
                            'Ação da Origem': start_info['origin_action'],
                            'Estado do Destino': destination_state,
                            'Tempo Inicial': start_info['start_time'],
                            'Tempo Final': end_time
                        })
            except (IndexError, ValueError):
                pass

    return pd.DataFrame(communications)

# --- Execução Principal ---
if __name__ == "__main__":
    nome_do_arquivo = 'gt.trace'
    df_resultado = analisar_trace_completo(nome_do_arquivo)

    if not df_resultado.empty:
        nome_arquivo_saida = 'communication_analysis_completo.csv'
        df_resultado.to_csv(nome_arquivo_saida, index=False)
        print(f"\nAnálise completa concluída com sucesso!")
        print(f"{len(df_resultado)} comunicações foram analisadas.")
        print(f"Resultados salvos em: {nome_arquivo_saida}")
        print("\nAs 15 primeiras comunicações encontradas:")
        print(df_resultado.head(15))
    else:
        print("Nenhuma comunicação completa foi encontrada no arquivo.")
