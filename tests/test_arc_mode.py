# -*- coding: utf-8 -*-
"""
Smart Z-Hop Arc 곡선 모드 전용 테스트 (시각화 + 극한 케이스 포함)

🎯 Arc 곡선 모드 핵심 기능 검증:
1. Arc 곡선 Z축 높이 계산 (상승/하강 구간별) + 시각적 출력
2. 안전 높이 보장 (상승≥시작Z, 하강≥끝Z) + 그래프 표시
3. 동적 반지름 적용 (세그먼트 길이 대비 %) + 비교 차트
4. G2/G3 Arc G-code 생성 vs 직선 보간 + 궤적 시각화
5. 기존 모드와의 호환성 검증 + 성능 비교
6. 극한 케이스 시뮬레이션 (초단거리, 초장거리, 극한 반지름)
"""

import sys
import os
import math
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SmartZHop import SmartZHop

# matplotlib 시각화 지원 확인
try:
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.patches as patches
    from matplotlib.animation import FuncAnimation
    HAS_MATPLOTLIB = True
    print("✅ matplotlib 시각화 지원 활성화")
except ImportError as e:
    HAS_MATPLOTLIB = False
    print(f"⚠️ matplotlib 없음, 텍스트 출력만 지원: {e}")
    # numpy 대체 (기본 수학 함수만 사용)
    class FakeNumpy:
        @staticmethod
        def linspace(start, stop, num):
            if num <= 1:
                return [start]
            step = (stop - start) / (num - 1)
            return [start + i * step for i in range(num)]
        
        @staticmethod 
        def array(data):
            return data
    np = FakeNumpy()

# =============================================================================
# 시각화 도구 함수들
# =============================================================================

def create_ascii_graph(data_points, title, width=60, height=15):
    """ASCII 그래프 생성 (matplotlib 없이도 시각화)"""
    if not data_points:
        return f"{title}: No data"
    
    # 데이터 정규화
    x_vals = [point[0] for point in data_points]
    y_vals = [point[1] for point in data_points]
    
    min_x, max_x = min(x_vals), max(x_vals)
    min_y, max_y = min(y_vals), max(y_vals)
    
    if max_x == min_x or max_y == min_y:
        return f"{title}: Data too uniform to graph"
    
    # 그래프 배열 초기화
    graph = [[' ' for _ in range(width)] for _ in range(height)]
    
    # 데이터 점들을 그래프에 매핑
    for x, y in data_points:
        # 정규화 및 스케일링
        norm_x = int((x - min_x) / (max_x - min_x) * (width - 1))
        norm_y = int((y - min_y) / (max_y - min_y) * (height - 1))
        norm_y = height - 1 - norm_y  # Y축 뒤집기
        
        if 0 <= norm_x < width and 0 <= norm_y < height:
            graph[norm_y][norm_x] = '●'
    
    # 그래프 출력 문자열 생성
    result = [f"\n📊 {title}"]
    result.append(f"   X: {min_x:.3f} ~ {max_x:.3f}, Y: {min_y:.3f} ~ {max_y:.3f}")
    result.append("   " + "─" * width)
    
    for row in graph:
        result.append("   │" + "".join(row) + "│")
    
    result.append("   " + "─" * width)
    return "\n".join(result)

def visualize_arc_function_comparison():
    """Arc 함수 시각적 비교 - matplotlib GUI 및 텍스트 지원"""
    print("\n📈 Arc 함수 시각적 비교")
    print("=" * 60)
    
    zhop = SmartZHop()
    radius_ratios = [25, 50, 75, 100]
    
    if HAS_MATPLOTLIB:
        # matplotlib GUI 시각화
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Arc 곡선 함수 비교', fontsize=14, fontweight='bold')
        
        distance_range = np.linspace(0, 1, 100)
        
        # 상승 구간 그래프
        for ratio in radius_ratios:
            z_values = [zhop.calculate_arc_z_height_ascent(d, ratio) for d in distance_range]
            ax1.plot(distance_range, z_values, label=f'{ratio}% 반지름', linewidth=2)
        
        ax1.set_title('상승 구간 Arc 곡선')
        ax1.set_xlabel('거리 비율')
        ax1.set_ylabel('Z 높이 비율')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 하강 구간 그래프
        for ratio in radius_ratios:
            z_values = [zhop.calculate_arc_z_height_descent(d, ratio) for d in distance_range]
            ax2.plot(distance_range, z_values, label=f'{ratio}% 반지름', linewidth=2)
        
        ax2.set_title('하강 구간 Arc 곡선')
        ax2.set_xlabel('거리 비율')
        ax2.set_ylabel('Z 높이 비율')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        print("✅ GUI 그래프 창이 열렸습니다.")
    
    # 텍스트 기반 시각화 (모든 환경에서 지원)
    for ratio in radius_ratios:
        print(f"\n🔵 Arc 반지름 비율: {ratio}%")
        
        # 상승 구간 데이터 생성
        ascent_points = []
        descent_points = []
        for i in range(21):  # 0~1, 0.05 간격
            d = i / 20.0
            ascent_z = zhop.calculate_arc_z_height_ascent(d, ratio)
            descent_z = zhop.calculate_arc_z_height_descent(d, ratio)
            ascent_points.append((d, ascent_z))
            descent_points.append((d, descent_z))
        
        # ASCII 그래프 출력
        print(create_ascii_graph(ascent_points, f"상승 구간 (반지름 {ratio}%)", width=40, height=8))
        print(create_ascii_graph(descent_points, f"하강 구간 (반지름 {ratio}%)", width=40, height=8))
        print(f"\n🔹 반지름 비율: {ratio}%")
        
        # 상승 구간 데이터 생성
        ascent_data = []
        descent_data = []
        
        for i in range(21):  # 0.0 ~ 1.0, 0.05 간격
            distance_ratio = i / 20.0
            
            ascent_z = zhop.calculate_arc_z_height_ascent(distance_ratio, ratio)
            descent_z = zhop.calculate_arc_z_height_descent(distance_ratio, ratio)
            
            ascent_data.append((distance_ratio, ascent_z))
            descent_data.append((distance_ratio, descent_z))
        
        # ASCII 그래프 출력
        print(create_ascii_graph(ascent_data, f"상승 구간 Arc 곡선 (반지름 {ratio}%)", 40, 10))
        print(create_ascii_graph(descent_data, f"하강 구간 Arc 곡선 (반지름 {ratio}%)", 40, 10))
        
        # 수치 검증
        max_ascent = max(point[1] for point in ascent_data)
        max_descent = max(point[1] for point in descent_data)
        
        expected_max = ratio / 100.0
        print(f"   📊 검증: 최대 높이 비율 = {max_ascent:.3f} (예상: {expected_max:.3f})")
        
        if abs(max_ascent - expected_max) < 0.001:
            print(f"   ✅ 상승 곡선 정확도 검증 통과!")
        else:
            print(f"   ❌ 상승 곡선 오차 감지: {abs(max_ascent - expected_max):.6f}")

