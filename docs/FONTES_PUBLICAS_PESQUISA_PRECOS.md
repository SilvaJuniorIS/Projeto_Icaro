# Fontes publicas complementares para pesquisa de precos

## Fontes prioritarias

1. PNCP
   - Melhor uso: editais, avisos, atas, contratos e publicacoes da Lei 14.133/2021.
   - Limite pratico: alguns endpoints sao mais estruturados que textuais; o Icaro deve coletar por filtros validos e ranquear localmente.

2. Compras.gov.br Dados Abertos - licitacoes e itens
   - Melhor uso: historico SIASG, UASG, itens de licitacao, modalidades, resultados e objetos.
   - Campos relevantes: UASG, orgao/unidade, item, material/servico, valor, modalidade e datas.

3. Compras.gov.br / Contratos.gov.br Dados Abertos
   - Melhor uso: contratos e itens de contrato, com dados do contratante e do fornecedor quando publicados.
   - Campos relevantes: unidade de compra, contratada, CNPJ/CPF quando disponivel, objeto, vigencia e valor.

4. Painel de Precos / Pesquisa de Precos
   - Melhor uso: estatisticas de preco, media, mediana, menor e maior valor de compras federais.
   - Uso recomendado: fonte de validacao e comparacao, nao substitui a memoria de calculo do processo.

5. Atas de Registro de Precos
   - Melhor uso: estudo de carona, aderencia e compatibilidade com quantitativos e vigencia.
   - Campos relevantes: orgao gerenciador, fornecedor, vigencia, saldo/quantidade e item registrado.

## Fontes auxiliares

- CATMAT/CATSER: normalizacao do objeto e descoberta de sinonimos oficiais.
- Portais de transparencia estaduais e municipais: ampliam cobertura local quando o objeto e regional.
- Diarios oficiais e paginas de licitacoes dos orgaos: uteis para anexos, termos de referencia e detalhes que nao aparecem em APIs.
- Bancos setoriais publicos: ANVISA/CMED para medicamentos, tabelas SINAPI/SICRO para obras e servicos de engenharia, quando o objeto permitir.

## Regra operacional no Icaro

Quando uma fonte localizar o objeto pesquisado, registrar no relatorio:

- descricao do objeto localizado;
- banco/fonte usada;
- orgao, unidade ou entidade contratante;
- fornecedor/contratada, se o banco publicar essa informacao;
- URL e data de acesso.
