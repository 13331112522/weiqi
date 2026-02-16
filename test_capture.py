"""
围棋提子功能测试脚本

测试场景：
1. 单子提子 - 一个棋子被完全包围
2. 棋串提子 - 多个相连棋子被包围
3. 边界提子 - 在棋盘边缘的提子
"""

import sys
sys.path.append("/Users/zhouql1978/Documents/first_web ")

# 导入提子函数
from server import get_group_and_liberties, check_and_remove_captures

def create_test_board():
    """创建一个空的19×19棋盘"""
    return [[0 for _ in range(19)] for _ in range(19)]

def print_board(board, message=""):
    """打印棋盘状态"""
    if message:
        print(f"\n{message}")
    print("   " + " ".join([f"{i:2}" for i in range(19)]))
    for i in range(19):
        print(f"{i:2} " + " ".join([f"{board[i][j]:2}" for j in range(19)]))

def test_single_stone_capture():
    """测试场景1：单子提子"""
    print("\n" + "="*60)
    print("测试场景1：单子提子")
    print("="*60)

    board = create_test_board()

    # 在中心放置一个黑子
    center_row, center_col = 9, 9
    board[center_row][center_col] = 1  # 黑子

    # 用3个白子部分包围黑子（留一个气）
    board[center_row-1][center_col] = 2  # 上
    board[center_row+1][center_col] = 2  # 下
    board[center_row][center_col-1] = 2  # 左

    print_board(board, "落子前：黑子被3个白子部分包围（还剩一口气）")

    # 白棋落子在第4个位置，完成包围
    board[center_row][center_col+1] = 2  # 右（落子）

    # 现在检查并提走气尽的对手棋子
    captured = check_and_remove_captures(board, center_row, center_col+1, 2)

    print_board(board, f"落子后：提走了 {len(captured)} 颗子")

    # 验证结果
    assert len(captured) == 1, f"应该提走1颗子，实际提走了{len(captured)}颗"
    assert board[center_row][center_col] == 0, "中心位置应该是空的"
    print("✓ 测试场景1通过：单子提子成功")

def test_group_capture():
    """测试场景2：棋串提子"""
    print("\n" + "="*60)
    print("测试场景2：棋串提子")
    print("="*60)

    board = create_test_board()

    # 创建一个3个黑子相连的棋串
    board[9][9] = 1
    board[9][10] = 1
    board[9][11] = 1

    # 用白子包围这个棋串
    # 上下
    for col in range(9, 12):
        board[8][col] = 2
        board[10][col] = 2
    # 左右
    board[9][8] = 2
    board[9][12] = 2

    print_board(board, "落子前：3个黑子相连，被白子包围")

    # 白棋落子，应该提走整个棋串
    captured = check_and_remove_captures(board, 8, 10, 2)

    print_board(board, f"落子后：提走了 {len(captured)} 颗子")

    # 验证结果
    assert len(captured) == 3, f"应该提走3颗子，实际提走了{len(captured)}颗"
    assert board[9][9] == 0 and board[9][10] == 0 and board[9][11] == 0, "三个位置都应该被清空"
    print("✓ 测试场景2通过：棋串提子成功")

def test_corner_capture():
    """测试场景3：角落提子"""
    print("\n" + "="*60)
    print("测试场景3：角落提子")
    print("="*60)

    board = create_test_board()

    # 在角落放置一个黑子
    board[0][0] = 1  # 左上角

    # 用2个白子包围（角落只需要2个子）
    board[0][1] = 2
    board[1][0] = 2

    print_board(board, "落子前：角落的黑子被包围")

    # 白棋落子，应该提走黑子
    captured = check_and_remove_captures(board, 0, 1, 2)

    print_board(board, f"落子后：提走了 {len(captured)} 颗子")

    # 验证结果
    assert len(captured) == 1, f"应该提走1颗子，实际提走了{len(captured)}颗"
    assert board[0][0] == 0, "角落位置应该是空的"
    print("✓ 测试场景3通过：角落提子成功")

def test_liberties_count():
    """测试场景4：气数计算"""
    print("\n" + "="*60)
    print("测试场景4：气数计算")
    print("="*60)

    board = create_test_board()

    # 创建一个2个黑子相连的棋串
    board[9][9] = 1
    board[9][10] = 1

    print_board(board, "棋盘：2个黑子水平相连")

    # 计算气
    stones, liberties = get_group_and_liberties(board, 9, 9)

    print(f"\n棋子位置：{stones}")
    print(f"气的位置：{sorted(liberties)}")
    print(f"气数：{len(liberties)}")

    # 验证结果
    assert len(stones) == 2, "应该找到2颗棋子"
    assert len(liberties) == 6, "应该有6口气"
    print("✓ 测试场景4通过：气数计算正确")

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("围棋提子功能测试")
    print("="*60)

    try:
        test_single_stone_capture()
        test_group_capture()
        test_corner_capture()
        test_liberties_count()

        print("\n" + "="*60)
        print("✅ 所有测试通过！提子功能工作正常")
        print("="*60)
        return True
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
