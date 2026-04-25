# Python 프로그래밍 기초

## Python이란?

Python은 1991년 귀도 반 로섬이 개발한 고급 프로그래밍 언어입니다. 읽기 쉬운 문법과 강력한 기능으로 전 세계에서 가장 인기 있는 언어 중 하나입니다.

## 주요 특징

### 1. 간결한 문법
```python
# Hello World
print("Hello, World!")

# 변수 선언
name = "Alice"
age = 30
```

### 2. 동적 타이핑
타입을 명시하지 않아도 자동으로 결정됩니다.

### 3. 객체 지향
클래스와 상속을 지원합니다.

### 4. 풍부한 라이브러리
표준 라이브러리와 PyPI를 통해 수많은 패키지를 사용할 수 있습니다.

## 데이터 타입

### 기본 타입
- **정수 (int)**: 1, 42, -10
- **실수 (float)**: 3.14, -0.5
- **문자열 (str)**: "hello", 'world'
- **불린 (bool)**: True, False

### 컬렉션
- **리스트 (list)**: [1, 2, 3]
- **튜플 (tuple)**: (1, 2, 3)
- **딕셔너리 (dict)**: {"key": "value"}
- **집합 (set)**: {1, 2, 3}

## 제어 구조

### 조건문
```python
if x > 0:
    print("양수")
elif x < 0:
    print("음수")
else:
    print("0")
```

### 반복문
```python
# for 루프
for i in range(5):
    print(i)

# while 루프
while x > 0:
    x -= 1
```

## 함수

```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")
```

## 클래스

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"I'm {self.name}, {self.age} years old"
```

## 활용 분야

1. **웹 개발**: Django, Flask
2. **데이터 과학**: Pandas, NumPy
3. **머신러닝**: TensorFlow, PyTorch
4. **자동화**: 스크립팅, 작업 자동화
