from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.map_marker import MapMarker
from app import db
import requests
import os

map_bp = Blueprint('map', __name__)

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# OpenRouteService API配置
ORS_API_KEY = os.getenv('ORS_API_KEY', 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImM1MTJhOTEyM2Y3MTQzMzM4NGIyODAwYzUzZmJmMDRmIiwiaCI6Im11cm11cjY0In0=')  # 免费API密钥
ORS_BASE_URL = 'https://api.openrouteservice.org'

@map_bp.route('/markers', methods=['GET'])
def get_markers():
    markers = MapMarker.query.all()
    return jsonify({'markers': [marker.to_dict() for marker in markers]}), 200

@map_bp.route('/markers', methods=['POST'])
@jwt_required()
def create_marker():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if not data or not data.get('title') or not data.get('latitude') or not data.get('longitude'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    marker = MapMarker(
        title=data['title'],
        description=data.get('description', ''),
        latitude=data['latitude'],
        longitude=data['longitude'],
        user_id=user_id
    )
    
    db.session.add(marker)
    db.session.commit()
    
    return jsonify({'message': 'Marker created successfully', 'marker': marker.to_dict()}), 201

@map_bp.route('/markers/<int:marker_id>', methods=['DELETE'])
@jwt_required()
def delete_marker(marker_id):
    user_id = get_jwt_identity()
    marker = MapMarker.query.get(marker_id)
    
    if not marker:
        return jsonify({'error': 'Marker not found'}), 404
    
    if marker.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(marker)
    db.session.commit()
    
    return jsonify({'message': 'Marker deleted successfully'}), 200

@map_bp.route('/route', methods=['POST'])
def get_route():
    """获取两点之间的路径"""
    data = request.get_json()
    
    if not data or not data.get('start') or not data.get('end'):
        return jsonify({'error': 'Missing start or end coordinates'}), 400
    
    try:
        start = data['start']
        end = data['end']
        
        # 验证坐标格式
        if (not isinstance(start, list) or len(start) != 2 or
            not isinstance(end, list) or len(end) != 2):
            return jsonify({'error': 'Invalid coordinates format'}), 400
        
        # OpenRouteService API调用
        headers = {
            'Authorization': ORS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'coordinates': [[start[1], start[0]], [end[1], end[0]]],  # ORS使用[longitude, latitude]格式
            'format': 'geojson',
            'geometry': 'true',
            'instructions': 'true'
        }
        
        logging.info(f"Sending request to ORS API. URL: {ORS_BASE_URL}/v2/directions/driving-car/geojson, Payload: {payload}")

        response = requests.post(
            f'{ORS_BASE_URL}/v2/directions/driving-car/geojson',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        logging.info(f"Received response from ORS API. Status: {response.status_code}, Response: {response.text}")

        if response.status_code == 200:
            route_data = response.json()
            
            # 提取路径信息
            route_info = {
                'coordinates': route_data['features'][0]['geometry']['coordinates'],
                'distance': route_data['features'][0]['properties']['segments'][0]['distance'],
                'duration': route_data['features'][0]['properties']['segments'][0]['duration'],
                'instructions': route_data['features'][0]['properties']['segments'][0]['steps']
            }
            
            return jsonify({
                'route': route_info,
                'message': 'Route calculated successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to calculate route'}), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@map_bp.route('/route/marker-to-marker', methods=['POST'])
def get_route_between_markers():
    """获取两个标记之间的路径"""
    data = request.get_json()
    
    if not data or not data.get('start_marker_id') or not data.get('end_marker_id'):
        return jsonify({'error': 'Missing marker IDs'}), 400
    
    try:
        start_marker = MapMarker.query.get(data['start_marker_id'])
        end_marker = MapMarker.query.get(data['end_marker_id'])
        
        if not start_marker or not end_marker:
            return jsonify({'error': 'One or both markers not found'}), 404
        
        # 使用标记坐标调用路径查找
        route_data = {
            'start': [start_marker.latitude, start_marker.longitude],
            'end': [end_marker.latitude, end_marker.longitude]
        }
        
        # 调用内部路径查找函数
        from flask import current_app
        with current_app.test_request_context('/api/map/route', json=route_data, method='POST'):
            return get_route()
            
    except Exception as e:
        return jsonify({'error': 'Failed to calculate route between markers'}), 500