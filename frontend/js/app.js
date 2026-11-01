document.addEventListener('DOMContentLoaded', () => {
    const btnAnalisar = document.getElementById('btnAnalisar');
    const txtA = document.getElementById('textoA');
    const txtB = document.getElementById('textoB');
    const painelResultado = document.getElementById('painelResultado');

    btnAnalisar.addEventListener('click', async () => {
        const texto_a = txtA.value.trim();
        const texto_b = txtB.value.trim();

        if (!texto_a || !texto_b) {
            alert('Por favor, preencha ambos os textos.');
            return;
        }

        btnAnalisar.disabled = true;
        btnAnalisar.textContent = 'A processar...';

        try {
            const resposta = await fetch('http://127.0.0.1:8000/api/comparar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto_a, texto_b })
            });

            if (!resposta.ok) throw new Error('Erro na comunicação com o servidor.');

            const dados = await resposta.json();
            
            document.getElementById('resSimilaridade').textContent = `${(dados.similaridade * 100).toFixed(2)}%`;
            document.getElementById('resInversoes').textContent = dados.inversoes;
            document.getElementById('resPalavras').textContent = dados.n_palavras;
            
            painelResultado.classList.remove('escondido');
        } catch (erro) {
            console.error(erro);
            alert('Ocorreu um erro ao analisar os textos.');
        } finally {
            btnAnalisar.disabled = false;
            btnAnalisar.textContent = 'Analisar Estrutura';
        }
    });
});