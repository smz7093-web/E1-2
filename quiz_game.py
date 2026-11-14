import json
import random
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
        self.best_correct = 0      # 최고 점수 기록 당시 맞힌 문제 수
        self.best_total = 0        # 최고 점수 기록 당시 전체 문제 수
        self.load()                # 시작할 때 불러오기

    # ---------- 파일 저장/불러오기 ----------
    def reset_to_default(self):
        """퀴즈를 기본 퀴즈로, 최고 점수 기록을 초기 상태로 되돌린다."""
        self.quizzes = get_default_quizzes()
        self.best_score = None
        self.best_correct = 0
        self.best_total = 0

    def load(self):
        """state.json을 읽어 퀴즈와 최고 점수를 복원한다. (없거나 손상되면 기본값)"""
        if not STATE_FILE.exists():      # 첫 실행
            print("📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            self.reset_to_default()
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
            self.reset_to_default()
            self.save()                                  # 정상 파일로 덮어쓰기
        except OSError as e:                             # 권한 문제 등 읽기 오류
            print(f"⚠️ 파일을 읽을 수 없습니다: {e}. 기본 퀴즈로 시작합니다.")
            self.reset_to_default()

    def save(self):
        """현재 퀴즈 목록과 최고 점수를 state.json에 저장한다."""
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
                number = None                         # 숫자가 아님 → 아래에서 오류 처리
            if number is not None and min_value <= number <= max_value:
                return number
            print(f"⚠️ 잘못된 입력입니다. {min_value}-{max_value} 사이의 숫자를 입력하세요.")

    def ask_answer(self, quiz):
        """정답 번호를 입력받는다. 힌트가 있으면 0으로 힌트를 볼 수 있다. → (답, 힌트 사용 여부)"""
        if not quiz.hint:
            return self.get_number("정답 입력: ", 1, 4), False
        answer = self.get_number("정답 입력 (0=힌트 보기): ", 0, 4)
        if answer != 0:
            return answer, False
        print(f"💡 힌트: {quiz.hint}  (힌트를 보면 맞혀도 절반 점수)")
        return self.get_number("정답 입력: ", 1, 4), True

    def get_text(self, prompt):
        """빈 문자열이 아닌 텍스트를 받을 때까지 반복해서 묻는다."""
        while True:
            text = input(prompt).strip()
            if text:
                return text
            print("⚠️ 빈 값은 입력할 수 없습니다.")

    # ---------- 메뉴 ----------
    def show_menu(self):
        """메인 메뉴를 출력한다."""
        print("=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 퀴즈 삭제")
        print("6. 종료")
        print("=" * 40)

    def run(self):
        """메뉴를 반복해서 보여주고 선택한 기능을 실행한다. (종료 / Ctrl+C / EOF 시 저장 후 종료)"""
        try:
            while True:
                self.show_menu()
                choice = self.get_number("선택: ", 1, 6)
                if choice == 1:
                    self.play()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                elif choice == 5:
                    self.delete_quiz()
                else:
                    self.save()
                    print("👋 게임을 종료합니다. 안녕히 가세요!")
                    break
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C → KeyboardInterrupt / 입력 스트림 종료(Ctrl+Z, Ctrl+D 등) → EOFError
            print("\n\n⚠️ 입력이 중단되었습니다. 데이터를 저장하고 종료합니다.")
            self.save()

    # ---------- 기능 ----------
    def play(self):
        """풀 문제 수를 입력받아 무작위로 골라 출제하고 결과를 보여준다."""
        if not self.quizzes:                       # 빈 리스트는 False로 취급
            print("📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return
        max_count = len(self.quizzes)
        count = self.get_number(f"\n몇 문제를 풀까요? (1-{max_count}): ", 1, max_count)
        # random.sample: 원본 리스트는 그대로 두고, count개를 겹치지 않게 무작위로 뽑아 새 리스트로 반환
        selected = random.sample(self.quizzes, count)
        total = len(selected)
        correct = 0
        points = 0          # 맞히면 1점, 힌트를 보고 맞히면 0.5점
        hints_used = 0
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제, 무작위 순서)\n")
        for number, quiz in enumerate(selected, start=1):
            quiz.display(number)
            user_answer, used_hint = self.ask_answer(quiz)
            if used_hint:
                hints_used += 1
            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!" + (" (힌트 사용: 절반 점수)" if used_hint else "") + "\n")
                correct += 1
                points += 0.5 if used_hint else 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.\n")
        score = int(points / total * 100)
        print("=" * 40)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if hints_used:
            print(f"💡 힌트 사용: {hints_used}회")
        print("=" * 40)
        self.update_best_score(score, correct, total)

    def add_quiz(self):
        """사용자에게 문제·선택지·정답·힌트(선택)를 입력받아 새 퀴즈를 추가하고 저장한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.\n")
        question = self.get_text("문제를 입력하세요: ")
        choices = [self.get_text(f"선택지 {i}: ") for i in range(1, 5)]   # 4개 입력
        answer = self.get_number("정답 번호 (1-4): ", 1, 4)
        hint = input("힌트 (없으면 Enter): ").strip()                     # 힌트는 선택 사항
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save()                                                       # 바로 파일에 저장
        print("\n✅ 퀴즈가 추가되었습니다!\n")

    def list_quizzes(self):
        """등록된 퀴즈의 문제 목록을 번호와 함께 출력한다."""
        if not self.quizzes:
            print("📭 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)\n")
        print("-" * 40)
        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"[{i}] {quiz.question}")
        print("-" * 40)

    def delete_quiz(self):
        """목록을 보여주고 번호를 입력받아 퀴즈를 삭제한 뒤 저장한다. (0 입력 시 취소)"""
        if not self.quizzes:
            print("📭 삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        number = self.get_number(f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}, 0=취소): ", 0, len(self.quizzes))
        if number == 0:
            print("↩️ 삭제를 취소했습니다.\n")
            return
        target = self.quizzes[number - 1]          # 화면 번호는 1부터, 리스트 인덱스는 0부터
        confirm = self.get_number(f"'{target.question}'\n정말 삭제할까요? (1=예, 2=아니오): ", 1, 2)
        if confirm == 2:
            print("↩️ 삭제를 취소했습니다.\n")
            return
        self.quizzes.pop(number - 1)
        self.save()
        print(f"🗑️ 퀴즈가 삭제되었습니다. (남은 퀴즈 {len(self.quizzes)}개)\n")

    def update_best_score(self, score, correct, total):
        """이번 점수가 최고 점수보다 높으면 갱신하고 저장한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            print("🎉 새로운 최고 점수입니다!")
            self.save()

    def show_score(self):
        """최고 점수 기록을 출력한다."""
        if self.best_score is None:
            print("📭 아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어보세요!")
            return
        print(f"\n🏆 최고 점수: {self.best_score}점 ({self.best_total}문제 중 {self.best_correct}문제 정답)\n")
