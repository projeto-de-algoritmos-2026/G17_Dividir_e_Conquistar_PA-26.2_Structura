export async function buscarAnalises() {
    const resposta = await fetch('/api/analises');
    if (!resposta.ok) throw new Error('Não foi possível carregar os tipos de análise.');
    return resposta.json();
}

export async function comparar(dados) {
    const resposta = await fetch('/api/comparar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    });

    if (!resposta.ok) throw new Error('Não foi possível concluir a análise. Tente novamente.');
    return resposta.json();
}
