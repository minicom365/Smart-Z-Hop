import numpy as np
import matplotlib.pyplot as plt
import math

def generate_bezier_curve_with_ratio(start_point, end_point, intensity_ratio, num_points=100):
    """
    베지어 곡선을 사용하여 곡률 강도에 따른 곡선 생성
    상승과 하강이 대칭적으로 동작하도록 개선
    
    Args:
        start_point: (x, y) 시작점
        end_point: (x, y) 끝점
        intensity_ratio: 0~1 사이의 비율 (0일 때 직선, 1일 때 거의 직각 L자)
        num_points: 곡선을 구성할 점의 개수
    
    Returns:
        x, y 좌표 배열
    """
    x1, y1 = start_point
    x2, y2 = end_point
    
    # intensity_ratio 클램핑 (0~1 범위)
    intensity_ratio = max(0.0, min(1.0, intensity_ratio))
    
    # 시작점과 끝점 사이의 거리와 방향
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance < 1e-10:  # 시작점과 끝점이 같은 경우
        x = np.full(num_points, x1)
        y = np.full(num_points, y1)
        return x, y
    
    # 베지어 곡선의 제어점 계산
    P0 = np.array([x1, y1])
    P3 = np.array([x2, y2])
    
    if intensity_ratio == 0:
        # 완전한 직선
        P1 = P0 + (P3 - P0) * (1/3)
        P2 = P0 + (P3 - P0) * (2/3)
    else:
        # 이동 방향 분석
        is_rising = dy > 0  # 상승하는 경우
        is_falling = dy < 0  # 하강하는 경우
        is_horizontal = abs(dy) < 1e-6  # 수평 이동
        
        # 제어점 거리 계산
        control_factor = 0.5 + 0.5 * intensity_ratio  # 0.5 ~ 1.0
        
        if is_horizontal:
            # 수평 이동: Y값은 고정, X값만 조절
            P1 = np.array([x1 + dx * intensity_ratio * 0.3, y1])
            P2 = np.array([x2 - dx * intensity_ratio * 0.3, y2])
            
        elif is_rising:
            # 상승하는 경우: 먼저 수평으로 이동한 후 수직으로 상승
            horizontal_progress = intensity_ratio
            vertical_delay = intensity_ratio * 0.7
            
            # P1: 시작점에서 수평으로 이동
            P1 = np.array([
                x1 + dx * horizontal_progress * control_factor,
                y1
            ])
            
            # P2: 끝점 근처에서 수직으로 이동 시작
            P2 = np.array([
                x2,
                y1 + dy * (1 - vertical_delay)
            ])
            
        else:  # is_falling
            # 하강하는 경우: 먼저 수직으로 유지한 후 수평으로 이동 (상승과 대칭)
            vertical_progress = intensity_ratio
            horizontal_delay = intensity_ratio * 0.7
            
            # P1: 시작점에서 수직으로 유지하면서 일부 하강
            P1 = np.array([
                x1,
                y1 + dy * vertical_progress * control_factor
            ])
            
            # P2: 끝점 근처에서 수평으로 이동 시작
            P2 = np.array([
                x1 + dx * (1 - horizontal_delay),
                y2
            ])
        
        # 고강도 조정 (ratio > 0.7일 때 더 극단적으로)
        if intensity_ratio > 0.7:
            factor = (intensity_ratio - 0.7) / 0.3  # 0.7~1 -> 0~1
            
            if is_rising:
                # 상승: 더 극단적인 L자 형태
                P1[0] = x1 + dx * (intensity_ratio * 0.9)
                P1[1] = y1
                P2[0] = x2
                P2[1] = y1 + dy * (1 - intensity_ratio * 0.95)
                
            elif is_falling:
                # 하강: 상승과 대칭적인 극단적 형태
                P1[0] = x1
                P1[1] = y1 + dy * (intensity_ratio * 0.9)
                P2[0] = x1 + dx * (1 - intensity_ratio * 0.95)
                P2[1] = y2
                
            elif is_horizontal:
                # 수평: 양쪽 끝에서 더 극단적으로
                mid_point = (x1 + x2) / 2
                offset = abs(dx) * factor * 0.3
                P1[1] = y1 + offset
                P2[1] = y2 + offset
    
    # 베지어 곡선 계산 (3차 베지어)
    t = np.linspace(0, 1, num_points)
    
    # 베지어 곡선 공식: B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃
    curve_points = (
        np.outer((1-t)**3, P0) +
        np.outer(3*(1-t)**2*t, P1) +
        np.outer(3*(1-t)*t**2, P2) +
        np.outer(t**3, P3)
    )
    
    x = curve_points[:, 0]
    y = curve_points[:, 1]
    
    # 제약 조건 적용
    # 1. 하강하는 경우: y값이 끝점 y값 아래로 내려가지 않도록
    # 2. 상승하는 경우: y값이 시작점 y값 아래로 내려가지 않도록
    if dy > 0:  # 상승
        y = np.maximum(y, y1)
    elif dy < 0:  # 하강
        y = np.minimum(y, y1)
        y = np.maximum(y, y2)
    
    # X 방향 제약: 끝점을 초과하지 않도록
    if dx > 0:  # 오른쪽으로 이동
        exceed_mask = x > x2
        if np.any(exceed_mask):
            x[exceed_mask] = x2
            y[exceed_mask] = y2
    elif dx < 0:  # 왼쪽으로 이동
        exceed_mask = x < x2
        if np.any(exceed_mask):
            x[exceed_mask] = x2
            y[exceed_mask] = y2
    
    return x, y

