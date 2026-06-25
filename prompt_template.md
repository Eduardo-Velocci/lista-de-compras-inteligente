# Instrução

Considere a imagem de nota fiscal para extrair as seguintes informações:
-nome do produto
-valor unitário do produto
-data da compra

## Nome do produto

Para o nome do produto, considere apenas o nome do objeto, descartando marca, medidas e quantidade. Por exemplo, a lista a seguir:

{produtos}

## Valor do produto

Para valor do produto, em caso de unidades inteiras, considerar o valor unitário. Caso seja em Kilogramas/gramas, considere o valor total.

## Resposta

Retorne os dados em formato json na seguinte estrutura:

{resposta}