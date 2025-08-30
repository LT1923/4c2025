import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import execute_query

def main():
    """
    为photos表添加status字段
    0: 正常状态
    1: 回收站
    """
    print("开始迁移：为photos表添加status字段...")
    
    try:
        # 检查status字段是否已经存在
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='photos' AND column_name='status'
        """
        result = execute_query(check_query, (), fetch=True)
        
        if result and len(result) > 0:
            print("status字段已存在，跳过")
            return
        
        # 添加status字段，默认值为0（正常状态）
        add_column_query = """
        ALTER TABLE photos
        ADD COLUMN status INTEGER DEFAULT 0
        """
        execute_query(add_column_query, ())
        
        print("成功添加status字段")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        sys.exit(1)
    
    print("迁移完成！")

if __name__ == "__main__":
    main() 