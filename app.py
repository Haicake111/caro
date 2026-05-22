from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

SIZE = 5
WIN_COUNT = 4 # Cần 4 quân liên tiếp để thắng trên bàn 5x5
MAX_DEPTH = 4 # Giới hạn độ sâu để tránh treo máy

def check_winner(b, player):
    # Kiểm tra hàng ngang
    for r in range(SIZE):
        for c in range(SIZE - WIN_COUNT + 1):
            if all(b[r * SIZE + c + i] == player for i in range(WIN_COUNT)): return True
    # Kiểm tra hàng dọc
    for c in range(SIZE):
        for r in range(SIZE - WIN_COUNT + 1):
            if all(b[(r + i) * SIZE + c] == player for i in range(WIN_COUNT)): return True
    # Kiểm tra chéo chính (\)
    for r in range(SIZE - WIN_COUNT + 1):
        for c in range(SIZE - WIN_COUNT + 1):
            if all(b[(r + i) * SIZE + c + i] == player for i in range(WIN_COUNT)): return True
    # Kiểm tra chéo phụ (/)
    for r in range(SIZE - WIN_COUNT + 1):
        for c in range(WIN_COUNT - 1, SIZE):
            if all(b[(r + i) * SIZE + c - i] == player for i in range(WIN_COUNT)): return True
    return False

def is_board_full(b):
    return ' ' not in b

# Minimax tích hợp Cắt tỉa Alpha-Beta và Giới hạn độ sâu
def minimax(b, depth, alpha, beta, is_maximizing):
    if check_winner(b, 'O'): return 10 + depth  # Ưu tiên thắng nhanh
    if check_winner(b, 'X'): return -10 - depth # Tránh thua sớm
    if is_board_full(b) or depth == 0: return 0 # Hòa hoặc đạt giới hạn độ sâu

    if is_maximizing:
        best_score = -math.inf
        for i in range(SIZE * SIZE):
            if b[i] == ' ':
                b[i] = 'O'
                score = minimax(b, depth - 1, alpha, beta, False)
                b[i] = ' '
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha: break # Cắt tỉa
        return best_score
    else:
        best_score = math.inf
        for i in range(SIZE * SIZE):
            if b[i] == ' ':
                b[i] = 'X'
                score = minimax(b, depth - 1, alpha, beta, True)
                b[i] = ' '
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha: break # Cắt tỉa
        return best_score

def get_best_move(b):
    best_score = -math.inf
    move = -1
    # Tối ưu: Nếu bàn cờ trống, đánh luôn vào giữa
    if b.count(' ') == SIZE * SIZE:
        return (SIZE * SIZE) // 2

    for i in range(SIZE * SIZE):
        if b[i] == ' ':
            b[i] = 'O'
            score = minimax(b, MAX_DEPTH, -math.inf, math.inf, False)
            b[i] = ' '
            if score > best_score:
                best_score = score
                move = i
    return move

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    board = data['board']
    
    if not is_board_full(board) and not check_winner(board, 'X'):
        ai_move = get_best_move(board)
    else:
        ai_move = -1
        
    return jsonify({'move': ai_move})

if __name__ == '__main__':
    app.run(debug=True, port=5000)