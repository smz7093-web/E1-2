from quiz import Quiz


def get_default_quizzes():
    """기본 퀴즈 목록(Python & Git 기초)을 새로 만들어 반환"""
    return [
        Quiz(
            "Python의 창시자는?",
            ["Guido van Rossum", "Linus Torvalds", "Bjarne Stroustrup", "James Gosling"],
            1,
        ),
        Quiz(
            "Python에서 리스트의 길이를 구하는 함수는?",
            ["size()", "count()", "len()", "length()"],
            3,
        ),
        Quiz(
            "다음 중 변경할 수 없는(immutable) 자료형은?",
            ["list", "dict", "set", "tuple"],
            4,
        ),
        Quiz(
            "Git에서 변경 사항을 스테이징 영역에 올리는 명령어는?",
            ["git commit", "git add", "git push", "git pull"],
            2,
        ),
        Quiz(
            "원격 저장소의 새 커밋을 가져와 현재 브랜치에 합치는 Git 명령어는?",
            ["git clone", "git push", "git pull", "git init"],
            3,
        ),
    ]
