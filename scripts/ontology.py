#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ontology CLI - 知识图谱管理工具
用法：
  python3 ontology.py create --type Person --props '{"name":"Alice"}'
  python3 ontology.py query --type Task --where '{"status":"open"}'
  python3 ontology.py relate --from proj_001 --rel has_task --to task_001
  python3 ontology.py related --id proj_001 --rel has_task
  python3 ontology.py list --type Person
  python3 ontology.py validate
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
import yaml

# ==================== 配置 ====================

WORKSPACE = Path('/Users/yangbowen/.openclaw/workspace')
GRAPH_FILE = WORKSPACE / 'memory/ontology/graph.jsonl'
SCHEMA_FILE = WORKSPACE / 'memory/ontology/schema.yaml'

# ==================== 工具函数 ====================

def generate_id(type_):
    """生成实体 ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    return f"{type_.lower()}_{timestamp}"

def load_schema():
    """加载 Schema"""
    if not SCHEMA_FILE.exists():
        return None
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_entity(type_, props, schema):
    """验证实体"""
    if not schema:
        return True, "No schema"
    
    types = schema.get('types', {})
    if type_ not in types:
        return True, f"Type {type_} not in schema"
    
    type_def = types[type_]
    
    # 检查必需字段
    required = type_def.get('required', [])
    for field in required:
        if field not in props:
            return False, f"Missing required field: {field}"
    
    # 检查枚举值
    for field, value in props.items():
        enum_key = f"{field}_enum"
        if enum_key in type_def:
            if value not in type_def[enum_key]:
                return False, f"Invalid enum value for {field}: {value}"
    
    return True, "Valid"

def validate_relation(from_id, rel_type, to_id, schema):
    """验证关系"""
    if not schema:
        return True, "No schema"
    
    relations = schema.get('relations', {})
    if rel_type not in relations:
        return True, f"Relation {rel_type} not in schema"
    
    rel_def = relations[rel_type]
    
    # 获取实体类型（简化：从 ID 推断）
    from_type = from_id.split('_')[0].capitalize()
    to_type = to_id.split('_')[0].capitalize()
    
    # 检查类型约束
    from_types = rel_def.get('from_types', [])
    to_types = rel_def.get('to_types', [])
    
    if from_types and from_type not in from_types:
        return False, f"Invalid from_type: {from_type}"
    
    if to_types and to_type not in to_types:
        return False, f"Invalid to_type: {to_type}"
    
    return True, "Valid"

# ==================== 核心操作 ====================

def create_entity(type_, props):
    """创建实体"""
    schema = load_schema()
    
    # 验证
    valid, msg = validate_entity(type_, props, schema)
    if not valid:
        print(f"❌ Validation failed: {msg}")
        return None
    
    entity_id = generate_id(type_)
    entity = {
        'id': entity_id,
        'type': type_,
        'properties': props,
        'relations': [],
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat()
    }
    
    # 写入 graph.jsonl
    with open(GRAPH_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'op': 'create', 'entity': entity}, ensure_ascii=False) + '\n')
    
    print(f"✅ Created {type_}: {entity_id}")
    print(f"   Properties: {json.dumps(props, ensure_ascii=False)}")
    return entity_id

def query_entities(type_, where=None):
    """查询实体"""
    entities = []
    
    if not GRAPH_FILE.exists():
        print("⚠️  Graph file not found")
        return entities
    
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            op = json.loads(line)
            if op['op'] == 'create' and op['entity']['type'] == type_:
                entity = op['entity']
                # 过滤条件
                if where is None:
                    entities.append(entity)
                else:
                    match = True
                    for k, v in where.items():
                        if entity['properties'].get(k) != v:
                            match = False
                            break
                    if match:
                        entities.append(entity)
    
    return entities

def list_entities(type_):
    """列出实体（简化版）"""
    entities = query_entities(type_)
    
    if not entities:
        print(f"ℹ️  No {type_} entities found")
        return
    
    print(f"\n📋 {type_} Entities ({len(entities)} total):\n")
    print(f"{'ID':<40} {'Properties':<60}")
    print("-" * 100)
    
    for e in entities:
        props_str = ', '.join([f"{k}={v}" for k, v in e['properties'].items()])
        print(f"{e['id']:<40} {props_str:<60}")
    
    print()

def relate(from_id, rel_type, to_id):
    """建立关系"""
    schema = load_schema()
    
    # 验证
    valid, msg = validate_relation(from_id, rel_type, to_id, schema)
    if not valid:
        print(f"❌ Validation failed: {msg}")
        return False
    
    relation = {
        'from_id': from_id,
        'relation_type': rel_type,
        'to_id': to_id,
        'created': datetime.now().isoformat()
    }
    
    with open(GRAPH_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'op': 'relate', 'relation': relation}, ensure_ascii=False) + '\n')
    
    print(f"✅ Related: {from_id} --[{rel_type}]--> {to_id}")
    return True

def get_related(id_, rel_type=None):
    """查询关联实体"""
    related = []
    
    if not GRAPH_FILE.exists():
        print("⚠️  Graph file not found")
        return related
    
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            op = json.loads(line)
            if op['op'] == 'relate':
                rel = op['relation']
                # 匹配关系
                if rel['from_id'] == id_:
                    if rel_type is None or rel['relation_type'] == rel_type:
                        related.append({
                            'relation': rel['relation_type'],
                            'target_id': rel['to_id']
                        })
                elif rel['to_id'] == id_:
                    if rel_type is None or rel['relation_type'] == rel_type:
                        related.append({
                            'relation': rel['relation_type'],
                            'target_id': rel['from_id']
                        })
    
    return related

def get_entity(id_):
    """获取单个实体"""
    if not GRAPH_FILE.exists():
        return None
    
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            op = json.loads(line)
            if op['op'] == 'create' and op['entity']['id'] == id_:
                return op['entity']
    
    return None

def show_related(id_, rel_type=None):
    """显示关联实体"""
    related = get_related(id_, rel_type)
    entity = get_entity(id_)
    
    if not entity:
        print(f"⚠️  Entity not found: {id_}")
        return
    
    print(f"\n🔗 Related to {id_} ({entity['type']}):\n")
    
    if not related:
        print("  (No relations found)")
        return
    
    for rel in related:
        target = get_entity(rel['target_id'])
        if target:
            props_str = ', '.join([f"{k}={v}" for k, v in target['properties'].items()])
            print(f"  {rel['relation']:<20} → {rel['target_id']:<30} ({props_str})")
    
    print()

def validate_graph():
    """验证图谱"""
    schema = load_schema()
    errors = []
    entities = {}
    relations = []
    
    if not GRAPH_FILE.exists():
        print("⚠️  Graph file not found")
        return
    
    # 读取所有实体和关系
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            op = json.loads(line)
            if op['op'] == 'create':
                entities[op['entity']['id']] = op['entity']
            elif op['op'] == 'relate':
                relations.append(op['relation'])
    
    # 验证关系
    for rel in relations:
        # 检查实体是否存在
        if rel['from_id'] not in entities:
            errors.append(f"Relation references non-existent entity: {rel['from_id']}")
        if rel['to_id'] not in entities:
            errors.append(f"Relation references non-existent entity: {rel['to_id']}")
        
        # Schema 验证
        if schema:
            valid, msg = validate_relation(rel['from_id'], rel['relation_type'], rel['to_id'], schema)
            if not valid:
                errors.append(f"Invalid relation {rel['from_id']}--[{rel['relation_type']}]-->{rel['to_id']}: {msg}")
    
    # 输出结果
    print("\n🔍 Ontology Validation Report\n")
    print(f"Entities: {len(entities)}")
    print(f"Relations: {len(relations)}")
    print()
    
    if errors:
        print(f"❌ Found {len(errors)} error(s):\n")
        for err in errors:
            print(f"  • {err}")
    else:
        print("✅ All validations passed!")
    
    print()

def init_schema():
    """初始化 Schema"""
    schema = {
        'types': {
            'Person': {
                'required': ['name'],
                'properties': {
                    'name': 'string',
                    'email': 'string',
                    'role': 'string'
                }
            },
            'Project': {
                'required': ['name', 'status'],
                'status_enum': ['planning', 'active', 'on_hold', 'completed', 'archived'],
                'properties': {
                    'name': 'string',
                    'status': 'string',
                    'start_date': 'date',
                    'end_date': 'date'
                }
            },
            'Task': {
                'required': ['title', 'status'],
                'status_enum': ['open', 'in_progress', 'blocked', 'done', 'cancelled'],
                'properties': {
                    'title': 'string',
                    'status': 'string',
                    'priority': 'enum[low, medium, high, urgent]',
                    'due_date': 'date',
                    'assignee': 'string'
                }
            },
            'Stock': {
                'required': ['name', 'code'],
                'properties': {
                    'name': 'string',
                    'code': 'string',
                    'industry': 'string'
                }
            },
            'Account': {
                'required': ['service'],
                'properties': {
                    'service': 'string',
                    'username': 'string',
                    'configured': 'boolean'
                }
            },
            'ScheduledTask': {
                'required': ['name', 'schedule'],
                'properties': {
                    'name': 'string',
                    'schedule': 'string',
                    'script': 'string',
                    'enabled': 'boolean'
                }
            },
            'Skill': {
                'required': ['name'],
                'properties': {
                    'name': 'string',
                    'status': 'enum[installed, active, inactive]',
                    'configured': 'boolean',
                    'purpose': 'string'
                }
            }
        },
        'relations': {
            'has_owner': {
                'from_types': ['Project', 'Task'],
                'to_types': ['Person'],
                'cardinality': 'many_to_one'
            },
            'has_task': {
                'from_types': ['Project'],
                'to_types': ['Task'],
                'cardinality': 'one_to_many'
            },
            'holds_stock': {
                'from_types': ['Person'],
                'to_types': ['Stock'],
                'cardinality': 'one_to_many'
            },
            'uses_account': {
                'from_types': ['Task', 'ScheduledTask'],
                'to_types': ['Account'],
                'cardinality': 'many_to_one'
            },
            'depends_on': {
                'from_types': ['Task'],
                'to_types': ['Task'],
                'cardinality': 'many_to_many',
                'acyclic': True
            }
        }
    }
    
    with open(SCHEMA_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(schema, f, allow_unicode=True, default_flow_style=False)
    
    print("✅ Schema initialized!")
    print(f"   File: {SCHEMA_FILE}")
    print(f"   Types: {len(schema['types'])}")
    print(f"   Relations: {len(schema['relations'])}")
    print()

# ==================== 主函数 ====================

def main():
    parser = argparse.ArgumentParser(description='Ontology CLI - 知识图谱管理工具')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # create
    create_parser = subparsers.add_parser('create', help='Create entity')
    create_parser.add_argument('--type', required=True, help='Entity type')
    create_parser.add_argument('--props', required=True, help='Properties (JSON)')
    
    # query
    query_parser = subparsers.add_parser('query', help='Query entities')
    query_parser.add_argument('--type', required=True, help='Entity type')
    query_parser.add_argument('--where', help='Filter (JSON)')
    
    # list
    list_parser = subparsers.add_parser('list', help='List entities')
    list_parser.add_argument('--type', required=True, help='Entity type')
    
    # relate
    relate_parser = subparsers.add_parser('relate', help='Create relation')
    relate_parser.add_argument('--from', dest='from_id', required=True, help='From entity ID')
    relate_parser.add_argument('--rel', required=True, help='Relation type')
    relate_parser.add_argument('--to', dest='to_id', required=True, help='To entity ID')
    
    # related
    related_parser = subparsers.add_parser('related', help='Show related entities')
    related_parser.add_argument('--id', required=True, help='Entity ID')
    related_parser.add_argument('--rel', help='Relation type (optional)')
    
    # get
    get_parser = subparsers.add_parser('get', help='Get entity by ID')
    get_parser.add_argument('--id', required=True, help='Entity ID')
    
    # validate
    subparsers.add_parser('validate', help='Validate graph')
    
    # init-schema
    subparsers.add_parser('init-schema', help='Initialize schema')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        props = json.loads(args.props)
        create_entity(args.type, props)
    
    elif args.command == 'query':
        where = json.loads(args.where) if args.where else None
        entities = query_entities(args.type, where)
        print(f"\n📊 Found {len(entities)} {args.type}(s):\n")
        for e in entities:
            print(f"  {e['id']}: {json.dumps(e['properties'], ensure_ascii=False)}")
        print()
    
    elif args.command == 'list':
        list_entities(args.type)
    
    elif args.command == 'relate':
        relate(args.from_id, args.rel, args.to_id)
    
    elif args.command == 'related':
        show_related(args.id, args.rel)
    
    elif args.command == 'get':
        entity = get_entity(args.id)
        if entity:
            print(f"\n📄 Entity: {entity['id']}\n")
            print(f"  Type: {entity['type']}")
            print(f"  Properties: {json.dumps(entity['properties'], ensure_ascii=False, indent=2)}")
            print(f"  Created: {entity['created']}")
            print(f"  Updated: {entity['updated']}")
            print()
        else:
            print(f"⚠️  Entity not found: {args.id}")
    
    elif args.command == 'validate':
        validate_graph()
    
    elif args.command == 'init-schema':
        init_schema()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