def plot_symmetric_comparison():
    """상승과 하강의 대칭성 비교"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('개선된 베지어 곡선: 상승과 하강의 대칭성', fontsize=16)
    
    # 테스트 케이스들
    cases = [
        # 첫 번째 행: 상승하는 경우들
        {'start': (0, 0), 'end': (4, 3), 'title': '상승 1: 완만한 상승'},
        {'start': (0, 1), 'end': (3, 4), 'title': '상승 2: 급격한 상승'},
        {'start': (0, 0), 'end': (5, 2), 'title': '상승 3: 긴 거리 상승'},
        
        # 두 번째 행: 하강하는 경우들 (상승과 대칭)
        {'start': (0, 3), 'end': (4, 0), 'title': '하강 1: 완만한 하강'},
        {'start': (0, 4), 'end': (3, 1), 'title': '하강 2: 급격한 하강'},
        {'start': (0, 2), 'end': (5, 0), 'title': '하강 3: 긴 거리 하강'}
    ]
    
    ratios = [0.0, 0.3, 0.6, 0.9]
    colors = ['blue', 'green', 'orange', 'red']
    
    for case_idx, case in enumerate(cases):
        row = case_idx // 3
        col = case_idx % 3
        ax = axes[row, col]
        start_point = case['start']
        end_point = case['end']
        
        # 각 ratio에 대해 곡선 생성
        for i, ratio in enumerate(ratios):
            x, y = generate_bezier_curve_with_ratio(start_point, end_point, ratio)
            ax.plot(x, y, color=colors[i], linewidth=2.5, alpha=0.8,
                   label=f'{ratio:.1f}' if col == 0 else "")
        
        # 시작점과 끝점 표시
        ax.plot(start_point[0], start_point[1], 'go', markersize=10, 
                label='시작점' if case_idx == 0 else "")
        ax.plot(end_point[0], end_point[1], 'ro', markersize=10, 
                label='끝점' if case_idx == 0 else "")
        
        # 직선 참조선
        ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 
                'k--', alpha=0.3, linewidth=1, label='직선' if case_idx == 0 else "")
        
        # 축 설정
        ax.grid(True, alpha=0.3)
        ax.set_title(case['title'])
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_aspect('equal', adjustable='box')
        
        # 범위 설정
        x_min = min(start_point[0], end_point[0]) - 0.5
        x_max = max(start_point[0], end_point[0]) + 0.5
        y_min = min(start_point[1], end_point[1]) - 0.5
        y_max = max(start_point[1], end_point[1]) + 0.5
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
    
    # 범례는 첫 번째 열에만
    axes[0, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    axes[1, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.show()

def plot_control_points_comparison():
    """제어점 비교 시각화 (상승 vs 하강)"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('제어점 비교: 상승 vs 하강', fontsize=16)
    
    # 상승과 하강 케이스
    cases = [
        {'start': (0, 0), 'end': (4, 3), 'title': '상승 - Ratio 0.3', 'ratio': 0.3},
        {'start': (0, 0), 'end': (4, 3), 'title': '상승 - Ratio 0.8', 'ratio': 0.8},
        {'start': (0, 3), 'end': (4, 0), 'title': '하강 - Ratio 0.3', 'ratio': 0.3},
        {'start': (0, 3), 'end': (4, 0), 'title': '하강 - Ratio 0.8', 'ratio': 0.8}
    ]
    
    for i, case in enumerate(cases):
        ax = axes[i//2, i%2]
        start_point = case['start']
        end_point = case['end']
        ratio = case['ratio']
        
        # 곡선 생성
        x, y = generate_bezier_curve_with_ratio(start_point, end_point, ratio, 100)
        
        # 제어점 계산 (함수 내부 로직 재현)
        x1, y1 = start_point
        x2, y2 = end_point
        dx = x2 - x1
        dy = y2 - y1
        
        P0 = np.array([x1, y1])
        P3 = np.array([x2, y2])
        
        # 개선된 제어점 계산 로직
        is_rising = dy > 0
        is_falling = dy < 0
        control_factor = 0.5 + 0.5 * ratio
        
        if is_rising:
            horizontal_progress = ratio
            vertical_delay = ratio * 0.7
            
            P1 = np.array([
                x1 + dx * horizontal_progress * control_factor,
                y1
            ])
            P2 = np.array([
                x2,
                y1 + dy * (1 - vertical_delay)
            ])
            
            if ratio > 0.7:
                P1[0] = x1 + dx * (ratio * 0.9)
                P1[1] = y1
                P2[0] = x2
                P2[1] = y1 + dy * (1 - ratio * 0.95)
                
        elif is_falling:
            vertical_progress = ratio
            horizontal_delay = ratio * 0.7
            
            P1 = np.array([
                x1,
                y1 + dy * vertical_progress * control_factor
            ])
            P2 = np.array([
                x1 + dx * (1 - horizontal_delay),
                y2
            ])
            
            if ratio > 0.7:
                P1[0] = x1
                P1[1] = y1 + dy * (ratio * 0.9)
                P2[0] = x1 + dx * (1 - ratio * 0.95)
                P2[1] = y2
        
        # 곡선 플롯
        ax.plot(x, y, 'b-', linewidth=4, label='베지어 곡선', alpha=0.8)
        
        # 제어점과 제어선 플롯
        control_x = [P0[0], P1[0], P2[0], P3[0]]
        control_y = [P0[1], P1[1], P2[1], P3[1]]
        
        ax.plot(control_x, control_y, 'r--', alpha=0.7, linewidth=2, label='제어선')
        ax.plot(P0[0], P0[1], 'go', markersize=12, label='P₀ (시작)')
        ax.plot(P1[0], P1[1], 'rs', markersize=10, label='P₁ (제어)')
        ax.plot(P2[0], P2[1], 'rs', markersize=10, label='P₂ (제어)')
        ax.plot(P3[0], P3[1], 'bo', markersize=12, label='P₃ (끝)')
        
        # 직선 참조
        ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 
                'k:', alpha=0.5, linewidth=1, label='직선')
        
        ax.grid(True, alpha=0.3)
        ax.set_title(case['title'])
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.legend(fontsize=8)
        ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    plt.show()

