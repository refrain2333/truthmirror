import pymysql
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

class SimpleDBService:
    """简单的数据库服务类，使用原生pymysql，避免SQLAlchemy的复杂性"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host='115.120.215.107',
                port=3306,
                user='truthmirror',
                password='truthmirror',
                database='truthmirror',
                charset='utf8mb4',
                autocommit=True  # 自动提交
            )
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        if not self.connection:
            if not self.connect():
                return []

        try:
            # 检查连接是否仍然有效
            self.connection.ping(reconnect=True)
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"查询执行失败: {e}")
            # 尝试重新连接
            self.connection = None
            if self.connect():
                try:
                    with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                        cursor.execute(sql, params)
                        return cursor.fetchall()
                except Exception as e2:
                    print(f"重连后查询仍然失败: {e2}")
            return []
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新/插入/删除操作，返回影响的行数或插入的ID"""
        if not self.connection:
            if not self.connect():
                return 0

        try:
            # 检查连接是否仍然有效
            self.connection.ping(reconnect=True)
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                # 如果是INSERT操作，返回最后插入的ID
                if sql.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid or affected_rows
                return affected_rows
        except Exception as e:
            print(f"更新执行失败: {e}")
            # 尝试重新连接
            self.connection = None
            if self.connect():
                try:
                    with self.connection.cursor() as cursor:
                        affected_rows = cursor.execute(sql, params)
                        if sql.strip().upper().startswith('INSERT'):
                            return cursor.lastrowid or affected_rows
                        return affected_rows
                except Exception as e2:
                    print(f"重连后更新仍然失败: {e2}")
            return 0
    
    # ===== Events 相关方法 =====
    
    def get_events(self, skip: int = 0, limit: int = 10, status: str = None) -> List[Dict[str, Any]]:
        """获取事件列表"""
        base_sql = """
        SELECT 
            e.id, e.title, e.description, e.keywords, e.status,
            e.interest_count, e.vote_count, e.support_votes, e.oppose_votes,
            e.ai_summary, e.ai_rating, e.nomination_deadline, e.creator_id,
            e.created_at, e.updated_at,
            u.username, u.nickname, u.role
        FROM events e
        LEFT JOIN users u ON e.creator_id = u.id
        """
        
        params = []
        if status:
            base_sql += " WHERE e.status = %s"
            params.append(status)
        
        base_sql += " ORDER BY e.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        results = self.execute_query(base_sql, tuple(params))
        print(f"成功获取了 {len(results)} 个事件")
        
        # 转换结果格式
        events = []
        for row in results:
            event = {
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "keywords": row["keywords"],
                "status": row["status"],
                "interest_count": row["interest_count"] or 0,
                "vote_count": row["vote_count"] or 0,
                "support_votes": row["support_votes"] or 0,
                "oppose_votes": row["oppose_votes"] or 0,
                "ai_summary": row["ai_summary"],
                "ai_rating": row["ai_rating"],
                "nomination_deadline": row["nomination_deadline"],
                "creator_id": row["creator_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "creator": {
                    "id": row["creator_id"],
                    "username": row["username"],
                    "nickname": row["nickname"],
                    "role": row["role"]
                } if row["username"] else None
            }
            events.append(event)
        
        return events

    def get_events_count(self, status: str = None) -> int:
        """获取事件总数"""
        base_sql = "SELECT COUNT(*) as count FROM events"
        params = []

        if status:
            base_sql += " WHERE status = %s"
            params.append(status)

        result = self.execute_query(base_sql, tuple(params))
        return result[0]['count'] if result else 0

    def get_event_detail(self, event_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """获取单个事件详情"""
        sql = """
        SELECT
            e.id, e.title, e.description, e.keywords, e.status,
            e.interest_count, e.vote_count, e.support_votes, e.oppose_votes,
            e.ai_summary, e.ai_rating, e.nomination_deadline, e.creator_id,
            e.created_at, e.updated_at,
            u.username, u.nickname, u.role
        FROM events e
        LEFT JOIN users u ON e.creator_id = u.id
        WHERE e.id = %s
        """

        results = self.execute_query(sql, (event_id,))
        if not results:
            return None

        row = results[0]

        # 检查用户是否已关注此事件
        user_interested = False
        if user_id:
            interest_check = self.execute_query(
                "SELECT id FROM event_interests WHERE event_id = %s AND user_id = %s",
                (event_id, user_id)
            )
            user_interested = len(interest_check) > 0

        # 获取信息源数据
        information_sources = []
        if row["status"] in ["voting", "confirmed"]:  # 在投票阶段和已确认阶段都返回信息源
            sources_sql = """
            SELECT id, url, title, website_name, ai_summary, relevance_score, created_at
            FROM information_sources
            WHERE event_id = %s
            ORDER BY relevance_score DESC, created_at ASC
            """
            sources_results = self.execute_query(sources_sql, (event_id,))
            information_sources = sources_results if sources_results else []

        return {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "keywords": row["keywords"],
            "status": row["status"],
            "interest_count": row["interest_count"] or 0,
            "vote_count": row["vote_count"] or 0,
            "support_votes": row["support_votes"] or 0,
            "oppose_votes": row["oppose_votes"] or 0,
            "ai_summary": row["ai_summary"],
            "ai_rating": row["ai_rating"],
            "nomination_deadline": row["nomination_deadline"],
            "creator_id": row["creator_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "user_interested": user_interested,
            "information_sources": information_sources,
            "creator": {
                "id": row["creator_id"],
                "username": row["username"],
                "nickname": row["nickname"],
                "role": row["role"]
            } if row["username"] else None
        }
    
    def create_event(self, title: str, description: str, keywords: str, creator_id: int = 1) -> Optional[Dict[str, Any]]:
        """创建新事件"""
        sql = """
        INSERT INTO events (title, description, keywords, creator_id, status, 
                           interest_count, vote_count, support_votes, oppose_votes,
                           created_at, updated_at)
        VALUES (%s, %s, %s, %s, 'pending', 0, 0, 0, 0, NOW(), NOW())
        """
        
        try:
            event_id = self.execute_update(sql, (title, description, keywords, creator_id))
            if event_id:
                # 更新用户统计
                self.execute_update(
                    "UPDATE users SET events_created = events_created + 1 WHERE id = %s",
                    (creator_id,)
                )
                # 返回创建的事件
                return self.get_event_detail(event_id)
        except Exception as e:
            print(f"创建事件失败: {e}")

        return None
    
    # ===== Users 相关方法 =====
    
    def get_users(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户列表"""
        sql = "SELECT id, username, email, nickname, role, created_at FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s"
        return self.execute_query(sql, (limit, skip))
    
    def get_user_detail(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户详情"""
        sql = "SELECT id, username, email, nickname, role, created_at FROM users WHERE id = %s"
        results = self.execute_query(sql, (user_id,))
        return results[0] if results else None
    
    def create_user(self, username: str, email: str, password: str, nickname: str = None) -> Optional[Dict[str, Any]]:
        """创建新用户"""
        sql = """INSERT INTO users (username, email, password, nickname, role, created_at, updated_at) 
                 VALUES (%s, %s, %s, %s, 'user', NOW(), NOW())"""
        
        try:
            user_id = self.execute_update(sql, (username, email, password, nickname or username))
            if user_id:
                return self.get_user_detail(user_id)
        except Exception as e:
            print(f"创建用户失败: {e}")
        
        return None
    
    # ===== Votes 相关方法 =====
    
    def create_vote(self, event_id: int, user_id: int, stance: str, user_comment: str = None) -> bool:
        """创建投票"""
        sql = "INSERT INTO votes (event_id, user_id, stance, user_comment, created_at) VALUES (%s, %s, %s, %s, NOW())"

        try:
            vote_id = self.execute_update(sql, (event_id, user_id, stance, user_comment))
            if vote_id:
                # 更新事件的投票统计
                if stance == "support":
                    self.execute_update(
                        "UPDATE events SET vote_count = vote_count + 1, support_votes = support_votes + 1 WHERE id = %s",
                        (event_id,)
                    )
                else:
                    self.execute_update(
                        "UPDATE events SET vote_count = vote_count + 1, oppose_votes = oppose_votes + 1 WHERE id = %s",
                        (event_id,)
                    )

                # 更新用户统计
                self.execute_update(
                    "UPDATE users SET votes_cast = votes_cast + 1 WHERE id = %s",
                    (user_id,)
                )
                return True
        except Exception as e:
            print(f"创建投票失败: {e}")
        
        return False
    
    def get_event_votes(self, event_id: int, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """获取事件的投票列表"""
        sql = """SELECT v.id, v.stance, v.user_comment, v.created_at,
                        u.username, u.nickname
                 FROM votes v
                 LEFT JOIN users u ON v.user_id = u.id
                 WHERE v.event_id = %s
                 ORDER BY v.created_at DESC
                 LIMIT %s OFFSET %s"""

        return self.execute_query(sql, (event_id, limit, skip))
    
    # ===== Event Interests 相关方法 =====

    def add_event_interest(self, event_id: int, user_id: int) -> bool:
        """添加事件兴趣"""
        try:
            # 检查是否已经表示过兴趣
            existing = self.execute_query(
                "SELECT id FROM event_interests WHERE event_id = %s AND user_id = %s",
                (event_id, user_id)
            )

            if existing:
                return False  # 已经表示过兴趣

            # 添加兴趣记录
            interest_id = self.execute_update(
                "INSERT INTO event_interests (event_id, user_id, created_at) VALUES (%s, %s, NOW())",
                (event_id, user_id)
            )

            if interest_id:
                # 更新事件的兴趣计数
                self.execute_update(
                    "UPDATE events SET interest_count = interest_count + 1 WHERE id = %s",
                    (event_id,)
                )

                # 更新用户统计
                self.execute_update(
                    "UPDATE users SET interests_marked = interests_marked + 1 WHERE id = %s",
                    (user_id,)
                )

                # 检查并更新事件状态
                self.check_and_update_event_status(event_id)

                return True

        except Exception as e:
            print(f"添加事件兴趣失败: {e}")

        return False

    def remove_event_interest(self, event_id: int, user_id: int) -> bool:
        """移除事件兴趣"""
        try:
            # 删除兴趣记录
            affected_rows = self.execute_update(
                "DELETE FROM event_interests WHERE event_id = %s AND user_id = %s",
                (event_id, user_id)
            )

            if affected_rows > 0:
                # 更新事件的兴趣计数
                self.execute_update(
                    "UPDATE events SET interest_count = interest_count - 1 WHERE id = %s",
                    (event_id,)
                )

                # 更新用户统计
                self.execute_update(
                    "UPDATE users SET interests_marked = interests_marked - 1 WHERE id = %s",
                    (user_id,)
                )
                return True

        except Exception as e:
            print(f"移除事件兴趣失败: {e}")

        return False

    def check_user_interest(self, event_id: int, user_id: int) -> bool:
        """检查用户是否对事件表示过兴趣"""
        try:
            result = self.execute_query(
                "SELECT id FROM event_interests WHERE event_id = %s AND user_id = %s",
                (event_id, user_id)
            )
            return len(result) > 0
        except Exception as e:
            print(f"检查用户兴趣失败: {e}")
            return False

    # ===== Event Status 相关方法 =====

    def update_event_status(self, event_id: int, new_status: str) -> bool:
        """更新事件状态"""
        try:
            affected_rows = self.execute_update(
                "UPDATE events SET status = %s WHERE id = %s",
                (new_status, event_id)
            )
            return affected_rows > 0
        except Exception as e:
            print(f"更新事件状态失败: {e}")
            return False

    def check_and_update_event_status(self, event_id: int, interest_threshold: int = 10) -> bool:
        """检查并自动更新事件状态"""
        try:
            # 获取事件当前状态和兴趣计数
            event_info = self.execute_query(
                "SELECT status, interest_count, vote_count FROM events WHERE id = %s",
                (event_id,)
            )

            if not event_info:
                return False

            current_status = event_info[0]['status']
            interest_count = event_info[0]['interest_count'] or 0
            vote_count = event_info[0]['vote_count'] or 0

            # 状态流转逻辑
            if current_status == 'nominated' and interest_count >= interest_threshold:
                # 从已提名转为AI处理状态，自动触发AI分析
                print(f"事件 {event_id} 达到关注阈值 ({interest_count}/{interest_threshold})，自动开始AI分析")
                success = self.update_event_status(event_id, 'processing')
                if success:
                    # 异步启动AI分析任务
                    self.start_ai_analysis_simulation(event_id)
                return success

            elif current_status == 'voting' and vote_count >= 20:
                # 投票达到20票后，自动转为确认状态
                print(f"事件 {event_id} 投票数达到阈值 ({vote_count}/20)，转为确认状态")
                return self.update_event_status(event_id, 'confirmed')

            return False

        except Exception as e:
            print(f"检查事件状态失败: {e}")
            return False

    def start_ai_processing(self, event_id: int) -> bool:
        """开始AI处理（从nominated状态转为processing）"""
        try:
            # 检查当前状态
            event_info = self.execute_query(
                "SELECT status FROM events WHERE id = %s",
                (event_id,)
            )

            if not event_info:
                return False

            current_status = event_info[0]['status']
            if current_status != 'nominated':
                print(f"事件 {event_id} 当前状态为 {current_status}，无法开始AI处理")
                return False

            # 更新状态为processing
            success = self.update_event_status(event_id, 'processing')
            if success:
                print(f"事件 {event_id} 开始AI处理")
                # 启动AI分析模拟
                self.start_ai_analysis_simulation(event_id)

            return success

        except Exception as e:
            print(f"开始AI处理失败: {e}")
            return False

    def complete_ai_processing(self, event_id: int, ai_summary: str = None, ai_rating: str = None) -> bool:
        """完成AI处理（从processing状态转为voting）"""
        try:
            # 检查当前状态
            event_info = self.execute_query(
                "SELECT status FROM events WHERE id = %s",
                (event_id,)
            )

            if not event_info:
                return False

            current_status = event_info[0]['status']
            if current_status != 'processing':
                print(f"事件 {event_id} 当前状态为 {current_status}，无法完成AI处理")
                return False

            # 更新AI分析结果和状态
            update_sql = "UPDATE events SET status = %s"
            params = ['voting']

            if ai_summary:
                update_sql += ", ai_summary = %s"
                params.append(ai_summary)

            if ai_rating is not None:
                update_sql += ", ai_rating = %s"
                params.append(ai_rating)

            update_sql += " WHERE id = %s"
            params.append(event_id)

            affected_rows = self.execute_update(update_sql, tuple(params))
            success = affected_rows > 0

            if success:
                print(f"事件 {event_id} AI处理完成，进入投票阶段")

            return success

        except Exception as e:
            print(f"完成AI处理失败: {e}")
            return False

    def start_ai_analysis_simulation(self, event_id: int):
        """启动AI分析模拟（异步执行）"""
        import threading
        import time
        import random

        def simulate_ai_analysis():
            try:
                print(f"开始模拟AI分析事件 {event_id}")

                # 模拟AI分析过程（10秒）
                time.sleep(10)

                # 生成模拟的AI分析结果
                ai_summaries = [
                    "经过AI深度分析，该事件具有较高的真实性和可信度。通过多源信息验证和语义分析，事件描述与已知事实高度吻合。",
                    "AI分析显示该事件存在一定争议性，需要进一步的人工验证。建议关注后续发展和更多证据收集。",
                    "根据AI模型分析，该事件涉及的关键信息已得到多方证实，事件的时间线和逻辑链条清晰完整。",
                    "AI检测发现该事件可能存在信息不完整的情况，建议补充更多细节和证据支持。",
                    "通过自然语言处理和事实核查，该事件的核心内容与公开资料基本一致，可信度较高。"
                ]

                ai_summary = random.choice(ai_summaries)
                # AI评级使用ENUM值
                ai_ratings = ['reliable', 'questionable', 'unreliable', 'insufficient']
                ai_rating = random.choice(ai_ratings)

                # 在线程中重新建立数据库连接
                from app.services.simple_db_service import SimpleDBService
                thread_db = SimpleDBService()
                if not thread_db.connect():
                    print(f"线程中数据库连接失败")
                    return

                # 填充10条模拟的兴趣数据
                thread_db.fill_simulation_interests(event_id)

                # 填充模拟的事件来源信息
                thread_db.fill_simulation_sources(event_id)

                # 更新事件的AI分析结果并转为投票状态
                success = thread_db.complete_ai_processing(event_id, ai_summary, ai_rating)

                if success:
                    print(f"事件 {event_id} AI分析完成，AI评级: {ai_rating}")
                else:
                    print(f"事件 {event_id} AI分析完成但状态更新失败")

                thread_db.close()

            except Exception as e:
                print(f"AI分析模拟失败: {e}")
                import traceback
                traceback.print_exc()

        # 在后台线程中执行
        thread = threading.Thread(target=simulate_ai_analysis)
        thread.daemon = True
        thread.start()

    def fill_simulation_interests(self, event_id: int):
        """填充模拟的兴趣数据"""
        try:
            # 生成10个模拟用户的兴趣记录
            simulation_users = [
                ("AI分析员001", "ai_analyst_001"),
                ("数据验证师", "data_validator"),
                ("事实核查员", "fact_checker"),
                ("信息分析师", "info_analyst"),
                ("真相追踪者", "truth_tracker"),
                ("证据收集员", "evidence_collector"),
                ("逻辑验证师", "logic_validator"),
                ("内容审核员", "content_reviewer"),
                ("可信度评估师", "credibility_assessor"),
                ("智能分析系统", "ai_analysis_system")
            ]

            for nickname, username in simulation_users:
                # 检查用户是否存在，不存在则创建
                user_id = self.get_or_create_simulation_user(username, nickname)

                # 添加兴趣记录（如果不存在）
                existing = self.execute_query(
                    "SELECT id FROM event_interests WHERE event_id = %s AND user_id = %s",
                    (event_id, user_id)
                )

                if not existing:
                    self.execute_update(
                        "INSERT INTO event_interests (event_id, user_id, created_at) VALUES (%s, %s, NOW())",
                        (event_id, user_id)
                    )

            # 更新事件的兴趣计数
            self.execute_update(
                "UPDATE events SET interest_count = (SELECT COUNT(*) FROM event_interests WHERE event_id = %s) WHERE id = %s",
                (event_id, event_id)
            )

            print(f"已为事件 {event_id} 填充10条模拟兴趣数据")

        except Exception as e:
            print(f"填充模拟兴趣数据失败: {e}")

    def get_or_create_simulation_user(self, username: str, nickname: str) -> int:
        """获取或创建模拟用户"""
        try:
            # 检查用户是否存在
            existing_user = self.execute_query(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )

            if existing_user:
                return existing_user[0]['id']

            # 创建新用户（添加email和password字段）
            email = f"{username}@ai-system.local"
            password = "ai_system_password"  # 模拟用户的默认密码
            self.execute_update(
                "INSERT INTO users (username, email, password, nickname, role, created_at) VALUES (%s, %s, %s, %s, 'ai_system', NOW())",
                (username, email, password, nickname)
            )

            # 获取刚创建的用户ID
            new_user = self.execute_query(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            user_id = new_user[0]['id'] if new_user else None

            return user_id

        except Exception as e:
            print(f"创建模拟用户失败: {e}")
            return None

    def fill_simulation_sources(self, event_id: int):
        """填充模拟的事件来源信息"""
        try:
            # 生成模拟的信息来源
            simulation_sources = [
                {
                    "url": "https://news.example.com/breaking-news-123",
                    "title": "权威媒体深度报道：事件真相调查",
                    "website_name": "权威新闻网",
                    "content": "经过深入调查，我们发现该事件涉及多个方面的复杂情况...",
                    "ai_summary": "权威媒体通过实地调查和多方采访，提供了详细的事件背景和发展过程。",
                    "relevance_score": 0.95
                },
                {
                    "url": "https://official.gov.cn/statement-456",
                    "title": "官方声明：关于近期事件的澄清说明",
                    "website_name": "官方网站",
                    "content": "针对近期网络传播的相关信息，现作出如下澄清...",
                    "ai_summary": "官方机构发布正式声明，对事件相关情况进行了官方澄清和说明。",
                    "relevance_score": 0.92
                },
                {
                    "url": "https://social.platform.com/witness-post-789",
                    "title": "目击者现场记录：第一手资料分享",
                    "website_name": "社交平台",
                    "content": "我当时就在现场，看到了整个过程的发生...",
                    "ai_summary": "现场目击者提供的第一手资料，包含了事件发生时的具体细节。",
                    "relevance_score": 0.88
                },
                {
                    "url": "https://expert.analysis.org/report-101",
                    "title": "专家分析报告：事件背景与影响评估",
                    "website_name": "专业分析机构",
                    "content": "从专业角度分析，该事件反映了深层次的社会问题...",
                    "ai_summary": "专业机构从多个维度对事件进行了深入分析，提供了专业见解。",
                    "relevance_score": 0.85
                },
                {
                    "url": "https://verify.factcheck.com/investigation-202",
                    "title": "事实核查：多方信息交叉验证结果",
                    "website_name": "事实核查网站",
                    "content": "通过对比多个信息源，我们对事件的真实性进行了核查...",
                    "ai_summary": "专业事实核查机构通过多方信息交叉验证，对事件真实性进行了评估。",
                    "relevance_score": 0.90
                }
            ]

            for source in simulation_sources:
                # 检查是否已存在相同URL的来源
                existing = self.execute_query(
                    "SELECT id FROM information_sources WHERE event_id = %s AND url = %s",
                    (event_id, source["url"])
                )

                if not existing:
                    self.execute_update(
                        """INSERT INTO information_sources
                           (event_id, url, title, website_name, content, ai_summary, relevance_score, created_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                        (event_id, source["url"], source["title"], source["website_name"],
                         source["content"], source["ai_summary"], source["relevance_score"])
                    )

            print(f"已为事件 {event_id} 填充5条模拟来源信息")

        except Exception as e:
            print(f"填充模拟来源信息失败: {e}")

    # ===== Search 相关方法 =====

    def search_events(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """搜索事件"""
        if not query:
            # 如果没有查询词，返回最新的事件
            sql = """SELECT e.id, e.title, e.description, e.keywords, e.status, 
                            e.created_at, u.username, u.nickname
                     FROM events e
                     LEFT JOIN users u ON e.creator_id = u.id
                     ORDER BY e.created_at DESC
                     LIMIT %s"""
            return self.execute_query(sql, (limit,))
        else:
            # 在标题、描述和关键词中搜索
            search_term = f"%{query}%"
            sql = """SELECT e.id, e.title, e.description, e.keywords, e.status, 
                            e.created_at, u.username, u.nickname
                     FROM events e
                     LEFT JOIN users u ON e.creator_id = u.id
                     WHERE e.title LIKE %s OR e.description LIKE %s OR e.keywords LIKE %s
                     ORDER BY e.created_at DESC
                     LIMIT %s"""
            return self.execute_query(sql, (search_term, search_term, search_term, limit))

# 创建全局数据库服务实例
db_service = SimpleDBService()