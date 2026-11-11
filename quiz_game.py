import json
from pathlib import Path

from quiz import Quiz
from default_quizzes import get_default_quizzes

# 프로젝트 루트(이 파일이 있는 폴더)의 state.json
# → 어느 폴더에서 실행하든 같은 위치를 사용하게 됨
STATE_FILE = Path(__file__).parent / "state.json"


class QuizGame:
    """게임 전체(메뉴, 진행, 저장)를 관리하는 클래스"""

    def __init__(self):
        self.quizzes = []          # 퀴즈 목록 (list of Quiz)
        self.best_score = None     # 최고 점수 (아직 없으면 None)
        self.best_correct = 0
        self.best_total = 0
        self.load()                # 시작할 때 불러오기

    # ---------- 파일 저장/불러오기 ----------
    def load(self):
        if not STATE_FILE.exists():      # 첫 실행
            print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            self.quizzes = get_default_quizzes()
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)                      # JSON 텍스트 → dict
            self.quizzes = [Quiz.from_dict(q) for q in data["quizzes"]]
            self.best_score = data.get("best_score")
            self.best_correct = data.get("best_correct", 0)
            self.best_total = data.get("best_total", 0)
            score_text = "없음" if self.best_score is None else f"{self.best_score}점"
            print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {score_text})")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # JSON 문법이 깨짐 / 키가 없음 / 타입이 이상함 / 값이 범위 밖
            print("⚠️ 데이터 파일이 손상되어 기본 퀴즈로 복구합니다.")
            self.quizzes = get_default_quizzes()
            self.best_score = None
            self.best_correct = 0
            self.best_total = 0
            self.save()                                  # 정상 파일로 덮어쓰기
        except OSError as e:                             # 권한 문제 등 읽기 오류
            print(f"⚠️ 파일을 읽을 수 없습니다: {e}. 기본 퀴즈로 시작합니다.")
            self.quizzes = get_default_quizzes()

    def save(self):
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],   # Quiz 객체 → dict
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)   # 한글 그대로, 보기 좋게
        except OSError as e:
            print(f"⚠️ 저장에 실패했습니다: {e}")

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

    def get_text(self, prompt):
        """빈 문자열이 아닌 텍스트를 받을 때까지 반복"""
        while True:
            text = input(prompt).strip()
            if text:
                return text
            print("⚠️ 빈 값은 입력할 수 없습니다.")

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
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_score()
            else:
                self.save()
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
        self.update_best_score(score, correct, total)

    def add_quiz(self):
        print("\n📌 새로운 퀴즈를 추가합니다.\n")
        question = self.get_text("문제를 입력하세요: ")
        choices = [self.get_text(f"선택지 {i}: ") for i in range(1, 5)]   # 4개 입력
        answer = self.get_number("정답 번호 (1-4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        self.save()                                                       # 바로 파일에 저장
        print("\n✅ 퀴즈가 추가되었습니다!\n")

    def list_quizzes(self):
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)\n")
        print("-" * 40)
        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"[{i}] {quiz.question}")
        print("-" * 40)

    def update_best_score(self, score, correct, total):
        """이번 점수가 최고 점수보다 높으면 갱신하고 저장"""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            print("🎉 새로운 최고 점수입니다!")
            self.save()

    def show_score(self):
        if self.best_score is None:
            print("📭 아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어보세요!")
            return
        print(f"\n🏆 최고 점수: {self.best_score}점 ({self.best_total}문제 중 {self.best_correct}문제 정답)\n")