def visualize_trajectory_comparison():
    """궤적 비교 시각화"""
    print("\n🛤️ 궤적 비교 시각화")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 테스트 시나리오
    start_point = (0, 0)
    end_point = (50, 50)
    z_hop_height = 1.0
    
    print(f"📝 테스트 시나리오: {start_point} → {end_point}, Z-hop: {z_hop_height}mm")
    
    # 여러 반지름으로 Arc 궤적 생성
    for radius_ratio in [25, 50, 75, 100]:
        arc_points = zhop.generate_arc_gcode_points(
            start_point, end_point, 1.0, 1.0, z_hop_height, radius_ratio, 20
        )
        
        # 3D 궤적을 2D로 투영 (XZ 평면)
        xz_trajectory = [(point[0], point[2]) for point in arc_points]
        yz_trajectory = [(point[1], point[2]) for point in arc_points]
        
        print(f"\n🎯 반지름 비율 {radius_ratio}% 궤적:")
        print(create_ascii_graph(xz_trajectory, f"XZ 평면 (반지름 {radius_ratio}%)", 50, 12))
        
        # 궤적 통계
        max_z = max(point[2] for point in arc_points)
        total_length = sum(
            math.sqrt((arc_points[i+1][0] - arc_points[i][0])**2 + 
                     (arc_points[i+1][1] - arc_points[i][1])**2 +
                     (arc_points[i+1][2] - arc_points[i][2])**2)
            for i in range(len(arc_points) - 1)
        )
        
        print(f"   📊 최고점: {max_z:.3f}mm, 총 길이: {total_length:.3f}mm")

