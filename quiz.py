class Quiz:
    """퀴즈 한 문제를 표현하는 클래스"""

    def __init__(self, question, choices, answer, hint=""):
        self.question = question    # str  : 문제
        self.choices = choices      # list : 선택지 4개
        self.answer = answer        # int  : 정답 번호 (1~4)
        self.hint = hint            # str  : 힌트 (없으면 빈 문자열)

    def display(self, number):
        """문제와 선택지를 화면에 출력"""
        print("-" * 40)
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for i, choice in enumerate(self.choices, start=1):   # 1부터 번호 붙이기
            print(f"{i}. {choice}")
        print()

    def is_correct(self, user_answer):
        """정답이면 True, 아니면 False (bool 반환)"""
        return user_answer == self.answer

    def to_dict(self):
        """JSON 저장용 dict로 변환"""
        return {"question": self.question, "choices": self.choices, "answer": self.answer, "hint": self.hint}

    @classmethod
    def from_dict(cls, data):
        """dict(JSON에서 읽은 값) → Quiz 객체. 형식이 틀리면 ValueError"""
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        hint = data.get("hint", "")      # 힌트 기능 이전에 저장된 파일에는 hint가 없음 → 빈 문자열
        if not isinstance(hint, str):
            raise ValueError("힌트 형식이 올바르지 않습니다.")
        if not isinstance(question, str) or not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("퀴즈 형식이 올바르지 않습니다.")
        if not isinstance(answer, int) or not 1 <= answer <= 4:
            raise ValueError("정답 번호가 올바르지 않습니다.")
        return cls(question, choices, answer, hint)
