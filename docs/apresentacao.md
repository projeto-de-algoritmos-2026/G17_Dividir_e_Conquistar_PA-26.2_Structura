# Roteiro da apresentação

1. **Problema.** "Parecido" pode significar duas coisas: escrito do mesmo jeito ou dizendo a mesma coisa. Cada modo responde a uma delas.
2. **Modo estrutural.** Compare "O menino comprou uma bola nova na loja do bairro. A menina levou uma boneca velha para a casa da avó." com "O ministro assinou uma lei nova no palácio da capital. A empresa vendeu uma fábrica velha para o grupo da China."
   - Nenhuma palavra de conteúdo é igual, mas a similaridade é alta: a construção é a mesma.
   - Mostre a lista "Frases com a mesma construção": cada frase achou sua par.
   - Frases isoladas, como "O gato dorme no sofá." × "O cão late na rua.", dão faixa inconclusiva: com poucos tokens, a construção coincide fácil.
   - **Hirschberg:** alinhou as frases dividindo o texto ao meio.
   - Mostre "Esperado por acaso" e explique por que ele é descontado da comparação do texto inteiro.
3. **Modo semântico.** Clique em "Usar exemplo" e analise.
   - Em "Frases equivalentes", mostre a frase reescrita que nenhuma comparação de palavras reconheceria.
   - Mostre "Ideia geral": ela reforça a nota, mas não basta sozinha, porque tratar do mesmo tema não é plágio.
4. **Reordenação.** Troque de lugar as frases do texto suspeito e analise de novo.
   - **Counting Inversions:** a métrica "Ordem" cai e tira até 15% da parte da nota que vem das frases, mas a suspeita continua alta: as ideias são as mesmas.
   - No modo estrutural, acontece o mesmo: "Ordem das frases" cai, mas a nota continua alta, porque cada frase segue construída do mesmo jeito.
5. **Contraste.** Compare uma paráfrase nos dois modos: a suspeita de plágio é alta e a similaridade estrutural é baixa.
6. **Citações.** Coloque uma citação curta entre aspas em um texto maior e mostre que ela sai da análise, com um aviso na tela. Depois coloque o texto inteiro entre aspas e mostre que a cópia continua detectada.
7. **Complexidade.** Mostre a tabela de `docs/algoritmos.md` e os resultados de `docs/testes.md`.
8. **Limites.** O modelo não entende inversão de sentido, e a nota orienta uma revisão humana, sem provar plágio.

**Antes de apresentar:** rode uma análise semântica uma vez, com internet. O modelo fica em `.cache/modelos`, dentro do projeto, e depois disso funciona offline.
