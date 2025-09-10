import sys
import time
import requests
sys.path.append('backend')
from app.services.simple_db_service import SimpleDBService

def test_10_users_auto_trigger():
    """测试10人关注自动触发AI分析功能"""
    
    # 创建数据库连接
    db = SimpleDBService()
    if not db.connect():
        print("❌ 数据库连接失败")
        return
    
    print("🚀 开始测试10人关注自动触发AI分析功能")
    print("=" * 50)
    
    # 第一步：创建测试事件
    print("📝 第一步：创建测试事件")
    event_result = db.create_event(
        title="10人关注自动触发测试事件",
        description="这是一个专门测试10人关注自动触发AI分析功能的事件。当达到10人关注时，系统应该自动开始AI分析。",
        keywords="自动触发,10人关注,AI分析,测试",
        creator_id=1
    )

    if not event_result:
        print("❌ 创建测试事件失败")
        db.close()
        return

    event_id = event_result['id']
    print(f"✅ 测试事件创建成功，ID: {event_id}")
    
    # 第二步：将事件设置为nominated状态
    print("\n📋 第二步：设置事件为nominated状态")
    success = db.update_event_status(event_id, 'nominated')
    if success:
        print("✅ 事件状态设置为nominated")
    else:
        print("❌ 设置事件状态失败")
        db.close()
        return
    
    # 第三步：创建10个测试用户并添加关注
    print("\n👥 第三步：模拟10个用户关注事件")
    test_users = [
        ("test_user_1", "测试用户1"),
        ("test_user_2", "测试用户2"), 
        ("test_user_3", "测试用户3"),
        ("test_user_4", "测试用户4"),
        ("test_user_5", "测试用户5"),
        ("test_user_6", "测试用户6"),
        ("test_user_7", "测试用户7"),
        ("test_user_8", "测试用户8"),
        ("test_user_9", "测试用户9"),
        ("test_user_10", "测试用户10")
    ]
    
    for i, (username, nickname) in enumerate(test_users, 1):
        # 创建或获取用户
        user_id = db.get_or_create_simulation_user(username, nickname)
        if not user_id:
            print(f"❌ 创建用户 {username} 失败")
            continue
            
        # 添加关注
        success = db.add_event_interest(event_id, user_id)
        if success:
            print(f"✅ 用户{i} ({nickname}) 关注成功")
        else:
            print(f"⚠️ 用户{i} ({nickname}) 关注失败（可能已关注）")
        
        # 检查事件状态
        event_info = db.execute_query(
            "SELECT status, interest_count FROM events WHERE id = %s",
            (event_id,)
        )
        
        if event_info:
            status = event_info[0]['status']
            interest_count = event_info[0]['interest_count']
            print(f"   当前状态: {status}, 关注人数: {interest_count}")
            
            # 如果状态变为processing，说明自动触发成功
            if status == 'processing':
                print(f"🎉 自动触发成功！在第{i}个用户关注后，事件状态变为processing")
                break
        
        time.sleep(0.5)  # 稍微延迟，避免过快
    
    # 第四步：等待AI分析完成
    print("\n⏳ 第四步：等待AI分析完成（最多15秒）")
    for i in range(15):
        event_info = db.execute_query(
            "SELECT status, ai_summary, ai_rating, interest_count FROM events WHERE id = %s",
            (event_id,)
        )
        
        if event_info:
            status = event_info[0]['status']
            ai_summary = event_info[0]['ai_summary']
            ai_rating = event_info[0]['ai_rating']
            interest_count = event_info[0]['interest_count']
            
            print(f"等待中... 状态: {status}, 关注人数: {interest_count}")
            
            if status == 'voting':
                print("🎉 AI分析完成！事件已进入投票阶段")
                break
        
        time.sleep(1)
    
    # 第五步：验证最终结果
    print("\n📊 第五步：验证最终结果")
    event_info = db.execute_query(
        "SELECT id, title, status, ai_summary, ai_rating, interest_count FROM events WHERE id = %s",
        (event_id,)
    )
    
    if event_info:
        e = event_info[0]
        print(f"事件ID: {e['id']}")
        print(f"标题: {e['title']}")
        print(f"最终状态: {e['status']}")
        print(f"AI摘要: {e['ai_summary']}")
        print(f"AI评级: {e['ai_rating']}")
        print(f"关注人数: {e['interest_count']}")
        
        # 检查兴趣记录数
        interests = db.execute_query('SELECT COUNT(*) as count FROM event_interests WHERE event_id = %s', (event_id,))
        print(f"实际兴趣记录数: {interests[0]['count']}")
        
        # 检查信息源数
        sources = db.execute_query('SELECT COUNT(*) as count FROM information_sources WHERE event_id = %s', (event_id,))
        print(f"信息源数量: {sources[0]['count']}")
        
        # 判断测试结果
        if e['status'] == 'voting' and e['ai_summary'] and e['ai_rating']:
            print("\n🎉 测试成功！10人关注自动触发AI分析功能正常工作")
        else:
            print("\n❌ 测试失败！AI分析未完成或数据不完整")
    
    db.close()
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_10_users_auto_trigger()
