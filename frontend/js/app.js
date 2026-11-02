import { buscarAnalises, comparar } from './api.js';
import { esconderResultado, mostrarResultado } from './resultado.js';

const EXEMPLO_A = `A leitura desenvolve o pensamento crítico dos estudantes porque apresenta pontos de vista diferentes. Bibliotecas públicas ampliam o acesso aos livros nas comunidades mais pobres. Sem políticas de incentivo, muitos jovens terminam a escola sem o hábito de ler.`;
const EXEMPLO_B = `Bibliotecas públicas ampliam o acesso aos livros nas comunidades mais pobres. Quem lê desde cedo aprende a pensar de forma crítica, pois entra em contato com opiniões variadas. Sem políticas de incentivo, muitos jovens terminam a escola sem o hábito de ler.`;

const btnAnalisar = document.getElementById('btnAnalisar');
const txtA = document.getElementById('textoA');
const txtB = document.getElementById('textoB');
const seletorModo = document.getElementById('seletorModo');
const descricaoModo = document.getElementById('descricaoModo');
const erro = document.getElementById('erro');

let modos = [];
let maxCaracteres = Infinity;

function mostrarErro(mensagem) {
    erro.textContent = mensagem;
    erro.classList.remove('escondido');
}

function modoAtual() {
    const id = seletorModo.querySelector('input:checked').value;
    return modos.find((modo) => modo.id === id);
}

function atualizarModo() {
    const modo = modoAtual();
    descricaoModo.textContent = modo.descricao;
    esconderResultado();
}

function criarSeletor() {
    modos.forEach((modo, indice) => {
        const rotulo = document.createElement('label');
        const opcao = document.createElement('input');
        opcao.type = 'radio';
        opcao.name = 'modo';
        opcao.value = modo.id;
        opcao.checked = indice === 0;
        opcao.addEventListener('change', atualizarModo);
        rotulo.append(opcao, modo.rotulo);
        seletorModo.append(rotulo);
    });
    atualizarModo();
}

function atualizarContador(campo, contador) {
    const total = campo.value.trim().split(/\s+/).filter(Boolean).length;
    contador.textContent = `${total} ${total === 1 ? 'palavra' : 'palavras'}`;
}

function atualizarContadores() {
    atualizarContador(txtA, document.getElementById('contadorA'));
    atualizarContador(txtB, document.getElementById('contadorB'));
}

function textosValidos(texto_a, texto_b) {
    if (!texto_a || !texto_b) {
        mostrarErro('Preencha os dois textos para continuar.');
        return false;
    }
    if (Math.max(texto_a.length, texto_b.length) > maxCaracteres) {
        mostrarErro(`Cada texto pode ter até ${maxCaracteres.toLocaleString('pt-BR')} caracteres.`);
        return false;
    }
    return true;
}

async function analisar() {
    const texto_a = txtA.value.trim();
    const texto_b = txtB.value.trim();
    const modo = modoAtual();

    erro.classList.add('escondido');
    if (!textosValidos(texto_a, texto_b)) return;

    btnAnalisar.disabled = true;
    btnAnalisar.textContent = 'Analisando...';

    try {
        const dados = await comparar({ texto_a, texto_b, modo: modo.id });
        mostrarResultado(dados, texto_a, texto_b);
    } catch (falha) {
        esconderResultado();
        mostrarErro(falha.message);
    } finally {
        btnAnalisar.disabled = false;
        btnAnalisar.textContent = 'Analisar textos';
    }
}

async function iniciar() {
    try {
        const dados = await buscarAnalises();
        modos = dados.modos;
        maxCaracteres = dados.max_caracteres;
        criarSeletor();
    } catch (falha) {
        btnAnalisar.disabled = true;
        mostrarErro(falha.message);
    }
}

btnAnalisar.addEventListener('click', analisar);
txtA.addEventListener('input', atualizarContadores);
txtB.addEventListener('input', atualizarContadores);
document.getElementById('btnExemplo').addEventListener('click', () => {
    txtA.value = EXEMPLO_A;
    txtB.value = EXEMPLO_B;
    atualizarContadores();
});

iniciar();
