document.addEventListener('DOMContentLoaded', () => {
    // Código existente para parâmetros do inversor...
    const parametrosExemplo = [
        {
            codigo: "ETH1",
            nome: "Tipo de IP",
            valorConfiguradoIHM: "DHCP",
            descricao: "Define o método de obtenção do endereço IP para a porta Ethernet 1.",
            faixaValores: "Fixo, DHCP, BOOTP",
            unidade: "N/A",
            valorFabrica: "DHCP",
            refImagem: "1000131563.jpg",
            categoria: "comunicacao"
        },
        {
            codigo: "-",
            nome: "Freq. Referência",
            valorConfiguradoIHM: "+60.0 Hz",
            descricao: "Frequência de referência atual do inversor.",
            faixaValores: "-500.0 a +500.0 Hz",
            unidade: "Hz",
            valorFabrica: "-",
            refImagem: "1000131574.jpg",
            categoria: "ihm"
        },
        {
            codigo: "8.7",
            nome: "Ativ Webserver incorp",
            valorConfiguradoIHM: "Sim",
            descricao: "Ativa ou desativa o servidor web incorporado ao inversor.",
            faixaValores: "Sim, Não",
            unidade: "N/A",
            valorFabrica: "Sim",
            refImagem: "1000131573.jpg",
            categoria: "comunicacao"
        },
        {
            codigo: "-",
            nome: "Velocidade IHM",
            valorConfiguradoIHM: "19200 bps",
            descricao: "Velocidade de comunicação da Modbus IHM.",
            faixaValores: "4800, 9600, 19200, 38400 bps",
            unidade: "bps",
            valorFabrica: "19200 bps",
            refImagem: "1000131562.jpg",
            categoria: "comunicacao"
        },
        {
            codigo: "-",
            nome: "Modo ventilador",
            valorConfiguradoIHM: "Padrão",
            descricao: "Define o modo de operação do ventilador de resfriamento do inversor.",
            faixaValores: "Padrão, Contínuo, Sob Demanda",
            unidade: "N/A",
            valorFabrica: "Padrão",
            refImagem: "1000131557.jpg",
            categoria: "motor"
        }
    ];

    const listaParametrosDiv = document.getElementById('listaParametros');
    const caixaPesquisaInput = document.getElementById('caixaPesquisa');
    const filtroCategoriaSelect = document.getElementById('filtroCategoria');

    function exibirParametros(parametros) {
        if (!listaParametrosDiv) return;
        listaParametrosDiv.innerHTML = '';
        if (parametros.length === 0) {
            listaParametrosDiv.innerHTML = '<p>Nenhum parâmetro encontrado com os critérios selecionados.</p>';
            return;
        }
        parametros.forEach(param => {
            const card = document.createElement('div');
            card.classList.add('parametro-card');
            card.setAttribute('data-categoria', param.categoria.toLowerCase());
            let refImagemHtml = param.refImagem ? `<p><strong>Ref. Imagem:</strong> ${param.refImagem}</p>` : '';
            card.innerHTML = `
                <h4>${param.codigo ? '[' + param.codigo + '] ' : ''}${param.nome}</h4>
                <p><strong>Valor Configurado (IHM):</strong> ${param.valorConfiguradoIHM || 'N/A'}</p>
                <p><strong>Descrição:</strong> ${param.descricao || 'N/A'}</p>
                <p><strong>Faixa de Valores:</strong> ${param.faixaValores || 'N/A'}</p>
                <p><strong>Unidade:</strong> ${param.unidade || 'N/A'}</p>
                <p><strong>Valor de Fábrica:</strong> ${param.valorFabrica || 'N/A'}</p>
                ${refImagemHtml}
            `;
            listaParametrosDiv.appendChild(card);
        });
    }

    window.filtrarParametros = function() {
        if (!caixaPesquisaInput || !filtroCategoriaSelect) return;
        const termoPesquisa = caixaPesquisaInput.value.toLowerCase();
        const categoriaSelecionada = filtroCategoriaSelect.value.toLowerCase();
        const parametrosFiltrados = parametrosExemplo.filter(param => {
            const correspondeCategoria = categoriaSelecionada === "" || param.categoria.toLowerCase() === categoriaSelecionada;
            const correspondePesquisa = 
                (param.nome && param.nome.toLowerCase().includes(termoPesquisa)) ||
                (param.codigo && param.codigo.toLowerCase().includes(termoPesquisa)) ||
                (param.descricao && param.descricao.toLowerCase().includes(termoPesquisa));
            return correspondeCategoria && correspondePesquisa;
        });
        exibirParametros(parametrosFiltrados);
    }

    if (listaParametrosDiv) {
        exibirParametros(parametrosExemplo);
    }

    // Código para Modal de Componentes
    const modalComponentes = document.getElementById("modalComponentes");
    window.abrirModalComponentes = function() {
        if (modalComponentes) modalComponentes.style.display = "block";
    }
    window.fecharModalComponentes = function() {
        if (modalComponentes) modalComponentes.style.display = "none";
    }
    window.onclick = function(event) {
        if (event.target == modalComponentes) {
            if (modalComponentes) modalComponentes.style.display = "none";
        }
    }

    // Código para Situações de Manutenção
    const btnAdicionarSituacao = document.getElementById('btnAdicionarSituacao');
    const listaSituacoesDiv = document.getElementById('listaSituacoes');
    let situacaoIdCounter = 0;

    function atualizarCorBordaSituacao(selectElement) {
        const situacaoHeader = selectElement.closest('.situacao-header');
        if (!situacaoHeader) return;

        // Remove classes de status anteriores
        situacaoHeader.classList.remove('status-pendente', 'status-em_analise', 'status-aguardando_confirmacao', 'status-cancelado', 'status-concluido');
        
        // Adiciona nova classe de status
        const statusSelecionado = selectElement.value;
        situacaoHeader.classList.add(`status-${statusSelecionado}`);
    }

    if (btnAdicionarSituacao) {
        btnAdicionarSituacao.addEventListener('click', () => {
            situacaoIdCounter++;
            const novaSituacaoDiv = document.createElement('div');
            novaSituacaoDiv.classList.add('situacao-item');
            novaSituacaoDiv.setAttribute('id', `situacao-${situacaoIdCounter}`);

            novaSituacaoDiv.innerHTML = `
                <div class="situacao-header">
                    <input type="text" placeholder="Nome da Situação/Tarefa" class="nome-situacao">
                    <select class="status-situacao">
                        <option value="pendente">Pendente</option>
                        <option value="em_analise">Em Análise</option>
                        <option value="aguardando_confirmacao">Aguardando Confirmação</option>
                        <option value="cancelado">Cancelado</option>
                        <option value="concluido">Concluído</option>
                    </select>
                </div>
                <div class="observacao-container">
                    <textarea placeholder="Observações sobre esta situação..." class="observacao-situacao"></textarea>
                    <input type="file" id="imagemSituacao-${situacaoIdCounter}" class="imagem-situacao-input" accept="image/*" style="display:none;">
                    <button class="btn-escolher-arquivo" onclick="document.getElementById('imagemSituacao-${situacaoIdCounter}').click()">Escolher Arquivo</button>
                </div>
                <img src="#" alt="Imagem da situação" class="preview-imagem-situacao" style="display:none; max-width: 200px; margin-top: 10px;">
                <button class="btn-remover-situacao" onclick="removerSituacao('situacao-${situacaoIdCounter}')">Remover</button>
            `;
            
            if (listaSituacoesDiv) {
                listaSituacoesDiv.appendChild(novaSituacaoDiv);

                const statusSelect = novaSituacaoDiv.querySelector('.status-situacao');
                if (statusSelect) {
                    statusSelect.addEventListener('change', function() {
                        atualizarCorBordaSituacao(this);
                    });
                    // Aplica a cor da borda inicial
                    atualizarCorBordaSituacao(statusSelect);
                }

                const imgInput = novaSituacaoDiv.querySelector(`#imagemSituacao-${situacaoIdCounter}`);
                const imgPreview = novaSituacaoDiv.querySelector('.preview-imagem-situacao');
                if(imgInput && imgPreview){
                    imgInput.addEventListener('change', function(event) {
                        if (event.target.files && event.target.files[0]) {
                            const reader = new FileReader();
                            reader.onload = function(e) {
                                imgPreview.src = e.target.result;
                                imgPreview.style.display = 'block';
                            }
                            reader.readAsDataURL(event.target.files[0]);
                        } else {
                            imgPreview.src = '#';
                            imgPreview.style.display = 'none';
                        }
                    });
                }
            }
        });
    }

    window.removerSituacao = function(situacaoId) {
        const situacaoParaRemover = document.getElementById(situacaoId);
        if (situacaoParaRemover && listaSituacoesDiv) {
            listaSituacoesDiv.removeChild(situacaoParaRemover);
        }
    }
});
