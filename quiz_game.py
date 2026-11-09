from default_quizzes import get_default_quizzes


class QuizGame:
    """게임 전체(메뉴, 진행, 저장)를 관리하는 클래스"""

    def __init__(self):
        self.quizzes = get_default_quizzes()   # 퀴즈 목록 (list of Quiz)
        self.best_score = None     # 최고 점수 (아직 없으면 None)

    # ---------- 입력 처리 ----------
    def get_number(self, prompt, min_value, max_value):
        """min_value~max_value 사이의 정수를 받을 때까지 반복해서 묻는다."""
        while True:
            raw = input(prompt).strip()               # 앞뒤 공백 제거
            if raw == "":
                print("⚠️ 입력이 비어 있습니다. 다시 입력하세요.")
                continue
            try:
                number = int(raw)                     # "abc"면 ValueError 발생
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            if not min_value <= number <= max_value:
                print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")
                continue
            return number

    # ---------- 메뉴 ----------
    def show_menu(self):
        print("=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def run(self):
        while True:
            self.show_menu()
            choice = self.get_number("선택: ", 1, 5)
            if choice == 1:
                self.play()
            elif choice == 2:
                print("(준비 중) 퀴즈 추가")
            elif choice == 3:
                print("(준비 중) 퀴즈 목록")
            elif choice == 4:
                print("(준비 중) 점수 확인")
            else:
                print("👋 게임을 종료합니다. 안녕히 가세요!")
                break

    # ---------- 기능 ----------
    def play(self):
        """저장된 퀴즈를 차례로 출제하고 결과를 보여준다."""
        if not self.quizzes:                       # 빈 리스트는 False로 취급
            print("📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return
        total = len(self.quizzes)
        correct = 0
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)\n")
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            user_answer = self.get_number("정답 입력: ", 1, 4)
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!\n")
                correct += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.\n")
        score = int(correct / total * 100)
        print("=" * 40)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        print("=" * 40)
