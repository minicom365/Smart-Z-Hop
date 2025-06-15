import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import math

def generate_curve_with_ratio(start_point, end_point, intensity_ratio, num_points=100):
    """
    3점원 생성법을 사용하여 곡선 생성
    
    Args:
        start_point: (x, y) 시작점
        end_point: (x, y) 끝점
        intensity_ratio: 0~최대값 사이의 비율 (0%일 때 직선, 100%일 때 최소 반지름)
        num_points: 곡선을 구성할 점의 개수
    
    Returns:
        x, y 좌표 배열
    """
    x1, y1 = start_point
    x2, y2 = end_point
    
    # 시작점과 끝점 사이의 거리
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # 최소 반지름 (시작점과 끝점 거리의 절반)
    min_radius = distance / 2
    
    # intensity_ratio가 0%일 때는 직선 (무한대 반지름)
    if intensity_ratio <= 0:
        x = np.linspace(x1, x2, num_points)
        y = np.linspace(y1, y2, num_points)
        return x, y
    
    # intensity_ratio에 따른 반지름 계산
    # ratio 0.0에서 무한대, ratio 1.0에서 최소 반지름
    if intensity_ratio >= 1.0:
        radius = min_radius
    else:
        # ratio가 1.0에 가까워질수록 min_radius에 수렴
        radius = min_radius / intensity_ratio if intensity_ratio > 0 else float('inf')
        radius = max(radius, min_radius)
    
    # 시작점과 끝점의 중점
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # 시작점과 끝점을 잇는 직선의 수직 방향 벡터
    dx = x2 - x1
    dy = y2 - y1
    
    # 수직 벡터 (정규화)
    if abs(dx) > 1e-10 or abs(dy) > 1e-10:
        perp_x = -dy
        perp_y = dx
        perp_length = math.sqrt(perp_x**2 + perp_y**2)
        perp_x /= perp_length
        perp_y /= perp_length
    else:
        perp_x, perp_y = 0, 1
    
    # 원의 중심에서 현까지의 거리
    chord_to_center = math.sqrt(radius**2 - (distance/2)**2) if radius > distance/2 else 0
    
    # 원의 중심점 계산 (상승 곡선을 위해 위쪽 방향)
    center_x = mid_x + perp_x * chord_to_center
    center_y = mid_y + perp_y * chord_to_center
    
    # 시작각과 끝각 계산
    start_angle = math.atan2(y1 - center_y, x1 - center_x)
    end_angle = math.atan2(y2 - center_y, x2 - center_x)
    
    # 각도 조정 (상승 곡선을 위해)
    if end_angle < start_angle:
        end_angle += 2 * math.pi
    
    # 각도 범위가 π보다 크면 반대 방향으로
    if end_angle - start_angle > math.pi:
        start_angle, end_angle = end_angle - 2*math.pi, start_angle
    
    # 곡선 점들 생성
    angles = np.linspace(start_angle, end_angle, num_points)
    x = center_x + radius * np.cos(angles)
    y = center_y + radius * np.sin(angles)
    
    # 제약 조건 적용
    # 1. z값이 시작점 z값 이하인 경우 시작점 z값으로 클램핑
    y = np.maximum(y, y1)
    
    # 2. 끝점 수직선을 초과하는 부분 처리
    # 끝점 x좌표를 초과하는 부분을 찾아서 직선으로 처리
    exceed_mask = x > x2
    if np.any(exceed_mask):
        # 초과하는 부분을 끝점에서 직선으로 연결
        exceed_indices = np.where(exceed_mask)[0]
        for idx in exceed_indices:
            # 끝점에서 수직선 처리 (x = x2, y = y2)
            x[idx] = x2
            y[idx] = y2
    
    return x, y

