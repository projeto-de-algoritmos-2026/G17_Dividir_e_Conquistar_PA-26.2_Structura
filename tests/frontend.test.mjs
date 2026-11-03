//Roda com: node --test tests/frontend.test.mjs
import assert from 'node:assert/strict';
import { test } from 'node:test';

globalThis.document = { getElementById: () => ({}) };
const { fatiarEmTrechos } = await import('../frontend/js/resultado.js');
const { comparar } = await import('../frontend/js/api.js');

const marcados = (pedacos) => pedacos.filter((p) => p.id !== undefined).map((p) => p.texto);
const inteiro = (pedacos) => pedacos.map((p) => p.texto).join('');

test('emoji antes do trecho não desloca o destaque', () => {
    const texto = 'Veja 😀😀😀 a leitura desenvolve';
    const inicio = Array.from('Veja 😀😀😀 a ').length;
    const pedacos = fatiarEmTrechos(texto, [{ inicio, fim: Array.from(texto).length, id: 0 }]);
    assert.deepEqual(marcados(pedacos), ['leitura desenvolve']);
});

test('nenhum caractere se perde, com ou sem emoji', () => {
    for (const texto of ['', 'abc', '😀', 'a😀b👨‍👩‍👧c🇧🇷d']) {
        const fim = Array.from(texto).length;
        assert.equal(inteiro(fatiarEmTrechos(texto, [{ inicio: 0, fim, id: 0 }])), texto);
        assert.equal(inteiro(fatiarEmTrechos(texto, [])), texto);
    }
});

test('trechos sobrepostos não duplicam texto', () => {
    const pedacos = fatiarEmTrechos('abcdefgh', [{ inicio: 0, fim: 5, id: 0 }, { inicio: 3, fim: 7, id: 1 }]);
    assert.equal(inteiro(pedacos), 'abcdefgh');
    assert.deepEqual(marcados(pedacos), ['abcde', 'fg']);
});

test('trecho contido em outro é ignorado', () => {
    assert.deepEqual(marcados(fatiarEmTrechos('abcdefgh', [{ inicio: 0, fim: 6, id: 0 }, { inicio: 2, fim: 4, id: 1 }])), ['abcdef']);
});

test('trechos fora de ordem saem ordenados', () => {
    assert.deepEqual(marcados(fatiarEmTrechos('abcdef', [{ inicio: 4, fim: 6, id: 1 }, { inicio: 0, fim: 2, id: 0 }])), ['ab', 'ef']);
});

const respostaHttp = (status, corpo) => ({ ok: status < 400, status, json: async () => corpo });

test('mensagem do backend chega à tela', async () => {
    globalThis.fetch = async () => respostaHttp(422, { detail: 'Cada texto pode ter até 6.000 palavras.' });
    await assert.rejects(comparar({}), /6\.000 palavras/);
});

test('erro de validação em lista usa a mensagem padrão', async () => {
    globalThis.fetch = async () => respostaHttp(422, { detail: [{ msg: 'campo' }] });
    await assert.rejects(comparar({}), /Tente novamente/);
});

test('erro sem JSON usa a mensagem padrão', async () => {
    globalThis.fetch = async () => ({ ok: false, json: async () => { throw new Error('html'); } });
    await assert.rejects(comparar({}), /Tente novamente/);
});

test('resposta boa passa direto', async () => {
    globalThis.fetch = async () => respostaHttp(200, { nota: 0.5 });
    assert.deepEqual(await comparar({}), { nota: 0.5 });
});
