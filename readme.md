# Fore Fire -- Mudanças

## Apresentação do novo modelo, em relação ao modelo original

O modelo original demonstra o fogo se espalhando de acordo com a densidade de árvores no local.
Foi adicionado um fator "bombeiros" que varia de acordo com a quantidade em relação a densidade de arvores.
Quanto mais bombeiros, menos o fogo irá se espalhar e quanto menos bombeiros, menos o fogo irá se espalhar e com uma quantidade quase 0 de bombeiros, as chamas se espalharão parecido com o modelo original.

A váriavel nova "firemans" é uma porcentagem que de acordo com a porcentagem de bombeiros, menor será a chance do fogo se espalhar. 

## Descrição da hipótese causal que você deseja comprovar:

Neste novo modelo, desejo comprovar que quanto mais bombeiros em um 
combate a uma floresta em chamas, menor é a possibilidade do fogo se espalhar
e maior é as chances do incêndio ser combatido o quanto antes.

## Justificativas para as mudanças que você fez, em relação ao código original:

Adicionei a váriavel firemans e umas verificação que de acordo com a quantidade de firemans, 
maior ou  menor será a possibilidade de uma árvore pegar fogo.

No momento que o fogo está se alastrando, é gerado aleatóriamente com base na chance que tem de o fogo se espalhar
Se uma árvore que não foi queimada e a possibilidade de combater o fogo for maior do que o de pegar fogo, a árvore que estiver em chamas, ficará bem (terá a condição de On Fire para Fine).

## Orientação sobre como usar o simulador:

Da mesma forma que usa o modelo original, não foi feito modificações nessa parte.

## Descrição das variáveis armazenadas no arquivo CSV:

firemans: chances de o fogo ser combatido de acordo com a quantidade de bombeiros selecionado (porcentagem)

fine: árvores que não foram queimadas

onfire: árvores que foram queimadas

density: densidade de árvores na floresta
