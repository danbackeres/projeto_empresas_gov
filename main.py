import pandas as pd
import os

if __name__ == '__main__':
    try:
        # Definir o caminho base
        base_path = r"D:\Projeto Empresas RF\arquivos"

        # CNAE
        cnaes = pd.read_csv(os.path.join(base_path, "cnae.csv"), sep=';', encoding='ISO-8859-1', header=None)
        cnaes.columns = ['codigo', 'descricao']
        cnaes_interesse = cnaes[cnaes['codigo'].isin([8630501, 8630502, 8630503, 8610101, 8610102])]

        # NATUREZAS
        naturezas = pd.read_csv(os.path.join(base_path, "naturezas.csv"), sep=';', encoding='ISO-8859-1', header=None)
        naturezas.columns = ['codigo', 'descricao']

        # MUNICIPIOS
        municipios = pd.read_csv(os.path.join(base_path, "municipios.csv"), sep=';', encoding='ISO-8859-1', header=None)
        municipios.columns = ['codigo', 'descricao']

        # SIMPLES
        simples = pd.read_csv(os.path.join(base_path, "simples.csv"), sep=';', encoding='ISO-8859-1', header=None)
        simples.columns = ['CNPJ BASICO', 'OPCAO PELO SIMPLES', 'DATA OPCAO SIMPLES', 'DATA EXCLUSAO SIMPLES', 
                           'OPCAO MEI', 'DATA OPCAO MEI', 'DATA EXCLUSAO MEI']

        # Converter CNPJ BASICO para string (object) no arquivo simples
        simples['CNPJ BASICO'] = simples['CNPJ BASICO'].apply(lambda x: str(x).zfill(8))

        # Lista dos municípios de interesse
        municipios_interesse = [5623, 5627, 5637, 5727, 5729, 5705, 5703, 5699, 5697, 5683, 5675, 
                                5673, 5667, 5663, 5661, 5655, 5651, 5647, 5645, 5629, 5611, 5609, 
                                5607, 5603, 5605, 5685, 5687, 5693, 5695, 5689, 5719]

        # EMPRESAS
        chunksize = 10 ** 6
        chunks_empresas = []
        empresas_colunas = [
            'CNPJ BASICO', 'NOME EMPRESARIAL', 'NATUREZA JURIDICA', 'QUALIFICACAO DO RESPONSAVEL', 
            'CAPITAL SOCIAL DA EMPRESA', 'PORTE DA EMPRESA', 'ENTE FEDERATIVO'
        ]
        for chunk in pd.read_csv(os.path.join(base_path, "empresas.csv"), sep=';', encoding='ISO-8859-1', header=None, chunksize=chunksize):
            chunk.columns = empresas_colunas
            chunk['PORTE DA EMPRESA'] = chunk['PORTE DA EMPRESA'].map({
                0: 'NÃO INFORMADO',
                1: 'MICRO EMPRESA',
                3: 'EMPRESA DE PEQUENO PORTE',
                5: 'DEMAIS'
            })
            chunk['CNPJ BASICO'] = chunk['CNPJ BASICO'].apply(lambda x: str(x).zfill(8)) 

            # Substituir o código da NATUREZA JURIDICA pela descrição
            chunk = pd.merge(chunk, naturezas, left_on='NATUREZA JURIDICA', right_on='codigo', how='left')
            chunk.drop(columns='NATUREZA JURIDICA', inplace=True)
            chunk.rename(columns={'descricao': 'NATUREZA JURIDICA'}, inplace=True)

            chunks_empresas.append(chunk)

        empresas = pd.concat(chunks_empresas, ignore_index=True)

        # ESTABELECIMENTOS
        chunksize = 10 ** 6
        chunks = []
        colunas_estabelecimentos = [
            'CNPJ BASICO', 'CNPJ ORDEM', 'CNPJ DV', 'MATRIZ/FILIAL', 'NOME FANTASIA', 
            'SITUACAO CADASTRAL', 'DATA SITUACAO CADASTRAL', 'MOTIVO SITUACAO CADASTRAL', 
            'NOME DA CIDADE NO EXTERIOR', 'PAIS', 'DATA DE INICIO ATIVIDADE', 'CNAE FISCAL PRINCIPAL', 
            'CNAE FISCAL SECUNDARIA', 'TIPO DE LOGRADOURO', 'LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 
            'BAIRRO', 'CEP', 'UF', 'MUNICIPIO', 'DDD 1', 'TELEFONE 1', 'DDD 2', 'TELEFONE 2', 
            'DDD DO FAX', 'FAX', 'EMAIL', 'SITUACAO ESPECIAL', 'DATA DA SITUACAO ESPECIAL'
        ]

        chunk_counter = 0
        for chunk in pd.read_csv(os.path.join(base_path, "estabelecimentos.csv"), sep=';', encoding='ISO-8859-1', header=None, chunksize=chunksize):
            chunk.columns = colunas_estabelecimentos
            chunk['CNPJ ORDEM'] = chunk['CNPJ ORDEM'].apply(lambda x: str(x).zfill(4))
            chunk['CNPJ DV'] = chunk['CNPJ DV'].apply(lambda x: str(x).zfill(2))
            chunk['CNPJ BASICO'] = chunk['CNPJ BASICO'].apply(lambda x: str(x).zfill(8))  
            chunk['CNPJ'] = chunk['CNPJ BASICO'] + chunk['CNPJ ORDEM'] + chunk['CNPJ DV']
            chunk['MATRIZ/FILIAL'] = chunk['MATRIZ/FILIAL'].map({1: 'MATRIZ', 2: 'FILIAL'})
            chunk['TELEFONE 1'] = chunk['DDD 1'].astype(str) + " " + chunk['TELEFONE 1'].astype(str)
            chunk['TELEFONE 2'] = chunk['DDD 2'].astype(str) + " " + chunk['TELEFONE 2'].astype(str)
            chunk['FAX'] = chunk['DDD DO FAX'].astype(str) + " " + chunk['FAX'].astype(str)

            # Substituir o código do MUNICIPIO pela descrição
            chunk = pd.merge(chunk, municipios, left_on='MUNICIPIO', right_on='codigo', how='left')
            chunk.drop(columns='MUNICIPIO', inplace=True)
            chunk.rename(columns={'descricao': 'MUNICIPIO'}, inplace=True)

            # Filtrar por municípios de interesse
            chunk_filtrado = chunk[
                (chunk['SITUACAO CADASTRAL'] == 2) & 
                (chunk['CNAE FISCAL PRINCIPAL'].isin(cnaes_interesse['codigo'])) &
                (chunk['codigo'].isin(municipios_interesse))
            ]
            
            chunk_filtrado = pd.merge(chunk_filtrado, cnaes, left_on='CNAE FISCAL PRINCIPAL', right_on='codigo', how='left')
            chunk_filtrado.drop(columns='CNAE FISCAL PRINCIPAL', inplace=True)
            chunk_filtrado.rename(columns={'descricao': 'CNAE FISCAL PRINCIPAL'}, inplace=True)

            chunks.append(chunk_filtrado)

            chunk_counter += 1
            print(f"Chunk {chunk_counter} processado.")

        df_estabelecimentos_filtrados = pd.concat(chunks, ignore_index=True)

        # Unir empresas e estabelecimentos
        df_final = pd.merge(empresas, df_estabelecimentos_filtrados, on='CNPJ BASICO')

        # Unir com SIMPLES.csv usando o CNPJ BASICO
        df_final = pd.merge(df_final, simples, on='CNPJ BASICO', how='left')

        # Salvar o resultado
        df_final.to_excel("D:\Projeto Empresas RF\estabelecimentos_filtrados.xlsx", index=False)

        print("Processamento concluído. Arquivo 'estabelecimentos_filtrados.xlsx' salvo com sucesso.")

    except Exception as e:
        print(f"Erro durante o processamento: {e}")