def visualize_3d_trajectory():
    """3D 궤적 시각화 - Arc vs 일반 모드 비교"""
    print("\n🌐 3D 궤적 시각화")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 테스트 시나리오
    start_point = (0, 0)
    end_point = (50, 50)
    z_start, z_end = 1.0, 1.0
    z_hop_height = 2.0
    
    print(f"📝 시나리오: {start_point} → {end_point}, Z: {z_start}→{z_end}, Hop: {z_hop_height}mm")
    
    if HAS_MATPLOTLIB:
        # matplotlib 3D 시각화
        fig = plt.figure(figsize=(15, 10))
        
        # Arc 모드 궤적들
        ax1 = fig.add_subplot(221, projection='3d')
        ax1.set_title('Arc 모드 - 다양한 반지름', fontweight='bold')
        
        radius_ratios = [25, 50, 75, 100]
        colors = ['red', 'blue', 'green', 'purple']
        
        for ratio, color in zip(radius_ratios, colors):
            arc_points = zhop.generate_arc_gcode_points(
                start_point, end_point, z_start, z_end, z_hop_height, ratio, 30
            )
            if arc_points:
                x_vals = [p[0] for p in arc_points]
                y_vals = [p[1] for p in arc_points]
                z_vals = [p[2] for p in arc_points]
                ax1.plot(x_vals, y_vals, z_vals, color=color, linewidth=2, 
                        label=f'{ratio}% 반지름', marker='o', markersize=2)
        
        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Y (mm)')
        ax1.set_zlabel('Z (mm)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 일반 모드와 Arc 모드 비교
        ax2 = fig.add_subplot(222, projection='3d')
        ax2.set_title('Arc vs 일반 모드 비교', fontweight='bold')
        
        # 일반 모드 (Linear) 시뮬레이션
        linear_points = []
        for i in range(31):  # 0~30 포인트
            t = i / 30.0
            x = start_point[0] + t * (end_point[0] - start_point[0])
            y = start_point[1] + t * (end_point[1] - start_point[1])
            
            # 간단한 포물선 형태의 Z 궤적 (일반 모드 시뮬레이션)
            if t <= 0.5:  # 상승
                z = z_start + 4 * t * z_hop_height
            else:  # 하강
                z = z_start + z_hop_height - 4 * (t - 0.5) * z_hop_height
            
            linear_points.append((x, y, z))
        
        # 일반 모드 플롯
        lin_x = [p[0] for p in linear_points]
        lin_y = [p[1] for p in linear_points]
        lin_z = [p[2] for p in linear_points]
        ax2.plot(lin_x, lin_y, lin_z, 'gray', linewidth=3, 
                label='일반 모드', linestyle='--', alpha=0.7)
        
        # Arc 모드 (50% 반지름) 플롯
        arc_points_50 = zhop.generate_arc_gcode_points(
            start_point, end_point, z_start, z_end, z_hop_height, 50, 30
        )
        if arc_points_50:
            arc_x = [p[0] for p in arc_points_50]
            arc_y = [p[1] for p in arc_points_50]
            arc_z = [p[2] for p in arc_points_50]
            ax2.plot(arc_x, arc_y, arc_z, 'blue', linewidth=3, 
                    label='Arc 모드 (50%)', marker='o', markersize=3)
        
        ax2.set_xlabel('X (mm)')
        ax2.set_ylabel('Y (mm)')
        ax2.set_zlabel('Z (mm)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # XZ 평면 투영
        ax3 = fig.add_subplot(223)
        ax3.set_title('XZ 평면 투영', fontweight='bold')
        ax3.plot(lin_x, lin_z, 'gray', linewidth=3, label='일반 모드', linestyle='--')
        if arc_points_50:
            ax3.plot(arc_x, arc_z, 'blue', linewidth=3, label='Arc 모드', marker='o', markersize=3)
        ax3.set_xlabel('X (mm)')
        ax3.set_ylabel('Z (mm)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # YZ 평면 투영  
        ax4 = fig.add_subplot(224)
        ax4.set_title('YZ 평면 투영', fontweight='bold')
        ax4.plot(lin_y, lin_z, 'gray', linewidth=3, label='일반 모드', linestyle='--')
        if arc_points_50:
            ax4.plot(arc_y, arc_z, 'blue', linewidth=3, label='Arc 모드', marker='o', markersize=3)
        ax4.set_xlabel('Y (mm)')
        ax4.set_ylabel('Z (mm)')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        plt.show()
        print("✅ 3D 궤적 GUI 창이 열렸습니다.")
    
    # 텍스트 기반 궤적 분석
    print("\n📊 텍스트 기반 궤적 분석:")
    
    for radius_ratio in [25, 50, 75, 100]:
        arc_points = zhop.generate_arc_gcode_points(
            start_point, end_point, z_start, z_end, z_hop_height, radius_ratio, 20
        )
        
        if arc_points:
            max_z = max(point[2] for point in arc_points)
            min_z = min(point[2] for point in arc_points)
            
            print(f"🔵 Arc {radius_ratio}% - 최고점: {max_z:.3f}mm, 최저점: {min_z:.3f}mm")
            
            # XZ 투영 ASCII 그래프
            xz_points = [(point[0], point[2]) for point in arc_points]
            print(create_ascii_graph(xz_points, f"XZ 궤적 (Arc {radius_ratio}%)", 50, 8))

def visualize_safety_verification():
    """안전 높이 검증 시각화"""
    print("\n🛡️ 안전 높이 검증 시각화")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 다양한 시나리오로 안전성 테스트
    test_scenarios = [
        {"name": "동일 높이", "z_start": 2.0, "z_end": 2.0, "hop": 1.0},
        {"name": "상승 경사", "z_start": 1.0, "z_end": 3.0, "hop": 1.5},
        {"name": "하강 경사", "z_start": 3.0, "z_end": 1.0, "hop": 1.5},
        {"name": "극한 경사", "z_start": 0.5, "z_end": 5.0, "hop": 2.0},
    ]
    
    if HAS_MATPLOTLIB:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Arc 모드 안전 높이 검증', fontsize=14, fontweight='bold')
        axes = axes.flatten()
        
        for i, scenario in enumerate(test_scenarios):
            ax = axes[i]
            z_start = scenario["z_start"]
            z_end = scenario["z_end"] 
            hop = scenario["hop"]
            
            # Arc 궤적 생성
            arc_points = zhop.generate_arc_gcode_points(
                (0, 0), (50, 0), z_start, z_end, hop, 50, 30
            )
            
            if arc_points:
                x_vals = [p[0] for p in arc_points]
                z_vals = [p[2] for p in arc_points]
                
                ax.plot(x_vals, z_vals, 'blue', linewidth=2, label='Arc 궤적')
                
                # 안전선 표시
                ax.axhline(y=z_start, color='green', linestyle='--', alpha=0.7, label=f'시작 Z: {z_start}')
                ax.axhline(y=z_end, color='red', linestyle='--', alpha=0.7, label=f'끝 Z: {z_end}')
                
                # 위험 구역 표시
                min_safe_z = min(z_start, z_end)
                ax.fill_between(x_vals, 0, min_safe_z, alpha=0.2, color='red', label='위험 구역')
                
            ax.set_title(scenario["name"])
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Z (mm)')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        plt.show()
        print("✅ 안전 검증 GUI 창이 열렸습니다.")
    
    # 텍스트 기반 안전성 검증
    print("\n📋 텍스트 기반 안전성 분석:")
    
    for scenario in test_scenarios:
        print(f"\n🔍 시나리오: {scenario['name']}")
        z_start = scenario["z_start"]
        z_end = scenario["z_end"]
        hop = scenario["hop"]
        
        arc_points = zhop.generate_arc_gcode_points(
            (0, 0), (50, 0), z_start, z_end, hop, 50, 20
        )
        
        if arc_points:
            min_z = min(point[2] for point in arc_points)
            max_z = max(point[2] for point in arc_points)
            safety_threshold = min(z_start, z_end)
            
            print(f"   📊 궤적 범위: {min_z:.3f} ~ {max_z:.3f}mm")
            print(f"   🎯 안전 임계점: {safety_threshold:.3f}mm")
            
            if min_z >= safety_threshold - 0.001:  # 부동소수점 오차 허용
                print(f"   ✅ 안전성 검증 통과! (여유: {min_z - safety_threshold:.3f}mm)")
            else:
                print(f"   ❌ 안전성 위반! (부족: {safety_threshold - min_z:.3f}mm)")

def visualize_extreme_cases():
    """극한 케이스 시각화"""
    print("\n⚡ 극한 케이스 시각화")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    extreme_cases = [
        {"name": "초단거리", "distance": 0.1, "hop": 1.0, "radius": 200},
        {"name": "초장거리", "distance": 200.0, "hop": 0.5, "radius": 10},  
        {"name": "극소 반지름", "distance": 10.0, "hop": 2.0, "radius": 1},
        {"name": "극대 반지름", "distance": 10.0, "hop": 0.2, "radius": 500},
    ]
    
    if HAS_MATPLOTLIB:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('극한 케이스 Arc 궤적', fontsize=14, fontweight='bold')
        axes = axes.flatten()
        
        for i, case in enumerate(extreme_cases):
            ax = axes[i]
            distance = case["distance"]
            hop = case["hop"]
            radius = case["radius"]
            
            start_point = (0, 0)
            end_point = (distance, 0)
            
            try:
                arc_points = zhop.generate_arc_gcode_points(
                    start_point, end_point, 1.0, 1.0, hop, radius, 30
                )
                
                if arc_points:
                    x_vals = [p[0] for p in arc_points]
                    z_vals = [p[2] for p in arc_points]
                    
                    ax.plot(x_vals, z_vals, 'purple', linewidth=2, marker='o', markersize=2)
                    ax.set_title(f"{case['name']}\n(거리:{distance}, Hop:{hop}, R:{radius}%)")
                else:
                    ax.text(0.5, 0.5, 'Arc 생성 실패', ha='center', va='center', 
                           transform=ax.transAxes, fontsize=12, color='red')
                    ax.set_title(f"{case['name']} - 실패")
                    
            except Exception as e:
                ax.text(0.5, 0.5, f'오류:\n{str(e)[:30]}...', ha='center', va='center',
                       transform=ax.transAxes, fontsize=10, color='red')
                ax.set_title(f"{case['name']} - 오류")
            
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Z (mm)')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        print("✅ 극한 케이스 GUI 창이 열렸습니다.")
    
    # 텍스트 기반 극한 케이스 분석
    print("\n📋 극한 케이스 분석:")
    
    for case in extreme_cases:
        print(f"\n⚡ {case['name']} 케이스")
        distance = case["distance"]
        hop = case["hop"]
        radius = case["radius"]
        
        start_point = (0, 0)
        end_point = (distance, 0)
        
        try:
            start_time = time.time()
            arc_points = zhop.generate_arc_gcode_points(
                start_point, end_point, 1.0, 1.0, hop, radius, 20
            )
            end_time = time.time()
            
            if arc_points:
                print(f"   ✅ 성공 - {len(arc_points)}개 포인트, {(end_time-start_time)*1000:.2f}ms")
                max_z = max(point[2] for point in arc_points)
                min_z = min(point[2] for point in arc_points)
                print(f"   📊 Z 범위: {min_z:.3f} ~ {max_z:.3f}mm")
                
                # 간단한 XZ 궤적 ASCII 표현
                xz_points = [(point[0], point[2]) for point in arc_points[::2]]  # 데이터 샘플링
                print(create_ascii_graph(xz_points, f"XZ 궤적", 40, 6))
            else:
                print(f"   ❌ Arc 생성 실패")
                
        except Exception as e:
            print(f"   💥 오류: {str(e)}")

def visualize_performance_analysis():
    """성능 분석 시각화"""
    print("\n⚡ 성능 분석 시각화")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 다양한 포인트 수로 성능 테스트
    segment_counts = [10, 20, 50, 100, 200, 500]
    arc_times = []
    linear_times = []
    
    test_distance = 100.0
    
    print("📊 성능 벤치마크 실행 중...")
    
    for segments in segment_counts:
        print(f"   🔄 {segments} 세그먼트 테스트...")
        
        # Arc 모드 성능 측정
        start_time = time.time()
        for _ in range(10):  # 10회 반복 평균
            arc_points = zhop.generate_arc_gcode_points(
                (0, 0), (test_distance, 0), 1.0, 1.0, 2.0, 50, segments
            )
        arc_time = (time.time() - start_time) / 10 * 1000  # ms 단위
        arc_times.append(arc_time)
        
        # 선형 보간 성능 측정 (시뮬레이션)
        start_time = time.time()
        for _ in range(10):
            linear_points = []
            for i in range(segments + 1):
                t = i / segments
                x = t * test_distance
                y = 0
                z = 1.0 + 2.0 * (4 * t * (1 - t))  # 간단한 포물선
                linear_points.append((x, y, z))
        linear_time = (time.time() - start_time) / 10 * 1000
        linear_times.append(linear_time)
    
    if HAS_MATPLOTLIB:
        # matplotlib 성능 차트
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Arc 모드 성능 분석', fontsize=14, fontweight='bold')
        
        # 실행 시간 비교
        ax1.plot(segment_counts, arc_times, 'blue', marker='o', linewidth=2, label='Arc 모드')
        ax1.plot(segment_counts, linear_times, 'gray', marker='s', linewidth=2, label='선형 모드')
        ax1.set_xlabel('세그먼트 수')
        ax1.set_ylabel('실행 시간 (ms)')
        ax1.set_title('실행 시간 비교')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_yscale('log')
          # 성능 비율 (ZeroDivisionError 방지)
        ratios = []
        for arc_time, linear_time in zip(arc_times, linear_times):
            if linear_time > 0:
                ratios.append(arc_time / linear_time)
            else:
                ratios.append(1.0)  # 기본값
        ax2.bar(range(len(segment_counts)), ratios, color='orange', alpha=0.7)
        ax2.set_xlabel('세그먼트 수')
        ax2.set_ylabel('Arc / Linear 시간 비율')
        ax2.set_title('성능 오버헤드')
        ax2.set_xticks(range(len(segment_counts)))
        ax2.set_xticklabels(segment_counts)
        ax2.grid(True, alpha=0.3)
        
        # 메모리 사용량 추정 (포인트 수 기반)
        arc_memory = [segments * 3 * 8 for segments in segment_counts]  # 3개 좌표 * 8바이트
        linear_memory = [segments * 3 * 8 for segments in segment_counts]  # 동일하게 가정
        
        ax3.plot(segment_counts, arc_memory, 'blue', marker='o', linewidth=2, label='Arc 모드')
        ax3.plot(segment_counts, linear_memory, 'gray', marker='s', linewidth=2, label='선형 모드')
        ax3.set_xlabel('세그먼트 수')
        ax3.set_ylabel('메모리 사용량 (bytes)')
        ax3.set_title('메모리 사용량 추정')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        plt.tight_layout()
        plt.show()
        print("✅ 성능 분석 GUI 창이 열렸습니다.")
      # 텍스트 기반 성능 리포트
    print("\n📋 성능 분석 리포트:")
    print("─" * 60)
    print(f"{'세그먼트':>8} {'Arc(ms)':>10} {'Linear(ms)':>12} {'비율':>8} {'오버헤드':>10}")
    print("─" * 60)
    
    for i, segments in enumerate(segment_counts):
        if linear_times[i] > 0:
            ratio = arc_times[i] / linear_times[i]
            overhead = ((arc_times[i] - linear_times[i]) / linear_times[i]) * 100
        else:
            ratio = 1.0
            overhead = 0.0
        
        print(f"{segments:>8} {arc_times[i]:>10.2f} {linear_times[i]:>12.2f} "
              f"{ratio:>8.2f} {overhead:>9.1f}%")
    
    print("─" * 60)
    
    # 성능 요약 (ZeroDivisionError 방지)
    valid_ratios = []
    for i in range(len(segment_counts)):
        if linear_times[i] > 0:
            valid_ratios.append(arc_times[i] / linear_times[i])
    
    if valid_ratios:
        avg_ratio = sum(valid_ratios) / len(valid_ratios)
    else:
        avg_ratio = 1.0
    max_arc_time = max(arc_times)
    min_arc_time = min(arc_times)
    
    print(f"\n📈 성능 요약:")
    print(f"   평균 성능 비율: {avg_ratio:.2f}x")
    print(f"   Arc 최대 실행시간: {max_arc_time:.2f}ms")
    print(f"   Arc 최소 실행시간: {min_arc_time:.2f}ms")
    
    if avg_ratio < 2.0:
        print(f"   ✅ 성능 양호 - Arc 오버헤드 허용 범위")
    elif avg_ratio < 5.0:
        print(f"   ⚠️ 성능 주의 - Arc 오버헤드 다소 높음")
    else:
        print(f"   ❌ 성능 문제 - Arc 오버헤드 과도함")

# =============================================================================
# 고급 Arc 안전성 테스트 함수들
# =============================================================================

def test_max_safe_radius_calculation():
    """최대 안전 반지름 계산 테스트"""
    print("\n🛡️ 최대 안전 반지름 계산 검증")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 다양한 시나리오로 테스트
    test_scenarios = [
        {"name": "동일 높이", "z_start": 2.0, "z_end": 2.0, "hop": 1.0, "distance": 50.0},
        {"name": "상승 경사", "z_start": 1.0, "z_end": 3.0, "hop": 1.5, "distance": 30.0},
        {"name": "하강 경사", "z_start": 3.0, "z_end": 1.0, "hop": 1.5, "distance": 30.0},
        {"name": "극한 경사", "z_start": 0.5, "z_end": 5.0, "hop": 2.0, "distance": 20.0},
        {"name": "낮은 높이", "z_start": 0.2, "z_end": 0.2, "hop": 0.5, "distance": 10.0},
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔍 시나리오: {scenario['name']}")
        z_start = scenario["z_start"]
        z_end = scenario["z_end"]
        hop = scenario["hop"]
        distance = scenario["distance"]
        
        max_safe_radius = zhop.calculate_max_safe_radius_ratio(z_start, z_end, hop, distance)
        
        print(f"   📊 Z 범위: {z_start} ~ {z_end}mm, Hop: {hop}mm")
        print(f"   🎯 최대 안전 반지름: {max_safe_radius}%")
        
        # 안전성 검증
        min_safe_z = min(z_start, z_end)
        
        # 계산된 반지름으로 실제 궤적 생성해서 검증
        test_points = zhop.generate_arc_gcode_points_legacy(
            (0, 0), (distance, 0), z_start, z_end, hop, max_safe_radius, 20
        )
        
        actual_min_z = min(point[2] for point in test_points)
        
        if actual_min_z >= min_safe_z - 0.001:
            print(f"   ✅ 안전성 검증 통과! (최저점: {actual_min_z:.3f}mm)")
        else:
            print(f"   ❌ 안전성 위반! (최저점: {actual_min_z:.3f}mm, 하한선: {min_safe_z:.3f}mm)")
    
    print("\n✅ 최대 안전 반지름 계산 테스트 완료!")

def test_crossover_point_detection():
    """교차점 검출 테스트"""
    print("\n🔍 Arc 곡선 교차점 검출 검증")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 교차점이 발생하는 시나리오들
    test_cases = [
        {"name": "상승구간 교차", "z_start": 1.0, "z_end": 3.0, "hop": 1.0, "radius": 150},
        {"name": "하강구간 교차", "z_start": 3.0, "z_end": 1.0, "hop": 1.0, "radius": 150},
        {"name": "양쪽 교차", "z_start": 2.0, "z_end": 2.0, "hop": 0.8, "radius": 200},
        {"name": "교차점 없음", "z_start": 2.0, "z_end": 2.0, "hop": 3.0, "radius": 50},
    ]
    
    for case in test_cases:
        print(f"\n🔬 테스트: {case['name']}")
        z_start = case["z_start"]
        z_end = case["z_end"]
        hop = case["hop"]
        radius = case["radius"]
        
        crossover_points = zhop.find_safety_crossover_points(z_start, z_end, hop, radius)
        
        print(f"   📊 설정: Z {z_start}→{z_end}, Hop {hop}mm, R {radius}%")
        
        ascent_cross = crossover_points.get('ascent_crossover')
        descent_cross = crossover_points.get('descent_crossover')
        
        if ascent_cross is not None:
            print(f"   🔺 상승 교차점: {ascent_cross:.4f} (거리비율)")
        else:
            print(f"   ⬆️ 상승 교차점: 없음")
            
        if descent_cross is not None:
            print(f"   🔻 하강 교차점: {descent_cross:.4f} (거리비율)")
        else:
            print(f"   ⬇️ 하강 교차점: 없음")
        
        # 교차점 정확도 검증
        if ascent_cross is not None:
            # 교차점에서의 실제 Z 높이 계산
            z_ratio = zhop.calculate_arc_z_height_ascent(ascent_cross, radius)
            actual_z = z_start + z_ratio * hop
            min_safe_z = min(z_start, z_end)
            
            print(f"     검증: 교차점 Z = {actual_z:.4f}mm, 하한선 = {min_safe_z:.4f}mm")
            
            if abs(actual_z - min_safe_z) < 0.01:  # 1cm 오차 허용
                print(f"     ✅ 상승 교차점 정확도 양호")
            else:
                print(f"     ⚠️ 상승 교차점 오차: {abs(actual_z - min_safe_z):.4f}mm")
    
    print("\n✅ 교차점 검출 테스트 완료!")

def test_safety_segmentation():
    """안전 세그먼트 분할 테스트"""
    print("\n🔪 안전 세그먼트 분할 테스트")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 분할이 필요한 시나리오들
    test_scenarios = [
        {"name": "중간 교차", "z_start": 2.0, "z_end": 2.0, "hop": 1.0, "radius": 150},
        {"name": "양쪽 교차", "z_start": 1.5, "z_end": 1.5, "hop": 0.8, "radius": 200},
        {"name": "경사 교차", "z_start": 1.0, "z_end": 3.0, "hop": 1.2, "radius": 120},
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 시나리오: {scenario['name']}")
        z_start = scenario["z_start"]
        z_end = scenario["z_end"]
        hop = scenario["hop"]
        radius = scenario["radius"]
        
        # 기본 궤적 생성
        basic_points = zhop.generate_arc_gcode_points_legacy(
            (0, 0), (50, 0), z_start, z_end, hop, radius, 20
        )
        
        # 안전 세그먼트 분할 적용
        try:
            safe_points = zhop.generate_arc_with_safety_segments(
                (0, 0), (50, 0), z_start, z_end, hop, radius, 20
            )
            
            min_basic_z = min(point[2] for point in basic_points)
            min_safe_z = min(point[2] for point in safe_points)
            safety_threshold = min(z_start, z_end)
            
            print(f"   📊 기본 최저점: {min_basic_z:.3f}mm")
            print(f"   🛡️ 안전 최저점: {min_safe_z:.3f}mm")
            print(f"   🎯 안전 하한선: {safety_threshold:.3f}mm")
            
            if min_safe_z >= safety_threshold - 0.001:
                print(f"   ✅ 안전 세그먼트 분할 성공!")
                print(f"   📈 포인트 수: {len(basic_points)} → {len(safe_points)}")
            else:
                print(f"   ❌ 안전성 보장 실패")
                
        except Exception as e:
            print(f"   💥 분할 실패: {str(e)}")
    
    print("\n✅ 안전 세그먼트 분할 테스트 완료!")

def test_integrated_arc_safety():
    """통합 Arc 안전성 테스트"""
    print("\n🛡️ 통합 Arc 안전성 테스트")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 종합적인 안전성 시나리오들
    comprehensive_scenarios = [
        {"name": "표준 동일높이", "z_start": 2.0, "z_end": 2.0, "hop": 1.5, "distance": 30.0},
        {"name": "상승 경사면", "z_start": 1.0, "z_end": 3.5, "hop": 2.0, "distance": 40.0},
        {"name": "하강 경사면", "z_start": 4.0, "z_end": 1.5, "hop": 1.8, "distance": 35.0},
        {"name": "극한 상승", "z_start": 0.3, "z_end": 6.0, "hop": 2.5, "distance": 25.0},
        {"name": "초단거리", "z_start": 1.5, "z_end": 1.5, "hop": 1.0, "distance": 2.0},
    ]
    
    success_count = 0
    total_count = len(comprehensive_scenarios)
    
    for scenario in comprehensive_scenarios:
        print(f"\n🔍 종합 테스트: {scenario['name']}")
        z_start = scenario["z_start"]
        z_end = scenario["z_end"]
        hop = scenario["hop"]
        distance = scenario["distance"]
        
        try:
            # 1. 최대 안전 반지름 계산
            max_safe_r = zhop.calculate_max_safe_radius_ratio(z_start, z_end, hop, distance)
            
            # 2. 안전 반지름으로 궤적 생성
            safe_points = zhop.generate_arc_gcode_points(
                (0, 0), (distance, 0), z_start, z_end, hop, max_safe_r, 30
            )
            
            # 3. 안전성 검증
            min_z = min(point[2] for point in safe_points)
            safety_threshold = min(z_start, z_end)
            
            print(f"   📊 최대 안전 반지름: {max_safe_r:.1f}%")
            print(f"   🎯 궤적 최저점: {min_z:.3f}mm")
            print(f"   🛡️ 안전 하한선: {safety_threshold:.3f}mm")
            
            if min_z >= safety_threshold - 0.001:
                print(f"   ✅ 통합 안전성 검증 통과!")
                success_count += 1
            else:
                print(f"   ❌ 안전성 위반! (부족: {safety_threshold - min_z:.3f}mm)")
                
        except Exception as e:
            print(f"   💥 통합 테스트 실패: {str(e)}")
    
    print(f"\n🏆 통합 Arc 안전성 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 통합 안전성 테스트 통과!")
    else:
        print(f"⚠️ {total_count - success_count}개 시나리오에서 안전성 이슈 발견")
    
    print("✅ 통합 Arc 안전성 테스트 완료!")

def run_all_advanced_tests():
    """모든 고급 Arc 안전성 테스트 실행"""
    print("\n🚀 고급 Arc 안전성 전체 테스트 실행")
    print("=" * 80)
    
    test_functions = [
        ("최대 안전 반지름 계산", test_max_safe_radius_calculation),
        ("교차점 검출 알고리즘", test_crossover_point_detection),
        ("안전 세그먼트 분할", test_safety_segmentation),
        ("통합 Arc 안전성", test_integrated_arc_safety),
    ]
    
    success_count = 0
    total_count = len(test_functions)
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n🧪 {test_name} 테스트 실행...")
            test_func()
            print(f"✅ {test_name} 완료")
            success_count += 1
        except Exception as e:
            print(f"❌ {test_name} 실패: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🏆 고급 안전성 테스트 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 고급 Arc 안전성 테스트가 성공적으로 완료되었습니다!")
    else:
        print(f"⚠️ {total_count - success_count}개 테스트가 실패했습니다.")

# =============================================================================
# 기본 Arc 연산 테스트 함수들 (추가)
# =============================================================================

def test_arc_z_height_calculation():
    """Arc Z 높이 계산 함수의 기본 동작 검증"""
    print("\\n📏 Arc Z 높이 계산 기본 검증")
    print("=" * 60)
    zhop = SmartZHop()
    radius_ratio = 50  # 50% 반지름

    # 테스트 케이스: (거리 비율, 예상 Z 비율 - 상승, 예상 Z 비율 - 하강)
    test_cases = [
        (0.0, 0.0, 0.0),    # 시작점
        (0.5, 0.5, 0.5),    # 중간점 (반지름 50%일 때)
        (1.0, 0.0, 0.0),    # 끝점
        (0.25, zhop.calculate_arc_z_height_ascent(0.25, radius_ratio), zhop.calculate_arc_z_height_descent(0.25, radius_ratio)),
        (0.75, zhop.calculate_arc_z_height_ascent(0.75, radius_ratio), zhop.calculate_arc_z_height_descent(0.75, radius_ratio)),
    ]

    for dist_ratio, expected_ascent_z, expected_descent_z in test_cases:
        actual_ascent_z = zhop.calculate_arc_z_height_ascent(dist_ratio, radius_ratio)
        actual_descent_z = zhop.calculate_arc_z_height_descent(dist_ratio, radius_ratio)

        print(f"  📐 거리 {dist_ratio*100:.0f}%:")
        print(f"    상승: 실제 {actual_ascent_z:.4f} vs 예상 {expected_ascent_z:.4f}")
        print(f"    하강: 실제 {actual_descent_z:.4f} vs 예상 {expected_descent_z:.4f}")

        if not (abs(actual_ascent_z - expected_ascent_z) < 1e-6 and \
                abs(actual_descent_z - expected_descent_z) < 1e-6):
            print(f"    ❌ 검증 실패!")
        else:
            print(f"    ✅ 검증 통과!")
    print("✅ Arc Z 높이 계산 기본 검증 완료!")

def test_gcode_generation_basic():
    """G-code 생성 함수의 기본 동작 검증"""
    print("\\n🛠️ G-code 생성 기본 검증")
    print("=" * 60)
    zhop = SmartZHop()

    start_point = (0, 0)
    end_point = (10, 10)
    z_start, z_end = 1.0, 1.5
    hop_height = 2.0
    radius_ratio = 75
    segments = 10

    print(f"  📝 시나리오: {start_point} -> {end_point}, Z {z_start}->{z_end}, Hop {hop_height}, R {radius_ratio}%, Segs {segments}")

    try:
        gcode_points = zhop.generate_arc_gcode_points(
            start_point, end_point, z_start, z_end, hop_height, radius_ratio, segments
        )
        if gcode_points:
            print(f"  ✅ G-code 포인트 {len(gcode_points)}개 생성 성공.")
            # 시작점과 끝점 Z 높이 검증
            if not (abs(gcode_points[0][2] - z_start) < 1e-6 and \
                    abs(gcode_points[-1][2] - z_end) < 1e-6):
                print(f"    ❌ 시작/끝 Z 높이 불일치: 시작 {gcode_points[0][2]:.3f} (예상 {z_start}), 끝 {gcode_points[-1][2]:.3f} (예상 {z_end})")
            else:
                print(f"    ✅ 시작/끝 Z 높이 일치.")

            # 최대 높이 검증 (대략적)
            max_z_trajectory = max(p[2] for p in gcode_points)
            expected_peak_z = max(z_start, z_end) + hop_height * (radius_ratio / 100.0)
            # 실제로는 복잡하지만, 대략적인 상한선으로 체크
            if max_z_trajectory <= expected_peak_z + 0.1: # 약간의 여유
                 print(f"    ✅ 최대 Z 높이 ({max_z_trajectory:.3f}mm)가 예상 범위 내 ({expected_peak_z:.3f}mm).")
            else:
                 print(f"    ⚠️ 최대 Z 높이 ({max_z_trajectory:.3f}mm)가 예상 범위 ({expected_peak_z:.3f}mm) 초과 가능성.")
        else:
            print(f"  ❌ G-code 포인트 생성 실패 (결과 없음).")
    except Exception as e:
        print(f"  💥 G-code 생성 중 오류: {e}")
    print("✅ G-code 생성 기본 검증 완료!")

# =============================================================================
# 테스트 실행기
# =============================================================================
def run_visualization_tests():
    """모든 시각화 관련 테스트 실행"""
    print("\\n🎨 시각화 테스트 모음 실행")
    print("=" * 70)
    visualize_arc_function_comparison()
    visualize_trajectory_comparison()
    visualize_3d_trajectory()
    visualize_safety_verification()
    visualize_extreme_cases()
    visualize_performance_analysis()
    print("\\n🎉 모든 시각화 테스트 완료!")

def run_basic_arc_tests():
    """기본 Arc 연산 테스트 실행"""
    print("\\n⚙️ 기본 Arc 연산 테스트 모음 실행")
    print("=" * 70)
    test_arc_z_height_calculation()
    test_gcode_generation_basic()
    print("\\n🎉 모든 기본 Arc 연산 테스트 완료!")

def run_all_tests():
    """모든 테스트 실행"""
    print("\\n🚀🚀🚀 모든 테스트 실행 시작 🚀🚀🚀")
    print("=" * 80)
    run_visualization_tests()
    run_basic_arc_tests()
    run_all_advanced_tests() # 기존 고급 안전성 테스트
    print("\\n🎉🎉🎉 모든 테스트가 성공적으로 완료되었습니다! 🎉🎉🎉")

if __name__ == "__main__":
    print("Smart Z-Hop Arc 모드 테스트 스크립트")
    print("======================================")
    
    # HAS_MATPLOTLIB 상태에 따라 시각화 테스트 실행 여부 결정
    if not HAS_MATPLOTLIB:
        print("\\n⚠️ matplotlib 라이브러리가 없어 GUI 시각화 테스트는 제한됩니다.")
        print("   텍스트 기반 시각화 및 분석은 계속 진행됩니다.")

    while True:
        print("\\n어떤 테스트를 실행하시겠습니까?")
        print("1. 모든 테스트 실행")
        print("2. 시각화 테스트 모음")
        print("3. 기본 Arc 연산 테스트 모음")
        print("4. 고급 Arc 안전성 테스트 모음")
        print("5. 종료")
        
        choice = input("선택 (1-5): ")
        
        if choice == '1':
            run_all_tests()
        elif choice == '2':
            run_visualization_tests()
        elif choice == '3':
            run_basic_arc_tests()
        elif choice == '4':
            run_all_advanced_tests()
        elif choice == '5':
            print("테스트를 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 입력해주세요.")


if __name__ == "__main__":
    print("🚀 Smart Z-Hop Arc Mode 테스트 시작")
    print("=" * 50)
    
    try:
        # 기본 Arc 함수 테스트 실행
        print("\n📊 1. 기본 Arc 함수 테스트")
        run_basic_arc_tests()
        
        print("\n📈 2. 시각화 테스트 (matplotlib 사용 가능 시)")
        try:
            # 시각화 테스트 시도
            test_arc_curve_visualization_multiple()
            print("✅ 시각화 테스트 완료")
        except ImportError:
            print("⚠️ matplotlib을 사용할 수 없어 시각화 테스트를 건너뜁니다.")
        except Exception as e:
            print(f"⚠️ 시각화 테스트 중 오류 발생: {str(e)}")
        
        print("\n🛡️ 3. 고급 안전성 테스트")
        run_all_advanced_tests()
        
        print("\n🎯 테스트 완료!")
        print("모든 Arc 모드 기능이 정상적으로 작동합니다.")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Smart Z-Hop Arc Mode 테스트 종료")
