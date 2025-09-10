import sys
sys.path.append('backend')
from app.services.simple_db_service import SimpleDBService

db_service = SimpleDBService()
if db_service.connect():
    event_id = 54
    
    # 模拟一些投票数据
    print("模拟投票数据...")
    
    # 添加一些支持票
    for i in range(7):  # 7票支持
        user_id = 100 + i
        db_service.execute_update(
            "INSERT IGNORE INTO votes (event_id, user_id, stance, created_at) VALUES (%s, %s, 'support', NOW())",
            (event_id, user_id)
        )
    
    # 添加一些反对票
    for i in range(3):  # 3票反对
        user_id = 200 + i
        db_service.execute_update(
            "INSERT IGNORE INTO votes (event_id, user_id, stance, created_at) VALUES (%s, %s, 'oppose', NOW())",
            (event_id, user_id)
        )
    
    # 更新事件的投票统计
    support_count = db_service.execute_query(
        "SELECT COUNT(*) as count FROM votes WHERE event_id = %s AND stance = 'support'",
        (event_id,)
    )[0]['count']
    
    oppose_count = db_service.execute_query(
        "SELECT COUNT(*) as count FROM votes WHERE event_id = %s AND stance = 'oppose'",
        (event_id,)
    )[0]['count']
    
    total_votes = support_count + oppose_count
    
    db_service.execute_update(
        "UPDATE events SET vote_count = %s, support_votes = %s, oppose_votes = %s WHERE id = %s",
        (total_votes, support_count, oppose_count, event_id)
    )
    
    print(f"投票统计更新完成:")
    print(f"总投票数: {total_votes}")
    print(f"支持票: {support_count}")
    print(f"反对票: {oppose_count}")
    print(f"支持率: {support_count/total_votes*100:.1f}%")
    
    db_service.close()
