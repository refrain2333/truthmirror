// 真相之镜 API 管理器 - v1.1 (端口修复版本)// 基于 API_GUIDE.md 的完整实现

class TruthMirrorAPI {
    constructor(baseUrl = 'http://127.0.0.1:8000/api/v1') {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    // 通用API调用方法
    async apiCall(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            // 提取并合并headers，避免被options覆盖
            const { headers: optionHeaders, ...restOptions } = options;
            const mergedHeaders = {
                ...this.headers,
                ...optionHeaders
            };

            const response = await fetch(url, {
                headers: mergedHeaders,
                mode: 'cors',  // 明确指定CORS模式
                ...restOptions
            });
            
            // 检查响应状态
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('资源不存在');
                } else if (response.status === 400) {
                    const error = await response.json();
                    throw new Error(error.detail || '请求参数错误');
                } else if (response.status === 422) {
                    // 处理验证错误
                    try {
                        const error = await response.json();
                        console.error('422验证错误详情:', error);
                        if (error.detail && Array.isArray(error.detail)) {
                            const errorMessages = error.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
                            throw new Error(`验证错误: ${errorMessages}`);
                        } else {
                            throw new Error(error.detail || '数据验证失败');
                        }
                    } catch (parseError) {
                        console.error('解析422错误响应失败:', parseError);
                        throw new Error('数据验证失败，请检查输入格式');
                    }
                } else if (response.status >= 500) {
                    throw new Error('服务器内部错误，请稍后重试');
                } else {
                    throw new Error(`请求失败: ${response.status}`);
                }
            }
            
            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                console.warn('API连接失败，可能需要启动后端服务');
                throw new Error('网络连接失败，请检查后端服务状态');
            }
            throw error;
        }
    }

    // ===== 事件管理API =====

    // 获取事件列表
    async getEvents(params = {}) {
        const { skip = 0, limit = 10, status = '', _t = null } = params;
        const queryParams = new URLSearchParams();
        if (skip) queryParams.append('skip', skip);
        if (limit) queryParams.append('limit', limit);
        if (status) queryParams.append('status', status);
        if (_t) queryParams.append('_t', _t); // 缓存破坏参数
        
        const endpoint = `/events/?${queryParams}`;
        return await this.apiCall(endpoint, { 
            method: 'GET',
            cache: 'no-cache' // 禁用缓存
        });
    }

    // 获取事件详情
    async getEventDetail(eventId) {
        // 获取当前用户ID
        const currentUser = this.getCurrentUser();
        const userId = currentUser ? currentUser.id : null;

        const headers = {};
        if (userId) {
            headers['x-user-id'] = userId.toString();
        }

        return await this.apiCall(`/events/${eventId}`, {
            method: 'GET',
            headers: headers
        });
    }

    // 创建新事件
    async createEvent(eventData) {
        // 从localStorage获取当前用户信息
        const currentUser = this.getCurrentUser();
        const headers = {
            'Content-Type': 'application/json'
        };

        // 如果有用户信息，添加到请求头
        if (currentUser && currentUser.id) {
            headers['x-user-id'] = currentUser.id.toString();
        }

        return await this.apiCall('/events/', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(eventData)
        });
    }

    // 获取当前用户信息的辅助方法
    getCurrentUser() {
        try {
            const userStr = localStorage.getItem('currentUser');
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('解析用户信息失败:', error);
            return null;
        }
    }

    // 更新用户信息
    async updateUser(userId, userData) {
        return await this.apiCall(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    // 更新事件
    async updateEvent(eventId, eventUpdate) {
        return await this.apiCall(`/events/${eventId}`, {
            method: 'PUT',
            body: JSON.stringify(eventUpdate)
        });
    }

    // 表示兴趣
    async addInterest(eventId) {
        // 获取当前用户ID
        const currentUser = this.getCurrentUser();
        const userId = currentUser ? currentUser.id : 1;

        return await this.apiCall(`/events/${eventId}/interest`, {
            method: 'POST',
            headers: {
                'x-user-id': userId.toString()
            }
        });
    }

    // 取消兴趣
    async removeInterest(eventId) {
        // 获取当前用户ID
        const currentUser = this.getCurrentUser();
        const userId = currentUser ? currentUser.id : 1;

        return await this.apiCall(`/events/${eventId}/interest`, {
            method: 'DELETE',
            headers: {
                'x-user-id': userId.toString()
            }
        });
    }

    // ===== 用户管理API =====

    // 创建用户（注册）
    async createUser(userData) {
        return await this.apiCall('/users/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // 获取用户信息
    async getUser(userId) {
        return await this.apiCall(`/users/${userId}`, { method: 'GET' });
    }

    // 获取用户列表
    async getUsers(params = {}) {
        const { skip = 0, limit = 10 } = params;
        const queryParams = new URLSearchParams({ skip, limit });
        return await this.apiCall(`/users/?${queryParams}`, { method: 'GET' });
    }

    // 更新用户信息
    async updateUser(userId, userUpdate) {
        return await this.apiCall(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userUpdate)
        });
    }

    // ===== 投票系统API =====

    // 创建投票
    async createVote(voteData) {
        return await this.apiCall('/votes/', {
            method: 'POST',
            body: JSON.stringify(voteData)
        });
    }

    // 获取事件投票列表
    async getEventVotes(eventId, params = {}) {
        const { skip = 0, limit = 100 } = params;
        const queryParams = new URLSearchParams({ skip, limit });
        return await this.apiCall(`/votes/event/${eventId}?${queryParams}`, {
            method: 'GET'
        });
    }

    // 获取投票统计
    async getVoteStats(eventId) {
        return await this.apiCall(`/votes/stats/${eventId}`, {
            method: 'GET'
        });
    }

    // 更新投票
    async updateVote(voteId, voteUpdate) {
        return await this.apiCall(`/votes/${voteId}`, {
            method: 'PUT',
            body: JSON.stringify(voteUpdate)
        });
    }

    // 删除投票
    async deleteVote(voteId) {
        return await this.apiCall(`/votes/${voteId}`, {
            method: 'DELETE'
        });
    }

    // ===== 搜索和AI分析API =====

    // 触发搜索和分析
    async triggerAnalysis(eventId) {
        return await this.apiCall(`/search/trigger/${eventId}`, {
            method: 'POST'
        });
    }

    // ===== 智能新闻分析API =====

    // 触发智能分析（按照事件生命周期流程）
    async analyzeEvent(eventTitle, eventDescription, eventId = null) {
        return await this.apiCall('/analysis/analyze', {
            method: 'POST',
            body: JSON.stringify({
                event_title: eventTitle,
                event_description: eventDescription,
                event_id: eventId
            })
        });
    }

    // 获取AI分析真实进度状态
    async getAnalysisStatus(eventId) {
        return await this.apiCall(`/analysis/status/${eventId}`, {
            method: 'GET',
            cache: 'no-cache'
        });
    }

    // 获取最终结果（用于完成后渲染与刷新恢复）
    async getAnalysisResult(eventId) {
        return await this.apiCall(`/analysis/result/${eventId}`, {
            method: 'GET',
            cache: 'no-cache'
        });
    }

    // 获取所有事件的分析状态（用于首页全量同步）
    async getAllAnalysisStatus() {
        return await this.apiCall('/analysis/status', {
            method: 'GET',
            cache: 'no-cache'
        });
    }

    // 测试智能分析
    async testAnalysis() {
        return await this.apiCall('/analysis/test', {
            method: 'POST'
        });
    }

    // 获取事件信息源
    async getEventSources(eventId, params = {}) {
        const { skip = 0, limit = 20 } = params;
        const queryParams = new URLSearchParams({ skip, limit });
        return await this.apiCall(`/events/${eventId}/sources?${queryParams}`, {
            method: 'GET'
        });
    }

    // 获取AI分析结果
    async getEventAnalysis(eventId) {
        return await this.apiCall(`/events/${eventId}/analysis`, {
            method: 'GET'
        });
    }

    // 获取事件详情信息
    async getEventDetailInfo(eventId) {
        return await this.apiCall(`/events/${eventId}/detail`, {
            method: 'GET'
        });
    }

    // 创建事件详情
    async createEventDetail(eventId, detailData) {
        return await this.apiCall(`/events/${eventId}/detail`, {
            method: 'POST',
            body: JSON.stringify({
                ...detailData,
                event_id: eventId
            })
        });
    }

    // 更新事件详情
    async updateEventDetail(eventId, detailUpdate) {
        return await this.apiCall(`/events/${eventId}/detail`, {
            method: 'PUT',
            body: JSON.stringify(detailUpdate)
        });
    }

    // ===== 高级组合方法 =====

    // 加载完整的事件页面数据
    async loadEventPage(eventId) {
        try {
            // 并行加载基础事件信息
            const eventDetail = await this.getEventDetail(eventId);
            
            // 根据事件状态加载额外数据
            const promises = [];
            
            // 如果事件有投票，加载投票统计
            if (['voting', 'confirmed'].includes(eventDetail.status)) {
                promises.push(this.getVoteStats(eventId));
            } else {
                promises.push(Promise.resolve(null));
            }
            
            // 如果有分析结果，加载AI分析
            if (['voting', 'confirmed'].includes(eventDetail.status)) {
                promises.push(
                    this.getEventAnalysis(eventId).catch(() => null)
                );
            } else {
                promises.push(Promise.resolve(null));
            }
            
            // 加载信息源
            promises.push(
                this.getEventSources(eventId).catch(() => [])
            );
            
            const [voteStats, aiAnalysis, informationSources] = await Promise.all(promises);
            
            return {
                ...eventDetail,
                vote_stats: voteStats,
                ai_analysis: aiAnalysis,
                information_sources: informationSources
            };
        } catch (error) {
            console.error('加载事件页面失败:', error);
            throw error;
        }
    }

    // 用户认证（使用登录API）
    async authenticateUser(username, password) {
        try {
            return await this.apiCall('/users/login', {
                method: 'POST',
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });
        } catch (error) {
            console.error('用户认证失败:', error);
            throw error;
        }
    }
}

// 事件状态枚举
const EVENT_STATUS = {
    PENDING: 'pending',
    NOMINATED: 'nominated', 
    PROCESSING: 'processing',
    VOTING: 'voting',
    CONFIRMED: 'confirmed'
};

const STATUS_LABELS = {
    [EVENT_STATUS.PENDING]: '待审核',
    [EVENT_STATUS.NOMINATED]: '已提名',
    [EVENT_STATUS.PROCESSING]: '处理中',
    [EVENT_STATUS.VOTING]: '投票中',
    [EVENT_STATUS.CONFIRMED]: '已确认'
};

// 投票立场枚举
const VOTE_STANCE = {
    SUPPORT: 'support',
    OPPOSE: 'oppose',
    NEUTRAL: 'neutral'
};

const STANCE_LABELS = {
    [VOTE_STANCE.SUPPORT]: '支持',
    [VOTE_STANCE.OPPOSE]: '反对',
    [VOTE_STANCE.NEUTRAL]: '中性'
};

// 用户角色枚举
const USER_ROLE = {
    USER: 'user',
    ADMIN: 'admin'
};

// 全局API实例
const api = new TruthMirrorAPI();

// 模拟数据（当API不可用时使用）
const MOCK_DATA = {
    events: [
        {
            id: 1,
            title: '某地发生重大交通事故',
            description: '据报道，今日上午某高速公路发生多车连环相撞事故，造成多人伤亡。目前相关部门正在调查事故原因。',
            keywords: '交通事故,高速公路,伤亡',
            status: 'voting',
            interest_count: 156,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            creator_id: 1,
            creator: {
                id: 1,
                username: 'news_reporter',
                email: 'reporter@example.com',
                role: 'user',
                is_active: true,
                created_at: new Date(Date.now() - 86400000).toISOString()
            }
        },
        {
            id: 2,
            title: '新型科技产品发布会',
            description: '某知名科技公司宣布将于下月举办新产品发布会，预计将推出革命性的新技术产品。',
            keywords: '科技,发布会,新产品',
            status: 'processing',
            interest_count: 234,
            created_at: new Date(Date.now() - 86400000).toISOString(),
            updated_at: new Date(Date.now() - 86400000).toISOString(),
            creator_id: 2,
            creator: {
                id: 2,
                username: 'tech_watcher',
                email: 'tech@example.com',
                role: 'user',
                is_active: true,
                created_at: new Date(Date.now() - 172800000).toISOString()
            }
        },
        {
            id: 3,
            title: '环保政策新规定实施',
            description: '政府部门发布新的环保政策，要求企业在未来三年内达到新的排放标准。',
            keywords: '环保,政策,排放标准',
            status: 'confirmed',
            interest_count: 78,
            created_at: new Date(Date.now() - 172800000).toISOString(),
            updated_at: new Date(Date.now() - 172800000).toISOString(),
            creator_id: 3,
            creator: {
                id: 3,
                username: 'policy_monitor',
                email: 'policy@example.com',
                role: 'user',
                is_active: true,
                created_at: new Date(Date.now() - 259200000).toISOString()
            }
        }
    ],
    
    voteStats: {
        1: {
            total_votes: 1123,
            support_votes: 892,
            oppose_votes: 231,
            support_percentage: 79.4,
            oppose_percentage: 20.6
        },
        3: {
            total_votes: 15432,
            support_votes: 12234,
            oppose_votes: 3198,
            support_percentage: 79.3,
            oppose_percentage: 20.7
        }
    },
    
    users: [
        {
            id: 1,
            username: 'admin',
            email: 'admin@truthmirror.com',
            role: 'admin',
            is_active: true,
            created_at: new Date(Date.now() - 604800000).toISOString()
        },
        {
            id: 2,
            username: 'user',
            email: 'user@example.com',
            role: 'user',
            is_active: true,
            created_at: new Date(Date.now() - 432000000).toISOString()
        }
    ]
};

// API调用助手 - 不使用模拟数据降级
async function apiWithFallback(apiCall, fallbackData) {
    return await apiCall();
}