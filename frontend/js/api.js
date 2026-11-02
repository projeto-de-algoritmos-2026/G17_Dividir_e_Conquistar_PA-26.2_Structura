export async function buscarAnalises() {
    const resposta = await fetch('/api/analises');
    if (!resposta.ok) throw new Error('Não foi possível carregar os tipos de análise.');
    return resposta.json();
}

async function mensagemDeErro(resposta) {
    const padrao = 'Não foi possível concluir a análise. Tente novamente.';
    try {
        const { detail } = await resposta.json();
        return typeof detail === 'string' ? detail : padrao;
    } catch {
        return padrao;
    }
}

export async function comparar(dados) {
    const resposta = await fetch('/api/comparar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    });

    if (!resposta.ok) throw new Error(await mensagemDeErro(resposta));
    return resposta.json();
}
