import sqlite3
import json
from datetime import datetime

# 定义数据库文件的名称
DB_NAME = "topik_evaluator.db"

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_NAME)

def init_db():
    """初始化数据库，如果表不存在则自动创建"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 创建“评估记录表”
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            topic TEXT,
            original_text TEXT,
            corrected_text TEXT,
            grammar_score INTEGER,
            content_score INTEGER,
            structure_score INTEGER,
            overall_feedback TEXT
        )
    ''')
    
    # 2. 创建“专属词汇记忆表”
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            original_word TEXT,
            advanced_word TEXT,
            reason TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def save_evaluation_data(username, topic, original, corrected, scores, feedback, vocab_list):
    """将评估结果保存到数据库中"""
    conn = get_connection()
    cursor = conn.cursor()
    # 获取当前时间
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 插入数据到 evaluations 表
    cursor.execute('''
        INSERT INTO evaluations 
        (username, timestamp, topic, original_text, corrected_text, grammar_score, content_score, structure_score, overall_feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, timestamp, topic, original, corrected, 
          scores.get('grammar', 0), scores.get('content', 0), scores.get('structure', 0), feedback))
    
    # 循环遍历 vocab_list，把每一个词汇都存入 vocabulary 表
    for vocab in vocab_list:
        cursor.execute('''
            INSERT INTO vocabulary (username, original_word, advanced_word, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, vocab.get('original', ''), vocab.get('advanced', ''), vocab.get('reason', ''), timestamp))
        
    conn.commit()
    conn.close()

def get_user_history(username):
    """根据用户名拉取历史成绩，用于画折线图"""
    conn = get_connection()
    cursor = conn.cursor()
    # 按照时间先后顺序 (ASC) 提取成绩
    cursor.execute('''
        SELECT timestamp, grammar_score, content_score, structure_score 
        FROM evaluations 
        WHERE username = ? 
        ORDER BY timestamp ASC
    ''', (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_vocabulary(username):
    """根据用户名拉取专属高级词汇库，用于展示表格"""
    conn = get_connection()
    cursor = conn.cursor()
    # 按照时间倒序 (DESC) 提取词汇，最新的排在最前面
    cursor.execute('''
        SELECT original_word, advanced_word, reason, timestamp 
        FROM vocabulary 
        WHERE username = ? 
        ORDER BY timestamp DESC
    ''', (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()