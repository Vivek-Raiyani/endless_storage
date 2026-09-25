import sqlite3
import uuid

def migrate_int_to_uuid():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # Mappings from old int ID to new UUID string for each table
    id_maps = {
        'users': {},
        'subscription_plans': {},
        'features': {},
    }
    
    # 1. Update primary tables (users, subscription_plans, features)
    for table in id_maps.keys():
        try:
            rows = cursor.execute(f"SELECT id FROM {table}").fetchall()
            for (old_id,) in rows:
                if isinstance(old_id, int) or (isinstance(old_id, str) and old_id.isdigit()):
                    new_id = uuid.uuid4().hex
                    id_maps[table][old_id] = new_id
                    cursor.execute(f"UPDATE {table} SET id = ? WHERE id = ?", (new_id, old_id))
        except sqlite3.OperationalError:
            pass # Table might not exist

    # 2. Update foreign keys and primary keys for dependent tables
    
    # user_subscriptions: id, user_id, plan_id
    try:
        rows = cursor.execute("SELECT id, user_id, plan_id FROM user_subscriptions").fetchall()
        for (old_id, old_user_id, old_plan_id) in rows:
            new_id = uuid.uuid4().hex if isinstance(old_id, int) or (isinstance(old_id, str) and old_id.isdigit()) else old_id
            new_user_id = id_maps['users'].get(old_user_id, old_user_id)
            new_plan_id = id_maps['subscription_plans'].get(old_plan_id, old_plan_id)
            
            cursor.execute(
                "UPDATE user_subscriptions SET id = ?, user_id = ?, plan_id = ? WHERE id = ?",
                (new_id, new_user_id, new_plan_id, old_id)
            )
    except sqlite3.OperationalError:
        pass
        
    # payment_history: id, user_id
    try:
        rows = cursor.execute("SELECT id, user_id FROM payment_history").fetchall()
        for (old_id, old_user_id) in rows:
            new_id = uuid.uuid4().hex if isinstance(old_id, int) or (isinstance(old_id, str) and old_id.isdigit()) else old_id
            new_user_id = id_maps['users'].get(old_user_id, old_user_id)
            
            cursor.execute(
                "UPDATE payment_history SET id = ?, user_id = ? WHERE id = ?",
                (new_id, new_user_id, old_id)
            )
    except sqlite3.OperationalError:
        pass

    # plan_features: id, plan_id, feature_id
    try:
        rows = cursor.execute("SELECT id, plan_id, feature_id FROM plan_features").fetchall()
        for (old_id, old_plan_id, old_feature_id) in rows:
            new_id = uuid.uuid4().hex if isinstance(old_id, int) or (isinstance(old_id, str) and old_id.isdigit()) else old_id
            new_plan_id = id_maps['subscription_plans'].get(old_plan_id, old_plan_id)
            new_feature_id = id_maps['features'].get(old_feature_id, old_feature_id)
            
            cursor.execute(
                "UPDATE plan_features SET id = ?, plan_id = ?, feature_id = ? WHERE id = ?",
                (new_id, new_plan_id, new_feature_id, old_id)
            )
    except sqlite3.OperationalError:
        pass

    # pages: id, user_id
    try:
        rows = cursor.execute("SELECT id, user_id FROM pages").fetchall()
        for (old_id, old_user_id) in rows:
            new_id = uuid.uuid4().hex if isinstance(old_id, int) or (isinstance(old_id, str) and old_id.isdigit()) else old_id
            new_user_id = id_maps['users'].get(old_user_id, old_user_id)
            
            cursor.execute(
                "UPDATE pages SET id = ?, user_id = ? WHERE id = ?",
                (new_id, new_user_id, old_id)
            )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print("Migration of int IDs to UUIDs completed successfully.")

if __name__ == '__main__':
    migrate_int_to_uuid()
