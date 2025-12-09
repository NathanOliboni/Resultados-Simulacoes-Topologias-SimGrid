import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re
from typing import Dict, List, Tuple

class MPILogAnalyzer:
    """Analisador de logs MPI para diferentes configurações de rede"""
    
    def __init__(self, csv_directory: str):
        """
        Inicializa o analisador
        
        Args:
            csv_directory: Diretório contendo os arquivos CSV
        """
        self.csv_directory = Path(csv_directory)
        self.data = {}
        self.results = {}
        
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """
        Extrai informações do nome do arquivo
        
        Args:
            filename: Nome do arquivo CSV
            
        Returns:
            Dicionário com metadados extraídos
        """
        pattern = r'(.+?)_(.+?)_(.+?)_(\d+)_completo\.csv'
        match = re.match(pattern, filename)
        
        if match:
            return {
                'tipo_comunicacao': match.group(1),
                'topologia': match.group(2),
                'tecnologia': match.group(3),
                'num_nos': int(match.group(4)),
                'arquivo': filename
            }
        return None
    
    def load_data(self):
        """Carrega todos os arquivos CSV do diretório"""
        csv_files = list(self.csv_directory.glob('*_completo.csv'))
        
        if not csv_files:
            print(f"Nenhum arquivo CSV encontrado em {self.csv_directory}")
            return
        
        print(f"Encontrados {len(csv_files)} arquivos CSV")
        
        for csv_file in csv_files:
            metadata = self.parse_filename(csv_file.name)
            
            if metadata:
                df = pd.read_csv(csv_file)
                
                # Calcula duração da comunicação
                df['Duracao'] = df['Tempo Final'] - df['Tempo Inicial']
                
                # Cria chave única para identificar a configuração
                key = f"{metadata['tipo_comunicacao']}_{metadata['topologia']}_{metadata['tecnologia']}_{metadata['num_nos']}"
                
                self.data[key] = {
                    'df': df,
                    'metadata': metadata
                }
                
                print(f"✓ Carregado: {csv_file.name}")
    
    def calcular_estatisticas_basicas(self) -> pd.DataFrame:
        """
        Calcula estatísticas básicas para cada configuração
        
        Returns:
            DataFrame com estatísticas resumidas
        """
        stats = []
        
        for key, data in self.data.items():
            df = data['df']
            meta = data['metadata']
            
            stat = {
                'Tipo Comunicação': meta['tipo_comunicacao'],
                'Topologia': meta['topologia'],
                'Tecnologia': meta['tecnologia'],
                'Nº Nós': meta['num_nos'],
                'Tempo Médio (s)': df['Duracao'].mean(),
                'Tempo Mediano (s)': df['Duracao'].median(),
                'Desvio Padrão (s)': df['Duracao'].std(),
                'Tempo Mínimo (s)': df['Duracao'].min(),
                'Tempo Máximo (s)': df['Duracao'].max(),
                'Total Comunicações': len(df)
            }
            
            stats.append(stat)
        
        df_stats = pd.DataFrame(stats)
        self.results['estatisticas_basicas'] = df_stats
        
        return df_stats
    
    def analisar_escalabilidade(self) -> pd.DataFrame:
        """
        Analisa como o tempo médio varia com o número de nós
        
        Returns:
            DataFrame com análise de escalabilidade
        """
        escala = []
        
        # Agrupa por tipo, topologia e tecnologia
        configs = {}
        for key, data in self.data.items():
            meta = data['metadata']
            config_key = f"{meta['tipo_comunicacao']}_{meta['topologia']}_{meta['tecnologia']}"
            
            if config_key not in configs:
                configs[config_key] = []
            
            configs[config_key].append({
                'num_nos': meta['num_nos'],
                'tempo_medio': data['df']['Duracao'].mean(),
                'metadata': meta
            })
        
        # Calcula variações
        for config_key, valores in configs.items():
            valores_ordenados = sorted(valores, key=lambda x: x['num_nos'])
            
            for i in range(len(valores_ordenados) - 1):
                atual = valores_ordenados[i]
                proximo = valores_ordenados[i + 1]
                
                variacao_percentual = ((proximo['tempo_medio'] - atual['tempo_medio']) / 
                                      atual['tempo_medio'] * 100)
                
                escala.append({
                    'Tipo Comunicação': atual['metadata']['tipo_comunicacao'],
                    'Topologia': atual['metadata']['topologia'],
                    'Tecnologia': atual['metadata']['tecnologia'],
                    'De Nós': atual['num_nos'],
                    'Para Nós': proximo['num_nos'],
                    'Tempo Médio Inicial (s)': atual['tempo_medio'],
                    'Tempo Médio Final (s)': proximo['tempo_medio'],
                    'Variação (%)': variacao_percentual,
                    'Variação Absoluta (s)': proximo['tempo_medio'] - atual['tempo_medio']
                })
        
        df_escala = pd.DataFrame(escala)
        self.results['escalabilidade'] = df_escala
        
        return df_escala
    
    def comparar_tecnologias(self) -> pd.DataFrame:
        """
        Compara diferentes tecnologias de interconexão
        
        Returns:
            DataFrame com comparação entre tecnologias
        """
        comp = []
        
        # Agrupa por tipo, topologia e número de nós
        configs = {}
        for key, data in self.data.items():
            meta = data['metadata']
            config_key = f"{meta['tipo_comunicacao']}_{meta['topologia']}_{meta['num_nos']}"
            
            if config_key not in configs:
                configs[config_key] = {}
            
            configs[config_key][meta['tecnologia']] = {
                'tempo_medio': data['df']['Duracao'].mean(),
                'metadata': meta
            }
        
        # Compara tecnologias
        for config_key, tecnologias in configs.items():
            if len(tecnologias) > 1:
                techs = list(tecnologias.keys())
                
                for i in range(len(techs)):
                    for j in range(i + 1, len(techs)):
                        tech1 = techs[i]
                        tech2 = techs[j]
                        
                        tempo1 = tecnologias[tech1]['tempo_medio']
                        tempo2 = tecnologias[tech2]['tempo_medio']
                        
                        melhor = tech1 if tempo1 < tempo2 else tech2
                        diferenca_percentual = abs((tempo2 - tempo1) / tempo1 * 100)
                        
                        comp.append({
                            'Tipo Comunicação': tecnologias[tech1]['metadata']['tipo_comunicacao'],
                            'Topologia': tecnologias[tech1]['metadata']['topologia'],
                            'Nº Nós': tecnologias[tech1]['metadata']['num_nos'],
                            'Tecnologia 1': tech1,
                            'Tempo Médio 1 (s)': tempo1,
                            'Tecnologia 2': tech2,
                            'Tempo Médio 2 (s)': tempo2,
                            'Melhor': melhor,
                            'Diferença (%)': diferenca_percentual,
                            'Diferença Absoluta (s)': abs(tempo2 - tempo1)
                        })
        
        df_comp = pd.DataFrame(comp)
        self.results['comparacao_tecnologias'] = df_comp
        
        return df_comp
    
    def comparar_topologias(self) -> pd.DataFrame:
        """
        Compara diferentes topologias de rede
        
        Returns:
            DataFrame com comparação entre topologias
        """
        comp = []
        
        # Agrupa por tipo, tecnologia e número de nós
        configs = {}
        for key, data in self.data.items():
            meta = data['metadata']
            config_key = f"{meta['tipo_comunicacao']}_{meta['tecnologia']}_{meta['num_nos']}"
            
            if config_key not in configs:
                configs[config_key] = {}
            
            configs[config_key][meta['topologia']] = {
                'tempo_medio': data['df']['Duracao'].mean(),
                'metadata': meta
            }
        
        # Compara topologias
        for config_key, topologias in configs.items():
            if len(topologias) > 1:
                topos = list(topologias.keys())
                
                for i in range(len(topos)):
                    for j in range(i + 1, len(topos)):
                        topo1 = topos[i]
                        topo2 = topos[j]
                        
                        tempo1 = topologias[topo1]['tempo_medio']
                        tempo2 = topologias[topo2]['tempo_medio']
                        
                        melhor = topo1 if tempo1 < tempo2 else topo2
                        diferenca_percentual = abs((tempo2 - tempo1) / tempo1 * 100)
                        
                        comp.append({
                            'Tipo Comunicação': topologias[topo1]['metadata']['tipo_comunicacao'],
                            'Tecnologia': topologias[topo1]['metadata']['tecnologia'],
                            'Nº Nós': topologias[topo1]['metadata']['num_nos'],
                            'Topologia 1': topo1,
                            'Tempo Médio 1 (s)': tempo1,
                            'Topologia 2': topo2,
                            'Tempo Médio 2 (s)': tempo2,
                            'Melhor': melhor,
                            'Diferença (%)': diferenca_percentual,
                            'Diferença Absoluta (s)': abs(tempo2 - tempo1)
                        })
        
        df_comp = pd.DataFrame(comp)
        self.results['comparacao_topologias'] = df_comp
        
        return df_comp
    
    def gerar_graficos(self, output_dir: str = 'graficos'):
        """
        Gera gráficos de análise
        
        Args:
            output_dir: Diretório para salvar os gráficos
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        sns.set_style("whitegrid")
        
        # Agrupa dados por padrão de comunicação
        padroes = {}
        for key, data in self.data.items():
            padrao = data['metadata']['tipo_comunicacao']
            if padrao not in padroes:
                padroes[padrao] = []
            padroes[padrao].append((key, data))
        
        # Para cada padrão, gerar UMA IMAGEM separada
        for padrao, dados_padrao in sorted(padroes.items()):
        
            plt.figure(figsize=(10, 6))
            
            # Agrupa por topologia e tecnologia
            configs = {}
            for key, data in dados_padrao:
                meta = data['metadata']
                config_label = f"{meta['topologia']}-{meta['tecnologia']}"
                
                if config_label not in configs:
                    configs[config_label] = {'nos': [], 'tempos': []}
                
                configs[config_label]['nos'].append(meta['num_nos'])
                configs[config_label]['tempos'].append(data['df']['Duracao'].mean())
        
            # Plotar cada curva (configuração topo-tec)
            for config_label, valores in configs.items():
                # Ordena os pontos: 16, 32, 64
                nos_ordenados = np.argsort(valores['nos'])
        
                plt.plot(
                    [valores['nos'][i] for i in nos_ordenados],
                    [valores['tempos'][i] for i in nos_ordenados],
                    marker='o', markersize=8, linewidth=2, label=config_label, alpha=0.7
                )
        
            plt.xlabel('Número de Nós', fontsize=11)
            plt.ylabel('Tempo Médio (s)', fontsize=11)
            plt.title(f'Escalabilidade — Padrão: {padrao.upper()}', fontsize=13, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.xticks([16, 32, 64])
            plt.legend(fontsize=9, loc='best')
        
            # 🔥 Salvar 1 PNG por padrão
            nome_fig = output_path / f'escalabilidade_{padrao}.png'
            plt.savefig(nome_fig, dpi=300, bbox_inches='tight')
            plt.close()
                
        # 2. Comparação de tecnologias (heatmap)
        for padrao, dados_padrao in sorted(padroes.items()):
            # Cria matriz para heatmap
            topologias = sorted(set(d['metadata']['topologia'] for _, d in dados_padrao))
            tecnologias = sorted(set(d['metadata']['tecnologia'] for _, d in dados_padrao))
            nos_list = sorted(set(d['metadata']['num_nos'] for _, d in dados_padrao))
            
            fig, axes = plt.subplots(1, len(nos_list), figsize=(6*len(nos_list), 5))
            if len(nos_list) == 1:
                axes = [axes]
            
            for idx, num_nos in enumerate(nos_list):
                matriz = np.zeros((len(topologias), len(tecnologias)))
                
                for i, topo in enumerate(topologias):
                    for j, tech in enumerate(tecnologias):
                        # Busca tempo médio para esta configuração
                        for _, data in dados_padrao:
                            meta = data['metadata']
                            if (meta['topologia'] == topo and 
                                meta['tecnologia'] == tech and 
                                meta['num_nos'] == num_nos):
                                matriz[i, j] = data['df']['Duracao'].mean()
                                break
                
                # Substitui zeros por NaN para melhor visualização
                matriz[matriz == 0] = np.nan
                
                sns.heatmap(matriz, annot=True, fmt='.6f', cmap='YlOrRd', 
                           xticklabels=tecnologias, yticklabels=topologias,
                           ax=axes[idx], cbar_kws={'label': 'Tempo Médio (s)'})
                axes[idx].set_title(f'{num_nos} Nós', fontsize=12)
                axes[idx].set_xlabel('Tecnologia', fontsize=10)
                axes[idx].set_ylabel('Topologia', fontsize=10)
            
            plt.suptitle(f'Comparação de Desempenho - {padrao.upper()}', 
                        fontsize=14, fontweight='bold', y=1.02)
            plt.tight_layout()
            plt.savefig(output_path / f'heatmap_{padrao}.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Boxplot comparativo por tipo de comunicação e tecnologia
        for padrao in sorted(padroes.keys()):
            tecnologias = sorted(set(d['metadata']['tecnologia'] for _, d in padroes[padrao]))
            
            fig, axes = plt.subplots(1, len(tecnologias), figsize=(7*len(tecnologias), 8))
            if len(tecnologias) == 1:
                axes = [axes]
            
            for idx, tecnologia in enumerate(tecnologias):
                dados_plot = []
                labels_plot = []
                
                for num_nos in [16, 32, 64]:
                    for topologia in sorted(set(d['metadata']['topologia'] for _, d in padroes[padrao])):
                        for key, data in self.data.items():
                            meta = data['metadata']
                            if (meta['tipo_comunicacao'] == padrao and 
                                meta['topologia'] == topologia and
                                meta['tecnologia'] == tecnologia and
                                meta['num_nos'] == num_nos):
                                dados_plot.append(data['df']['Duracao'].values)
                                labels_plot.append(f"{topologia}\n{num_nos}n")
                
                if dados_plot:
                    bp = axes[idx].boxplot(dados_plot, labels=labels_plot, patch_artist=True)
                    
                    # Colorir por topologia
                    cores_topo = {'fattree': 'lightblue', 'torus': 'lightgreen', 'dragonfly': 'lightyellow'}
                    for patch, label in zip(bp['boxes'], labels_plot):
                        topo = label.split('\n')[0]
                        patch.set_facecolor(cores_topo.get(topo, 'white'))
                
                    axes[idx].set_title(f'{tecnologia.upper()}', fontsize=12, fontweight='bold')
                    axes[idx].set_ylabel('Duração (s)', fontsize=11)
                    axes[idx].tick_params(axis='x', rotation=45, labelsize=9)
                    axes[idx].grid(True, alpha=0.3, axis='y')
            
            plt.suptitle(f'Distribuição de Tempos - {padrao.upper()}', 
                fontsize=14, fontweight='bold', y=1.02)
            plt.tight_layout()
            plt.savefig(output_path / f'boxplot_{padrao}.png', dpi=300, bbox_inches='tight')
            plt.close()        
        # 4. Gráfico de barras - Melhor configuração por padrão
        fig, ax = plt.subplots(figsize=(14, 8))
        
        melhores = []
        padroes_ordem = []
        
        for padrao, dados_padrao in sorted(padroes.items()):
            melhor_tempo = float('inf')
            melhor_config = None
            
            for key, data in dados_padrao:
                tempo_medio = data['df']['Duracao'].mean()
                if tempo_medio < melhor_tempo:
                    melhor_tempo = tempo_medio
                    melhor_config = data['metadata']
            
            if melhor_config:
                melhores.append(melhor_tempo)
                padroes_ordem.append(f"{padrao}\n({melhor_config['topologia']}-{melhor_config['tecnologia']}-{melhor_config['num_nos']}n)")
        
        bars = ax.bar(range(len(melhores)), melhores, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xticks(range(len(melhores)))
        ax.set_xticklabels(padroes_ordem, rotation=45, ha='right', fontsize=10)
        ax.set_ylabel('Tempo Médio (s)', fontsize=12)
        ax.set_title('Melhor Desempenho por Padrão de Comunicação', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores nas barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.6f}s', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path / 'melhores_configuracoes.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n✓ Gráficos salvos em: {output_path}")
        print(f"  - escalabilidade_por_padrao.png")
        print(f"  - heatmap_[padrao].png (um para cada padrão)")
        print(f"  - boxplot_tecnologias.png")
        print(f"  - melhores_configuracoes.png")
    
    def gerar_relatorio_completo(self, output_file: str = 'relatorio_analise.txt'):
        """
        Gera um relatório completo em texto
        
        Args:
            output_file: Arquivo de saída do relatório
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RELATÓRIO DE ANÁLISE DE LOGS MPI\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total de configurações analisadas: {len(self.data)}\n\n")
            
            # Estatísticas básicas
            if 'estatisticas_basicas' in self.results:
                f.write("\n" + "="*80 + "\n")
                f.write("1. ESTATÍSTICAS BÁSICAS\n")
                f.write("="*80 + "\n\n")
                f.write(self.results['estatisticas_basicas'].to_string(index=False))
                f.write("\n")
            
            # Escalabilidade
            if 'escalabilidade' in self.results:
                f.write("\n" + "="*80 + "\n")
                f.write("2. ANÁLISE DE ESCALABILIDADE\n")
                f.write("="*80 + "\n\n")
                f.write(self.results['escalabilidade'].to_string(index=False))
                f.write("\n")
            
            # Comparação de tecnologias
            if 'comparacao_tecnologias' in self.results:
                f.write("\n" + "="*80 + "\n")
                f.write("3. COMPARAÇÃO DE TECNOLOGIAS\n")
                f.write("="*80 + "\n\n")
                f.write(self.results['comparacao_tecnologias'].to_string(index=False))
                f.write("\n")
            
            # Comparação de topologias
            if 'comparacao_topologias' in self.results:
                f.write("\n" + "="*80 + "\n")
                f.write("4. COMPARAÇÃO DE TOPOLOGIAS\n")
                f.write("="*80 + "\n\n")
                f.write(self.results['comparacao_topologias'].to_string(index=False))
                f.write("\n")
        
        print(f"\n✓ Relatório salvo em: {output_file}")


# Exemplo de uso
if __name__ == "__main__":
    # Inicializa o analisador
    analyzer = MPILogAnalyzer(csv_directory='../../resultados/csv_compilados_simulacao2/')
    
    # Carrega os dados
    analyzer.load_data()
    
    # Executa análises
    print("\n" + "="*80)
    print("EXECUTANDO ANÁLISES")
    print("="*80)
    
    print("\n1. Calculando estatísticas básicas...")
    stats = analyzer.calcular_estatisticas_basicas()
    print(stats)
    
    print("\n2. Analisando escalabilidade...")
    escala = analyzer.analisar_escalabilidade()
    print(escala)
    
    print("\n3. Comparando tecnologias de interconexão...")
    comp_tech = analyzer.comparar_tecnologias()
    print(comp_tech)
    
    print("\n4. Comparando topologias...")
    comp_topo = analyzer.comparar_topologias()
    print(comp_topo)
    
    # Gera gráficos
    print("\n5. Gerando gráficos...")
    analyzer.gerar_graficos()
    
    # Gera relatório completo
    print("\n6. Gerando relatório completo...")
    analyzer.gerar_relatorio_completo()
    
    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA!")
    print("="*80)