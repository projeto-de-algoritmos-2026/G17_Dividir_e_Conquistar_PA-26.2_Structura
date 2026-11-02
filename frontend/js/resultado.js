const painel = document.getElementById('painelResultado');

function animarNota(nota) {
    const elemento = document.getElementById('resNota');
    const alvo = Math.round(nota * 100);
    const inicio = performance.now();

    function quadro(agora) {
        const progresso = Math.min((agora - inicio) / 500, 1);
        elemento.textContent = `${Math.round(alvo * progresso)}%`;
        if (progresso < 1) requestAnimationFrame(quadro);
    }
    requestAnimationFrame(quadro);
}

function desenharMetricas(metricas) {
    const lista = document.getElementById('resMetricas');
    lista.replaceChildren();

    for (const { rotulo, valor } of metricas) {
        const grupo = document.createElement('div');
        const titulo = document.createElement('dt');
        const dado = document.createElement('dd');
        titulo.textContent = rotulo;
        dado.textContent = valor;
        grupo.append(titulo, dado);
        lista.append(grupo);
    }
}

function destacarPar(id, ativo) {
    painel.querySelectorAll(`mark[data-trecho="${id}"]`)
        .forEach((marca) => marca.classList.toggle('ativo', ativo));
}

function desenharTexto(elemento, texto, faixas) {
    elemento.replaceChildren();
    let posicao = 0;

    for (const { inicio, fim, id } of [...faixas].sort((a, b) => a.inicio - b.inicio)) {
        if (fim <= posicao) continue;
        const comeco = Math.max(inicio, posicao);
        elemento.append(texto.slice(posicao, comeco));

        const marca = document.createElement('mark');
        marca.textContent = texto.slice(comeco, fim);
        marca.dataset.trecho = id;
        marca.addEventListener('mouseenter', () => destacarPar(id, true));
        marca.addEventListener('mouseleave', () => destacarPar(id, false));
        elemento.append(marca);
        posicao = fim;
    }
    elemento.append(texto.slice(posicao));
}

function desenharPares(pares) {
    const lista = document.getElementById('resPares');
    lista.replaceChildren();
    document.getElementById('blocoPares').classList.toggle('escondido', pares.length === 0);

    for (const { texto_a, texto_b, nota } of pares) {
        const linha = document.createElement('div');
        const original = document.createElement('span');
        const suspeito = document.createElement('span');
        const valor = document.createElement('strong');
        linha.className = 'par';
        original.textContent = texto_a;
        suspeito.textContent = texto_b;
        valor.textContent = `${Math.round(nota * 100)}%`;
        linha.append(original, suspeito, valor);
        lista.append(linha);
    }
}

export function esconderResultado() {
    painel.classList.add('escondido');
}

export function mostrarResultado(dados, textoA, textoB) {
    animarNota(dados.nota);
    document.getElementById('resFaixa').textContent = dados.titulo;
    document.getElementById('resExplicacao').textContent = dados.explicacao;
    desenharMetricas(dados.metricas);

    document.getElementById('resLegenda').textContent = dados.legenda;

    const faixasA = dados.trechos.map((t, id) => ({ inicio: t.inicio_a, fim: t.fim_a, id }));
    const faixasB = dados.trechos.map((t, id) => ({ inicio: t.inicio_b, fim: t.fim_b, id }));
    desenharTexto(document.getElementById('marcadoA'), textoA, faixasA);
    desenharTexto(document.getElementById('marcadoB'), textoB, faixasB);

    desenharPares(dados.pares);
    painel.classList.remove('escondido');
}
