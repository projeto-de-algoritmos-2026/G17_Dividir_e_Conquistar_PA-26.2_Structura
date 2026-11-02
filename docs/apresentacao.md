# Roteiro da apresentação

1. **Problema.** Comparar palavras soltas não basta: quem plagia troca a ordem e reescreve frases.
2. **Modo estrutural.** Clique em "Usar exemplo" e analise.
   - Mostre os trechos destacados e passe o mouse sobre um deles.
   - **Hirschberg:** alinhou as partes em comum dividindo o texto ao meio.
3. **Reordenação.** Troque de lugar as duas primeiras frases do texto suspeito e analise de novo.
   - **Inversões significativas:** a nota continua alta, pois blocos inteiros foram movidos, não embaralhados.
   - **Counting Inversions:** mostre o valor de "Inversões" e a diferença entre palavras e blocos.
4. **Modo semântico.** Mude o seletor e analise o exemplo original.
   - Em "Frases equivalentes", mostre a frase reescrita que o modo estrutural não reconheceu.
   - Mude a exigência no controle deslizante e veja o efeito.
   - Reforce que o pipeline D&C é o mesmo; só mudou o que conta como igual.
5. **Citações.** Coloque um trecho do texto suspeito entre aspas e mostre que ele sai da análise.
6. **Complexidade.** Mostre a tabela de `docs/algoritmos.md`.
7. **Limites.** A nota é um indício para revisão humana, não uma prova de plágio.

**Antes de apresentar:** rode uma análise semântica uma vez, para que o modelo já esteja baixado.
