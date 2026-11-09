from quiz_game import QuizGame


def main():
    game = QuizGame()   # 객체 생성 → __init__ 자동 실행
    game.run()


if __name__ == "__main__":   # 이 파일을 직접 실행할 때만 main() 호출
    main()
