# Guia da apresentação

**Antes de apresentar:** rode uma análise semântica com internet, para o modelo ficar salvo. Depois disso, tudo funciona offline.

## O projeto em uma frase

Compara dois textos de duas formas: se as frases foram **construídas do mesmo jeito** (estrutural) e se **as ideias vêm do original** (semântica). O resultado orienta uma revisão humana e não prova plágio.

| | Estrutural | Semântica |
|---|---|---|
| **Pergunta** | As frases têm a mesma construção? | As ideias vêm do original? |
| **Compara** | Classe gramatical das palavras | Significado das frases |
| **Olha o assunto?** | Não | Sim |
| **Resultado** | Similaridade | Suspeita de plágio |
| **Faixas** | Baixa < 30% ≤ moderada < 60% ≤ alta | As mesmas |

## Roteiro

1. **Problema.** "Parecido" pode significar escrito do mesmo jeito ou dizendo a mesma coisa. Cada modo responde a uma dessas perguntas.
2. **Estrutural.** Compare "O menino comprou uma bola nova na loja do bairro. A menina levou uma boneca velha para a casa da avó. O cachorro achou um osso grande no quintal do vizinho." com "O ministro assinou uma lei nova no palácio da capital. A empresa vendeu uma fábrica velha para o grupo da China. O técnico montou um time forte no clube do interior."
   - Nenhuma ideia em comum, mas a nota é 100%: a construção é a mesma.
   - Mostre "Frases com a mesma construção": cada frase achou sua par. É o **Hirschberg** alinhando as frases.
   - "O gato dorme no sofá." × "O cão late na rua." dá faixa inconclusiva: com poucos tokens, a construção coincide fácil.
3. **Semântica.** Clique em "Usar exemplo" e analise.
   - Em "Frases equivalentes", mostre a frase reescrita que nenhuma comparação de palavras reconheceria.
   - Mostre "Ideia geral": ela reforça a nota, mas não basta sozinha.
4. **Reordenação.** Troque as frases de lugar e analise nos dois modos.
   - **Counting Inversions:** a ordem cai e tira até 15% da nota, mas ela continua alta, porque as frases e as ideias são as mesmas.
5. **Contraste.** Compare uma paráfrase nos dois modos: suspeita alta, similaridade estrutural baixa.
6. **Citações.** Coloque uma citação curta entre aspas e mostre que ela sai da análise, com aviso. Depois coloque o texto inteiro entre aspas e mostre que a cópia continua detectada.
7. **Limites.** O modelo não entende inversão de sentido, e a nota não prova plágio.

## Algoritmos em uma frase

- **Hirschberg:** corta A ao meio, acha o melhor corte em B e resolve os dois lados. Dá a mesma resposta da tabela completa, com memória linear. `O(nm)` em tempo, `O(n + m)` em espaço.
- **Hirschberg ponderado:** a mesma divisão, somando similaridades em vez de contar pares, para escolher os melhores pares de frases.
- **Counting Inversions:** no merge, quando um elemento da direita passa à frente, ele inverte com todos os restantes da esquerda. `O(n log n)`.
- **Inversões significativas:** a mesma ideia, contando só pares `a[i] > a[j] + tolerância`.

## Como as notas são calculadas

**Estrutural**

1. Cada palavra vira uma classe gramatical.
2. Cada frase procura a par de construção mais parecida, em qualquer posição.
3. As inversões medem quanto a ordem mudou.
4. O texto inteiro também é comparado, descontando o acaso, para reconhecer frases fundidas ou divididas.

```
por frases = cobertura × (0,85 + 0,15 × ordem)
nota       = max(por frases, comparação contínua sem o acaso)
```

**Semântica**

1. Cada frase vira um vetor de significado.
2. Duas frases contam como iguais a partir de 55%.
3. Hirschberg ponderado alinha as frases, e uma varredura recupera as que mudaram de lugar.
4. Frases sem par são comparadas com duas vizinhas somadas, para reconhecer fusões e divisões.

```
frases = max(cobertura, original) × (0,85 + 0,15 × ordem)
nota   = max(frases, min(ideia geral, frases + 0,20))
```

## O que cada estatística diz

**Estrutural**

| Estatística | O que diz |
|---|---|
| Frases de mesma construção | Quantas frases têm uma par com a mesma estrutura |
| Ordem das frases | Se elas seguem a mesma ordem; 100% é a mesma ordem |
| Inversões | Pares de frases em ordem trocada |
| Formato em comum | Quanto do texto inteiro coincide, antes do desconto |
| Esperado por acaso | Quanto coincidiria com as mesmas classes em ordem aleatória |
| Palavras idênticas | Palavras de conteúdo do suspeito que estão no original; não entra na nota |
| Maior trecho idêntico | Maior sequência copiada, sem palavras comuns |
| Trechos idênticos | Quantos blocos de palavras iguais foram achados |

**Semântica**

| Estatística | O que diz |
|---|---|
| Ideia geral | Proximidade dos textos inteiros; indica tema próximo, não cópia |
| Cobertura do suspeito | Quanto do suspeito tem equivalente no original |
| Original aproveitado | Quanto do original aparece no suspeito |
| Ordem | Se as ideias seguem a mesma ordem |
| Blocos | Grupos de frases seguidas que correspondem |
| Inversões | Pares de frases em ordem trocada |
| Frases em comum | Quantas frases do suspeito têm par no original |

Cobertura baixa com original alto indica uma cópia diluída em texto novo.

## Exemplos para citar

| Caso | Estrutural | Semântica | O que mostra |
|---|---|---|---|
| Cópia exata | 100% | 100% | Os dois modos concordam |
| Frases reordenadas | 92% | 100% | Mudar a ordem não apaga construção nem ideias |
| Paráfrase | 36% | 87% | Palavras diferentes, mesma ideia |
| Mesma construção, outro tema | 100% | 0% | Mesma forma, ideias diferentes |
| Cópia com 40 frases novas | 100% | 100% | O enchimento não esconde a cópia |

## Perguntas prováveis

- **Por que Hirschberg, e não a tabela completa?** Dá o mesmo resultado, com memória linear em vez de quadrática.
- **Por que dois modos?** Cada um vê o que o outro não vê: paráfrase na semântica, construção no estrutural.
- **Por que classe gramatical, e não tamanho da palavra?** O tamanho separava "menino" de "ministro", que têm a mesma função. Em artigos reais, o acerto foi de 53,8% para 99,6%.
- **Onde as inversões entram na nota?** Nos dois modos, pela Ordem, que tira no máximo 15%.
- **Por que limitar o tamanho do texto?** O alinhamento é quadrático; sem limite, o pior caso levava 84 segundos no estrutural e 164 na semântica. Hoje leva cerca de 9.
- **E citações?** Citações curtas e referências saem da análise, com aviso. Aspas longas não escondem cópia.
- **Dá para burlar com caracteres invisíveis ou letras parecidas?** Não: eles são normalizados antes da análise.
- **Quais os pontos fracos?** Inversão de sentido passa despercebida ("eleva" × "reduz" dá 88%), textos muito curtos são imprecisos, e a validação usou pares gerados por programa, não textos de alunos.
- **Como sabemos que funciona?** Os algoritmos batem com a força bruta em entradas aleatórias, e a análise estrutural foi validada em artigos que não participaram da calibração.

Fórmulas completas, limites e testes estão em [infraestrutura.md](infraestrutura.md).
