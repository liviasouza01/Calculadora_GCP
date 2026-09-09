# Relatório PDF multicloud

## Objetivo

Quando uma proposta preencher mais de uma nuvem, o botão de exportação deve gerar um único PDF com o detalhamento de todas as nuvens e um resumo consolidado. Propostas de uma única nuvem continuam usando o relatório atual.

## Comportamento

- A exportação será considerada multicloud quando existirem resultados habilitados em pelo menos duas nuvens.
- O PDF terá uma seção por nuvem, na ordem GCP, Azure, AWS e Databricks.
- Cada seção mostrará os serviços habilitados daquela nuvem com itens cobrados, quantidades, preços unitários, subtotais, total do serviço e notas.
- Depois das seções específicas, o PDF mostrará uma comparação por função equivalente.
- A comparação indicará a função, os recursos presentes em cada nuvem e seus valores mensais.
- O encerramento mostrará o total mensal de cada nuvem.
- Nuvens e serviços não preenchidos não aparecerão.
- Serviços sem equivalente continuarão no detalhamento da própria nuvem e poderão aparecer em uma linha exclusiva no consolidado.

## Estrutura técnica

Será criado um módulo frontend pequeno e independente para transformar `ServiceDefinition[]` e `CalculationResult[]` em:

- grupos detalhados por provedor;
- linhas de equivalência funcional;
- totais por provedor.

O mapa de equivalências do relatório seguirá as mesmas funções usadas pelo agente: armazenamento, warehouse SQL, mensageria, CDC, transferência, ETL, Spark, orquestração, streaming, ML, busca vetorial, monitoramento, visão, serverless, observabilidade, secrets, CI/CD e BI.

`downloadProjectReport` receberá opcionalmente todos os serviços e resultados habilitados. Com uma nuvem, preservará a saída atual. Com duas ou mais, renderizará o novo formato e salvará `relatorio-comparativo-multicloud.pdf`.

`ProjectSummary` continuará exibindo os dados da aba selecionada, mas passará todos os resultados habilitados para a exportação quando houver comparação multicloud.

## Testes

Testes unitários validarão que:

- resultados são agrupados pelo provedor correto;
- equivalentes são reunidos na mesma função;
- serviços exclusivos não desaparecem;
- totais por nuvem são calculados separadamente;
- uma única nuvem não ativa o formato multicloud.

O build TypeScript validará a integração com a geração do PDF.

## Fora do escopo

- Alterar cálculos ou preços.
- Modificar os relatórios AS IS versus TO-BE.
- Gerar arquivos separados ou ZIP.
- Alterar a interface visual da calculadora.