def plot_curves_with_ratios():
    """다양한 intensity_ratio 값으로 곡선들을 플롯"""
    
    # 플롯 설정
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('3점원 생성법 곡선 생성 (Intensity Ratio 변화)', fontsize=14)
    
    # 세 가지 경우의 시작점과 끝점
    cases = [
        # Case 1: 직선적 상승
        {'start': (0, 0), 'end': (2, 3), 'title': 'Case 1: Linear Rise'},
        # Case 2: 곡선적 상승  
        {'start': (0, 0), 'end': (3, 2), 'title': 'Case 2: Curved Rise'},
        # Case 3: 원호 형태
        {'start': (0, 1), 'end': (3, 1), 'title': 'Case 3: Arc Shape'}
    ]
    
    # 10개의 ratio 샘플 (0부터 1.5까지)
    ratios = np.linspace(0, 1.5, 10)
    colors = plt.cm.viridis(np.linspace(0, 1, len(ratios)))
    
    for case_idx, case in enumerate(cases):
        ax = axes[case_idx]
        start_point = case['start']
        end_point = case['end']
        
        # 각 ratio에 대해 곡선 생성
        for i, ratio in enumerate(ratios):
            x, y = generate_curve_with_ratio(start_point, end_point, ratio)
            
            # 곡선 플롯
            ax.plot(x, y, color=colors[i], alpha=0.7, linewidth=2, 
                   label=f'Ratio: {ratio:.2f}' if case_idx == 0 and i % 2 == 0 else "")
        
        # 시작점과 끝점 표시
        ax.plot(start_point[0], start_point[1], 'ro', markersize=8, label='Start' if case_idx == 0 else "")
        ax.plot(end_point[0], end_point[1], 'bo', markersize=8, label='End' if case_idx == 0 else "")
        
        # z=시작점z 기준선
        ax.axhline(y=start_point[1], color='red', linestyle='--', alpha=0.5, linewidth=1, label='Min Z' if case_idx == 0 else "")
        # 끝점 수직선
        ax.axvline(x=end_point[0], color='orange', linestyle='--', alpha=0.5, linewidth=1, label='Max X' if case_idx == 0 else "")
        
        # 축 설정
        ax.grid(True, alpha=0.3)
        ax.set_title(case['title'])
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_aspect('equal', adjustable='box')
        
        # 범위 설정
        ax.set_xlim(-0.5, max(end_point[0], start_point[0]) + 0.5)
        ax.set_ylim(-0.5, max(end_point[1], start_point[1]) + 1)
    
    # 범례는 첫 번째 서브플롯에만
    axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    plt.tight_layout()
    plt.show()

def demonstrate_formula():
    """수식과 원리 설명"""
    print("=== 3점원 생성법 곡선 생성 수식 ===\n")
    
    print("1. 기본 원리:")
    print("   - 시작점 P1(x1, y1)과 끝점 P2(x2, y2)를 지나는 원호 생성")
    print("   - intensity_ratio에 따라 원의 반지름 R 조절")
    print("   - 0.0: R → ∞ (직선)")
    print("   - 1.0: R = 최소값 (시작점-끝점 거리의 절반)")
    print("   - 1.0 초과: R = 최소값 유지")
    
    print("\n2. 핵심 수식:")
    print("   거리 d = √[(x2-x1)² + (y2-y1)²]")
    print("   최소반지름 R_min = d/2")
    print("   반지름 R = R_min / intensity_ratio (ratio > 0)")
    print("   R = R_min (ratio ≥ 1.0)")
    print("   원의 중심 = 중점 + 수직방향 × √(R² - (d/2)²)")
    
    print("\n3. 각도 계산:")
    print("   시작각 θ1 = atan2(y1-cy, x1-cx)")
    print("   끝각 θ2 = atan2(y2-cy, x2-cx)")
    print("   곡선점 = (cx + R×cos(θ), cy + R×sin(θ))")
    
    print("\n4. 제약 조건:")
    print("   - z ≤ 시작점z 인 값은 시작점z로 클램핑")
    print("   - 끝점 수직선(x > 끝점x) 초과 시 직선 처리")
    print("   - R ≥ R_min (물리적 제약)")
    print("   - 연속성 보장을 위한 각도 조정")

# 실행
if __name__ == "__main__":
    demonstrate_formula()
    print("\n" + "="*50)
    plot_curves_with_ratios()
    
    # 개별 테스트
    print("\n=== 개별 곡선 테스트 ===")
    start = (0, 0)
    end = (4, 3)
    
    plt.figure(figsize=(12, 8))
    ratios = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]
    colors = plt.cm.rainbow(np.linspace(0, 1, len(ratios)))
    
    for i, ratio in enumerate(ratios):
        x, y = generate_curve_with_ratio(start, end, ratio, 50)
        plt.plot(x, y, color=colors[i], linewidth=2, label=f'{ratio:.1f}')
    
    plt.plot(start[0], start[1], 'ro', markersize=10, label='Start Point')
    plt.plot(end[0], end[1], 'bo', markersize=10, label='End Point')
    plt.axhline(y=start[1], color='red', linestyle='--', alpha=0.5, label='Min Z (Start Z)')
    plt.axvline(x=end[0], color='orange', linestyle='--', alpha=0.5, label='Max X (End X)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.title('Intensity Ratio에 따른 곡선 변화')
    plt.xlabel('X')
    plt.ylabel('Z')
    plt.axis('equal')
    plt.show()