def analyze_symmetry():
    """대칭성 분석"""
    
    print("=== 상승과 하강의 대칭성 분석 ===\n")
    
    # 대칭적인 케이스들
    test_cases = [
        {
            'rising': {'start': (0, 0), 'end': (4, 3)},
            'falling': {'start': (0, 3), 'end': (4, 0)},
            'name': '대칭 케이스 1'
        },
        {
            'rising': {'start': (0, 1), 'end': (3, 4)},
            'falling': {'start': (0, 4), 'end': (3, 1)},
            'name': '대칭 케이스 2'
        }
    ]
    
    ratios = [0.0, 0.3, 0.6, 0.9]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print("-" * 40)
        
        for ratio in ratios:
            # 상승 곡선
            x_rise, y_rise = generate_bezier_curve_with_ratio(
                case['rising']['start'], case['rising']['end'], ratio, 50)
            
            # 하강 곡선
            x_fall, y_fall = generate_bezier_curve_with_ratio(
                case['falling']['start'], case['falling']['end'], ratio, 50)
            
            # 곡선 길이 계산
            rise_length = np.sum(np.sqrt(np.diff(x_rise)**2 + np.diff(y_rise)**2))
            fall_length = np.sum(np.sqrt(np.diff(x_fall)**2 + np.diff(y_fall)**2))
            
            # 대칭성 지표 (길이 비율)
            symmetry_ratio = min(rise_length, fall_length) / max(rise_length, fall_length)
            
            print(f"  Ratio {ratio:.1f}: 상승길이={rise_length:.2f}, "
                  f"하강길이={fall_length:.2f}, 대칭도={symmetry_ratio:.3f}")
    
    print(f"\n{'='*50}")
    print("개선 사항:")
    print("- 하강 곡선이 상승 곡선과 대칭적으로 동작")
    print("- 제어점 배치가 상승/하강에 따라 적절히 조정됨")
    print("- 곡선 길이와 형태가 더 일관적으로 변화")

