# Requisitos de uso: pesquisa, itens, fontes e atas

## 1. Pesquisa

A pesquisa representa o objeto central a ser analisado no processo de pesquisa de precos.

Exemplo:

- Material de informatica.
- Material de expediente.
- Equipamentos de limpeza.

O objeto central orienta o escopo geral, a justificativa, a verificacao de atas vigentes e o relatorio final.

## 2. Itens

Cada pesquisa pode conter varios itens. Os itens devem ser mais especificos que o objeto central, pois cada item precisa ter seu proprio valor unitario pesquisado.

Exemplo para o objeto central `material de informatica`:

- HD SSD 480GB SATA.
- Pendrive 64GB USB 3.0.
- Monitor LED 24 polegadas.

Cada item deve poder ser buscado independentemente no PNCP e em outras bases para formar sua propria cesta de fontes e calcular seu valor unitario.

## 3. Fontes de preco

As fontes podem vir de:

- PNCP.
- Compras.gov.br / compras publicas.
- Banco de precos ou painel de precos.
- Atas de registro de precos.
- Fornecedores ou outras fontes justificadas.

Quando o objeto ou item for localizado, o sistema deve registrar, sempre que a base informar:

- valor unitario;
- orgao, unidade ou entidade responsavel;
- fornecedor ou contratado;
- URL da fonte;
- data de referencia e data de acesso;
- justificativa quando a fonte for descartada.

## 4. Atas

As atas devem ser pesquisadas a partir do objeto central da pesquisa, pois a carona depende da compatibilidade entre o objeto da ata e a necessidade geral do processo.

O sistema deve apoiar a busca de atas em vigor e registrar:

- numero da ata;
- orgao gerenciador;
- fornecedor;
- objeto da ata;
- item aderente;
- valor unitario;
- vigencia;
- quantidade registrada e estimativa disponivel;
- URL;
- observacoes sobre aderencia, saldo, anuencia e compatibilidade.

## 5. Regra pratica no fluxo

1. Criar a pesquisa com o objeto central.
2. Cadastrar os itens especificos.
3. Buscar cada item de forma independente para obter valor unitario.
4. Salvar fontes com valor, orgao e fornecedor quando houver.
5. Buscar atas vigentes usando o objeto central.
6. Registrar apenas atas potencialmente aderentes para analise de carona.
7. Exportar relatorio com fontes, orgaos, fornecedores, atas e justificativas.
