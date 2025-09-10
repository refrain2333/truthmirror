#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试20票自动确认功能
当投票数达到20票时，事件状态应该自动从voting转换为confirmed
"""

import sys
import os
import time
import random

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.simple_db_service import SimpleDBService

def test_20_votes_auto_confirm():
    """测试20票自动确认功能"""
    
    print("🎯 测试20票自动确认功能")
    print("=" * 50)
    
    # 初始化数据库服务
    db = SimpleDBService()
    
    try:
        # 第一步：找到一个处于voting状态的事件
        print("\n📋 第一步：查找投票中的事件")
        voting_events = db.execute_query(
            "SELECT id, title, status, vote_count FROM events WHERE status = 'voting' ORDER BY id DESC LIMIT 1"
        )
        
        if not voting_events:
            print("❌ 没有找到处于投票状态的事件")
            return False
        
        event = voting_events[0]
        event_id = event['id']
        current_votes = event['vote_count'] or 0
        
        print(f"✅ 找到事件: {event['title']}")
        print(f"   事件ID: {event_id}")
        print(f"   当前状态: {event['status']}")
        print(f"   当前投票数: {current_votes}")
        
        # 第二步：计算需要添加的投票数
        votes_needed = 20 - current_votes
        if votes_needed <= 0:
            print(f"⚠️  事件已有{current_votes}票，应该已经转为confirmed状态")
            # 检查状态
            current_event = db.execute_query("SELECT status FROM events WHERE id = %s", (event_id,))
            if current_event:
                print(f"   实际状态: {current_event[0]['status']}")
            return True
        
        print(f"\n🎲 第二步：需要添加 {votes_needed} 票来达到20票阈值")
        
        # 第三步：创建测试用户（如果需要）
        print("\n👥 第三步：准备测试用户")
        
        # 获取现有用户数量
        user_count = db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
        print(f"   当前用户数: {user_count}")
        
        # 确保有足够的用户来投票
        users_needed = max(0, votes_needed - user_count + 1)  # +1 for admin
        if users_needed > 0:
            print(f"   需要创建 {users_needed} 个新用户")
            for i in range(users_needed):
                username = f"test_voter_{user_count + i + 1}"
                email = f"{username}@test.com"
                db.execute_update(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (username, email, "test_hash", "user")
                )
                print(f"   ✅ 创建用户: {username}")
        
        # 第四步：获取可用用户列表
        all_users = db.execute_query("SELECT id, username FROM users ORDER BY id")
        
        # 获取已投票的用户
        voted_users = db.execute_query(
            "SELECT user_id FROM votes WHERE event_id = %s",
            (event_id,)
        )
        voted_user_ids = [vote['user_id'] for vote in voted_users]
        
        # 过滤出未投票的用户
        available_users = [user for user in all_users if user['id'] not in voted_user_ids]
        
        print(f"   可用于投票的用户数: {len(available_users)}")
        
        if len(available_users) < votes_needed:
            print(f"❌ 可用用户不足，需要{votes_needed}个，只有{len(available_users)}个")
            return False
        
        # 第五步：模拟投票过程
        print(f"\n🗳️  第四步：开始模拟投票过程")
        
        for i in range(votes_needed):
            user = available_users[i]
            user_id = user['id']
            username = user['username']
            
            # 随机选择支持或反对
            stance = random.choice(['support', 'oppose'])
            stance_text = '认同' if stance == 'support' else '不认同'
            
            print(f"   投票 {current_votes + i + 1}/20: {username} -> {stance_text}")
            
            # 创建投票
            vote_id = db.execute_update(
                "INSERT INTO votes (event_id, user_id, stance, created_at) VALUES (%s, %s, %s, NOW())",
                (event_id, user_id, stance)
            )
            
            if vote_id:
                # 更新事件投票统计
                if stance == 'support':
                    db.execute_update(
                        "UPDATE events SET vote_count = vote_count + 1, support_votes = support_votes + 1 WHERE id = %s",
                        (event_id,)
                    )
                else:
                    db.execute_update(
                        "UPDATE events SET vote_count = vote_count + 1, oppose_votes = oppose_votes + 1 WHERE id = %s",
                        (event_id,)
                    )
                
                # 检查状态转换
                db.check_and_update_event_status(event_id)
                
                # 检查当前状态
                current_event = db.execute_query(
                    "SELECT status, vote_count FROM events WHERE id = %s",
                    (event_id,)
                )[0]
                
                current_status = current_event['status']
                current_vote_count = current_event['vote_count']
                
                print(f"      -> 当前投票数: {current_vote_count}, 状态: {current_status}")
                
                # 如果状态已经转为confirmed，停止投票
                if current_status == 'confirmed':
                    print(f"🎉 状态已自动转换为confirmed！投票数: {current_vote_count}")
                    break
                
                # 短暂延迟
                time.sleep(0.1)
            else:
                print(f"      ❌ 投票失败")
        
        # 第六步：验证最终结果
        print(f"\n📊 第五步：验证最终结果")
        final_event = db.execute_query(
            "SELECT id, title, status, vote_count, support_votes, oppose_votes FROM events WHERE id = %s",
            (event_id,)
        )[0]
        
        print(f"事件ID: {final_event['id']}")
        print(f"标题: {final_event['title']}")
        print(f"最终状态: {final_event['status']}")
        print(f"总投票数: {final_event['vote_count']}")
        print(f"认同票: {final_event['support_votes']}")
        print(f"不认同票: {final_event['oppose_votes']}")
        
        if final_event['status'] == 'confirmed' and final_event['vote_count'] >= 20:
            print("✅ 测试成功！事件已自动转为confirmed状态")
            return True
        else:
            print("❌ 测试失败！状态转换未按预期工作")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_20_votes_auto_confirm()
    if success:
        print("\n🎉 20票自动确认功能测试通过！")
    else:
        print("\n❌ 20票自动确认功能测试失败！")
