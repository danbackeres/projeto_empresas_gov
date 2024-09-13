# Projeto de Unificação dos Dados Abertos do CNPJ

Este projeto em **Python** visa a unificação dos **Dados Abertos do Cadastro Nacional de Pessoa Jurídica (CNPJ)**, disponibilizados pelo Governo Federal. O objetivo principal é processar, filtrar e consolidar os dados de empresas e estabelecimentos com base em critérios definidos, como o CNAE e o município de operação.

Sinta-se à vontade para pegar como exemplo, filtrar e estabelecer regras para sua necessidade.

O legal desse projeto é mostrar que você pode encontrar e usar os dados das empresas cadastras no Brasil para diversos fins.

## Fonte dos Dados

Os dados utilizados neste projeto são provenientes do portal de dados abertos do Governo Federal, que basicamente é um repositório de dados. Disponível neste link:
<https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj>

## Prepare os Arquivos

### 1. Como Obter os Dados

Para obter os dados do [site](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj) do governo, siga os passos abaixo.

Para o meu exemplo, baixei os dados do Cnae, Empresas, Estabelecimentos, Simples, Municípios e Natureza.

1. Acesse o site: <https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj>;
2. Clique no menu **Recursos** para expandí-lo;
3. Confira a estrutura de dados na seção **Dicionário de Dados do Cadastro Nacional da Pessoa Jurídica**. Essa estrutura é importante para você entender como é o relacionamento entre os objetos (arquivos) e o que eventualmente poderá usar para filtrar os dados;
4. Baixe os dados na seção **DADOS ABERTOS CNPJ**
   1. Ao acessar o [Recurso](https://dadosabertos.rfb.gov.br/CNPJ/dados_abertos_cnpj/?C=N;O=D), você verá uma estrutura de pastas. Os dados são atualizados mensalmente;
   2. Acesse o diretório mais recente;
   3. Os dados de empresas e estabelecimentos são fraguimentados em vários arquivos `.zip`. Você deverá baixar todos.

NOTA: o campo CNPJ BÁSICO é presente em todas as bases (empresas, estabelecimentos, simples, socios) e ele será o identificador para relacionar os objetos dessas bases.

### 2. Como Extrair os Dados

PAra a extração e junção dos arquivos, você pode fazer de forma manual ou executar o script a seguir no _PowerShell_ do Windows, no caso dos arquivos das Empresas e Estabelecimentos.

Antes de executar o script, primeiro organizei e extraí os arquivos Cnae, Simples, Município e Natureza, conforme mostro abaixo.

![arquivos-para-processar](https://raw.githubusercontent.com/danbackeres/projeto_empresas_gov/main/img/arquivos-para-processar.png)

Depois executei o script:

```bash
# Diretório
$basePath = "D:\Projeto Empresas RF\arquivos"

# 1. Extrai os arquivos do Zip
Get-ChildItem -Path $basePath -Filter "*.zip" | ForEach-Object {
    Expand-Archive -Path $_.FullName -DestinationPath $basePath
}

# 2. Junta os arquivos Empresas
Get-ChildItem -Path $basePath -Filter "*.EMPRECSV" | ForEach-Object {
    Get-Content $_.FullName | Add-Content "$basePath\empresas.csv"
}

# 3. Junta os arquivos Estabelecimentos
Get-ChildItem -Path $basePath -Filter "*.ESTABELE" | ForEach-Object {
    Get-Content $_.FullName | Add-Content "$basePath\estabelecimentos.csv"
}

# 4. Exclui os arquivos Zip
Get-ChildItem -Path $basePath -Filter "*.zip" | Remove-Item
```

NOTA: você pode copiar e colar esse script no _PowerShell_ do Windows. E atente-se para alterar o diretório de onde estão os seus arquivos.

Depois de extrair e juntar os arquivos, deixei o diretório organizado assim:

![arquivos-organizados](https://raw.githubusercontent.com/danbackeres/projeto_empresas_gov/main/img/arquivos-organizados.png)

## Como Executar o Projeto

### 1. Clonar o Repositório

Primeiro, você precisa clonar o repositório do projeto no GitHub para a sua máquina local:

```bash
git clone https://github.com/danbackeres/projeto_empresas_gov.git
```

### 2. Instalar as Dependências

Este projeto depende de algumas bibliotecas Python que você pode instalar utilizando o pip. Para isso, execute o comando abaixo:

```bash
pip install pandas openpyxl
```

- pandas: Biblioteca usada para manipulação de dados, especialmente útil para processar grandes conjuntos de dados.
- openpyxl: Usada para exportar os dados processados em formato Excel.

### 3. Executar o Script

Para rodar o projeto, execute o script principal main.py:

```bash
python main.py
```

O script processará os arquivos CSV e exportará os resultados filtrados e processados para um arquivo Excel (estabelecimentos_filtrados.xlsx) no diretório raíz do projeto.

## Algumas Explicações do Código

### Filtragem de CNAEs

No projeto, filtrei os dados de estabelecimentos com base no CNAE. A filtragem ocorre logo após o carregamento do arquivo cnae.csv:

```python
cnaes_interesse = cnaes[cnaes['codigo'].isin([8630501, 8630502, 8630503, 8610101, 8610102])]
```

Os códigos CNAE são usados para identificar atividades econômicas específicas, como estabelecimentos que atuam na área de saúde. Esse filtro é essencial para garantir que o processamento seja focado apenas nos tipos de atividades de interesse, porque do contrário, o processamento ficaria muito pesado.

### Filtragem de Municípios

Outro ponto importante do projeto é a filtragem dos municípios. Apenas os estabelecimentos localizados em municípios específicos são incluídos no processamento. A lista de municípios de interesse é definida no código, e o filtro é aplicado no momento em que os dados de estabelecimentos são processados. Para o exemplo, usei alguns municípios do estado do ES:

```python
municipios_interesse = [5623, 5627, 5637, 5727, 5729, ...]
chunk_filtrado = chunk[chunk['codigo'].isin(municipios_interesse)]
```

### Chunks

Como os arquivos CSV fornecidos pelo Gov são enormes, especialmente as empresas e estabelecimentos, precisei utilizar a técnica de processamentos por **chunks**. Isso garante que o arquivo seja processado em partes menores, em vez de ser carregado toda vez na memória, o que poderia causar _overflow_ de memória.

```python
for chunk in pd.read_csv("estabelecimentos.csv", chunksize=10**6):
    # Processamento do chunk
```

Cada **chunk** processa 1 milhão de linhas por vez (`chunksize=10**6`). Você pode ajustar o valor do `chunksize` de acordo com a sua necessidade e claro, de acordo com o recurso que você possuir.

### Junção e Exportação dos Dados

Após o processamento e a aplicação dos filtros, os dados são unificados e exportados para um arquivo Excel, que contém todas as informações sobre os estabelecimentos e empresas filtrados:

```python
df_final.to_excel("estabelecimentos_filtrados.xlsx", index=False)
```

### Consideração Final

O resultado:

![resultado-final](https://raw.githubusercontent.com/danbackeres/projeto_empresas_gov/main/img/resultado.png)

Obviamente esses arquivos poderiam ser exportados para uma base de dados e trabalhados lá da mesma forma, mas assim não teria graça, não é mesmo? 😊