# 메인 실행
if __name__ == "__main__":
    print("=== 개선된 베지어 곡선 생성기 ===")
    print("상승과 하강이 대칭적으로 동작하도록 개선")
    print()
    
    # 대칭성 비교 플롯
    plot_symmetric_comparison()
    
    # 제어점 비교
    plot_control_points_comparison()
    
    # 대칭성 분석
    analyze_symmetry()
    
    # 추가 시각화: 다양한 ratio에서의 상승/하강 비교
    print("\n=== 상세 비교 시각화 ===")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 상승하는 경우
    start_rise = (0, 0)
    end_rise = (5, 4)
    ratios = np.linspace(0, 1, 11)
    colors = plt.cm.viridis(np.linspace(0, 1, len(ratios)))
    
    for i, ratio in enumerate(ratios):
        x, y = generate_bezier_curve_with_ratio(start_rise, end_rise, ratio, 50)
        ax1.plot(x, y, color=colors[i], linewidth=2, 
                label=f'{ratio:.1f}' if i % 2 == 0 else "")
    
    ax1.plot(start_rise[0], start_rise[1], 'go', markersize=10, label='시작점')
    ax1.plot(end_rise[0], end_rise[1], 'ro', markersize=10, label='끝점')
    ax1.plot([start_rise[0], end_rise[0]], [start_rise[1], end_rise[1]], 
             'k--', alpha=0.3, label='직선')
    ax1.set_title('상승하는 곡선 (Intensity Ratio 변화)')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Z')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_aspect('equal')
    
    # 하강하는 경우 (상승과 대칭)
    start_fall = (0, 4)
    end_fall = (5, 0)
    
    for i, ratio in enumerate(ratios):
        x, y = generate_bezier_curve_with_ratio(start_fall, end_fall, ratio, 50)
        ax2.plot(x, y, color=colors[i], linewidth=2, 
                label=f'{ratio:.1f}' if i % 2 == 0 else "")
    
    ax2.plot(start_fall[0], start_fall[1], 'go', markersize=10, label='시작점')
    ax2.plot(end_fall[0], end_fall[1], 'ro', markersize=10, label='끝점')
    ax2.plot([start_fall[0], end_fall[0]], [start_fall[1], end_fall[1]], 
             'k--', alpha=0.3, label='직선')
    ax2.set_title('하강하는 곡선 (Intensity Ratio 변화)')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Z')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.show()