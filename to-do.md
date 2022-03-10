# Ideia dos bombeiros

Pronto, consegui gerar o csv, agora preciso adicionar uma VARIÁVEL que irá ter seu valor
alterado durante as execuções, ou seja, um valor que irá mensurar e mostrar os impactos obtidos 
quando se tem uma grande quantidade de árvores sendo queimadas e uma quantidade de bombeiros para apagar as chamas.
Então:

- Posso pegar a quantidade de arvores apagandas:
    - Quando uma árvore se enconta na situação On Fire e é voltada para Fine:
        - Salvo essa informação de por exemplo: árvore_recuperada
    - Quantidade de árvores que iniciaram sendo queimadas
        - Salvar toda quantidade de árvore que pegou fogo (On Fire)
    - Salva a quantidade de árvore que foi totalmente queimada (Burned Out)

Essas informações irão variar de acordo com a porcentagem de bombeiros direcionados para o incendio.
