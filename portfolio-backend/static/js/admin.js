/**
 * Admin Dashboard JavaScript
 * Handles CRUD operations for projects and certificates
 */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
    currentSection: 'projetos',
    projetos: [],
    certificados: [],
    visitas: 0,
    editingId: null,
    deleteId: null,
};

// ============================================================================
// DOM ELEMENTS
// ============================================================================

const elements = {
    navItems: document.querySelectorAll('.nav-item'),
    sections: document.querySelectorAll('.section'),
    addItemBtn: document.getElementById('add-item-btn'),
    itemModal: document.getElementById('item-modal'),
    deleteModal: document.getElementById('delete-modal'),
    itemForm: document.getElementById('item-form'),
    modalTitle: document.getElementById('modal-title'),
    sectionTitle: document.getElementById('section-title'),
    projetosList: document.getElementById('projetos-list'),
    certificadosList: document.getElementById('certificados-list'),
    visitsCount: document.getElementById('visits-count'),
    resetVisitsBtn: document.getElementById('reset-visits-btn'),
    toast: document.getElementById('toast'),
    cancelDeleteBtn: document.getElementById('cancel-delete-btn'),
    confirmDeleteBtn: document.getElementById('confirm-delete-btn'),
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadProjetos();
    loadCertificados();
    loadVisitas();
});

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function setupEventListeners() {
    // Navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            switchSection(section);
        });
    });

    // Add Item Button
    elements.addItemBtn.addEventListener('click', openAddModal);

    // Modal Close
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });

    // Modal Outside Click
    [elements.itemModal, elements.deleteModal].forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModals();
        });
    });

    // Form Submit
    elements.itemForm.addEventListener('submit', handleFormSubmit);

    // Delete Confirmation
    elements.cancelDeleteBtn.addEventListener('click', closeModals);
    elements.confirmDeleteBtn.addEventListener('click', confirmDelete);

    // Reset Visits
    elements.resetVisitsBtn.addEventListener('click', resetVisits);

    // Keyboard
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModals();
    });
}

// ============================================================================
// SECTION SWITCHING
// ============================================================================

function switchSection(section) {
    state.currentSection = section;

    // Update navigation
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });

    // Update sections
    elements.sections.forEach(s => {
        s.classList.remove('active');
    });
    document.getElementById(`${section}-section`).classList.add('active');

    // Update title
    const titles = {
        projetos: 'Gerenciar Projetos',
        certificados: 'Gerenciar Certificados',
        visitas: 'Contador de Visitas',
    };
    elements.sectionTitle.textContent = titles[section];

    // Show/hide add button
    elements.addItemBtn.style.display = section === 'visitas' ? 'none' : 'block';
}

// ============================================================================
// MODAL MANAGEMENT
// ============================================================================

function openAddModal() {
    state.editingId = null;
    elements.modalTitle.textContent = 
        state.currentSection === 'projetos' ? 'Novo Projeto' : 'Novo Certificado';
    
    renderFormFields();
    elements.itemForm.reset();
    elements.itemModal.classList.add('show');
}

function openEditModal(id) {
    state.editingId = id;
    elements.modalTitle.textContent = 
        state.currentSection === 'projetos' ? 'Editar Projeto' : 'Editar Certificado';
    
    renderFormFields();
    
    const data = state.currentSection === 'projetos' 
        ? state.projetos.find(p => p.id === id)
        : state.certificados.find(c => c.id === id);
    
    if (data) {
        Object.keys(data).forEach(key => {
            const input = elements.itemForm.querySelector(`[name="${key}"]`);
            if (input) input.value = data[key] || '';
        });
    }
    
    elements.itemModal.classList.add('show');
}

function openDeleteModal(id) {
    state.deleteId = id;
    elements.deleteModal.classList.add('show');
}

function closeModals() {
    elements.itemModal.classList.remove('show');
    elements.deleteModal.classList.remove('show');
    state.editingId = null;
    state.deleteId = null;
}

// ============================================================================
// FORM RENDERING
// ============================================================================

function renderFormFields() {
    elements.itemForm.innerHTML = '';

    if (state.currentSection === 'projetos') {
        elements.itemForm.innerHTML = `
            <div class="form-group">
                <label for="titulo">Título do Projeto *</label>
                <input type="text" id="titulo" name="titulo" required>
            </div>
            <div class="form-group">
                <label for="descricao">Descrição *</label>
                <textarea id="descricao" name="descricao" required></textarea>
            </div>
            <div class="form-group">
                <label for="tecnologias">Tecnologias *</label>
                <input type="text" id="tecnologias" name="tecnologias" 
                       placeholder="Ex: React, Node.js, Tailwind CSS" required>
            </div>
            <div class="form-group">
                <label for="link_github">Link GitHub</label>
                <input type="url" id="link_github" name="link_github" 
                       placeholder="https://github.com/...">
            </div>
            <div class="form-group">
                <label for="link_deploy">Link Deploy</label>
                <input type="url" id="link_deploy" name="link_deploy" 
                       placeholder="https://seu-projeto.com">
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModals()">Cancelar</button>
                <button type="submit" class="btn btn-primary">Salvar Projeto</button>
            </div>
        `;
    } else if (state.currentSection === 'certificados') {
        elements.itemForm.innerHTML = `
            <div class="form-group">
                <label for="nome">Nome do Curso/Certificação *</label>
                <input type="text" id="nome" name="nome" required>
            </div>
            <div class="form-group">
                <label for="instituicao">Instituição *</label>
                <input type="text" id="instituicao" name="instituicao" required>
            </div>
            <div class="form-group">
                <label for="origem">Origem</label>
                <select id="origem" name="origem">
                    <option value="">Selecione uma origem</option>
                    <option value="FIAP">FIAP</option>
                    <option value="Alura">Alura</option>
                    <option value="Coursera">Coursera</option>
                    <option value="Udemy">Udemy</option>
                    <option value="Outro">Outro</option>
                </select>
            </div>
            <div class="form-group">
                <label for="data_conclusao">Data de Conclusão *</label>
                <input type="date" id="data_conclusao" name="data_conclusao" required>
            </div>
            <div class="form-group">
                <label for="link_certificado">Link do Certificado</label>
                <input type="url" id="link_certificado" name="link_certificado" 
                       placeholder="https://...">
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModals()">Cancelar</button>
                <button type="submit" class="btn btn-primary">Salvar Certificado</button>
            </div>
        `;
    }
}

