// API Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// API Helper Functions
const api = {
    // Generic fetch wrapper
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Auth endpoints
    auth: {
        async getCaptcha() {
            return api.request('/captcha');
        },

        async login(email, password, role, captcha) {
            return api.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password, role, captcha })
            });
        },

        async signup(fullName, email, password, role, captcha) {
            return api.request('/auth/signup', {
                method: 'POST',
                body: JSON.stringify({ fullName, email, password, role, captcha })
            });
        },

        async logout() {
            return api.request('/auth/logout', { method: 'POST' });
        },

        async getCurrentUser() {
            return api.request('/auth/me');
        }
    },

    // Advertisement endpoints
    advertisements: {
        async getAll(status = null) {
            const query = status ? `?status=${status}` : '';
            return api.request(`/advertisements${query}`);
        },

        async getById(id) {
            return api.request(`/advertisements/${id}`);
        },

        async getItems(advertisementId) {
            return api.request(`/advertisements/${advertisementId}/items`);
        },

        async updateStatus(id, status) {
            return api.request(`/advertisements/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ status })
            });
        }
    },

    // Item endpoints
    items: {
        async getAll(status = null) {
            const query = status ? `?status=${status}` : '';
            return api.request(`/items${query}`);
        },

        async getById(id) {
            return api.request(`/items/${id}`);
        },

        async update(id, data) {
            return api.request(`/items/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },

        async completeBoard(itemId, expertIds, panelType = 'Final Interview Panel') {
            return api.request(`/items/${itemId}/complete-board`, {
                method: 'POST',
                body: JSON.stringify({ expertIds, panelType })
            });
        },

        async getPanel(itemId) {
            return api.request(`/items/${itemId}/panel`);
        }
    },

    // Expert endpoints
    experts: {
        async getAll(category = null) {
            const query = category ? `?category=${category}` : '';
            return api.request(`/experts${query}`);
        },

        async getById(id) {
            return api.request(`/experts/${id}`);
        }
    },

    // Panel endpoints
    panels: {
        async create(itemId, expertIds, boardType) {
            return api.request('/panels', {
                method: 'POST',
                body: JSON.stringify({ itemId, expertIds, boardType })
            });
        },

        async getById(id) {
            return api.request(`/panels/${id}`);
        },

        async updateInviteStatus(panelId, expertId, status) {
            return api.request(`/panels/${panelId}/invite`, {
                method: 'PUT',
                body: JSON.stringify({ expertId, status })
            });
        }
    },

    // PDF Upload endpoints
    pdf: {
        async upload(file) {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/pdf/upload`, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            return data;
        },

        async preview(file) {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/pdf/preview`, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Preview failed');
            }
            return data;
        },

        async reprocess(advertisementId) {
            return api.request(`/pdf/reprocess/${advertisementId}`, { method: 'POST' });
        }
    },

    // AI Matching endpoints
    matching: {
        async calculateScores(itemId, options = {}) {
            return api.request(`/matching/calculate/${itemId}`, {
                method: 'POST',
                body: JSON.stringify(options)
            });
        },

        async generatePanel(itemId, options = {}) {
            return api.request(`/matching/generate-panel/${itemId}`, {
                method: 'POST',
                body: JSON.stringify(options)
            });
        },

        async getScoreBreakdown(itemId, expertId, useLlm = true) {
            return api.request(`/matching/score/${itemId}/${expertId}?use_llm=${useLlm}`);
        },

        async updateEmbeddings() {
            return api.request('/matching/update-embeddings', { method: 'POST' });
        },

        async getExpertsWithScores(itemId) {
            return api.request(`/matching/experts-with-scores/${itemId}`);
        }
    },

    // Seed database
    async seedDatabase() {
        return api.request('/seed', { method: 'POST' });
    }
};

// Session helpers using localStorage as backup
const session = {
    setUser(user) {
        localStorage.setItem('mira_user', JSON.stringify(user));
    },

    getUser() {
        const user = localStorage.getItem('mira_user');
        return user ? JSON.parse(user) : null;
    },

    clearUser() {
        localStorage.removeItem('mira_user');
    },

    isLoggedIn() {
        return this.getUser() !== null;
    }
};

// Toast notification helper
function showToast(message, type = 'success') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// URL parameter helper
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Check auth and redirect if not logged in
function requireAuth() {
    if (!session.isLoggedIn()) {
        window.location.href = 'login.html';
        return false;
    }
    // Setup navbar based on role
    setupNavbar();
    return true;
}

// Setup navbar visibility based on user role
function setupNavbar() {
    const user = session.getUser();
    if (!user) return;

    const userRole = user.role || 'candidate';

    // Find all nav links with data-role attribute
    document.querySelectorAll('[data-role]').forEach(link => {
        const allowedRoles = link.dataset.role.split(',').map(r => r.trim());

        // Hide link if user's role is not in allowed roles
        if (!allowedRoles.includes(userRole)) {
            link.style.display = 'none';
        }
    });
}

// Redirect if user doesn't have required role
function requireRole(allowedRoles) {
    const user = session.getUser();
    if (!user) {
        window.location.href = 'login.html';
        return false;
    }

    if (!allowedRoles.includes(user.role)) {
        showToast('Access denied. You do not have permission to view this page.', 'error');
        window.location.href = 'home.html';
        return false;
    }
    return true;
}
