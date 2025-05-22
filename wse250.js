// Arquivo JavaScript para integração com o backend
document.addEventListener('DOMContentLoaded', () => {
    // Código existente para parâmetros do inversor e outras funcionalidades...
    
    // Função para carregar itens faltantes da WSE250 do backend
    async function carregarItensFaltantes() {
        try {
            // Inicializa os itens da WSE250 no backend (se ainda não existirem)
            await fetch('/api/itens-faltantes/inicializar-wse250', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            // Busca os itens atualizados
            const response = await fetch('/api/itens-faltantes/wse250');
            if (!response.ok) {
                throw new Error('Erro ao carregar itens faltantes');
            }
            
            const itens = await response.json();
            atualizarListaItensFaltantes(itens);
        } catch (error) {
            console.error('Erro ao carregar itens faltantes:', error);
            // Exibe mensagem de erro para o usuário
            const listaItens = document.querySelector('.lista-itens-faltantes');
            if (listaItens) {
                listaItens.innerHTML = `<p class="erro-carregamento">Erro ao carregar itens. Por favor, recarregue a página.</p>`;
            }
        }
    }
    
    // Função para atualizar a interface com os itens faltantes
    function atualizarListaItensFaltantes(itens) {
        const listaItens = document.querySelector('.lista-itens-faltantes');
        if (!listaItens) return;
        
        // Limpa a lista atual
        listaItens.innerHTML = '';
        
        // Agrupa itens por categoria
        const itensPorCategoria = {};
        itens.forEach(item => {
            if (!itensPorCategoria[item.categoria]) {
                itensPorCategoria[item.categoria] = [];
            }
            itensPorCategoria[item.categoria].push(item);
        });
        
        // Cria elementos HTML para cada categoria e seus itens
        Object.keys(itensPorCategoria).forEach(categoria => {
            // Cria cabeçalho da categoria
            const categoriaHeader = document.createElement('h4');
            categoriaHeader.textContent = categoria;
            listaItens.appendChild(categoriaHeader);
            
            // Cria elementos para cada item da categoria
            itensPorCategoria[categoria].forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('item-faltante');
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `item-${item.id}`;
                checkbox.classList.add('checkbox-item');
                checkbox.checked = item.adquirido;
                checkbox.dataset.itemId = item.id;
                
                const label = document.createElement('label');
                label.htmlFor = `item-${item.id}`;
                label.textContent = item.descricao;
                if (item.adquirido) {
                    label.classList.add('item-adquirido');
                }
                
                // Adiciona evento para atualizar o status do item no backend
                checkbox.addEventListener('change', async function() {
                    try {
                        const response = await fetch(`/api/itens-faltantes/${item.id}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                adquirido: this.checked
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error('Erro ao atualizar item');
                        }
                        
                        // Atualiza a aparência do item
                        if (this.checked) {
                            label.classList.add('item-adquirido');
                        } else {
                            label.classList.remove('item-adquirido');
                        }
                    } catch (error) {
                        console.error('Erro ao atualizar item:', error);
                        // Reverte o estado do checkbox em caso de erro
                        this.checked = !this.checked;
                        alert('Erro ao salvar alteração. Por favor, tente novamente.');
                    }
                });
                
                itemDiv.appendChild(checkbox);
                itemDiv.appendChild(label);
                listaItens.appendChild(itemDiv);
            });
        });
    }
    
    // Carrega os itens faltantes ao iniciar a página
    if (document.querySelector('.lista-itens-faltantes')) {
        carregarItensFaltantes();
    }
    
    // Código para Modal de Componentes
    const modalComponentes = document.getElementById("modalComponentes");
    window.abrirModalComponentes = function() {
        if (modalComponentes) modalComponentes.style.display = "block";
    }
    window.fecharModalComponentes = function() {
        if (modalComponentes) modalComponentes.style.display = "none";
    }
    // Fecha o modal se clicar fora do conteúdo
    window.onclick = function(event) {
        if (event.target == modalComponentes) {
            if (modalComponentes) modalComponentes.style.display = "none";
        }
    }
    
    // Código para Situações de Manutenção
    const btnAdicionarSituacao = document.getElementById('btnAdicionarSituacao');
    const listaSituacoesDiv = document.getElementById('listaSituacoes');
    let situacaoIdCounter = 0;
    
    // Função para atualizar a cor da borda conforme o status
    function atualizarCorBordaSituacao(selectElement) {
        const situacaoHeader = selectElement.closest('.situacao-header');
        if (!situacaoHeader) return;
        
        // Remove classes de status anteriores
        situacaoHeader.classList.remove('status-pendente', 'status-em_analise', 'status-aguardando_confirmacao', 'status-cancelado', 'status-concluido');
        
        // Adiciona nova classe de status
        const statusSelecionado = selectElement.value;
        situacaoHeader.classList.add(`status-${statusSelecionado}`);
    }
    
    // Inicializa os status selects existentes
    document.querySelectorAll('.status-situacao').forEach(select => {
        select.addEventListener('change', function() {
            atualizarCorBordaSituacao(this);
        });
    });
    
    if (btnAdicionarSituacao) {
        btnAdicionarSituacao.addEventListener('click', () => {
            situacaoIdCounter++;
            const novaSituacaoDiv = document.createElement('div');
            novaSituacaoDiv.classList.add('situacao-item');
            novaSituacaoDiv.setAttribute('id', `situacao-${situacaoIdCounter}`);
            
            novaSituacaoDiv.innerHTML = `
                <div class="situacao-header status-pendente">
                    <input type="text" placeholder="Nome da Situação/Tarefa" class="nome-situacao">
                    <select class="status-situacao">
                        <option value="pendente" selected>Pendente</option>
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
                // Insere a nova situação após a primeira (que é a lista de itens faltantes)
                const primeiroItem = listaSituacoesDiv.querySelector('.situacao-item');
                if (primeiroItem) {
                    listaSituacoesDiv.insertBefore(novaSituacaoDiv, primeiroItem.nextSibling);
                } else {
                    listaSituacoesDiv.appendChild(novaSituacaoDiv);
                }
                
                const statusSelect = novaSituacaoDiv.querySelector('.status-situacao');
                if (statusSelect) {
                    statusSelect.addEventListener('change', function() {
                        atualizarCorBordaSituacao(this);
                    });
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