// ============================================================================
// FORM SUBMISSION
// ============================================================================

async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(elements.itemForm);
    const data = Object.fromEntries(formData);

    try {
        if (state.editingId) {
            await updateItem(state.editingId, data);
        } else {
            await createItem(data);
        }
        closeModals();
        
        if (state.currentSection === 'projetos') {
            loadProjetos();
        } else {
            loadCertificados();
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================================
// API CALLS
// ============================================================================

async function loadProjetos() {
    try {
        const response = await fetch('/admin/api/projetos');
        if (!response.ok) throw new Error('Erro ao carregar projetos');
        state.projetos = await response.json();
        renderProjetos();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function loadCertificados() {
    try {
        const response = await fetch('/admin/api/certificados');
        if (!response.ok) throw new Error('Erro ao carregar certificados');
        state.certificados = await response.json();
        renderCertificados();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function loadVisitas() {
    try {
        const response = await fetch('/admin/api/visitas');
        if (!response.ok) throw new Error('Erro ao carregar visitas');
        const data = await response.json();
        state.visitas = data.total || 0;
        elements.visitsCount.textContent = state.visitas.toLocaleString('pt-BR');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function createItem(data) {
    const endpoint = state.currentSection === 'projetos' 
        ? '/admin/api/projetos' 
        : '/admin/api/certificados';

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erro ao criar item');
    }

    showToast('Item criado com sucesso!', 'success');
}

async function updateItem(id, data) {
    const endpoint = state.currentSection === 'projetos' 
        ? `/admin/api/projetos/${id}` 
        : `/admin/api/certificados/${id}`;

    const response = await fetch(endpoint, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erro ao atualizar item');
    }

    showToast('Item atualizado com sucesso!', 'success');
}

async function deleteItem(id) {
    const endpoint = state.currentSection === 'projetos' 
        ? `/admin/api/projetos/${id}` 
        : `/admin/api/certificados/${id}`;

    const response = await fetch(endpoint, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erro ao deletar item');
    }

    showToast('Item deletado com sucesso!', 'success');
}

async function resetVisits() {
    if (!confirm('Tem certeza que deseja resetar o contador de visitas?')) return;

    try {
        // Reset to 0 by updating directly
        state.visitas = 0;
        elements.visitsCount.textContent = '0';
        showToast('Contador resetado!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================================
// RENDERING
// ============================================================================

function renderProjetos() {
    if (state.projetos.length === 0) {
        elements.projetosList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📁</div>
                <h3>Nenhum projeto ainda</h3>
                <p>Clique em "Novo Item" para adicionar seu primeiro projeto</p>
            </div>
        `;
        return;
    }

    elements.projetosList.innerHTML = state.projetos.map(projeto => `
        <div class="item-card">
            <h4>${projeto.titulo}</h4>
            <p>${projeto.descricao}</p>
            <div class="item-meta">
                ${projeto.tecnologias.split(',').map(tech => 
                    `<span class="meta-tag">${tech.trim()}</span>`
                ).join('')}
            </div>
            <div class="item-actions">
                <button class="btn btn-secondary btn-small" onclick="openEditModal(${projeto.id})">
                    ✏️ Editar
                </button>
                <button class="btn btn-danger btn-small" onclick="openDeleteModal(${projeto.id})">
                    🗑️ Deletar
                </button>
            </div>
        </div>
    `).join('');
}

function renderCertificados() {
    if (state.certificados.length === 0) {
        elements.certificadosList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🎓</div>
                <h3>Nenhum certificado ainda</h3>
                <p>Clique em "Novo Item" para adicionar seu primeiro certificado</p>
            </div>
        `;
        return;
    }

    elements.certificadosList.innerHTML = state.certificados.map(cert => `
        <div class="item-card">
            <h4>${cert.nome}</h4>
            <p>${cert.instituicao}</p>
            <div class="item-meta">
                ${cert.origem ? `<span class="meta-tag origin">${cert.origem}</span>` : ''}
                <span class="meta-tag">${formatDate(cert.data_conclusao)}</span>
            </div>
            <div class="item-actions">
                <button class="btn btn-secondary btn-small" onclick="openEditModal(${cert.id})">
                    ✏️ Editar
                </button>
                <button class="btn btn-danger btn-small" onclick="openDeleteModal(${cert.id})">
                    🗑️ Deletar
                </button>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// DELETE CONFIRMATION
// ============================================================================

async function confirmDelete() {
    try {
        await deleteItem(state.deleteId);
        closeModals();
        
        if (state.currentSection === 'projetos') {
            loadProjetos();
        } else {
            loadCertificados();
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================================
// UTILITIES
// ============================================================================

function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('pt-BR', options);
}

